"""Create batch, manifest, accepted staging, and quarantine tables."""

import sqlalchemy as sa
from alembic import op

revision = "20261121_01"
down_revision = "b01d4334f030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("batch_type", sa.String(length=32), nullable=False),
        sa.Column("batch_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False, unique=True),
        sa.Column("submitted_by", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="validated"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "import_manifests",
        sa.Column(
            "batch_id",
            sa.String(length=64),
            sa.ForeignKey("import_batches.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("expected_rows", sa.Integer(), nullable=False),
        sa.Column("received_rows", sa.Integer(), nullable=False),
        sa.Column("accepted_rows", sa.Integer(), nullable=False),
        sa.Column("rejected_rows", sa.Integer(), nullable=False),
        sa.Column("quarantined_rows", sa.Integer(), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "import_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "batch_id",
            sa.String(length=64),
            sa.ForeignKey("import_batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("record_id", sa.String(length=64), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "batch_id", "source_type", "record_id", name="uq_import_record_batch_id"
        ),
    )
    op.create_index("ix_import_records_batch_id", "import_records", ["batch_id"])
    op.create_table(
        "quarantine_rows",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "batch_id",
            sa.String(length=64),
            sa.ForeignKey("import_batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.String(length=64), nullable=True),
        sa.Column("reason_code", sa.String(length=64), nullable=False),
        sa.Column("reason_detail", sa.Text(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_quarantine_rows_batch_id", "quarantine_rows", ["batch_id"])


def downgrade() -> None:
    op.drop_index("ix_quarantine_rows_batch_id", table_name="quarantine_rows")
    op.drop_table("quarantine_rows")
    op.drop_index("ix_import_records_batch_id", table_name="import_records")
    op.drop_table("import_records")
    op.drop_table("import_manifests")
    op.drop_table("import_batches")
