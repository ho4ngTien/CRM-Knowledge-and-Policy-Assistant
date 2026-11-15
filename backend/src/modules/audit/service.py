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
