"""Identity & 4-Role IAM HTTP router (/api/v1/identity/*)."""

from fastapi import APIRouter, Depends

from src.modules.identity.schemas import (
    IamEnvironmentStatusResponse,
    PermissionCheckRequest,
    PermissionCheckResponse,
    TokenRequest,
    TokenResponse,
    UserProfileResponse,
)
from src.modules.identity.service import IdentityService
from src.shared.auth import AuthenticatedUser, get_current_user, require_roles
from src.shared.enums import UserRole

router = APIRouter()
service = IdentityService()


@router.post("/token", response_model=TokenResponse)
async def issue_token(payload: TokenRequest) -> TokenResponse:
    """Authenticate against Gate G1 20 named users directory and issue env-bound JWT."""
    return service.exchange_token(payload.id_token)


@router.post("/logout")
async def logout_session(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, object]:
    """Release the authenticated user's active session slot and record SEC 08 audit."""
    return service.logout(current_user)


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> UserProfileResponse:
    """Return the signed-in user's organizational identity and scopes."""
    return service.get_profile(current_user)


@router.post("/check-permission", response_model=PermissionCheckResponse)
async def verify_audience_permission(
    payload: PermissionCheckRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PermissionCheckResponse:
    """Verify whether the authenticated user may access a policy audience tag list."""
    return service.check_audience(current_user, payload.required_audiences)


@router.get("/iam-status", response_model=IamEnvironmentStatusResponse)
async def get_iam_and_environment_isolation_status(
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.ADMINISTRATOR, UserRole.PRIVACY_SECURITY_OWNER)
    ),
) -> IamEnvironmentStatusResponse:
    """Inspect SEC 06 Test/Prod isolation, SEC 04 training lock, and 4-role IAM telemetry."""
    return service.get_iam_environment_status(current_user)
