"""Governed feedback queue service (KNW 06 no-auto-train guard + KNW 07 reasons)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.feedback.models import FeedbackCandidate
from src.modules.feedback.schemas import FeedbackCandidateResponse, FeedbackCreateRequest
from src.shared.auth import AuthenticatedUser
from src.shared.enums import FeedbackReason, PolicyLifecycleStatus


class FeedbackService:
    """Queues feedback candidates for steward triage without mutating active knowledge."""

    async def submit_feedback(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        payload: FeedbackCreateRequest,
    ) -> FeedbackCandidateResponse:
        """Persist staff feedback strictly as a review candidate (auto_applied=False)."""
        item = FeedbackCandidate(
            id=f"FBK-{uuid.uuid4().hex[:10].upper()}",
            task_id=payload.task_id,
            answer_package_id=payload.answer_package_id,
            reporter_id=user.user_id,
            reason=payload.reason.value,
            unanswered_topic=payload.unanswered_topic,
            comment=payload.comment,
            candidate_status=PolicyLifecycleStatus.FEEDBACK_CANDIDATE.value,
            auto_applied=False,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return self._to_schema(item)

    async def list_candidates(
        self, db: AsyncSession, reason_filter: FeedbackReason | None = None
    ) -> list[FeedbackCandidateResponse]:
        """List governed feedback candidates for steward & policy owner triage."""
        stmt = select(FeedbackCandidate)
        if reason_filter is not None:
            stmt = stmt.where(FeedbackCandidate.reason == reason_filter.value)
        stmt = stmt.order_by(FeedbackCandidate.created_at.desc())
        rows = (await db.execute(stmt)).scalars().all()
        return [self._to_schema(r) for r in rows]

    def _to_schema(self, row: FeedbackCandidate) -> FeedbackCandidateResponse:
        return FeedbackCandidateResponse(
            id=row.id,
            task_id=row.task_id,
            answer_package_id=row.answer_package_id,
            reporter_id=row.reporter_id,
            reason=FeedbackReason(row.reason),
            unanswered_topic=row.unanswered_topic,
            comment=row.comment,
            candidate_status=row.candidate_status,
            auto_applied=row.auto_applied,
            created_at=row.created_at,
        )
