"""ORM models for organizational identity & least-privilege RBAC (SEC 01, SRS-FR-02)."""

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, TimestampMixin


class User(TimestampMixin, Base):
    """Enterprise user synced from organizational identity provider."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(64), default="SN", nullable=False)
    branch: Mapped[str] = mapped_column(String(64), default="all", nullable=False)
    department: Mapped[str] = mapped_column(String(64), default="crm", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserRoleAssignment(TimestampMixin, Base):
    """Explicit least-privilege role grant bounded by scope."""

    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_name", name="uq_user_role"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_name: Mapped[str] = mapped_column(String(64), nullable=False)
    allowed_audiences: Mapped[str] = mapped_column(String(255), default="reader", nullable=False)
