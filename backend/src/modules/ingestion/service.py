"""UTF-8 CSV validators and DAT 08 quarantine enforcement for Base Scope 2-CSV ingestion."""

import csv
import io

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.ingestion.models import QuarantineRow
from src.modules.ingestion.schemas import (
    CsvValidationReport,
    QuarantineIssue,
    QuarantineItemResponse,
)
from src.shared.enums import BatchType, RecordAction

PASSAGES_CSV_COLUMNS: tuple[str, ...] = (
    "passage_id",
    "document_id",
    "document_version_id",
    "title",
    "content",
    "source_ref",
    "page_number",
    "clause_ref",
    "language",
    "owner",
    "approver",
    "recorded_at",
    "published_at",
    "effective_from",
    "effective_to",
    "scope",
    "audience",
    "status",
    "supersedes",
    "has_essential_attachments",
    "record_action",
)

CRITICAL_FIELDS_CSV_COLUMNS: tuple[str, ...] = (
    "field_id",
    "policy_id",
    "policy_version_id",
    "document_version_id",
    "field_name",
    "field_type",
    "operator",
    "value",
    "unit",
    "currency",
    "approval_role",
    "time_limit",
    "exception_condition",
    "required_documents",
    "effective_from",
    "effective_to",
    "scope",
    "audience",
    "source_clause",
    "owner",
    "approver",
    "status",
    "record_action",
)


class IngestionService:
    """Validates Base Scope 2-CSV imports and prevents silent deletion."""

    def validate_csv_bytes(
        self,
        raw_bytes: bytes,
        *,
        source_type: str,
        batch_type: BatchType,
        expected_rows: int | None = None,
    ) -> CsvValidationReport:
        """Validate UTF-8 encoding, exact schema headers, batch bounds, and DAT 08 completeness."""
        expected_cols = (
            PASSAGES_CSV_COLUMNS if source_type == "passages" else CRITICAL_FIELDS_CSV_COLUMNS
        )
        text = raw_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        actual_cols = tuple(reader.fieldnames or ())
        if actual_cols != expected_cols:
            return CsvValidationReport(
                batch_type=batch_type,
                source_type=source_type,
                expected_rows=expected_rows or 0,
                received_rows=0,
                accepted_rows=0,
                rejected_rows=1,
                quarantined_rows=0,
                quarantine_issues=[
                    QuarantineIssue(
                        row_number=1,
                        reason_code="SCHEMA_HEADER_MISMATCH",
                        reason_detail=(
                            f"Header mismatch for {source_type}: expected {len(expected_cols)} "
                            f"columns, got {len(actual_cols)}."
                        ),
                    )
                ],
            )

        rows = list(reader)
        issues: list[QuarantineIssue] = []
        accepted = 0
        if len(rows) > settings.IMPORT_MAX_ROWS_PER_BATCH:
            issues.append(
                QuarantineIssue(
                    row_number=0,
                    reason_code="BATCH_LIMIT_EXCEEDED",
                    reason_detail=(
                        f"Received {len(rows)} rows exceeding limit "
                        f"{settings.IMPORT_MAX_ROWS_PER_BATCH}."
                    ),
                )
            )
            return CsvValidationReport(
                batch_type=batch_type,
                source_type=source_type,
                expected_rows=expected_rows if expected_rows is not None else len(rows),
                received_rows=len(rows),
                accepted_rows=0,
                rejected_rows=len(rows),
                quarantined_rows=0,
                quarantine_issues=issues,
            )

        for idx, row in enumerate(rows, start=2):
            reason = self._validate_row(row, source_type=source_type)
            if reason is not None:
                code, detail, rec_id = reason
                issues.append(
                    QuarantineIssue(
                        row_number=idx,
                        record_id=rec_id,
                        reason_code=code,
                        reason_detail=detail,
                    )
                )
            else:
                accepted += 1

        return CsvValidationReport(
            batch_type=batch_type,
            source_type=source_type,
            expected_rows=expected_rows if expected_rows is not None else len(rows),
            received_rows=len(rows),
            accepted_rows=accepted,
            rejected_rows=0,
            quarantined_rows=len(issues),
            quarantine_issues=issues,
        )

    def _validate_row(
        self, row: dict[str, str | None], *, source_type: str
    ) -> tuple[str, str, str | None] | None:
        id_col = "passage_id" if source_type == "passages" else "field_id"
        rec_id = (row.get(id_col) or "").strip() or None
        action = (row.get("record_action") or "").strip().lower()
        if action not in {RecordAction.UPSERT.value, RecordAction.TOMBSTONE.value}:
            return ("INVALID_RECORD_ACTION", "record_action must be upsert or tombstone.", rec_id)

        if source_type == "passages":
            content = row.get("content") or ""
            if len(content) > settings.PASSAGE_MAX_CHARS:
                return (
                    "PASSAGE_TOO_LONG",
                    f"Content length {len(content)} exceeds {settings.PASSAGE_MAX_CHARS} chars.",
                    rec_id,
                )
            att = (row.get("has_essential_attachments") or "").strip().lower()
            if att != "true":
                return (
                    "MISSING_ESSENTIAL_ATTACHMENTS",
                    "DAT 08 Quarantine: missing essential table, diagram, or footnote.",
                    rec_id,
                )
        else:
            if (row.get("field_type") or "").strip() == "currency" and not (
                row.get("currency") or ""
            ).strip():
                return (
                    "MISSING_CURRENCY_UNIT",
                    "OPS 04 Quarantine: currency field requires explicit currency code (VND/USD).",
                    rec_id,
                )
        return None

    async def list_quarantine(
        self, db: AsyncSession, *, unresolved_only: bool = True
    ) -> list[QuarantineItemResponse]:
        """List quarantined CSV records awaiting steward remediation."""
        stmt = select(QuarantineRow)
        if unresolved_only:
            stmt = stmt.where(QuarantineRow.resolved.is_(False))
        rows = (await db.execute(stmt.order_by(QuarantineRow.id.desc()))).scalars().all()
        return [
            QuarantineItemResponse(
                id=r.id,
                batch_id=r.batch_id,
                row_number=r.row_number,
                record_id=r.record_id,
                reason_code=r.reason_code,
                reason_detail=r.reason_detail,
                resolved=r.resolved,
            )
            for r in rows
        ]
