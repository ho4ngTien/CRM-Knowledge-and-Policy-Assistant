"""Pydantic schemas for organizational authentication and 4-role IAM introspection."""

from pydantic import BaseModel, Field

from src.shared.enums import UserRole


class TokenRequest(BaseModel):
    """Organization-managed OIDC/SSO assertion exchange payload (SEC 01)."""

    id_token: str = Field(..., min_length=16, max_length=4096)


class TokenResponse(BaseModel):
    """Issued bearer session metadata."""

    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int = 3600


class UserProfileResponse(BaseModel):
    """Authenticated user profile with least-privilege scopes."""

    user_id: str
    email: str
    roles: list[UserRole]
    company: str
    branch: str
    allowed_audiences: list[str]


class PermissionCheckRequest(BaseModel):
    """Request to verify organizational permission against policy audience tags."""

    required_audiences: list[str] = Field(default_factory=list)


class PermissionCheckResponse(BaseModel):
    """Result of policy audience & role verification."""

    allowed: bool
    user_id: str
    effective_roles: list[UserRole]


class IamEnvironmentStatusResponse(BaseModel):
    """Gate G1 isolated Test vs Prod (VPC/DB/Storage/Keys) & 4-role IAM telemetry."""

    app_env: str
    isolated_from_production: bool
    isolation_layers: dict[str, bool]
    llm_allow_training: bool
    llm_zero_data_retention: bool
    llm_telemetry_enabled: bool
    core_system_roles: list[UserRole]
    named_users_count: int
    max_named_users: int
    active_sessions_count: int
    max_concurrent_sessions: int
    audit_events_count: int
