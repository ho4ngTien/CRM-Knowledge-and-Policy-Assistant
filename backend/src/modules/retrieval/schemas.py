"""Pydantic schemas for pre-filtered hybrid Vietnamese retrieval (ANS 02, VN 01)."""

from datetime import date

from pydantic import BaseModel, Field

from src.modules.knowledge.schemas import PassageSummary


class RetrievalSearchRequest(BaseModel):
    """Pre-filtered retrieval query constrained by VN governing date and scope."""

    query: str = Field(..., min_length=1, max_length=2000)
    governing_date: date | None = None
    scope_filter: str | None = None
    allow_historical: bool = False
    allow_future_preview: bool = False
    top_k: int = Field(default=8, ge=1, le=8)


class RetrievalSearchResponse(BaseModel):
    """Bounded curated context packet returned from hybrid retrieval (<= 8 passages)."""

    normalized_query: str
    expanded_terms: list[str] = Field(default_factory=list)
    preserved_negations: list[str] = Field(default_factory=list)
    passages: list[PassageSummary] = Field(default_factory=list, max_length=8)
    total_candidates_filtered: int = 0
