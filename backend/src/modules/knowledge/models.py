"""ORM models for curated documents, version lineage, passages, and pgvector embeddings."""

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class Document(TimestampMixin, Base):
    """Canonical Base Scope policy/SOP document header (<= 30 active documents)."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    policy_family: Mapped[str] = mapped_column(String(64), nullable=False)
    authority_tier: Mapped[str] = mapped_column(String(64), default="policy", nullable=False)
    owner: Mapped[str] = mapped_column(String(128), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(500), nullable=False)


class DocumentVersion(TimestampMixin, Base):
    """Immutable version record separating effective dates from recorded timestamps (DAT 01)."""

    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    approver: Mapped[str | None] = mapped_column(String(128), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False, index=True)
    supersedes_version_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class Passage(TimestampMixin, Base):
    """Curated UTF-8 policy passage (<= 300 total, <= 6000 Unicode chars each, DAT 01/08)."""

    __tablename__ = "passages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_version_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    clause_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(8), default="vi", nullable=False)
    scope: Mapped[str] = mapped_column(String(500), nullable=False)
    audience: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False, index=True)
    has_essential_attachments: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_tombstoned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)


class PassageEmbedding(TimestampMixin, Base):
    """Vector index row decoupled from Passage content for safe re-indexing."""

    __tablename__ = "passage_embeddings"

    passage_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("passages.id", ondelete="CASCADE"), primary_key=True
    )
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
