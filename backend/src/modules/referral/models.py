"""ORM model for local CRM policy referrals (KNW 04)."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class LocalReferral(TimestampMixin, Base):
    """Escalation ticket linking unresolved/conflicting tasks to a Policy Owner."""

    __tablename__ = "local_referrals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    answer_package_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    requester_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_owner: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    policy_family: Mapped[str] = mapped_column(String(64), nullable=False)
    question_summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="referred", nullable=False, index=True)
    owner_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
