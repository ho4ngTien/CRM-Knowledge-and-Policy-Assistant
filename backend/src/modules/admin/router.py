"""Admin governance HTTP router (/api/v1/admin/*)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.admin.schemas import (
    AdminOpsSummaryResponse,
    EmergencyDisableRequest,
    InstantWithdrawalRequest,
    InstantWithdrawalResponse,
    LifecycleTransitionRequest,
    LifecycleTransitionResponse,
)
from src.modules.admin.service import AdminService
from src.modules.knowledge.change_impact_schemas import ChangeImpactReportResponse
from src.shared.auth import AuthenticatedUser, require_roles
from src.shared.enums import UserRole

router = APIRouter()
service = AdminService()


@router.post("/policies/{policy_version_id}/transition", response_model=LifecycleTransitionResponse)
async def transition_policy_lifecycle(
    policy_version_id: str,
    payload: LifecycleTransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> LifecycleTransitionResponse:
    """Execute an auditable KNW 03 lifecycle state transition."""
    return await service.transition_policy_status(
        db, current_user, policy_version_id, payload.target_status, payload.reason
    )


@router.post("/policies/{policy_version_id}/withdraw", response_model=InstantWithdrawalResponse)
async def withdraw_policy_immediately(
    policy_version_id: str,
    payload: InstantWithdrawalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> InstantWithdrawalResponse:
    """Immediately withdraw a policy, block live retrieval, and purge caches within <= 5m."""
    return await service.withdraw_policy_immediately(
        db, current_user, policy_version_id, payload.reason
    )


@router.post("/emergency-disable")
async def toggle_emergency_disable(
    payload: EmergencyDisableRequest,
    current_user: AuthenticatedUser = Depends(require_roles(UserRole.ADMINISTRATOR)),
) -> dict[str, object]:
    """Toggle emergency disable mode while preserving manual CSV lookup fallback (OPS 05)."""
    return await service.set_emergency_disable(
        current_user, payload.disabled, payload.reason
    )


@router.get("/ops-summary", response_model=AdminOpsSummaryResponse)
async def get_admin_ops_summary(
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> AdminOpsSummaryResponse:
    """Inspect active RFP/SRS Base Scope limits and runtime flags."""
    _ = current_user
    return service.get_ops_summary()


@router.get("/change-impacts", response_model=list[ChangeImpactReportResponse])
async def list_change_impacts(
    policy_version_id: str | None = Query(default=None, max_length=64),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> list[ChangeImpactReportResponse]:
    """List source/lifecycle change reports and stale-answer counts (KNW 04)."""
    _ = current_user
    return await service.list_change_impacts(
        db, policy_version_id=policy_version_id, limit=limit
    )
