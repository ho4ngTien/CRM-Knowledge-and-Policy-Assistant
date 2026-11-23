"""ORM models for policy authority matrix, lifecycle versions, and critical fields."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class AuthorityEntry(TimestampMixin, Base):
    """Source authority hierarchy entry separated by tier and scope (DAT 03)."""

    __tablename__ = "authority_matrix"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    authority_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    policy_family: Mapped[str] = mapped_column(String(64), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(128), nullable=False)
    owner_role: Mapped[str] = mapped_column(String(64), nullable=False)
    backup_owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    escalation_sla_hours: Mapped[int] = mapped_column(default=24, nullable=False)


class Policy(TimestampMixin, Base):
    """Logical CRM business policy identifier."""

    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    policy_family: Mapped[str] = mapped_column(String(64), nullable=False)
    authority_entry_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("authority_matrix.id"), nullable=True
    )


class PolicyVersion(TimestampMixin, Base):
    """Dated, scoped, auditable policy version governing answer applicability (KNW 03, DAT 04)."""

    __tablename__ = "policy_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    policy_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_version_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("document_versions.id"), nullable=False, index=True
    )
    scope: Mapped[str] = mapped_column(String(500), nullable=False)
    audience: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False, index=True)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    supersedes_version_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    owner: Mapped[str] = mapped_column(String(128), nullable=False)
    approver: Mapped[str | None] = mapped_column(String(128), nullable=True)


class CriticalField(TimestampMixin, Base):
    """Typed deterministic policy parameter linked to its source clause (DAT 06, OPS 04)."""

    __tablename__ = "critical_fields"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    policy_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    policy_version_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("policy_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_version_id: Mapped[str] = mapped_column(String(64), nullable=False)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(32), nullable=False)
    operator: Mapped[str] = mapped_column(String(16), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    approval_role: Mapped[str] = mapped_column(String(128), nullable=False)
    time_limit: Mapped[str | None] = mapped_column(String(128), nullable=True)
    exception_condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_documents: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_clause: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(500), nullable=False)
    audience: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False, index=True)
    is_tombstoned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    tombstoned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tombstone_batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    withdrawal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_batch_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    source_recorded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class PolicyLifecycleEvent(TimestampMixin, Base):
    """Immutable actor/role/timestamp audit record for every lifecycle transition (KNW 03)."""

    __tablename__ = "policy_lifecycle_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    policy_version_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("policy_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
