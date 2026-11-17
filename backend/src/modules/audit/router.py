"""Audit, Cost Meter, and Open Export HTTP router (/api/v1/audit/*)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.audit.schemas import (
    AuditLogResponse,
    CostMeterSummaryResponse,
    OpenExportResponse,
)
from src.modules.audit.service import AuditService
from src.shared.auth import AuthenticatedUser, require_roles
from src.shared.enums import UserRole

router = APIRouter()
service = AuditService()


@router.get("/logs", response_model=list[AuditLogResponse])
async def get_restricted_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            UserRole.PRIVACY_SECURITY_OWNER,
            UserRole.LEGAL_OWNER,
            UserRole.ADMINISTRATOR,
        )
    ),
) -> list[AuditLogResponse]:
    """Read access-restricted audit trail (privacy_security_owner / legal_owner / administrator only)."""
    _ = current_user
    return await service.list_audit_logs(db, limit=limit)


@router.get("/cost-meter", response_model=CostMeterSummaryResponse)
async def get_monthly_cost_meter(
    month_key: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            UserRole.ADMINISTRATOR,
            UserRole.POLICY_OWNER,
            UserRole.PUBLISHER,
        )
    ),
) -> CostMeterSummaryResponse:
    """Inspect monthly LLM calls, tokens, packages, holds, and errors (OPS 06)."""
    _ = current_user
    return await service.summarize_month_usage(db, month_key=month_key)


@router.get("/export-open", response_model=OpenExportResponse)
async def export_open_handover_manifest(
    current_user: AuthenticatedUser = Depends(
        require_roles(
            UserRole.ADMINISTRATOR,
            UserRole.POLICY_OWNER,
            UserRole.PUBLISHER,
            UserRole.STEWARD,
        )
    ),
) -> OpenExportResponse:
    """Export open non-proprietary dataset metadata supporting exit without lock-in (OPS 08)."""
    _ = current_user
    return service.build_open_export_manifest()
