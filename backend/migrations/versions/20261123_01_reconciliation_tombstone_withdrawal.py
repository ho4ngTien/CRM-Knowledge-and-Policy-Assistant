"""Add reconciliation, tombstone, and withdrawal metadata to authoritative records."""

import sqlalchemy as sa
from alembic import op

revision = "20261123_01"
down_revision = "20261121_01"
branch_labels = None
depends_on = None


def _upgrade_authoritative_table(table_name: str) -> None:
    op.add_column(
        table_name,
        sa.Column("is_tombstoned", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(f"ix_{table_name}_is_tombstoned", table_name, ["is_tombstoned"])
    op.add_column(table_name, sa.Column("tombstoned_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(table_name, sa.Column("tombstone_batch_id", sa.String(length=64), nullable=True))
    op.add_column(table_name, sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(table_name, sa.Column("withdrawn_by", sa.String(length=64), nullable=True))
    op.add_column(table_name, sa.Column("withdrawal_reason", sa.Text(), nullable=True))
    op.add_column(table_name, sa.Column("last_batch_id", sa.String(length=64), nullable=True))
    op.add_column(
        table_name, sa.Column("last_batch_timestamp", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        table_name, sa.Column("source_recorded_at", sa.DateTime(timezone=True), nullable=True)
    )


def upgrade() -> None:
    _upgrade_authoritative_table("passages")
    _upgrade_authoritative_table("critical_fields")


def downgrade() -> None:
    for table_name in ("critical_fields", "passages"):
        op.drop_index(f"ix_{table_name}_is_tombstoned", table_name=table_name)
        for column_name in (
            "source_recorded_at",
            "last_batch_timestamp",
            "last_batch_id",
            "withdrawal_reason",
            "withdrawn_by",
            "withdrawn_at",
            "tombstone_batch_id",
            "tombstoned_at",
            "is_tombstoned",
        ):
            op.drop_column(table_name, column_name)
