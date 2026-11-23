"""Pydantic schemas for the mandatory 7-part AnswerPackage (ANS 01, ANS 03, SRS-FR-06.1) [CKPA-17]."""  # noqa: E501

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from src.modules.policy.schemas import CriticalFieldItem
from src.shared.enums import AnswerStatus


class AnswerCitation(BaseModel):
    """Verified clickable citation anchored to a curated document passage."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    document_version_id: str
    passage_id: str
    title: str
    page_number: int = Field(..., ge=1)
    clause_ref: str
    quoted_text: str
    evidence_url: str


class AnswerQueryRequest(BaseModel):
    """Staff policy query with optional VN governing date & Base Scope filters."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(..., min_length=2, max_length=2000)
    task_id: str | None = Field(default=None, max_length=64)
    governing_date: date | None = None
    scope: str = Field(default="company:SN;branch:all;role:all;customer_group:all;product:all")
    allow_future_preview: bool = False


class AnswerPackage(BaseModel):
    """Complete 7-part verified response returned only AFTER post-generation validation.

    Strictly frozen under Gate G1, SRS Mục 4.3, 7.2, SRS-FR-06.1
    | RFP: ANS03, ANS04, DEL02 [CKPA-17].
    """

    model_config = ConfigDict(extra="forbid")

    answer_id: str
    task_id: str
    status: AnswerStatus

    # Part 1: Original question
    original_question: str

    # Part 2: Governing date (Asia/Ho_Chi_Minh) & matched scope flags
    governing_date: date
    timezone: str = "Asia/Ho_Chi_Minh"
    scope: str
    is_historical: bool = False
    is_future_preview: bool = False

    # Part 3: Concise Vietnamese explanation & separated verbatim quotes
    guidance_text: str
    verbatim_quotes: list[str] = Field(default_factory=list)

    # Part 4: Grounded source citations
    citations: list[AnswerCitation] = Field(default_factory=list)

    # Part 5: Deterministic structured critical fields
    critical_fields: list[CriticalFieldItem] = Field(default_factory=list)

    # Part 6: Missing facts, Hold reason & uncertainty/clarification guidance
    missing_facts: list[str] = Field(default_factory=list)
    hold_reason: str | None = None
    uncertainty_note: str | None = None

    # Part 7: Local referral target & mandatory internal-use disclaimer
    referral_target: str | None = None
    internal_use_warning: str

    # Runtime governance metadata
    pii_warning: str | None = None
    snapshot_age_hours: float | None = None
    llm_calls_used: int = Field(default=0, ge=0, le=2)
