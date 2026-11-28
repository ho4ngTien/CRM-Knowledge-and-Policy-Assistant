"""Admin lifecycle approval, instant withdrawal, and Base Scope ops service."""

import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from celery import Celery
from kombu.exceptions import KombuError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.admin.models import ALLOWED_LIFECYCLE_TRANSITIONS, KNW03_LIFECYCLE_STATUSES
from src.modules.admin.schemas import (
    AdminOpsSummaryResponse,
    InstantWithdrawalResponse,
    LifecycleTransitionResponse,
)
from src.modules.knowledge.change_impact import ChangeImpactService
from src.modules.knowledge.change_impact_schemas import ChangeImpactReportResponse
from src.modules.knowledge.models import ChangeImpactReport, DocumentVersion, Passage
from src.modules.policy.models import CriticalField, PolicyLifecycleEvent, PolicyVersion
from src.shared.auth import AuthenticatedUser
from src.shared.contracts import CachePurgePort
from src.shared.enums import PolicyLifecycleStatus, UserRole
from src.shared.exceptions import AccessDenied, PolicyNotFound, SourceConflict


class AdminService:
    """Enforces 7-state policy governance and instant withdrawal semantics (KNW 03, KNW 04)."""

    def __init__(self) -> None:
        self._emergency_disabled: bool = False
        self._emergency_disable_reason: str | None = None
        self._change_impact = ChangeImpactService()

    async def transition_policy_status(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        policy_version_id: str,
        target_status: PolicyLifecycleStatus,
        reason: str,
        cache_purger: CachePurgePort | None = None,
    ) -> LifecycleTransitionResponse:
        """Advance a policy version strictly along allowed KNW 03 transitions."""
        version = await db.get(PolicyVersion, policy_version_id)
        if version is None:
            raise PolicyNotFound(f"Policy version {policy_version_id} was not found.")

        current_status = PolicyLifecycleStatus(version.status)
        if (
            current_status == PolicyLifecycleStatus.QUARANTINED
            or target_status == PolicyLifecycleStatus.QUARANTINED
        ):
            raise SourceConflict(
                "QUARANTINED is a DAT 02 ingestion state and cannot be entered or exited "
                "through the KNW 03 lifecycle transition API."
            )
        if current_status not in KNW03_LIFECYCLE_STATUSES or target_status not in (
            KNW03_LIFECYCLE_STATUSES
        ):
            raise SourceConflict(
                "Only the seven KNW 03 lifecycle states may use the lifecycle transition API."
            )
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
        if target_status in {
            PolicyLifecycleStatus.EFFECTIVE,
            PolicyLifecycleStatus.SUPERSEDED,
            PolicyLifecycleStatus.WITHDRAWN,
        }:
            await self._sync_authoritative_status(
                db,
                policy_version_id=policy_version_id,
                document_version_id=version.document_version_id,
                target_status=target_status,
                actor_id=user.user_id,
                reason=reason,
            )
        impact_report = None
        if target_status in {
            PolicyLifecycleStatus.EFFECTIVE,
            PolicyLifecycleStatus.SUPERSEDED,
            PolicyLifecycleStatus.WITHDRAWN,
        }:
            impact_report = await self._change_impact.record_impact(
                db,
                event_type=f"lifecycle_{target_status.value}",
                source_type="policy_lifecycle",
                source_id=policy_version_id,
                document_version_id=version.document_version_id,
                policy_version_id=policy_version_id,
                actor_id=user.user_id,
                reason=reason,
            )

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
        if target_status == PolicyLifecycleStatus.WITHDRAWN:
            await self._trigger_cache_purge(
                policy_version_id, version.document_version_id, cache_purger
            )
        return LifecycleTransitionResponse(
            policy_version_id=policy_version_id,
            previous_status=current_status,
            current_status=target_status,
            actor_id=user.user_id,
            change_impact_report_id=impact_report.id if impact_report else None,
        )

    async def withdraw_policy_immediately(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        policy_version_id: str,
        reason: str,
        cache_purger: CachePurgePort | None = None,
    ) -> InstantWithdrawalResponse:
        """Update authoritative DB to withdrawn first, invalidate answers, and trigger purge."""
        version = await db.get(PolicyVersion, policy_version_id)
        if version is None:
            raise PolicyNotFound(f"Policy version {policy_version_id} was not found.")

        prev_status = version.status
        version.status = PolicyLifecycleStatus.WITHDRAWN.value
        await self._sync_authoritative_status(
            db,
            policy_version_id=policy_version_id,
            document_version_id=version.document_version_id,
            target_status=PolicyLifecycleStatus.WITHDRAWN,
            actor_id=user.user_id,
            reason=reason,
        )
        impact_report = await self._change_impact.record_impact(
            db,
            event_type="immediate_withdrawal",
            source_type="policy_lifecycle",
            source_id=policy_version_id,
            document_version_id=version.document_version_id,
            policy_version_id=policy_version_id,
            actor_id=user.user_id,
            reason=reason,
        )

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
        await self._trigger_cache_purge(
            policy_version_id, version.document_version_id, cache_purger
        )

        return InstantWithdrawalResponse(
            policy_version_id=policy_version_id,
            status=PolicyLifecycleStatus.WITHDRAWN,
            stale_answers_marked=impact_report.stale_answers_marked,
            cache_purge_deadline_seconds=settings.CACHE_WITHDRAWAL_MAX_SECONDS,
            change_impact_report_id=impact_report.id,
        )

    async def list_change_impacts(
        self,
        db: AsyncSession,
        *,
        policy_version_id: str | None = None,
        limit: int = 50,
    ) -> list[ChangeImpactReportResponse]:
        statement = select(ChangeImpactReport).order_by(ChangeImpactReport.created_at.desc())
        if policy_version_id is not None:
            statement = statement.where(ChangeImpactReport.policy_version_id == policy_version_id)
        rows = (await db.execute(statement.limit(limit))).scalars().all()
        return [
            ChangeImpactReportResponse(
                id=row.id,
                event_type=row.event_type,
                source_type=row.source_type,
                source_id=row.source_id,
                document_version_id=row.document_version_id,
                policy_version_id=row.policy_version_id,
                actor_id=row.actor_id,
                reason=row.reason,
                stale_answers_marked=row.stale_answers_marked,
                active_view_refresh_interval_seconds=row.active_view_refresh_interval_seconds,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def _sync_authoritative_status(
        self,
        db: AsyncSession,
        *,
        policy_version_id: str,
        document_version_id: str,
        target_status: PolicyLifecycleStatus,
        actor_id: str,
        reason: str,
    ) -> None:
        """Synchronize DocumentVersion, Passage, and CriticalField rows on lifecycle transitions."""
        await db.execute(
            update(DocumentVersion)
            .where(DocumentVersion.id == document_version_id)
            .values(status=target_status.value)
        )
        passage_values: dict[str, object] = {"status": target_status.value}
        field_values: dict[str, object] = {"status": target_status.value}
        if target_status == PolicyLifecycleStatus.WITHDRAWN:
            withdrawn_at = datetime.now(UTC)
            withdrawal_meta = {
                "withdrawn_at": withdrawn_at,
                "withdrawn_by": actor_id,
                "withdrawal_reason": reason,
            }
            passage_values.update(withdrawal_meta)
            field_values.update(withdrawal_meta)
        await db.execute(
            update(Passage)
            .where(Passage.document_version_id == document_version_id)
            .values(**passage_values)
        )
        await db.execute(
            update(CriticalField)
            .where(CriticalField.policy_version_id == policy_version_id)
            .values(**field_values)
        )

    @staticmethod
    async def _trigger_cache_purge(
        policy_version_id: str,
        document_version_id: str,
        cache_purger: CachePurgePort | None,
    ) -> None:
        if cache_purger is not None:
            await cache_purger.purge_policy_caches(policy_version_id, document_version_id)
            return
        try:
            purge_app = Celery(
                "ckpa-withdrawal-purge",
                broker=settings.CELERY_BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND,
            )
            purge_app.send_task(
                "src.tasks.index_task.withdraw_and_purge_cache",
                args=(policy_version_id, document_version_id),
            )
        except KombuError as exc:
            logging.getLogger(__name__).warning(
                "withdrawal_cache_purge_enqueue_failed",
                exc_info=exc,
                extra={"policy_version_id": policy_version_id},
            )

    async def set_emergency_disable(
        self,
        user: AuthenticatedUser,
        disabled: bool,
        reason: str,
    ) -> dict[str, object]:
        """Toggle OPS 05 emergency assistant disable state (Redis scaffold for Gate G1)."""
        # TODO(G1): Persist toggle in Redis under settings.EMERGENCY_DISABLE_CACHE_KEY and audit.
        self._emergency_disabled = disabled
        self._emergency_disable_reason = reason
        return {
            "disabled": self._emergency_disabled,
            "reason": reason,
            "actor_id": user.user_id,
            "cache_key": settings.EMERGENCY_DISABLE_CACHE_KEY,
        }

    async def is_emergency_disabled(self) -> bool:
        """Check whether OPS 05 emergency assistant disable mode is currently active."""
        # TODO(G1): Read state from Redis under settings.EMERGENCY_DISABLE_CACHE_KEY.
        return self._emergency_disabled

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
