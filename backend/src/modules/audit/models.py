"""ORM models for restricted security audit logs and Common Bid Basis cost metering."""

from sqlalchemy import JSON, Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class AuditLog(TimestampMixin, Base):
    """Access-restricted audit trail for auth, lifecycle, withdrawal, and eval access."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    actor_role: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(64), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class UsageCostMeter(TimestampMixin, Base):
    """Per-task meter tracking tokens, LLM calls, holds, errors, and monthly quotas (OPS 06)."""

    __tablename__ = "usage_cost_meters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    month_key: Mapped[str] = mapped_column(String(7), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    answer_package_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    llm_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_hold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_error: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_cost_vnd: Mapped[float] = mapped_column(Numeric(14, 2), default=0.0, nullable=False)
