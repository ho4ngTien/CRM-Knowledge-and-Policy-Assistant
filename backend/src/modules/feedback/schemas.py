"""Pydantic schemas for KNW 07 5-reason feedback and KNW 06 review queue."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.shared.enums import FeedbackReason


class FeedbackCreateRequest(BaseModel):
    """Staff feedback submission constrained to KNW 07 categories (never auto-updates rules)."""

    task_id: str = Field(..., min_length=1, max_length=64)
    answer_package_id: str | None = None
    reason: FeedbackReason
    unanswered_topic: str | None = Field(default=None, max_length=255)
    comment: str = Field(..., min_length=3, max_length=2000)


class FeedbackCandidateResponse(BaseModel):
    """Governed feedback candidate awaiting steward & owner review."""

    id: str
    task_id: str
    answer_package_id: str | None = None
    reporter_id: str
    reason: FeedbackReason
    unanswered_topic: str | None = None
    comment: str
    candidate_status: str
    auto_applied: bool = False
    created_at: datetime


class UnansweredTopicCount(BaseModel):
    """Anonymous aggregated topic frequency, suppressed until k=5."""

    topic: str
    count: int = Field(..., ge=5)
