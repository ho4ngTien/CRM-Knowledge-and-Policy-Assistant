"""Local escalation service preserving task continuity (KNW 04)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.referral.models import LocalReferral
from src.modules.referral.schemas import (
    ReferralCreateRequest,
    ReferralResponse,
    ReferralUpdateRequest,
)
from src.shared.auth import AuthenticatedUser
from src.shared.enums import PolicyFamily, ReferralStatus, UserRole
from src.shared.exceptions import PolicyNotFound

_REFERRAL_PRIVILEGED_ROLES: frozenset[UserRole] = frozenset(
    {
        UserRole.POLICY_OWNER,
        UserRole.REFERRAL_HANDLER,
        UserRole.STEWARD,
        UserRole.ADMINISTRATOR,
    }
)


class ReferralService:
    """Manages local referrals across referred -> owner_responded -> closed states."""

    async def create_referral(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        payload: ReferralCreateRequest,
    ) -> ReferralResponse:
        """Create a persisted local referral ticket linked to task_id."""
        ref = LocalReferral(
            id=f"REF-{uuid.uuid4().hex[:10].upper()}",
            task_id=payload.task_id,
            answer_package_id=payload.answer_package_id,
            requester_id=user.user_id,
            target_owner=payload.target_owner,
            policy_family=payload.policy_family.value,
            question_summary=payload.question_summary,
            status=ReferralStatus.REFERRED.value,
        )
        db.add(ref)
        await db.commit()
        await db.refresh(ref)
        return self._to_schema(ref)

    async def list_referrals(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        status_filter: ReferralStatus | None = None,
    ) -> list[ReferralResponse]:
        """List referral tickets scoped to requester unless user holds privileged handler role."""
        stmt = select(LocalReferral)
        if not (user.roles & _REFERRAL_PRIVILEGED_ROLES):
            stmt = stmt.where(LocalReferral.requester_id == user.user_id)
        if status_filter is not None:
            stmt = stmt.where(LocalReferral.status == status_filter.value)
        rows = (await db.execute(stmt.order_by(LocalReferral.created_at.desc()))).scalars().all()
        return [self._to_schema(r) for r in rows]

    async def update_referral(
        self,
        db: AsyncSession,
        referral_id: str,
        payload: ReferralUpdateRequest,
    ) -> ReferralResponse:
        """Update referral status and owner response note."""
        ref = await db.get(LocalReferral, referral_id)
        if ref is None:
            raise PolicyNotFound(f"Referral {referral_id} was not found.")
        ref.status = payload.status.value
        if payload.owner_response is not None:
            ref.owner_response = payload.owner_response
        if payload.resolution_note is not None:
            ref.resolution_note = payload.resolution_note
        await db.commit()
        await db.refresh(ref)
        return self._to_schema(ref)

    def _to_schema(self, row: LocalReferral) -> ReferralResponse:
        return ReferralResponse(
            id=row.id,
            task_id=row.task_id,
            answer_package_id=row.answer_package_id,
            requester_id=row.requester_id,
            target_owner=row.target_owner,
            policy_family=PolicyFamily(row.policy_family),
            question_summary=row.question_summary,
            status=ReferralStatus(row.status),
            owner_response=row.owner_response,
            resolution_note=row.resolution_note,
            created_at=row.created_at,
        )
