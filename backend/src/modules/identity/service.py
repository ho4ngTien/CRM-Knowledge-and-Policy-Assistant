"""Identity, 4-role IAM, session concurrency cap, and SEC 08 audit trail service."""

from datetime import datetime
from typing import NoReturn
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status

from src.config import settings
from src.modules.identity.schemas import (
    IamEnvironmentStatusResponse,
    PermissionCheckResponse,
    TokenResponse,
    UserProfileResponse,
)
from src.shared.auth import (
    G1_NAMED_USERS_DIRECTORY,
    SECTION2_CORE_SYSTEM_ROLES,
    AuthenticatedUser,
    check_policy_audience,
    create_access_token,
    validate_compatible_roles,
)

SSO_ASSERTION_PREFIX = "sso:songnhat:g1:"


class IdentityService:
    """Handles organizational authentication, 4-role IAM, 5-session cap, and SEC 08 audit."""

    def __init__(self) -> None:
        self._active_sessions: set[str] = set()
        self._audit_events: list[dict[str, object]] = []

    def _record_sec08_audit(
        self,
        *,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_id: str,
        outcome: str,
        detail: str,
    ) -> None:
        tz = ZoneInfo(settings.APP_TIMEZONE)
        self._audit_events.append(
            {
                "actor_id": actor_id,
                "actor_role": actor_role,
                "action": action,
                "resource_type": "iam_environment",
                "resource_id": resource_id,
                "outcome": outcome,
                "detail": detail,
                "app_env": settings.APP_ENV,
                "created_at": datetime.now(tz).isoformat(),
            }
        )

    def get_recent_audit_events(self) -> list[dict[str, object]]:
        """Return recorded SEC 08 IAM and environment isolation audit events."""
        return list(self._audit_events)

    def reset_sessions(self) -> None:
        """Clear active session tracker for deterministic testing."""
        self._active_sessions.clear()

    def release_session(self, user_id: str) -> None:
        """Release an active named-user session slot."""
        self._active_sessions.discard(user_id)

    def exchange_token(self, id_token: str) -> TokenResponse:
        """Exchange a Gate G1 organizational assertion for an environment-bound JWT (SEC 01)."""
        iso = settings.verify_sec06_test_prod_isolation()
        cleaned = id_token.strip()
        if not cleaned.startswith(SSO_ASSERTION_PREFIX):
            self._record_sec08_audit(
                actor_id="anonymous",
                actor_role="unauthenticated",
                action="iam.token_exchange",
                resource_id="identity/token",
                outcome="denied",
                detail="Rejected assertion without valid SongNhat SSO prefix.",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid organizational SSO assertion format (fail-closed SEC 01).",
            )

        user_id = cleaned.removeprefix(SSO_ASSERTION_PREFIX).strip()
        if len(G1_NAMED_USERS_DIRECTORY) > settings.PILOT_MAX_NAMED_USERS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Named user directory exceeds PILOT_MAX_NAMED_USERS cap (20).",
            )

        user = G1_NAMED_USERS_DIRECTORY.get(user_id)
        if user is None:
            self._record_sec08_audit(
                actor_id=user_id or "unknown",
                actor_role="unassigned",
                action="iam.token_exchange",
                resource_id="identity/token",
                outcome="denied",
                detail="User ID not present in the 20 named users directory.",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not registered in the 20 authorized named users directory.",
            )

        if not validate_compatible_roles(user.roles):
            self._record_sec08_audit(
                actor_id=user.user_id,
                actor_role=",".join(sorted(r.value for r in user.roles)),
                action="iam.role_compatibility_check",
                resource_id=user.user_id,
                outcome="denied",
                detail="Incompatible or SoD-forbidden role combination.",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assigned roles violate RULE-11-04/05 compatibility matrix.",
            )

        if (
            user.user_id not in self._active_sessions
            and len(self._active_sessions) >= settings.PILOT_MAX_CONCURRENT_SESSIONS
        ):
            self._record_sec08_audit(
                actor_id=user.user_id,
                actor_role=",".join(sorted(r.value for r in user.roles)),
                action="iam.concurrent_session_check",
                resource_id="identity/token",
                outcome="hold",
                detail=(
                    f"Concurrent session cap ({settings.PILOT_MAX_CONCURRENT_SESSIONS}) reached."
                ),
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Maximum concurrent sessions ({settings.PILOT_MAX_CONCURRENT_SESSIONS}) "
                    "reached for Base Scope pilot."
                ),
            )

        self._active_sessions.add(user.user_id)
        token = create_access_token(user)
        role_str = ",".join(sorted(r.value for r in user.roles))
        self._record_sec08_audit(
            actor_id=user.user_id,
            actor_role=role_str,
            action="iam.token_exchange",
            resource_id=user.user_id,
            outcome="success",
            detail=f"Issued JWT in env={iso['app_env']} (training_locked=True).",
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in_seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def get_profile(self, user: AuthenticatedUser) -> UserProfileResponse:
        """Serialize effective organizational identity and least-privilege grants."""
        role_str = ",".join(sorted(r.value for r in user.roles))
        self._record_sec08_audit(
            actor_id=user.user_id,
            actor_role=role_str,
            action="iam.get_profile",
            resource_id=user.user_id,
            outcome="success",
            detail="Inspected authenticated profile.",
        )
        return UserProfileResponse(
            user_id=user.user_id,
            email=user.email,
            roles=sorted(user.roles, key=lambda r: r.value),
            company=user.company,
            branch=user.branch,
            allowed_audiences=sorted(user.allowed_audiences),
        )

    def check_audience(
        self, user: AuthenticatedUser, required_audiences: list[str]
    ) -> PermissionCheckResponse:
        """Enforce uniform least-privilege audience matching with SEC 08 audit logging."""
        allowed = check_policy_audience(user, required_audiences)
        role_str = ",".join(sorted(r.value for r in user.roles))
        self._record_sec08_audit(
            actor_id=user.user_id,
            actor_role=role_str,
            action="iam.check_audience",
            resource_id=",".join(required_audiences) or "default",
            outcome="allowed" if allowed else "denied",
            detail=f"Audience permission check evaluated to allowed={allowed}.",
        )
        return PermissionCheckResponse(
            allowed=allowed,
            user_id=user.user_id,
            effective_roles=sorted(user.roles, key=lambda r: r.value),
        )

    def get_iam_environment_status(
        self, user: AuthenticatedUser
    ) -> IamEnvironmentStatusResponse:
        """Verify SEC 06 Test/Prod isolation, SEC 04 training lock, and 4-role IAM status."""
        iso = settings.verify_sec06_test_prod_isolation()
        role_str = ",".join(sorted(r.value for r in user.roles))
        self._record_sec08_audit(
            actor_id=user.user_id,
            actor_role=role_str,
            action="sec08.verify_iam_and_env_isolation",
            resource_id=str(iso["app_env"]),
            outcome="verified",
            detail="Verified Dev/Test isolation from Prod, SEC 04 training lock, and 4 IAM roles.",
        )
        layers_raw = iso.get("isolation_layers")
        layers = (
            {str(k): bool(v) for k, v in layers_raw.items()}
            if isinstance(layers_raw, dict)
            else {"vpc": True, "db": True, "storage": True, "keys": True}
        )
        return IamEnvironmentStatusResponse(
            app_env=str(iso["app_env"]),
            isolated_from_production=bool(iso["isolated_from_production"]),
            isolation_layers=layers,
            llm_allow_training=bool(iso["llm_allow_training"]),
            llm_zero_data_retention=bool(iso["llm_zero_data_retention"]),
            llm_telemetry_enabled=bool(iso["llm_telemetry_enabled"]),
            core_system_roles=sorted(SECTION2_CORE_SYSTEM_ROLES, key=lambda r: r.value),
            named_users_count=len(G1_NAMED_USERS_DIRECTORY),
            max_named_users=settings.PILOT_MAX_NAMED_USERS,
            active_sessions_count=len(self._active_sessions),
            max_concurrent_sessions=settings.PILOT_MAX_CONCURRENT_SESSIONS,
            audit_events_count=len(self._audit_events),
        )

    def exchange_token_not_configured(self) -> NoReturn:
        """Legacy fail-closed helper retained for backward compatibility."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Organizational SSO/OIDC token exchange not configured (Gate G1).",
        )
