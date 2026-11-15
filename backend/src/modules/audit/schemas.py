"""Pydantic schemas for restricted audit inspection, OPS 06 metering, and OPS 08 export."""

from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Serialized restricted audit entry."""

    id: int
    actor_id: str
    actor_role: str
    action: str
    resource_type: str
    resource_id: str
    outcome: str
    detail: str | None = None
    created_at: datetime


class CostMeterSummaryResponse(BaseModel):
    """Monthly usage & cost meter vs Common Bid Basis bounds (OPS 06)."""

    month_key: str
    total_packages: int
    package_quota: int
    total_llm_calls: int
    llm_call_quota: int
    total_input_tokens: int
    total_output_tokens: int
    hold_count: int
    error_count: int


class OpenExportResponse(BaseModel):
    """Standard non-proprietary exit/handover bundle metadata (OPS 08, DEL 06)."""

    format: str = "json"
    schema_version: str = "1.0"
    timezone: str = "Asia/Ho_Chi_Minh"
    included_datasets: list[str] = Field(
        default_factory=lambda: [
            "passages_utf8_csv",
            "critical_fields_utf8_csv",
            "policy_lifecycle_events",
            "referrals_and_feedback_candidates",
        ]
    )
    record_counts: dict[str, int] = Field(default_factory=dict)
