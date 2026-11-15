"""Identity & RBAC HTTP router (/api/v1/identity/*)."""

from fastapi import APIRouter, Depends

from src.modules.identity.schemas import (
    PermissionCheckRequest,
    PermissionCheckResponse,
    TokenRequest,
    TokenResponse,
    UserProfileResponse,
)
from src.modules.identity.service import IdentityService
from src.shared.auth import AuthenticatedUser, get_current_user

router = APIRouter()
service = IdentityService()


@router.post("/token", response_model=TokenResponse)
async def issue_token(payload: TokenRequest) -> TokenResponse:
    """Authenticate against enterprise identity provider (Gate G1)."""
    _ = payload
    service.exchange_token_not_configured()


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserProfileResponse:
    """Return the signed-in user's organizational identity and scopes."""
    return UserProfileResponse(**service.get_profile(current_user))


@router.post("/check-permission", response_model=PermissionCheckResponse)
async def verify_audience_permission(
    payload: PermissionCheckRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PermissionCheckResponse:
    """Verify whether the authenticated user may access a policy audience tag list."""
    result = service.check_audience(current_user, payload.required_audiences)
    return PermissionCheckResponse(**result)
