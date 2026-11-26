"""Local referral HTTP router (/api/v1/referral/*) — KNW 05 & Annex B."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.referral.annex_b_handler import AnnexBReferralHandler
from src.modules.referral.schemas import (
    AnnexBHandlingResult,
    AnnexBReferralRequest,
    ReferralCreateRequest,
    ReferralResponse,
    ReferralUpdateRequest,
)
from src.modules.referral.service import ReferralService
from src.shared.auth import AuthenticatedUser, get_current_user, require_roles
from src.shared.enums import ReferralStatus, UserRole

router = APIRouter()
service = ReferralService()
annex_b_handler = AnnexBReferralHandler(service)


@router.post("", response_model=ReferralResponse, status_code=201)
async def create_local_referral(
    payload: ReferralCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ReferralResponse:
    """Create a local policy owner escalation linked to the user's task (KNW 05)."""
    return await service.create_referral(db, current_user, payload)


@router.post("/annex-b", response_model=AnnexBHandlingResult, status_code=201)
async def handle_annex_b_referral(
    payload: AnnexBReferralRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AnnexBHandlingResult:
    """Evaluate one of 9 Annex B cases (SC-01..SC-09) and create a Local Referral on Hold."""
    return await annex_b_handler.handle_case(db, current_user, payload)


@router.get("", response_model=list[ReferralResponse])
async def list_local_referrals(
    status: ReferralStatus | None = Query(default=None),
    task_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[ReferralResponse]:
    """List local referral tickets for tracking (KNW 05)."""
    return await service.list_referrals(db, current_user, status_filter=status, task_id=task_id)


@router.get("/{referral_id}", response_model=ReferralResponse)
async def get_local_referral(
    referral_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ReferralResponse:
    """Fetch a single local referral record by ID (KNW 05)."""
    return await service.get_referral(db, current_user, referral_id)


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
    """Record owner response or close a referral — enforces KNW 05 3-state machine."""
    return await service.update_referral(db, referral_id, payload, current_user)
