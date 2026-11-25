"""Policy authority, critical fields, and applicability router (/api/v1/policy/*)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.policy.schemas import (
    AuthorityEntryResponse,
    CriticalFieldItem,
    ThresholdCheckRequest,
    ThresholdCheckResponse,
)
from src.modules.policy.service import PolicyService
from src.shared.auth import AuthenticatedUser, get_current_user

router = APIRouter()
service = PolicyService()


@router.get("/authority-matrix", response_model=list[AuthorityEntryResponse])
async def list_authority_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[AuthorityEntryResponse]:
    """Return configured organizational policy owners and authority tiers."""
    _ = current_user
    return await service.list_authority_entries(db)


@router.get("/versions/{policy_version_id}/critical-fields", response_model=list[CriticalFieldItem])
async def get_critical_fields(
    policy_version_id: str,
    allow_historical: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[CriticalFieldItem]:
    """Fetch deterministic critical policy parameters for a policy version."""
    return await service.list_critical_fields(
        db, current_user, policy_version_id, allow_historical=allow_historical
    )


@router.post("/threshold-check", response_model=ThresholdCheckResponse)
async def check_threshold(
    payload: ThresholdCheckRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ThresholdCheckResponse:
    """Compute a deterministic threshold comparison outside the LLM."""
    _ = current_user
    satisfied = service.evaluate_numeric_threshold(
        payload.operator, payload.actual_value, payload.threshold_value
    )
    return ThresholdCheckResponse(
        satisfied=satisfied,
        operator=payload.operator,
        actual_value=payload.actual_value,
        threshold_value=payload.threshold_value,
    )
