"""Admin lifecycle approval, instant withdrawal, and Base Scope ops service."""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.admin.models import ALLOWED_LIFECYCLE_TRANSITIONS
from src.modules.admin.schemas import (
    AdminOpsSummaryResponse,
    InstantWithdrawalResponse,
    LifecycleTransitionResponse,
)
from src.modules.answer.models import AnswerCitationRecord, AnswerPackageRecord
from src.modules.knowledge.models import DocumentVersion, Passage
from src.modules.policy.models import CriticalField, PolicyLifecycleEvent, PolicyVersion
from src.shared.auth import AuthenticatedUser
from src.shared.enums import PolicyLifecycleStatus, UserRole
from src.shared.exceptions import AccessDenied, PolicyNotFound, SourceConflict


class AdminService:
    """Enforces 7-state policy governance and instant withdrawal semantics (KNW 03, KNW 04)."""

    async def transition_policy_status(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        policy_version_id: str,
        target_status: PolicyLifecycleStatus,
        reason: str,
    ) -> LifecycleTransitionResponse:
        """Advance a policy version strictly along allowed KNW 03 transitions."""
        version = await db.get(PolicyVersion, policy_version_id)
        if version is None:
            raise PolicyNotFound(f"Policy version {policy_version_id} was not found.")

        current_status = PolicyLifecycleStatus(version.status)
        if target_status not in ALLOWED_LIFECYCLE_TRANSITIONS.get(current_status, frozenset()):
            raise SourceConflict(
                f"Illegal transition from {current_status.value} to {target_status.value}."
            )

        if target_status in {
            PolicyLifecycleStatus.APPROVED,
            PolicyLifecycleStatus.SCHEDULED,
            PolicyLifecycleStatus.EFFECTIVE,
        } and not (user.roles & {UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR}):
            raise AccessDenied("Only policy_owner or administrator may approve or publish rules.")

        if target_status == PolicyLifecycleStatus.EFFECTIVE:
            tz = ZoneInfo(settings.APP_TIMEZONE)
            now_vn = datetime.now(tz)
            eff_from = (
                version.effective_from.astimezone(tz)
                if version.effective_from.tzinfo is not None
                else version.effective_from.replace(tzinfo=tz)
            )
            if eff_from > now_vn:
                raise SourceConflict(
                    "Scheduled policy cannot become effective prior to VN effective_from timestamp."
                )

        version.status = target_status.value
        db.add(
            PolicyLifecycleEvent(
                policy_version_id=policy_version_id,
                from_status=current_status.value,
                to_status=target_status.value,
                actor_id=user.user_id,
                actor_role=",".join(sorted(r.value for r in user.roles)),
                reason=reason,
            )
        )
        await db.commit()
        return LifecycleTransitionResponse(
            policy_version_id=policy_version_id,
            previous_status=current_status,
            current_status=target_status,
            actor_id=user.user_id,
        )

    async def withdraw_policy_immediately(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        policy_version_id: str,
        reason: str,
    ) -> InstantWithdrawalResponse:
        """Update authoritative DB to withdrawn first, invalidate answers, and trigger purge."""
        version = await db.get(PolicyVersion, policy_version_id)
        if version is None:
            raise PolicyNotFound(f"Policy version {policy_version_id} was not found.")

        prev_status = version.status
        version.status = PolicyLifecycleStatus.WITHDRAWN.value

        await db.execute(
            update(DocumentVersion)
            .where(DocumentVersion.id == version.document_version_id)
            .values(status=PolicyLifecycleStatus.WITHDRAWN.value)
        )
        await db.execute(
            update(Passage)
            .where(Passage.document_version_id == version.document_version_id)
            .values(status=PolicyLifecycleStatus.WITHDRAWN.value)
        )
        await db.execute(
            update(CriticalField)
            .where(CriticalField.policy_version_id == policy_version_id)
            .values(status=PolicyLifecycleStatus.WITHDRAWN.value)
        )

        stmt = (
            update(AnswerPackageRecord)
            .where(
                AnswerPackageRecord.id.in_(
                    AnswerCitationRecord.__table__.select()
                    .with_only_columns(AnswerCitationRecord.answer_package_id)
                    .where(
                        AnswerCitationRecord.document_version_id == version.document_version_id
                    )
                )
            )
            .values(is_stale=True)
        )
        stale_result = await db.execute(stmt)

        db.add(
            PolicyLifecycleEvent(
                policy_version_id=policy_version_id,
                from_status=prev_status,
                to_status=PolicyLifecycleStatus.WITHDRAWN.value,
                actor_id=user.user_id,
                actor_role=",".join(sorted(r.value for r in user.roles)),
                reason=reason,
            )
        )
        await db.commit()

        return InstantWithdrawalResponse(
            policy_version_id=policy_version_id,
            status=PolicyLifecycleStatus.WITHDRAWN,
            stale_answers_marked=int(stale_result.rowcount or 0),
            cache_purge_deadline_seconds=settings.CACHE_WITHDRAWAL_MAX_SECONDS,
        )

    def get_ops_summary(self) -> AdminOpsSummaryResponse:
        """Expose active RFP/SRS boundaries and Base Scope pilot telemetry limits."""
        return AdminOpsSummaryResponse(
            timezone=settings.APP_TIMEZONE,
            answer_streaming_enabled=settings.ENABLE_ANSWER_STREAMING,
            snapshot_staleness_threshold_hours=settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
            cache_withdrawal_max_seconds=settings.CACHE_WITHDRAWAL_MAX_SECONDS,
            pilot_max_named_users=settings.PILOT_MAX_NAMED_USERS,
            pilot_max_concurrent_sessions=settings.PILOT_MAX_CONCURRENT_SESSIONS,
            corpus_max_documents=settings.CORPUS_MAX_DOCUMENTS,
            corpus_max_passages=settings.CORPUS_MAX_PASSAGES,
            corpus_max_critical_fields=settings.CORPUS_MAX_CRITICAL_FIELDS,
        )
