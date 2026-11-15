"""Authentication & RBAC dependency scaffolding (SEC 01, SRS-FR-02)."""

from collections.abc import Callable
from dataclasses import dataclass, field

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.shared.enums import EvalPartition, UserRole
from src.shared.exceptions import AccessDenied

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/identity/token")


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Verified organizational identity and least-privilege authorization context."""

    user_id: str
    email: str
    roles: frozenset[UserRole]
    company: str = "SN"
    branch: str = "all"
    allowed_audiences: frozenset[str] = field(default_factory=lambda: frozenset({"reader"}))


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    """Fail-closed placeholder until organizational OIDC/JWT validation lands in Gate G1."""
    _ = token
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Identity token verification not implemented yet (scheduled Gate G1).",
    )


def require_roles(*allowed_roles: UserRole) -> Callable[..., AuthenticatedUser]:
    """Dependency factory enforcing least-privilege endpoint access (SEC 01)."""
    allowed = frozenset(allowed_roles)

    async def _role_checker(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if not (current_user.roles & allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privilege for this operation.",
            )
        return current_user

    return _role_checker


def check_policy_audience(user: AuthenticatedUser, record_audiences: list[str]) -> bool:
    """Enforce consistent audience filtering across pre-retrieval, generation, and display."""
    if UserRole.ADMINISTRATOR in user.roles:
        return True
    normalized = {aud.strip().lower() for aud in record_audiences if aud.strip()}
    user_scopes = {role.value for role in user.roles} | user.allowed_audiences
    return bool(normalized & user_scopes)


def ensure_partition_access(user: AuthenticatedUser, partition: EvalPartition) -> None:
    """Enforce Chinese Wall isolation on the 100 Sealed evaluation partition."""
    if partition == EvalPartition.SEALED_100 and not (
        user.roles & {UserRole.INDEPENDENT_EVALUATOR, UserRole.ADMINISTRATOR}
    ):
        raise AccessDenied(
            "Chinese Wall violation: sealed_100 restricted to independent_evaluator."
        )
