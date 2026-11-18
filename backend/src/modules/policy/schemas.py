"""Pydantic schemas for critical fields, governing-date applicability, and authority tiers [CKPA-17]."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.shared.enums import (
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyFamily,
    PolicyLifecycleStatus,
)


class CriticalFieldItem(BaseModel):
    """Typed structured policy parameter rendered deterministically by UI & validation.

    Strictly frozen under Gate G1, SRS Mục 4.3, SRS-FR-06.1 [CKPA-17].
    """

    model_config = ConfigDict(extra="forbid")

    field_id: str
    policy_id: str
    policy_version_id: str
    document_version_id: str
    field_name: str
    field_type: CriticalFieldType
    operator: ComparisonOperator
    value: str
    unit: str | None = None
    currency: str | None = None
    approval_role: str
    time_limit: str | None = None
    exception_condition: str | None = None
    required_documents: list[str] = Field(default_factory=list)
    source_clause: str
    status: PolicyLifecycleStatus


class AuthorityEntryResponse(BaseModel):
    """Authority matrix entry separating company policy from staff notes (DAT 03)."""

    id: str
    authority_tier: AuthorityTier
    policy_family: PolicyFamily
    owner_name: str
    owner_role: str
    backup_owner: str | None = None
    escalation_sla_hours: int


class ApplicabilityCandidate(BaseModel):
    """Minimal version candidate evaluated for governing-date and conflict rules."""

    version_id: str
    authority_tier: AuthorityTier
    status: PolicyLifecycleStatus
    effective_from: datetime
    effective_to: datetime | None = None
    scope: str


class ApplicabilityResult(BaseModel):
    """Deterministic applicability and conflict-hold result (DAT 04, DAT 05, OPS 03)."""

    governing_date: date
    timezone: str = "Asia/Ho_Chi_Minh"
    is_historical: bool = False
    is_future_preview: bool = False
    applicable_version_ids: list[str] = Field(default_factory=list)
    has_conflict: bool = False
    hold_reason: str | None = None


class ThresholdCheckRequest(BaseModel):
    """Deterministic threshold comparison input (OPS 04)."""

    operator: ComparisonOperator
    actual_value: Decimal
    threshold_value: str


class ThresholdCheckResponse(BaseModel):
    """Exact code-computed threshold comparison result."""

    satisfied: bool
    operator: ComparisonOperator
    actual_value: Decimal
    threshold_value: str
