"""Restricted audit logging, OPS 06 usage metering, and OPS 08 open exit export service."""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.audit.models import AuditLog, UsageCostMeter
from src.modules.audit.schemas import (
    AuditLogResponse,
    CostMeterSummaryResponse,
    OpenExportResponse,
)
from src.shared.contracts import QuotaStatus


class AuditService:
    """Provides access-controlled audit logs and full-lifecycle cost telemetry."""

    async def list_audit_logs(
        self, db: AsyncSession, *, limit: int = 100
    ) -> list[AuditLogResponse]:
        """Return recent audit entries strictly for authorized security/admin reviewers."""
        rows = (
            await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit))
        ).scalars().all()
        return [
            AuditLogResponse(
                id=r.id,
                actor_id=r.actor_id,
                actor_role=r.actor_role,
                action=r.action,
                resource_type=r.resource_type,
                resource_id=r.resource_id,
                outcome=r.outcome,
                detail=r.detail,
                created_at=r.created_at,
            )
            for r in rows
        ]

    async def summarize_month_usage(
        self, db: AsyncSession, month_key: str | None = None
    ) -> CostMeterSummaryResponse:
        """Aggregate monthly packages, LLM calls, tokens, holds, and errors (OPS 06)."""
        target_month = month_key or datetime.now(ZoneInfo(settings.APP_TIMEZONE)).strftime("%Y-%m")
        stmt = select(
            func.count(UsageCostMeter.id),
            func.coalesce(func.sum(UsageCostMeter.llm_calls), 0),
            func.coalesce(func.sum(UsageCostMeter.input_tokens), 0),
            func.coalesce(func.sum(UsageCostMeter.output_tokens), 0),
        ).where(UsageCostMeter.month_key == target_month)
        total_pkg, total_calls, total_in, total_out = (await db.execute(stmt)).one()

        holds = (
            await db.execute(
                select(func.count(UsageCostMeter.id)).where(
                    UsageCostMeter.month_key == target_month,
                    UsageCostMeter.is_hold.is_(True),
                )
            )
        ).scalar_one()
        errors = (
            await db.execute(
                select(func.count(UsageCostMeter.id)).where(
                    UsageCostMeter.month_key == target_month,
                    UsageCostMeter.is_error.is_(True),
                )
            )
        ).scalar_one()

        return CostMeterSummaryResponse(
            month_key=target_month,
            total_packages=int(total_pkg),
            package_quota=settings.ANSWER_MAX_PACKAGES_PER_MONTH,
            total_llm_calls=int(total_calls),
            llm_call_quota=settings.LLM_MAX_CALLS_PER_MONTH,
            total_input_tokens=int(total_in),
            total_output_tokens=int(total_out),
            hold_count=int(holds),
            error_count=int(errors),
        )

    def build_open_export_manifest(self) -> OpenExportResponse:
        """Describe open non-proprietary export bundle for OPS 08 / Gate G4 exit readiness."""
        return OpenExportResponse(
            timezone=settings.APP_TIMEZONE,
            record_counts={"passages": 0, "critical_fields": 0, "referrals": 0},
        )

    async def check_monthly_quota(
        self,
        db: AsyncSession | None = None,
        month_key: str | None = None,
    ) -> QuotaStatus:
        """Check Common Bid Basis monthly package and LLM call quotas (OPS 06)."""
        target_month = month_key or datetime.now(ZoneInfo(settings.APP_TIMEZONE)).strftime("%Y-%m")
        if db is None:
            return QuotaStatus(
                month_key=target_month,
                packages_used=0,
                package_quota=settings.ANSWER_MAX_PACKAGES_PER_MONTH,
                llm_calls_used=0,
                llm_call_quota=settings.LLM_MAX_CALLS_PER_MONTH,
                allowed=False,
                reason="Authoritative database session required for OPS 06 quota check.",
            )

        summary = await self.summarize_month_usage(db, month_key=target_month)
        pkg_ok = summary.total_packages < summary.package_quota
        llm_ok = summary.total_llm_calls < summary.llm_call_quota
        allowed = pkg_ok and llm_ok
        reason: str | None = None
        if not pkg_ok:
            reason = (
                f"Monthly AnswerPackage quota reached "
                f"({summary.total_packages}/{summary.package_quota})."
            )
        elif not llm_ok:
            reason = (
                f"Monthly LLM call quota reached "
                f"({summary.total_llm_calls}/{summary.llm_call_quota})."
            )
        return QuotaStatus(
            month_key=target_month,
            packages_used=summary.total_packages,
            package_quota=summary.package_quota,
            llm_calls_used=summary.total_llm_calls,
            llm_call_quota=summary.llm_call_quota,
            allowed=allowed,
            reason=reason,
        )

    async def record_usage_meter(
        self,
        db: AsyncSession | None = None,
        *,
        task_id: str,
        answer_package_id: str | None = None,
        llm_calls: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        is_hold: bool = False,
        is_error: bool = False,
        estimated_cost_vnd: float = 0.0,
    ) -> None:
        """Record per-task token and call usage into UsageCostMeter (OPS 06)."""
        if db is None:
            return
        month_key = datetime.now(ZoneInfo(settings.APP_TIMEZONE)).strftime("%Y-%m")
        db.add(
            UsageCostMeter(
                month_key=month_key,
                task_id=task_id,
                answer_package_id=answer_package_id,
                llm_calls=llm_calls,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                is_hold=is_hold,
                is_error=is_error,
                estimated_cost_vnd=estimated_cost_vnd,
            )
        )
        await db.commit()

    async def record_audit_event(
        self,
        db: AsyncSession | None = None,
        *,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        outcome: str,
        detail: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        """Append an access-restricted audit trail record."""
        if db is None:
            return
        db.add(
            AuditLog(
                actor_id=actor_id,
                actor_role=actor_role,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                outcome=outcome,
                detail=detail,
                metadata_json=metadata or {},
            )
        )
        await db.commit()
