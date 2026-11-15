"""Pydantic schemas for local policy referral workflow (KNW 04)."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.shared.enums import PolicyFamily, ReferralStatus


class ReferralCreateRequest(BaseModel):
    """Create a structured local escalation ticket to a designated owner."""

    task_id: str = Field(..., min_length=1, max_length=64)
    answer_package_id: str | None = None
    target_owner: str = Field(..., min_length=1, max_length=128)
    policy_family: PolicyFamily
    question_summary: str = Field(..., min_length=5, max_length=2000)


class ReferralUpdateRequest(BaseModel):
    """Transition referral status or record owner resolution guidance."""

    status: ReferralStatus
    owner_response: str | None = Field(default=None, max_length=4000)
    resolution_note: str | None = Field(default=None, max_length=2000)


class ReferralResponse(BaseModel):
    """Local referral status record preserving task lineage."""

    id: str
    task_id: str
    answer_package_id: str | None = None
    requester_id: str
    target_owner: str
    policy_family: PolicyFamily
    question_summary: str
    status: ReferralStatus
    owner_response: str | None = None
    resolution_note: str | None = None
    created_at: datetime
