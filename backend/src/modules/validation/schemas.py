"""Pydantic schemas for pre-delivery citation and authoritative state validation."""

from pydantic import BaseModel, Field

from src.shared.enums import PolicyLifecycleStatus


class CitationCheckInput(BaseModel):
    """Citation reference verified against authoritative curated passages."""

    passage_id: str
    document_id: str
    document_version_id: str
    quoted_text: str


class FinalValidationRequest(BaseModel):
    """Payload submitted right before returning an AnswerPackage to UI (KNW 04)."""

    answer_id: str
    citations: list[CitationCheckInput] = Field(default_factory=list)
    required_audiences: list[str] = Field(default_factory=list)
    current_source_statuses: dict[str, PolicyLifecycleStatus] = Field(default_factory=dict)
    allow_historical: bool = False
    allow_future_preview: bool = False


class FinalValidationResponse(BaseModel):
    """Fail-closed validation decision blocking withdrawn or fabricated evidence."""

    is_valid: bool
    stale: bool = False
    verified_citations_count: int = 0
    errors: list[str] = Field(default_factory=list)
    active_view_refresh_interval_seconds: int = 60
