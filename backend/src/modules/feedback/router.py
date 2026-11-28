"""Feedback & knowledge candidate HTTP router (/api/v1/feedback/*)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.feedback.schemas import (
    FeedbackCandidateResponse,
    FeedbackCreateRequest,
    UnansweredTopicCount,
)
from src.modules.feedback.service import FeedbackService
from src.shared.auth import AuthenticatedUser, get_current_user, require_roles
from src.shared.enums import FeedbackReason, UserRole

router = APIRouter()
service = FeedbackService()


@router.post("", response_model=FeedbackCandidateResponse, status_code=201)
async def submit_feedback(
    payload: FeedbackCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> FeedbackCandidateResponse:
    """Record 5-reason staff feedback (queued as candidate; never auto-trained)."""
    return await service.submit_feedback(db, current_user, payload)


@router.get("/candidates", response_model=list[FeedbackCandidateResponse])
async def list_feedback_candidates(
    reason: FeedbackReason | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> list[FeedbackCandidateResponse]:
    """List feedback candidates awaiting steward curation."""
    _ = current_user
    return await service.list_candidates(db, reason_filter=reason)


@router.get("/unanswered-topics", response_model=list[UnansweredTopicCount])
async def list_anonymous_unanswered_topics(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> list[UnansweredTopicCount]:
    """Return repeated unanswered topics without reporter or task identifiers (KNW 07)."""
    _ = current_user
    return await service.unanswered_topic_counts(db)
