"""Authentication, 4-role IAM & RBAC enforcement (SEC 01, SEC 06, SRS-FR-02)."""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.config import settings
from src.shared.enums import EvalPartition, UserRole
from src.shared.exceptions import AccessDenied

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/identity/token")

# Four core software system roles defined in RFP Section 2 (p.4) / SYS-01..SYS-04
SECTION2_CORE_SYSTEM_ROLES: frozenset[UserRole] = frozenset(
    {
        UserRole.READER,
        UserRole.POLICY_OWNER,
        UserRole.STEWARD,
        UserRole.ADMINISTRATOR,
    }
)

# Compatible combined roles approved by Privacy & Security Owner [P5] per RULE-11-04
COMPATIBLE_COMBINED_ROLE_SETS: tuple[frozenset[UserRole], ...] = (
    frozenset({UserRole.READER, UserRole.POLICY_OWNER}),
    frozenset({UserRole.READER, UserRole.STEWARD}),
    frozenset({UserRole.POLICY_OWNER, UserRole.REFERRAL_HANDLER}),
    frozenset({UserRole.STEWARD, UserRole.REFERRAL_HANDLER}),
    frozenset({UserRole.ADMINISTRATOR, UserRole.PRIVACY_SECURITY_OWNER}),
)


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Verified organizational identity and least-privilege authorization context."""

    user_id: str
    email: str
    roles: frozenset[UserRole]
    company: str = "SN"
    branch: str = "all"
    allowed_audiences: frozenset[str] = field(default_factory=lambda: frozenset({"reader"}))


def validate_compatible_roles(roles: frozenset[UserRole]) -> bool:
    """Enforce RFP Section 2 & RULE-11-04/05 role combination & SoD boundaries."""
    if not roles:
        return False
    # RULE-11-05: Independent evaluator (S4) must remain strictly isolated from build/curation
    if UserRole.INDEPENDENT_EVALUATOR in roles and len(roles) > 1:
        return False
    if len(roles) == 1:
        return True
    return roles in COMPATIBLE_COMBINED_ROLE_SETS


def _build_g1_named_users_directory() -> dict[str, AuthenticatedUser]:
    """Construct the 20 named users directory for SongNhat G1 isolated test environment."""
    users: list[AuthenticatedUser] = [
        # P1..P5 Purchaser & S1..S5 Supplier Team (10 core RFP Section 11 members)
        AuthenticatedUser(
            user_id="p1-my-van",
            email="my.van@songnhat.vn",
            roles=frozenset({UserRole.READER, UserRole.POLICY_OWNER}),
            allowed_audiences=frozenset({"reader", "policy_owner", "sponsor"}),
        ),
        AuthenticatedUser(
            user_id="p2-huu-tai",
            email="huu.tai@songnhat.vn",
            roles=frozenset({UserRole.POLICY_OWNER}),
            allowed_audiences=frozenset({"reader", "policy_owner"}),
        ),
        AuthenticatedUser(
            user_id="p3-chi-kha",
            email="chi.kha@songnhat.vn",
            roles=frozenset({UserRole.STEWARD}),
            allowed_audiences=frozenset({"reader", "steward"}),
        ),
        AuthenticatedUser(
            user_id="p4-tra-my",
            email="tra.my@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            allowed_audiences=frozenset({"reader", "sales", "cs", "warranty"}),
        ),
        AuthenticatedUser(
            user_id="p5-anh-khoa",
            email="anh.khoa@songnhat.vn",
            roles=frozenset({UserRole.ADMINISTRATOR, UserRole.PRIVACY_SECURITY_OWNER}),
            allowed_audiences=frozenset({"reader", "administrator", "privacy_security_owner"}),
        ),
        AuthenticatedUser(
            user_id="s1-hoang-tien",
            email="hoang.tien@supplier.songnhat.vn",
            roles=frozenset({UserRole.READER}),
            allowed_audiences=frozenset({"reader"}),
        ),
        AuthenticatedUser(
            user_id="s2-quoc-hung",
            email="quoc.hung@supplier.songnhat.vn",
            roles=frozenset({UserRole.STEWARD}),
            allowed_audiences=frozenset({"reader", "steward"}),
        ),
        AuthenticatedUser(
            user_id="s3-yen-nhi",
            email="yen.nhi@supplier.songnhat.vn",
            roles=frozenset({UserRole.READER}),
            allowed_audiences=frozenset({"reader"}),
        ),
        AuthenticatedUser(
            user_id="s4-quy-hai",
            email="quy.hai@supplier.songnhat.vn",
            roles=frozenset({UserRole.INDEPENDENT_EVALUATOR}),
            allowed_audiences=frozenset({"reader", "independent_evaluator"}),
        ),
        AuthenticatedUser(
            user_id="s5-ngoc-duy",
            email="ngoc.duy@supplier.songnhat.vn",
            roles=frozenset({UserRole.ADMINISTRATOR}),
            allowed_audiences=frozenset({"reader", "administrator"}),
        ),
        # 3 Policy Owner Substitutes (P2-SUB for the 3 policy families - VN 04)
        AuthenticatedUser(
            user_id="p2-sub-quoting",
            email="sub.quoting@songnhat.vn",
            roles=frozenset({UserRole.POLICY_OWNER}),
            allowed_audiences=frozenset({"reader", "policy_owner", "sales"}),
        ),
        AuthenticatedUser(
            user_id="p2-sub-custinfo",
            email="sub.custinfo@songnhat.vn",
            roles=frozenset({UserRole.POLICY_OWNER}),
            allowed_audiences=frozenset({"reader", "policy_owner", "cs"}),
        ),
        AuthenticatedUser(
            user_id="p2-sub-warranty",
            email="sub.warranty@songnhat.vn",
            roles=frozenset({UserRole.POLICY_OWNER}),
            allowed_audiences=frozenset({"reader", "policy_owner", "warranty"}),
        ),
        # 2 Data Reconciliation / Steward backups (P3-REC)
        AuthenticatedUser(
            user_id="p3-rec-steward-01",
            email="steward.rec01@songnhat.vn",
            roles=frozenset({UserRole.STEWARD}),
            allowed_audiences=frozenset({"reader", "steward"}),
        ),
        AuthenticatedUser(
            user_id="p3-rec-steward-02",
            email="steward.rec02@songnhat.vn",
            roles=frozenset({UserRole.READER, UserRole.STEWARD}),
            allowed_audiences=frozenset({"reader", "steward"}),
        ),
        # 5 Additional SongNhat Representative Staff Users (P4 readers -> total 20 named users)
        AuthenticatedUser(
            user_id="p4-staff-sales-01",
            email="staff.sales01@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            branch="HCM",
            allowed_audiences=frozenset({"reader", "sales"}),
        ),
        AuthenticatedUser(
            user_id="p4-staff-sales-02",
            email="staff.sales02@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            branch="HN",
            allowed_audiences=frozenset({"reader", "sales"}),
        ),
        AuthenticatedUser(
            user_id="p4-staff-cs-01",
            email="staff.cs01@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            branch="HCM",
            allowed_audiences=frozenset({"reader", "cs"}),
        ),
        AuthenticatedUser(
            user_id="p4-staff-warranty-01",
            email="staff.warranty01@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            branch="DN",
            allowed_audiences=frozenset({"reader", "warranty"}),
        ),
        AuthenticatedUser(
            user_id="p4-staff-warranty-02",
            email="staff.warranty02@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            branch="HCM",
            allowed_audiences=frozenset({"reader", "warranty"}),
        ),
    ]
    return {u.user_id: u for u in users}


G1_NAMED_USERS_DIRECTORY: dict[str, AuthenticatedUser] = _build_g1_named_users_directory()


def create_access_token(
    user: AuthenticatedUser,
    *,
    expires_minutes: int | None = None,
    app_env: str | None = None,
) -> str:
    """Mint an environment-bound JWT bearer token for a verified named user (SEC 01, SEC 06)."""
    if not validate_compatible_roles(user.roles):
        raise ValueError("Incompatible or SoD-forbidden role combination (RULE-11-04/05).")

    ttl_minutes = (
        expires_minutes
        if expires_minutes is not None
        else settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    now = datetime.now(UTC)
    target_env = (app_env if app_env is not None else settings.APP_ENV).strip().lower()
    claims: dict[str, object] = {
        "sub": user.user_id,
        "email": user.email,
        "roles": sorted(r.value for r in user.roles),
        "company": user.company,
        "branch": user.branch,
        "allowed_audiences": sorted(user.allowed_audiences),
        "env": target_env,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
    }
    return str(
        jwt.encode(claims, settings.APP_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    )


def verify_access_token(token: str) -> AuthenticatedUser:
    """Verify JWT signature, expiry, SEC 06 environment boundary, and RULE-11-04 roles."""
    try:
        payload = jwt.decode(
            token,
            settings.APP_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token (fail-closed SEC 01).",
        ) from exc

    token_env = str(payload.get("env") or "").strip().lower()
    current_env = settings.APP_ENV.strip().lower()
    if token_env != current_env:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(
                f"SEC 06 environment boundary violation: token issued for {token_env!r} "
                f"rejected in {current_env!r}."
            ),
        )

    user_id = str(payload.get("sub") or "").strip()
    email = str(payload.get("email") or "").strip()
    raw_roles = payload.get("roles")
    if not user_id or not email or not isinstance(raw_roles, list) or not raw_roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed identity claims in bearer token.",
        )

    try:
        parsed_roles = frozenset(UserRole(str(r)) for r in raw_roles)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unrecognized role claim in bearer token.",
        ) from exc

    if not validate_compatible_roles(parsed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role combination violates least-privilege or SoD policy (RULE-11-04/05).",
        )

    raw_aud = payload.get("allowed_audiences")
    audiences = (
        frozenset(str(a).strip().lower() for a in raw_aud if str(a).strip())
        if isinstance(raw_aud, list) and raw_aud
        else frozenset({"reader"})
    )
    return AuthenticatedUser(
        user_id=user_id,
        email=email,
        roles=parsed_roles,
        company=str(payload.get("company") or "SN"),
        branch=str(payload.get("branch") or "all"),
        allowed_audiences=audiences,
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    """Authenticate organizational bearer token and fail closed on any anomaly (SEC 01)."""
    return verify_access_token(token)


def require_roles(
    *allowed_roles: UserRole,
) -> Callable[..., Coroutine[Any, Any, AuthenticatedUser]]:
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
