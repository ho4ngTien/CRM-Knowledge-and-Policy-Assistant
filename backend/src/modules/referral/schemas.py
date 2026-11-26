"""Pydantic schemas for local policy referral workflow (KNW 05).

Three-state lifecycle: referred -> owner_responded -> closed.
No CRM writeback. No external message dispatch. No auto-approval.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from src.shared.enums import PolicyFamily, ReferralStatus


class ReferralCreateRequest(BaseModel):
    """Create a local escalation ticket linked to a task (KNW 05 / UI-GOV-02)."""

    task_id: str = Field(..., min_length=1, max_length=64)
    answer_package_id: str | None = None
    owner_role: str = Field(default="policy_owner", min_length=1, max_length=64)
    target_owner: str = Field(..., min_length=1, max_length=128)
    policy_family: PolicyFamily
    question_summary: str = Field(..., min_length=5, max_length=2000)
    minimal_context: dict[str, Any] = Field(default_factory=dict)
    hold_reason: str | None = Field(default=None, max_length=64)


class ReferralUpdateRequest(BaseModel):
    """Transition referral status or record owner resolution (KNW 05 state machine guard)."""

    status: ReferralStatus
    owner_response: str | None = Field(default=None, max_length=4000)
    resolution_note: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_owner_response_when_responding(self) -> "ReferralUpdateRequest":
        """Ensure owner_responded state always records a non-empty owner response."""
        if self.status == ReferralStatus.OWNER_RESPONDED:
            if not self.owner_response or len(self.owner_response.strip()) < 3:
                raise ValueError(
                    "owner_response must be provided (>= 3 chars) when transitioning "
                    "to owner_responded."
                )
        return self


class ReferralResponse(BaseModel):
    """Local referral status record preserving task lineage and 3-state tracking (KNW 05)."""

    id: str
    task_id: str
    answer_package_id: str | None = None
    requester_id: str
    owner_role: str
    target_owner: str
    policy_family: PolicyFamily
    question_summary: str
    minimal_context: dict[str, Any] = Field(default_factory=dict)
    hold_reason: str | None = None
    status: ReferralStatus
    owner_response: str | None = None
    owner_responded_at: datetime | None = None
    responded_by: str | None = None
    resolution_note: str | None = None
    closed_at: datetime | None = None
    closed_by: str | None = None
    created_at: datetime


class AnnexBReferralRequest(BaseModel):
    """Evaluate and optionally record a Local Referral for one of Annex B cases SC-01..SC-09."""

    case_id: str = Field(..., min_length=3, max_length=16)
    task_id: str = Field(..., min_length=1, max_length=64)
    answer_package_id: str | None = None
    question: str = Field(..., min_length=5, max_length=2000)
    scope: str = Field(default="", max_length=500)
    governing_date: str | None = Field(default=None, max_length=32)
    answer_status: str = Field(default="hold", max_length=32)
    hold_reason: str | None = Field(default=None, max_length=64)
    missing_facts: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    has_essential_attachments: bool = True
    has_contract_conflict: bool = False
    is_staff_note_rule_request: bool = False
    is_crm_writeback_request: bool = False
    is_auto_approve_request: bool = False
    is_withdrawn: bool = False


class AnnexBHandlingResult(BaseModel):
    """Outcome of Annex B handler evaluation and local referral persistence."""

    case_id: str
    matrix_id: str
    rfp_map_id: str
    referral_created: bool
    hold_reason: str | None = None
    owner_role: str
    target_owner: str
    referral: ReferralResponse | None = None
    crm_writeback_count: int = 0
    messages_dispatched: int = 0
    auto_approved: bool = False
