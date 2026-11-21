"""UTF-8 CSV validators and DAT 08 quarantine enforcement for Base Scope imports."""

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.ingestion.models import (
    ImportBatch,
    ImportManifest,
    ImportRecord,
    QuarantineRow,
)
from src.modules.ingestion.schemas import (
    CsvValidationReport,
    QuarantineIssue,
    QuarantineItemResponse,
)
from src.shared.enums import (
    BatchType,
    ComparisonOperator,
    CriticalFieldType,
    PolicyLifecycleStatus,
    RecordAction,
    UserRole,
)

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

MANIFEST_CSV_COLUMNS: tuple[str, ...] = (
    "record_type",
    "record_id",
    "document_id",
    "version_id",
    "status",
    "source_ref",
    "source_uri",
    "source_uri_exists",
    "dat08_has_essential_attachments",
    "unicode_char_len",
    "sha256_checksum",
    "reverified_by",
    "reverified_at_vn",
)

_PASSAGE_REQUIRED = (
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
    "recorded_at",
    "effective_from",
    "scope",
    "audience",
    "status",
    "has_essential_attachments",
    "record_action",
)
_CRITICAL_FIELD_REQUIRED = (
    "field_id",
    "policy_id",
    "policy_version_id",
    "document_version_id",
    "field_name",
    "field_type",
    "operator",
    "value",
    "approval_role",
    "effective_from",
    "scope",
    "audience",
    "source_clause",
    "owner",
    "approver",
    "status",
    "record_action",
)
_NUMERIC_TYPES = {
    CriticalFieldType.NUMBER.value,
    CriticalFieldType.CURRENCY.value,
    CriticalFieldType.DURATION.value,
}
_DATE_FIELDS = ("recorded_at", "published_at", "effective_from", "effective_to")
_REQUIRED_SCOPE_DIMS = ("company", "branch", "role", "product", "transaction_scope")


@dataclass(frozen=True)
class _ValidatedBatch:
    report: CsvValidationReport
    accepted_rows: tuple[tuple[int, dict[str, str | None]], ...] = ()
    quarantined_rows: tuple[tuple[int, dict[str, str | None], QuarantineIssue], ...] = ()


class IdempotencyKeyConflict(Exception):
    """Raised when an import idempotency key is reused for different content."""


class IngestionService:
    """Validates, isolates, and stages Base Scope 2-CSV imports."""

    def validate_csv_bytes(
        self,
        raw_bytes: bytes,
        *,
        source_type: str,
        batch_type: BatchType,
        expected_rows: int | None = None,
        manifest_bytes: bytes | None = None,
    ) -> CsvValidationReport:
        """Dry-run validate one UTF-8 CSV, optionally checking its SHA-256 manifest."""
        return self._validate_batch(
            raw_bytes,
            source_type=source_type,
            batch_type=batch_type,
            expected_rows=expected_rows,
            manifest_bytes=manifest_bytes,
        ).report

    async def import_csv_bytes(
        self,
        db: AsyncSession,
        raw_bytes: bytes,
        *,
        source_type: str,
        batch_type: BatchType,
        expected_rows: int | None,
        manifest_bytes: bytes,
        idempotency_key: str,
        submitted_by: str,
    ) -> CsvValidationReport:
        """Persist accepted rows, manifest counts, and quarantined raw rows as one batch."""
        validated = self._validate_batch(
            raw_bytes,
            source_type=source_type,
            batch_type=batch_type,
            expected_rows=expected_rows,
            manifest_bytes=manifest_bytes,
        )
        content_sha256 = hashlib.sha256(raw_bytes + b"\0" + manifest_bytes).hexdigest()
        existing = (
            await db.execute(
                select(ImportBatch).where(ImportBatch.idempotency_key == idempotency_key)
            )
        ).scalar_one_or_none()
        if existing is not None:
            manifest = await db.get(ImportManifest, existing.id)
            existing_digest = (
                manifest.summary_json.get("content_sha256") if manifest is not None else None
            )
            if existing_digest != content_sha256:
                raise IdempotencyKeyConflict(
                    "This idempotency_key already belongs to a different CSV/manifest pair."
                )
            return validated.report.model_copy(
                update={
                    "batch_id": existing.id,
                    "imported_rows": manifest.accepted_rows if manifest else 0,
                }
            )

        batch_id = uuid4().hex
        report = validated.report.model_copy(
            update={"batch_id": batch_id, "imported_rows": len(validated.accepted_rows)}
        )
        batch = ImportBatch(
            id=batch_id,
            source_type=source_type,
            batch_type=batch_type.value,
            batch_timestamp=datetime.now(ZoneInfo(settings.APP_TIMEZONE)),
            idempotency_key=idempotency_key,
            submitted_by=submitted_by,
            status="completed" if report.rejected_rows == 0 else "rejected",
        )
        summary = {
            "content_sha256": content_sha256,
            "quarantine_issue_count": report.quarantined_rows,
            "reason_codes": sorted({issue.reason_code for issue in report.quarantine_issues}),
        }
        manifest = ImportManifest(
            batch_id=batch_id,
            expected_rows=report.expected_rows,
            received_rows=report.received_rows,
            accepted_rows=report.accepted_rows,
            rejected_rows=report.rejected_rows,
            quarantined_rows=report.quarantined_rows,
            summary_json=summary,
        )
        db.add(batch)
        db.add(manifest)
        db.add_all(
            [
                ImportRecord(
                    batch_id=batch_id,
                    source_type=source_type,
                    record_id=self._record_id(row, source_type),
                    row_number=row_number,
                    raw_payload=self._json_payload(row),
                )
                for row_number, row in validated.accepted_rows
            ]
        )
        db.add_all(
            [
                QuarantineRow(
                    batch_id=batch_id,
                    row_number=row_number,
                    record_id=issue.record_id,
                    reason_code=issue.reason_code,
                    reason_detail=issue.reason_detail,
                    raw_payload=self._json_payload(row),
                )
                for row_number, row, issue in validated.quarantined_rows
            ]
        )
        await db.commit()
        return report

    def _validate_batch(
        self,
        raw_bytes: bytes,
        *,
        source_type: str,
        batch_type: BatchType,
        expected_rows: int | None,
        manifest_bytes: bytes | None,
    ) -> _ValidatedBatch:
        if source_type not in {"passages", "critical_fields"}:
            raise ValueError(f"Unsupported source_type: {source_type}")
        expected_columns = (
            PASSAGES_CSV_COLUMNS if source_type == "passages" else CRITICAL_FIELDS_CSV_COLUMNS
        )
        try:
            text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            return self._batch_failure(
                batch_type,
                source_type,
                expected_rows if expected_rows is not None else 0,
                "INVALID_UTF8_ENCODING",
                "The uploaded CSV is not valid UTF-8 or UTF-8-SIG.",
            )

        try:
            reader = csv.DictReader(io.StringIO(text), strict=True)
            actual_columns = tuple(reader.fieldnames or ())
            rows = list(reader)
        except csv.Error as exc:
            return self._batch_failure(
                batch_type,
                source_type,
                expected_rows if expected_rows is not None else 0,
                "MALFORMED_CSV",
                str(exc),
            )
        if actual_columns != expected_columns:
            return self._batch_failure(
                batch_type,
                source_type,
                expected_rows if expected_rows is not None else 0,
                "SCHEMA_HEADER_MISMATCH",
                f"Header mismatch for {source_type}: expected {len(expected_columns)} columns, "
                f"got {len(actual_columns)}.",
            )

        received = len(rows)
        expected = received if expected_rows is None else expected_rows
        if received > settings.IMPORT_MAX_ROWS_PER_BATCH:
            issue = QuarantineIssue(
                row_number=0,
                reason_code="BATCH_LIMIT_EXCEEDED",
                reason_detail=(
                    f"Received {received} rows exceeding limit "
                    f"{settings.IMPORT_MAX_ROWS_PER_BATCH}."
                ),
            )
            return _ValidatedBatch(
                CsvValidationReport(
                    batch_type=batch_type,
                    source_type=source_type,
                    expected_rows=expected,
                    received_rows=received,
                    accepted_rows=0,
                    rejected_rows=received,
                    quarantined_rows=0,
                    quarantine_issues=[issue],
                )
            )

        checksums: dict[str, str] | None = None
        if manifest_bytes is not None:
            checksums, manifest_error = self._parse_checksums(manifest_bytes, source_type)
            if manifest_error is not None:
                return _ValidatedBatch(
                    CsvValidationReport(
                        batch_type=batch_type,
                        source_type=source_type,
                        expected_rows=expected,
                        received_rows=received,
                        accepted_rows=0,
                        rejected_rows=received or 1,
                        quarantined_rows=0,
                        quarantine_issues=[manifest_error],
                    )
                )

        accepted_rows: list[tuple[int, dict[str, str | None]]] = []
        quarantined_rows: list[tuple[int, dict[str, str | None], QuarantineIssue]] = []
        seen_ids: set[str] = set()
        for row_number, raw_row in enumerate(rows, start=2):
            row = self._normalize_row(raw_row)
            record_id = self._record_id(row, source_type)
            reason: tuple[str, str, str | None] | None = None
            if None in raw_row:
                reason = (
                    "CSV_ROW_COLUMN_COUNT_MISMATCH",
                    "CSV row has more values than the declared header.",
                    record_id,
                )
            elif record_id and record_id in seen_ids:
                reason = (
                    "DUPLICATE_RECORD_ID",
                    f"Duplicate {self._id_column(source_type)} {record_id} in this batch.",
                    record_id,
                )
            else:
                if record_id:
                    seen_ids.add(record_id)
                reason = self._validate_row(row, source_type=source_type)
                if reason is None and checksums is not None:
                    expected_hash = checksums.get(record_id or "")
                    if expected_hash is None:
                        reason = (
                            "CHECKSUM_MISSING",
                            "No matching SHA-256 checksum was provided in the manifest.",
                            record_id,
                        )
                    elif (
                        self._row_checksum(row, source_type).casefold() != expected_hash.casefold()
                    ):
                        reason = (
                            "CHECKSUM_MISMATCH",
                            "CSV row content does not match the manifest SHA-256 checksum.",
                            record_id,
                        )
            if reason is None:
                accepted_rows.append((row_number, row))
            else:
                code, detail, issue_record_id = reason
                quarantined_rows.append(
                    (
                        row_number,
                        row,
                        QuarantineIssue(
                            row_number=row_number,
                            record_id=issue_record_id,
                            reason_code=code,
                            reason_detail=detail,
                        ),
                    )
                )

        quarantined_issues = [entry[2] for entry in quarantined_rows]
        if expected != received:
            mismatch = QuarantineIssue(
                row_number=0,
                reason_code="EXPECTED_ROW_COUNT_MISMATCH",
                reason_detail=f"Expected {expected} rows, received {received}.",
            )
            return _ValidatedBatch(
                CsvValidationReport(
                    batch_type=batch_type,
                    source_type=source_type,
                    expected_rows=expected,
                    received_rows=received,
                    accepted_rows=0,
                    rejected_rows=received or 1,
                    quarantined_rows=0,
                    quarantine_issues=[mismatch],
                )
            )

        return _ValidatedBatch(
            CsvValidationReport(
                batch_type=batch_type,
                source_type=source_type,
                expected_rows=expected,
                received_rows=received,
                accepted_rows=len(accepted_rows),
                rejected_rows=0,
                quarantined_rows=len(quarantined_rows),
                quarantine_issues=quarantined_issues,
            ),
            tuple(accepted_rows),
            tuple(quarantined_rows),
        )

    def _batch_failure(
        self,
        batch_type: BatchType,
        source_type: str,
        expected_rows: int,
        reason_code: str,
        detail: str,
    ) -> _ValidatedBatch:
        return _ValidatedBatch(
            CsvValidationReport(
                batch_type=batch_type,
                source_type=source_type,
                expected_rows=expected_rows,
                received_rows=0,
                accepted_rows=0,
                rejected_rows=1,
                quarantined_rows=0,
                quarantine_issues=[
                    QuarantineIssue(
                        row_number=1,
                        reason_code=reason_code,
                        reason_detail=detail,
                    )
                ],
            )
        )

    def _parse_checksums(
        self, raw_bytes: bytes, source_type: str
    ) -> tuple[dict[str, str] | None, QuarantineIssue | None]:
        try:
            text = raw_bytes.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text), strict=True)
            if tuple(reader.fieldnames or ()) != MANIFEST_CSV_COLUMNS:
                return None, QuarantineIssue(
                    row_number=1,
                    reason_code="CHECKSUM_MANIFEST_SCHEMA_MISMATCH",
                    reason_detail="Checksum manifest header does not match the G1 manifest schema.",
                )
            record_type = "passage" if source_type == "passages" else "critical_field"
            checksums: dict[str, str] = {}
            for entry in reader:
                record_id = (entry.get("record_id") or "").strip()
                checksum = (entry.get("sha256_checksum") or "").strip()
                if entry.get("record_type") != record_type or not record_id or not checksum:
                    continue
                if record_id in checksums:
                    return None, QuarantineIssue(
                        row_number=0,
                        record_id=record_id,
                        reason_code="DUPLICATE_CHECKSUM_ENTRY",
                        reason_detail=(
                            f"Manifest contains duplicate checksum entry for {record_id}."
                        ),
                    )
                checksums[record_id] = checksum
            return checksums, None
        except (UnicodeDecodeError, csv.Error) as exc:
            return None, QuarantineIssue(
                row_number=1,
                reason_code="INVALID_CHECKSUM_MANIFEST",
                reason_detail=f"Checksum manifest could not be parsed: {exc}",
            )

    def _validate_row(
        self, row: dict[str, str | None], *, source_type: str
    ) -> tuple[str, str, str | None] | None:
        id_column = self._id_column(source_type)
        record_id = (row.get(id_column) or "").strip() or None
        required_fields = (
            _PASSAGE_REQUIRED if source_type == "passages" else _CRITICAL_FIELD_REQUIRED
        )
        missing = [field for field in required_fields if not (row.get(field) or "").strip()]
        if missing:
            return (
                "MISSING_REQUIRED_FIELD",
                f"Required field(s) are empty: {', '.join(missing)}.",
                record_id,
            )

        action = (row.get("record_action") or "").strip().lower()
        if action not in {item.value for item in RecordAction}:
            return (
                "INVALID_RECORD_ACTION",
                "record_action must be upsert or tombstone.",
                record_id,
            )

        status = (row.get("status") or "").strip()
        if status not in {
            item.value
            for item in PolicyLifecycleStatus
            if item
            not in {PolicyLifecycleStatus.FEEDBACK_CANDIDATE, PolicyLifecycleStatus.QUARANTINED}
        }:
            return ("INVALID_STATUS", f"Unsupported lifecycle status: {status}.", record_id)

        if source_type == "passages":
            content = row.get("content") or ""
            if len(content) > settings.PASSAGE_MAX_CHARS:
                return (
                    "PASSAGE_TOO_LONG",
                    f"Content length {len(content)} exceeds "
                    f"{settings.PASSAGE_MAX_CHARS} Unicode chars.",
                    record_id,
                )
            if (row.get("language") or "").strip() not in {"vi", "en"}:
                return ("INVALID_LANGUAGE", "language must be vi or en.", record_id)
            page_number = row.get("page_number") or ""
            if not page_number.isdecimal() or int(page_number) < 1:
                return ("INVALID_PAGE_NUMBER", "page_number must be an integer >= 1.", record_id)
            attachments = (row.get("has_essential_attachments") or "").strip().lower()
            if attachments not in {"true", "false"}:
                return (
                    "INVALID_BOOLEAN",
                    "has_essential_attachments must be true or false.",
                    record_id,
                )
            if attachments != "true":
                return (
                    "MISSING_ESSENTIAL_ATTACHMENTS",
                    "DAT 08 Quarantine: missing essential table, diagram, or footnote.",
                    record_id,
                )
        else:
            field_type = (row.get("field_type") or "").strip()
            if field_type not in {item.value for item in CriticalFieldType}:
                return ("INVALID_FIELD_TYPE", f"Unsupported field_type: {field_type}.", record_id)
            operator = (row.get("operator") or "").strip()
            if operator not in {item.value for item in ComparisonOperator}:
                return ("INVALID_OPERATOR", f"Unsupported operator: {operator}.", record_id)
            if (
                field_type == CriticalFieldType.CURRENCY.value
                and not (row.get("currency") or "").strip()
            ):
                return (
                    "MISSING_CURRENCY_UNIT",
                    "Currency fields require an explicit currency code.",
                    record_id,
                )
            if field_type in _NUMERIC_TYPES:
                if not (row.get("unit") or "").strip():
                    return (
                        "MISSING_REQUIRED_UNIT",
                        "Numeric fields require an explicit unit.",
                        record_id,
                    )
                value = (row.get("value") or "").strip()
                try:
                    if operator == ComparisonOperator.BETWEEN.value:
                        bounds = [part.strip() for part in value.split(";")]
                        if len(bounds) != 2 or any(not part for part in bounds):
                            raise ValueError("between requires two semicolon-separated numbers")
                        for bound in bounds:
                            parsed_bound = Decimal(bound)
                            if not parsed_bound.is_finite():
                                raise ValueError("numeric bounds must be finite")
                    elif operator not in {
                        ComparisonOperator.IN.value,
                        ComparisonOperator.REQUIRED.value,
                    }:
                        parsed_value = Decimal(value)
                        if not parsed_value.is_finite():
                            raise ValueError("numeric values must be finite")
                except (InvalidOperation, ValueError):
                    return (
                        "INVALID_NUMERIC_VALUE",
                        f"Invalid numeric value for {field_type}/{operator}: {value}.",
                        record_id,
                    )

        for field in _DATE_FIELDS:
            value = (row.get(field) or "").strip()
            if value and not self._is_timezone_datetime(value):
                return (
                    "INVALID_TIMESTAMP",
                    f"{field} must be an ISO-8601 datetime with timezone.",
                    record_id,
                )
        if not self._has_required_scope_dimensions(row.get("scope") or ""):
            return (
                "INVALID_SCOPE",
                "scope must include company, branch, role, customer_group/customer_category, "
                "product, and transaction_scope.",
                record_id,
            )
        allowed_roles = {role.value for role in UserRole}
        audience = (row.get("audience") or "").split(",")
        if any(role.strip() not in allowed_roles for role in audience):
            return (
                "INVALID_AUDIENCE_ROLE",
                "audience contains an unsupported user role.",
                record_id,
            )
        return None

    @staticmethod
    def _has_required_scope_dimensions(scope: str) -> bool:
        dimensions: dict[str, str] = {}
        for pair in scope.split(";"):
            key, separator, value = pair.partition(":")
            if separator and value.strip():
                dimensions[key.strip()] = value.strip()
        return all(dimension in dimensions for dimension in _REQUIRED_SCOPE_DIMS) and (
            "customer_group" in dimensions or "customer_category" in dimensions
        )

    @staticmethod
    def _is_timezone_datetime(value: str) -> bool:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None and parsed.utcoffset() is not None

    @staticmethod
    def _row_checksum(row: dict[str, str | None], source_type: str) -> str:
        parts: tuple[str | None, ...]
        if source_type == "passages":
            parts = (
                row.get("passage_id"),
                row.get("document_id"),
                row.get("document_version_id"),
                row.get("clause_ref"),
                row.get("content"),
                row.get("scope"),
                row.get("status"),
            )
        else:
            parts = (
                row.get("field_id"),
                row.get("policy_id"),
                row.get("policy_version_id"),
                row.get("field_type"),
                row.get("operator"),
                row.get("value"),
                row.get("unit"),
                row.get("currency"),
                row.get("approval_role"),
                row.get("status"),
            )
        canonical = "|".join(part or "" for part in parts)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_row(row: dict[str | None, str | None]) -> dict[str, str | None]:
        normalized = {key: value for key, value in row.items() if key is not None}
        if None in row:
            normalized["_extra_columns"] = "|".join(value or "" for value in row[None] or [])
        return normalized

    @staticmethod
    def _id_column(source_type: str) -> str:
        return "passage_id" if source_type == "passages" else "field_id"

    def _record_id(self, row: dict[str, str | None], source_type: str) -> str:
        return (row.get(self._id_column(source_type)) or "").strip()

    @staticmethod
    def _json_payload(row: dict[str, str | None]) -> dict[str, object]:
        return {key: value for key, value in row.items()}

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
                id=row.id,
                batch_id=row.batch_id,
                row_number=row.row_number,
                record_id=row.record_id,
                reason_code=row.reason_code,
                reason_detail=row.reason_detail,
                resolved=row.resolved,
            )
            for row in rows
        ]
