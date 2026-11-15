"""Validation HTTP router (/api/v1/validation/*) — never trusts unverified LLM outputs."""

from fastapi import APIRouter, Depends

from src.modules.validation.schemas import FinalValidationRequest, FinalValidationResponse
from src.shared.auth import AuthenticatedUser, check_policy_audience, get_current_user
from src.shared.enums import PolicyLifecycleStatus

router = APIRouter()


@router.post("/verify", response_model=FinalValidationResponse)
async def verify_authoritative_state(
    payload: FinalValidationRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> FinalValidationResponse:
    """Check whether cited sources remain permitted and non-withdrawn prior to display."""
    errors: list[str] = []
    stale = False

    if payload.required_audiences and not check_policy_audience(
        current_user, payload.required_audiences
    ):
        errors.append("Access revoked for one or more cited audience scopes.")

    for pid, status in payload.current_source_statuses.items():
        if status in {PolicyLifecycleStatus.WITHDRAWN, PolicyLifecycleStatus.QUARANTINED}:
            stale = True
            errors.append(f"Source {pid} transitioned to {status.value}; answer marked stale.")

    return FinalValidationResponse(
        is_valid=not errors and bool(payload.citations),
        stale=stale,
        verified_citations_count=len(payload.citations) if not errors else 0,
        errors=errors,
    )
