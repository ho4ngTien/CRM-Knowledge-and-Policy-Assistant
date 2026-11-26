"""Local referral service — KNW 05 three-state lifecycle.

State machine (strict sequential, no skipping):
  referred -> owner_responded -> closed

Invariants:
- 0% CRM writeback (never creates CRM tasks or updates CRM customer records)
- 0% external message dispatch (local record only)
- 0% self-approval
- Stores: PII-sanitized question, minimal context, hold_reason & owner_role
- Separately tracks all 3 KNW 05 states with timestamps and actor IDs
"""

import uuid
from datetime import UTC, datetime
from typing import Any

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
from src.shared.exceptions import AccessDenied, PolicyNotFound, SourceConflict
from src.shared.pii_guard import scan_query_for_pii

_REFERRAL_PRIVILEGED_ROLES: frozenset[UserRole] = frozenset(
    {
        UserRole.POLICY_OWNER,
        UserRole.REFERRAL_HANDLER,
        UserRole.STEWARD,
        UserRole.ADMINISTRATOR,
    }
)

# KNW 05: allowed forward transitions only — no backward, no skip
_ALLOWED_TRANSITIONS: dict[ReferralStatus, frozenset[ReferralStatus]] = {
    ReferralStatus.REFERRED: frozenset({ReferralStatus.OWNER_RESPONDED}),
    ReferralStatus.OWNER_RESPONDED: frozenset({ReferralStatus.CLOSED}),
    ReferralStatus.CLOSED: frozenset(),  # terminal state
}


def _sanitize_context_value(value: Any) -> Any:
    """Recursively strip suspected PII from minimal_context values (SEC 02)."""
    if isinstance(value, str):
        scan = scan_query_for_pii(value)
        return scan.redacted_preview if scan.has_suspected_pii else value
    if isinstance(value, list):
        return [_sanitize_context_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _sanitize_context_value(v) for k, v in value.items()}
    return value


class ReferralService:
    """Manages local referrals across referred -> owner_responded -> closed (KNW 05)."""

    async def create_referral(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        payload: ReferralCreateRequest,
    ) -> ReferralResponse:
        """Create a persisted local referral record linked to task_id.

        Saves PII-minimized question, minimal_context, hold_reason, and owner_role.
        Does NOT send messages, create CRM tasks, or self-approve.
        """
        question_scan = scan_query_for_pii(payload.question_summary)
        safe_question = (
            question_scan.redacted_preview
            if question_scan.has_suspected_pii
            else payload.question_summary
        )
        safe_context = _sanitize_context_value(payload.minimal_context)

        ref = LocalReferral(
            id=f"REF-{uuid.uuid4().hex[:10].upper()}",
            task_id=payload.task_id,
            answer_package_id=payload.answer_package_id,
            requester_id=user.user_id,
            owner_role=payload.owner_role,
            target_owner=payload.target_owner,
            policy_family=payload.policy_family.value,
            question_summary=safe_question,
            minimal_context=safe_context if isinstance(safe_context, dict) else {},
            hold_reason=payload.hold_reason,
            status=ReferralStatus.REFERRED.value,
        )
        db.add(ref)
        await db.commit()
        await db.refresh(ref)
        return self._to_schema(ref)

    async def get_referral(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        referral_id: str,
    ) -> ReferralResponse:
        """Fetch a single local referral record, enforcing requester/owner scope."""
        ref = await db.get(LocalReferral, referral_id)
        if ref is None:
            raise PolicyNotFound(f"Referral {referral_id} not found.")
        if not (user.roles & _REFERRAL_PRIVILEGED_ROLES) and ref.requester_id != user.user_id:
            raise AccessDenied("User lacks permission to view another user's referral.")
        return self._to_schema(ref)

    async def list_referrals(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        status_filter: ReferralStatus | None = None,
        task_id: str | None = None,
    ) -> list[ReferralResponse]:
        """List referral tickets scoped to requester unless user holds privileged handler role."""
        stmt = select(LocalReferral)
        if not (user.roles & _REFERRAL_PRIVILEGED_ROLES):
            stmt = stmt.where(LocalReferral.requester_id == user.user_id)
        if status_filter is not None:
            stmt = stmt.where(LocalReferral.status == status_filter.value)
        if task_id is not None:
            stmt = stmt.where(LocalReferral.task_id == task_id)
        rows = (await db.execute(stmt.order_by(LocalReferral.created_at.desc()))).scalars().all()
        return [self._to_schema(r) for r in rows]

    async def update_referral(
        self,
        db: AsyncSession,
        referral_id: str,
        payload: ReferralUpdateRequest,
        user: AuthenticatedUser,
    ) -> ReferralResponse:
        """Transition referral status enforcing KNW 05 sequential state machine.

        Guard: referred -> owner_responded -> closed only.
        Raises AccessDenied if user lacks privileged handler role.
        Raises PolicyNotFound if referral_id does not exist.
        Raises SourceConflict if state transition is illegal.
        """
        if not (user.roles & _REFERRAL_PRIVILEGED_ROLES):
            raise AccessDenied(
                "Only policy_owner, referral_handler, steward, or administrator may "
                "record owner responses or close a referral."
            )

        ref = await db.get(LocalReferral, referral_id)
        if ref is None:
            raise PolicyNotFound(f"Referral {referral_id} not found.")

        current = ReferralStatus(ref.status)
        allowed = _ALLOWED_TRANSITIONS[current]
        if payload.status not in allowed:
            allowed_labels = [s.value for s in allowed] or ["none (terminal)"]
            raise SourceConflict(
                f"KNW 05 state guard: transition {current.value!r} -> {payload.status.value!r} "
                f"is not allowed. Allowed next states: {allowed_labels}."
            )

        now = datetime.now(UTC)
        ref.status = payload.status.value
        if payload.status == ReferralStatus.OWNER_RESPONDED:
            ref.owner_response = payload.owner_response
            ref.owner_responded_at = now
            ref.responded_by = user.user_id
        elif payload.status == ReferralStatus.CLOSED:
            if payload.owner_response is not None:
                ref.owner_response = payload.owner_response
            ref.resolution_note = payload.resolution_note
            ref.closed_at = now
            ref.closed_by = user.user_id

        await db.commit()
        await db.refresh(ref)
        return self._to_schema(ref)

    def _to_schema(self, row: LocalReferral) -> ReferralResponse:
        return ReferralResponse(
            id=row.id,
            task_id=row.task_id,
            answer_package_id=row.answer_package_id,
            requester_id=row.requester_id,
            owner_role=row.owner_role,
            target_owner=row.target_owner,
            policy_family=PolicyFamily(row.policy_family),
            question_summary=row.question_summary,
            minimal_context=row.minimal_context or {},
            hold_reason=row.hold_reason,
            status=ReferralStatus(row.status),
            owner_response=row.owner_response,
            owner_responded_at=row.owner_responded_at,
            responded_by=row.responded_by,
            resolution_note=row.resolution_note,
            closed_at=row.closed_at,
            closed_by=row.closed_by,
            created_at=row.created_at,
        )
