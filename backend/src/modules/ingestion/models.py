"""ORM models for idempotent CSV import batches, reconciliation manifests, and quarantine."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class ImportBatch(TimestampMixin, Base):
    """Explicit daily or full-snapshot import batch preventing late-batch overwrite (DAT 02)."""

    __tablename__ = "import_batches"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    batch_type: Mapped[str] = mapped_column(String(32), nullable=False)
    batch_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    submitted_by: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="validated", nullable=False)


class ImportManifest(TimestampMixin, Base):
    """Per-batch row count reconciliation and quarantine summary (DAT 02)."""

    __tablename__ = "import_manifests"

    batch_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("import_batches.id", ondelete="CASCADE"), primary_key=True
    )
    expected_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    received_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    accepted_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    rejected_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    quarantined_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    summary_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class ImportRecord(TimestampMixin, Base):
    """Validated row staged by an import batch without publishing it to retrieval."""

    __tablename__ = "import_records"
    __table_args__ = (
        UniqueConstraint("batch_id", "source_type", "record_id", name="uq_import_record_batch_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    record_id: Mapped[str] = mapped_column(String(64), nullable=False)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class QuarantineRow(TimestampMixin, Base):
    """Quarantined record failing UTF-8, attachment completeness, or boundary rules (DAT 08)."""

    __tablename__ = "quarantine_rows"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    record_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_detail: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
