"""ORM models for Chinese-Wall-isolated independent evaluation runs (RFP Section 8, VN 02)."""

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class EvaluationRun(TimestampMixin, Base):
    """Stores gate evaluation metrics strictly separated between real_200 and challenges_80."""

    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    release_gate: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    partition: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    evaluator_id: Mapped[str] = mapped_column(String(64), nullable=False)
    total_cases: Mapped[int] = mapped_column(Integer, nullable=False)
    critical_control_errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    applicability_rate: Mapped[float] = mapped_column(Float, nullable=False)
    grounding_rate: Mapped[float] = mapped_column(Float, nullable=False)
    completeness_rate: Mapped[float] = mapped_column(Float, nullable=False)
    recall_at_5: Mapped[float] = mapped_column(Float, nullable=False)
    usefulness_rate: Mapped[float] = mapped_column(Float, nullable=False)
    fabrication_on_unanswerable_rate: Mapped[float] = mapped_column(Float, nullable=False)
    passed_thresholds: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class EvaluationCaseResult(TimestampMixin, Base):
    """Per-case evaluation outcome partitioned under Chinese Wall access rules."""

    __tablename__ = "evaluation_case_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    case_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    partition: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    is_answerable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    critical_error: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
