"""Add KNW 05 3-state tracking, minimal_context, hold_reason, and owner_role to local_referrals.

CKPA-92 (G2-AC01): Local Referral 3-state service stores question, minimal context,
hold_reason, and owner_role, while separately tracking referred -> owner_responded -> closed.

Revision ID: 20261127_01
Revises: 20261123_01
Create Date: 2026-11-27
"""

import sqlalchemy as sa
from alembic import op

revision = "20261127_01"
down_revision = "20261123_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "local_referrals",
        sa.Column(
            "owner_role",
            sa.String(length=64),
            nullable=False,
            server_default="policy_owner",
        ),
    )
    op.create_index("ix_local_referrals_owner_role", "local_referrals", ["owner_role"])

    op.add_column(
        "local_referrals",
        sa.Column(
            "minimal_context",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )

    op.add_column(
        "local_referrals",
        sa.Column("hold_reason", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_local_referrals_hold_reason", "local_referrals", ["hold_reason"])

    op.add_column(
        "local_referrals",
        sa.Column("owner_responded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "local_referrals",
        sa.Column("responded_by", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "local_referrals",
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "local_referrals",
        sa.Column("closed_by", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("local_referrals", "closed_by")
    op.drop_column("local_referrals", "closed_at")
    op.drop_column("local_referrals", "responded_by")
    op.drop_column("local_referrals", "owner_responded_at")
    op.drop_index("ix_local_referrals_hold_reason", table_name="local_referrals")
    op.drop_column("local_referrals", "hold_reason")
    op.drop_column("local_referrals", "minimal_context")
    op.drop_index("ix_local_referrals_owner_role", table_name="local_referrals")
    op.drop_column("local_referrals", "owner_role")
