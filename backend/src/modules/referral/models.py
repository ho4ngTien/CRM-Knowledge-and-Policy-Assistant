"""ORM model for local CRM policy referrals (KNW 05).

Three-state local referral lifecycle mandated by KNW 05 (Annex B UI-GOV-02):
  referred -> owner_responded -> closed
No CRM writeback, no external workflow engine, no message dispatch, no auto-approval.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class LocalReferral(TimestampMixin, Base):
    """Escalation ticket linking unresolved/conflicting tasks to an accountable owner (KNW 05)."""

    __tablename__ = "local_referrals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    answer_package_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    requester_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # owner_role: organizational role of accountable handler (e.g. "policy_owner", "steward")
    owner_role: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_owner: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    policy_family: Mapped[str] = mapped_column(String(64), nullable=False)
    question_summary: Mapped[str] = mapped_column(Text, nullable=False)
    # minimal_context: PII-free structured context (scope, governing_date, missing_facts, case_id)
    minimal_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    # hold_reason: HOLD trigger code (HOLD_ANS06, HOLD_ANS07, HOLD_DAT05, HOLD_DAT08, HOLD_SEC05)
    hold_reason: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # KNW 05 separate 3-state tracking: referred -> owner_responded -> closed
    status: Mapped[str] = mapped_column(String(32), default="referred", nullable=False, index=True)
    owner_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    responded_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
