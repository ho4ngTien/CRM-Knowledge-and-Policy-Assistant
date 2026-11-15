"""Local referral HTTP router (/api/v1/referral/*)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.referral.schemas import (
    ReferralCreateRequest,
    ReferralResponse,
    ReferralUpdateRequest,
)
from src.modules.referral.service import ReferralService
from src.shared.auth import AuthenticatedUser, get_current_user, require_roles
from src.shared.enums import ReferralStatus, UserRole

router = APIRouter()
service = ReferralService()


@router.post("", response_model=ReferralResponse, status_code=201)
async def create_local_referral(
    payload: ReferralCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ReferralResponse:
    """Create a local policy owner escalation linked to the user's task."""
    return await service.create_referral(db, current_user, payload)


@router.get("", response_model=list[ReferralResponse])
async def list_local_referrals(
    status: ReferralStatus | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[ReferralResponse]:
    """List local referral tickets for tracking."""
    _ = current_user
    return await service.list_referrals(db, status_filter=status)


@router.patch("/{referral_id}", response_model=ReferralResponse)
async def update_local_referral(
    referral_id: str,
    payload: ReferralUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            UserRole.POLICY_OWNER,
            UserRole.REFERRAL_HANDLER,
            UserRole.STEWARD,
            UserRole.ADMINISTRATOR,
        )
    ),
) -> ReferralResponse:
    """Record owner response or close a referral ticket."""
    _ = current_user
    return await service.update_referral(db, referral_id, payload)
