"""Pydantic schemas for the Selection layer (DAT 04–06, DAT 08, OPS 03–04, VN 01) [CRM-G1-SUB14]."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# 6-Dimension Scope Matcher  (DAT 04)
# ---------------------------------------------------------------------------

class ScopeDimensions(BaseModel):
    """Six mandatory applicability dimensions for scope matching (DAT 04).

    All fields accept ``None`` to represent "not specified / wildcard".
    A policy scope marked ``"all"`` for a dimension matches any value.
    """

    model_config = ConfigDict(extra="forbid")

    company: str | None = Field(
        default=None,
        description="Legal entity / company code (e.g. 'SONGNHAT_HN').",
    )
    branch: str | None = Field(
        default=None,
        description="Branch or location code (e.g. 'HN01', 'HCM02').",
    )
    role: str | None = Field(
        default=None,
        description="Organisational role of the querying user (e.g. 'sales_executive').",
    )
    customer_category: str | None = Field(
        default=None,
        description="Customer segment code (e.g. 'b2b', 'b2c', 'loyal').",
    )
    product: str | None = Field(
        default=None,
        description="Product line or SKU family (e.g. '3-phase-motor', 'inverter').",
    )
    transaction_scope: str | None = Field(
        default=None,
        description="Transaction type or approval scope (e.g. 'quotation', 'warranty').",
    )


class ScopeMatchResult(BaseModel):
    """Result of a 6-dimension scope match."""

    model_config = ConfigDict(extra="forbid")

    version_id: str
    matched: bool
    unmatched_dimensions: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Governing Date Resolver  (DAT 04 / UTC+7)
# ---------------------------------------------------------------------------

class GoverningDateResult(BaseModel):
    """Resolved governing calendar date in UTC+7 (Asia/Ho_Chi_Minh)."""

    model_config = ConfigDict(extra="forbid")

    governing_date: date
    timezone: str = "Asia/Ho_Chi_Minh"
    is_historical: bool = False
    is_future_preview: bool = False
    resolved_from: Literal["request", "system_now"] = "system_now"


# ---------------------------------------------------------------------------
# Critical Field Lookup  (DAT 06, DAT 08) ≤ 50 rows
# ---------------------------------------------------------------------------

class CriticalFieldLookupRequest(BaseModel):
    """Request to fetch deterministic critical fields for a policy version set."""

    model_config = ConfigDict(extra="forbid")

    version_ids: list[str] = Field(
        ...,
        description="Applicable policy_version_id list from the gate decision.",
        min_length=1,
    )
    governing_date: date = Field(
        ...,
        description="Resolved UTC+7 date used to filter field effective windows.",
    )


class CriticalFieldLookupResult(BaseModel):
    """Deterministic structured critical-field set resolved without LLM (DAT 06)."""

    model_config = ConfigDict(extra="forbid")

    version_id: str
    fields_found: int
    fields: list[dict[str, object]] = Field(default_factory=list)
    has_missing_annotations: bool = False
    missing_annotation_detail: str | None = None


# ---------------------------------------------------------------------------
# Hold Decision  (DAT 04, DAT 05, DAT 08, OPS 03)
# ---------------------------------------------------------------------------

class HoldTrigger(BaseModel):
    """Single hold trigger with its RFP code and human-readable reason."""

    model_config = ConfigDict(extra="forbid")

    code: Literal[
        "DAT04_NO_GOVERNING_DATE",
        "DAT04_NO_APPLICABLE_VERSION",
        "DAT05_SOURCE_CONFLICT",
        "DAT08_MISSING_TABLE_OR_ANNOTATION",
        "OPS03_MANDATORY_HOLD",
    ]
    reason_vi: str


class SelectionHoldDecision(BaseModel):
    """Mandatory Hold gate result emitted by the Selection service (OPS 03).

    ``must_hold`` is ``True`` whenever **any** of the three forced-hold
    conditions (DAT 04 missing date/version, DAT 08 missing attachment,
    DAT 05 source conflict) is detected.  The pipeline **must not** proceed
    to LLM generation when this flag is set.
    """

    model_config = ConfigDict(extra="forbid")

    must_hold: bool
    triggers: list[HoldTrigger] = Field(default_factory=list)
    combined_reason_vi: str | None = None


# ---------------------------------------------------------------------------
# Full Selection Result
# ---------------------------------------------------------------------------

class SelectionResult(BaseModel):
    """Composite result of the Selection layer (WP03, DEL02) [CRM-G1-SUB14].

    Encapsulates:
    - Resolved governing date (UTC+7)
    - 6-dimension scope match results
    - Deterministic critical-field lookup (≤ 50 rows, 0% LLM)
    - Mandatory Hold decision
    """

    model_config = ConfigDict(extra="forbid")

    task_id: str
    governing_date_result: GoverningDateResult
    scope_matches: list[ScopeMatchResult] = Field(default_factory=list)
    applicable_version_ids: list[str] = Field(default_factory=list)
    critical_field_lookups: list[CriticalFieldLookupResult] = Field(default_factory=list)
    hold_decision: SelectionHoldDecision
    llm_used: bool = Field(
        default=False,
        description="Always False – Selection layer is 100% deterministic (0% LLM).",
    )
    resolved_at: datetime | None = None
