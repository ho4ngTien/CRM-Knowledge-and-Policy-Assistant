"""Pydantic schemas for lifecycle approval, instant withdrawal, and operational controls."""

from pydantic import BaseModel, Field

from src.shared.enums import PolicyLifecycleStatus


class LifecycleTransitionRequest(BaseModel):
    """Explicit auditable state transition request (KNW 03)."""

    target_status: PolicyLifecycleStatus
    reason: str = Field(..., min_length=3, max_length=1000)


class LifecycleTransitionResponse(BaseModel):
    """Confirmed authoritative policy lifecycle transition."""

    policy_version_id: str
    previous_status: PolicyLifecycleStatus
    current_status: PolicyLifecycleStatus
    actor_id: str
    change_impact_report_id: str | None = None


class InstantWithdrawalRequest(BaseModel):
    """Emergency policy withdrawal payload triggering <= 5 minute cache purge (KNW 04)."""

    reason: str = Field(..., min_length=5, max_length=1000)


class InstantWithdrawalResponse(BaseModel):
    """Result after synchronous DB withdrawal & cache invalidation scheduling."""

    policy_version_id: str
    status: PolicyLifecycleStatus = PolicyLifecycleStatus.WITHDRAWN
    stale_answers_marked: int
    cache_purge_deadline_seconds: int
    change_impact_report_id: str


class EmergencyDisableRequest(BaseModel):
    """OPS 05 emergency assistant disable toggle while keeping manual CSV lookup intact."""

    disabled: bool
    reason: str = Field(..., min_length=5, max_length=500)


class AdminOpsSummaryResponse(BaseModel):
    """Operational telemetry panel respecting Base Scope pilot & corpus limits."""

    timezone: str
    answer_streaming_enabled: bool
    snapshot_staleness_threshold_hours: int
    cache_withdrawal_max_seconds: int
    pilot_max_named_users: int
    pilot_max_concurrent_sessions: int
    corpus_max_documents: int
    corpus_max_passages: int
    corpus_max_critical_fields: int
