"""ORM models for persisted AnswerPackage deliveries and verified citations."""

from datetime import date

from sqlalchemy import JSON, Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class AnswerPackageRecord(TimestampMixin, Base):
    """Persisted post-validation answer package supporting follow-up & withdrawal invalidation."""

    __tablename__ = "answer_packages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    original_question: Mapped[str] = mapped_column(Text, nullable=False)
    governing_date: Mapped[date] = mapped_column(Date, nullable=False)
    scope: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    guidance_text: Mapped[str] = mapped_column(Text, nullable=False)
    hold_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    referral_target: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    llm_calls_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    package_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class AnswerCitationRecord(TimestampMixin, Base):
    """Normalized citation link enabling instant stale invalidation upon policy withdrawal."""

    __tablename__ = "answer_citations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    answer_package_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("answer_packages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    passage_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    document_version_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    clause_ref: Mapped[str] = mapped_column(String(255), nullable=False)
