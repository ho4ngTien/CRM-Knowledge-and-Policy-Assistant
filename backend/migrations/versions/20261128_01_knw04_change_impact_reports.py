"""Persist KNW 04 Change Impact reports and active-view refresh limits.

Revision ID: 20261128_01
Revises: 20261127_01
"""

import sqlalchemy as sa
from alembic import op

revision = "20261128_01"
down_revision = "20261127_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "change_impact_reports",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=True),
        sa.Column("policy_version_id", sa.String(length=64), nullable=True),
        sa.Column("document_version_id", sa.String(length=64), nullable=True),
        sa.Column("actor_id", sa.String(length=64), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("stale_answers_marked", sa.Integer(), nullable=False),
        sa.Column("active_view_refresh_interval_seconds", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_change_impact_reports_event_type", "change_impact_reports", ["event_type"]
    )
    op.create_index(
        "ix_change_impact_reports_policy_version_id",
        "change_impact_reports",
        ["policy_version_id"],
    )
    op.create_index(
        "ix_change_impact_reports_document_version_id",
        "change_impact_reports",
        ["document_version_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_change_impact_reports_document_version_id", table_name="change_impact_reports"
    )
    op.drop_index(
        "ix_change_impact_reports_policy_version_id", table_name="change_impact_reports"
    )
    op.drop_index("ix_change_impact_reports_event_type", table_name="change_impact_reports")
    op.drop_table("change_impact_reports")
