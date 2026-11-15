"""ORM model for feedback & unanswered topic candidates (KNW 06, KNW 07)."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class FeedbackCandidate(TimestampMixin, Base):
    """Structured feedback/owner note queued for steward review (never auto-trained)."""

    __tablename__ = "feedback_candidates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    answer_package_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    reporter_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    unanswered_topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    candidate_status: Mapped[str] = mapped_column(
        String(32), default="feedback_candidate", nullable=False
    )
    auto_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
