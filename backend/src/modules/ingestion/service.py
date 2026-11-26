"""UTF-8 CSV validators and DAT 08 quarantine enforcement for Base Scope imports."""

import csv
import hashlib
import io
import re
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import cast
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
from src.modules.knowledge.models import Document, DocumentVersion, Passage
from src.modules.policy.models import CriticalField, Policy, PolicyVersion
from src.shared.enums import (
    BatchType,
    ComparisonOperator,
    CriticalFieldType,
    PolicyFamily,
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


class StaleBatchRejected(Exception):
    """Raised when an incoming batch is older than the authoritative state."""


class CorpusCeilingExceeded(Exception):
    """Raised when an import would exceed the Base Scope corpus ceiling."""


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
        batch_timestamp: datetime | None = None,
        enforce_corpus_ceiling: bool = False,
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

        effective_batch_timestamp = self._normalize_timestamp(batch_timestamp)
        latest_batch = (
            await db.execute(
                select(ImportBatch)
                .where(
                    ImportBatch.source_type == source_type,
                    ImportBatch.status != "rejected",
                )
                .order_by(ImportBatch.batch_timestamp.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if latest_batch is not None:
            latest_utc = self._as_utc(latest_batch.batch_timestamp)
            if effective_batch_timestamp < latest_utc:
                raise StaleBatchRejected(
                    "Incoming batch_timestamp is older than the latest committed batch."
                )
        if enforce_corpus_ceiling and validated.accepted_rows:
            await self._check_corpus_ceiling(
                db,
                source_type=source_type,
                batch_type=batch_type,
                validated=validated,
            )
        batch_id = uuid4().hex
        applied_rows = await self._apply_authoritative_rows(
            db,
            source_type=source_type,
            batch_type=batch_type,
            batch_id=batch_id,
            batch_timestamp=effective_batch_timestamp,
            validated=validated,
        )
        report = validated.report.model_copy(
            update={"batch_id": batch_id, "imported_rows": applied_rows}
        )
        batch = ImportBatch(
            id=batch_id,
            source_type=source_type,
            batch_type=batch_type.value,
            batch_timestamp=effective_batch_timestamp,
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

    async def _check_corpus_ceiling(
        self,
        db: AsyncSession,
        *,
        source_type: str,
        batch_type: BatchType,
        validated: _ValidatedBatch,
    ) -> None:
        """Reject imports that would exceed Base Scope document/passage/field ceilings."""
        quarantined_ids = {
            issue.record_id for _, _, issue in validated.quarantined_rows if issue.record_id
        }
        present_ids = {
            self._record_id(row, source_type) for _, row in validated.accepted_rows
        } | quarantined_ids

        if source_type == "passages":
            rows = (
                await db.execute(
                    select(Passage.id, Passage.document_id).where(Passage.is_tombstoned.is_(False))
                )
            ).all()
            active_passages: dict[str, str] = {pid: doc_id for pid, doc_id in rows}
            if batch_type == BatchType.FULL_SNAPSHOT:
                active_passages = {
                    pid: doc_id for pid, doc_id in active_passages.items() if pid in present_ids
                }
            for _, row in validated.accepted_rows:
                pid = self._record_id(row, "passages")
                action = (row.get("record_action") or "").strip().lower()
                if action in {RecordAction.TOMBSTONE.value, RecordAction.DELETE.value}:
                    active_passages.pop(pid, None)
                else:
                    active_passages[pid] = row.get("document_id") or ""
            if len(active_passages) > settings.CORPUS_MAX_PASSAGES:
                raise CorpusCeilingExceeded(
                    f"Post-import active passages ({len(active_passages)}) exceeds Base Scope "
                    f"ceiling ({settings.CORPUS_MAX_PASSAGES})."
                )
            active_docs = {doc_id for doc_id in active_passages.values() if doc_id}
            if len(active_docs) > settings.CORPUS_MAX_DOCUMENTS:
                raise CorpusCeilingExceeded(
                    f"Post-import active documents ({len(active_docs)}) exceeds Base Scope "
                    f"ceiling ({settings.CORPUS_MAX_DOCUMENTS})."
                )
        else:
            existing_ids = (
                await db.execute(
                    select(CriticalField.id).where(CriticalField.is_tombstoned.is_(False))
                )
            ).scalars().all()
            active_fields: set[str] = set(existing_ids)
            if batch_type == BatchType.FULL_SNAPSHOT:
                active_fields &= present_ids
            for _, row in validated.accepted_rows:
                fid = self._record_id(row, "critical_fields")
                action = (row.get("record_action") or "").strip().lower()
                if action in {RecordAction.TOMBSTONE.value, RecordAction.DELETE.value}:
                    active_fields.discard(fid)
                else:
                    active_fields.add(fid)
            if len(active_fields) > settings.CORPUS_MAX_CRITICAL_FIELDS:
                raise CorpusCeilingExceeded(
                    f"Post-import active critical fields ({len(active_fields)}) exceeds Base Scope "
                    f"ceiling ({settings.CORPUS_MAX_CRITICAL_FIELDS})."
                )

    async def _apply_authoritative_rows(
        self,
        db: AsyncSession,
        *,
        source_type: str,
        batch_type: BatchType,
        batch_id: str,
        batch_timestamp: datetime,
        validated: _ValidatedBatch,
    ) -> int:
        """Apply accepted rows, preserve quarantined LKG, and reconcile full-snapshot omissions."""
        quarantined_ids = {
            issue.record_id for _, _, issue in validated.quarantined_rows if issue.record_id
        }
        applied = 0
        # Batch-prefetch existing authoritative rows and parent IDs to avoid N+1 round-trips.
        record_ids = {self._record_id(row, source_type) for _, row in validated.accepted_rows}
        existing_by_id: dict[str, Passage | CriticalField] = {}
        if record_ids:
            if source_type == "passages":
                prefetched_passages = (
                    await db.execute(select(Passage).where(Passage.id.in_(record_ids)))
                ).scalars().all()
                existing_by_id = {obj.id: obj for obj in prefetched_passages}
            else:
                prefetched_fields = (
                    await db.execute(select(CriticalField).where(CriticalField.id.in_(record_ids)))
                ).scalars().all()
                existing_by_id = {obj.id: obj for obj in prefetched_fields}

        seen_documents: set[str] = set()
        seen_doc_versions: set[str] = set()
        seen_policies: set[str] = set()
        seen_policy_versions: set[str] = set()

        if validated.accepted_rows:
            if source_type == "passages":
                doc_ids = {row.get("document_id") or "" for _, row in validated.accepted_rows}
                doc_ver_pks = {
                    self._compose_document_version_id(
                        row.get("document_id") or "", row.get("document_version_id") or ""
                    )
                    for _, row in validated.accepted_rows
                }
            else:
                doc_ids = {
                    (row.get("policy_id") or row.get("document_version_id") or "")
                    for _, row in validated.accepted_rows
                }
                doc_ver_pks = {
                    self._compose_document_version_id(
                        (row.get("policy_id") or row.get("document_version_id") or ""),
                        row.get("document_version_id") or "",
                    )
                    for _, row in validated.accepted_rows
                }
                policy_ids = {row.get("policy_id") or "" for _, row in validated.accepted_rows}
                policy_ver_ids = {
                    row.get("policy_version_id") or "" for _, row in validated.accepted_rows
                }
                if policy_ids:
                    seen_policies = set(
                        (await db.execute(select(Policy.id).where(Policy.id.in_(policy_ids))))
                        .scalars()
                        .all()
                    )
                if policy_ver_ids:
                    seen_policy_versions = set(
                        (
                            await db.execute(
                                select(PolicyVersion.id).where(
                                    PolicyVersion.id.in_(policy_ver_ids)
                                )
                            )
                        )
                        .scalars()
                        .all()
                    )

            if doc_ids:
                seen_documents = set(
                    (await db.execute(select(Document.id).where(Document.id.in_(doc_ids))))
                    .scalars()
                    .all()
                )
            if doc_ver_pks:
                seen_doc_versions = set(
                    (
                        await db.execute(
                            select(DocumentVersion.id).where(DocumentVersion.id.in_(doc_ver_pks))
                        )
                    )
                    .scalars()
                    .all()
                )

        no_autoflush_ctx = getattr(db, "no_autoflush", nullcontext())
        with no_autoflush_ctx:
            for _, row in validated.accepted_rows:
                record_id = self._record_id(row, source_type)
                action = (row.get("record_action") or "").strip().lower()
                current = existing_by_id.get(record_id)

                incoming_version = (
                    self._compose_document_version_id(
                        row.get("document_id") or "", row.get("document_version_id") or ""
                    )
                    if source_type == "passages"
                    else row.get("policy_version_id")
                )
                if current is not None:
                    current_timestamp = current.last_batch_timestamp
                    if current_timestamp is not None:
                        current_utc = self._as_utc(current_timestamp)
                        if batch_timestamp < current_utc:
                            continue
                        if batch_timestamp == current_utc:
                            current_version = (
                                current.document_version_id
                                if source_type == "passages"
                                else (
                                    current.policy_version_id
                                    if isinstance(current, CriticalField)
                                    else None
                                )
                            )
                            if not self._higher_version(incoming_version, current_version):
                                continue

                if action in {RecordAction.TOMBSTONE.value, RecordAction.DELETE.value}:
                    if current is not None:
                        current.is_tombstoned = True
                        current.status = PolicyLifecycleStatus.WITHDRAWN.value
                        current.tombstoned_at = batch_timestamp
                        current.tombstone_batch_id = batch_id
                        current.last_batch_id = batch_id
                        current.last_batch_timestamp = batch_timestamp
                        applied += 1
                    continue

                if source_type == "passages":
                    existing_by_id[record_id] = self._upsert_passage(
                        db,
                        row,
                        record_id,
                        batch_id,
                        batch_timestamp,
                        current=cast(Passage | None, current),
                        seen_documents=seen_documents,
                        seen_doc_versions=seen_doc_versions,
                    )
                else:
                    existing_by_id[record_id] = self._upsert_critical_field(
                        db,
                        row,
                        record_id,
                        batch_id,
                        batch_timestamp,
                        current=cast(CriticalField | None, current),
                        seen_documents=seen_documents,
                        seen_doc_versions=seen_doc_versions,
                        seen_policies=seen_policies,
                        seen_policy_versions=seen_policy_versions,
                    )
                applied += 1

        if batch_type == BatchType.FULL_SNAPSHOT and validated.accepted_rows:
            present_ids = {
                self._record_id(row, source_type) for _, row in validated.accepted_rows
            } | quarantined_ids
            existing_rows: list[Passage | CriticalField] = (
                list((await db.execute(select(Passage))).scalars().all())
                if source_type == "passages"
                else list((await db.execute(select(CriticalField))).scalars().all())
            )
            for existing_row in existing_rows:
                if existing_row.id in present_ids or existing_row.is_tombstoned:
                    continue
                existing_row.is_tombstoned = True
                existing_row.status = PolicyLifecycleStatus.WITHDRAWN.value
                existing_row.tombstoned_at = batch_timestamp
                existing_row.tombstone_batch_id = batch_id
                existing_row.last_batch_id = batch_id
                existing_row.last_batch_timestamp = batch_timestamp
                applied += 1

        return applied

    @staticmethod
    def _compose_document_version_id(prefix: str, document_version_id: str) -> str:
        if ":" in document_version_id or not prefix:
            return document_version_id
        return f"{prefix}:{document_version_id}"

    @staticmethod
    def _infer_policy_family(
        *, identifier: str = "", title: str = "", scope: str = ""
    ) -> str:
        hints = f"{identifier} {title} {scope}".lower()
        if any(
            token in hints
            for token in (
                "customer_info",
                "privacy",
                "pii",
                "bảo mật",
                "thông tin khách hàng",
                "dữ liệu cá nhân",
                "family2",
                "doc-002",
                "pol-002",
            )
        ):
            return PolicyFamily.CUSTOMER_INFO_HANDLING.value
        if any(
            token in hints
            for token in (
                "service_warranty",
                "warranty",
                "bảo hành",
                "dịch vụ",
                "kỹ thuật",
                "sự cố",
                "family3",
                "doc-003",
                "pol-003",
            )
        ):
            return PolicyFamily.SERVICE_WARRANTY_ROUTING.value
        return PolicyFamily.COMMERCIAL_QUOTING_APPROVAL.value

    @staticmethod
    def _normalize_timestamp(value: datetime | None) -> datetime:
        tz = ZoneInfo(settings.APP_TIMEZONE)
        ts = value or datetime.now(tz)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=tz)
        return ts.astimezone(UTC)

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _higher_version(incoming: str | None, current: str | None) -> bool:
        if not incoming or not current:
            return False
        incoming_ver = incoming.rsplit(":", 1)[-1]
        current_ver = current.rsplit(":", 1)[-1]
        incoming_nums = tuple(int(n) for n in re.findall(r"\d+", incoming_ver))
        current_nums = tuple(int(n) for n in re.findall(r"\d+", current_ver))
        if incoming_nums and current_nums:
            return incoming_nums > current_nums
        return incoming_ver > current_ver

    def _upsert_passage(
        self,
        db: AsyncSession,
        row: dict[str, str | None],
        record_id: str,
        batch_id: str,
        batch_timestamp: datetime,
        *,
        current: Passage | None,
        seen_documents: set[str],
        seen_doc_versions: set[str],
    ) -> Passage:
        recorded_at = self._parse_datetime(row.get("recorded_at")) or batch_timestamp
        effective_from = self._parse_datetime(row.get("effective_from")) or batch_timestamp
        effective_to = self._parse_datetime(row.get("effective_to"))
        published_at = self._parse_datetime(row.get("published_at"))
        document_id = row.get("document_id") or ""
        raw_doc_ver_id = row.get("document_version_id") or ""
        doc_ver_pk = self._compose_document_version_id(document_id, raw_doc_ver_id)
        if document_id not in seen_documents:
            db.add(
                Document(
                    id=document_id,
                    title=(row.get("title") or "")[:500],
                    policy_family=self._infer_policy_family(
                        identifier=document_id,
                        title=row.get("title") or "",
                        scope=row.get("scope") or "",
                    ),
                    authority_tier="policy",
                    owner=row.get("owner") or "",
                    source_ref=row.get("source_ref") or "",
                )
            )
            seen_documents.add(document_id)
        if doc_ver_pk not in seen_doc_versions:
            db.add(
                DocumentVersion(
                    id=doc_ver_pk,
                    document_id=document_id,
                    approver=row.get("approver"),
                    recorded_at=recorded_at,
                    published_at=published_at,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    status=row.get("status") or "draft",
                    supersedes_version_id=row.get("supersedes") or None,
                )
            )
            seen_doc_versions.add(doc_ver_pk)

        payload = dict(
            document_id=document_id,
            document_version_id=doc_ver_pk,
            title=row.get("title") or "",
            content=row.get("content") or "",
            source_ref=row.get("source_ref") or "",
            page_number=int(row.get("page_number") or "1"),
            clause_ref=row.get("clause_ref") or "",
            language=row.get("language") or "vi",
            scope=row.get("scope") or "",
            audience=row.get("audience") or "",
            status=row.get("status") or "draft",
            has_essential_attachments=(row.get("has_essential_attachments") or "").lower()
            == "true",
            is_tombstoned=False,
            tombstoned_at=None,
            tombstone_batch_id=None,
            last_batch_id=batch_id,
            last_batch_timestamp=batch_timestamp,
            source_recorded_at=recorded_at,
        )
        if current is None:
            passage = Passage(id=record_id, **payload)
            db.add(passage)
            return passage
        for key, value in payload.items():
            setattr(current, key, value)
        return current

    def _upsert_critical_field(
        self,
        db: AsyncSession,
        row: dict[str, str | None],
        record_id: str,
        batch_id: str,
        batch_timestamp: datetime,
        *,
        current: CriticalField | None,
        seen_documents: set[str],
        seen_doc_versions: set[str],
        seen_policies: set[str],
        seen_policy_versions: set[str],
    ) -> CriticalField:
        policy_id = row.get("policy_id") or ""
        policy_version_id = row.get("policy_version_id") or ""
        raw_doc_ver_id = row.get("document_version_id") or ""
        doc_id = policy_id or raw_doc_ver_id
        doc_ver_pk = self._compose_document_version_id(doc_id, raw_doc_ver_id)
        effective_from = self._parse_datetime(row.get("effective_from")) or batch_timestamp
        effective_to = self._parse_datetime(row.get("effective_to"))
        recorded_at = self._parse_datetime(row.get("recorded_at")) or effective_from
        scope = row.get("scope") or ""
        audience = row.get("audience") or ""
        status = row.get("status") or "draft"
        owner = row.get("owner") or ""
        approver = row.get("approver") or None
        policy_family = self._infer_policy_family(
            identifier=policy_id,
            title=row.get("field_name") or "",
            scope=scope,
        )

        if doc_id not in seen_documents:
            db.add(
                Document(
                    id=doc_id,
                    title=(row.get("field_name") or doc_id)[:500],
                    policy_family=policy_family,
                    authority_tier="policy",
                    owner=owner,
                    source_ref=row.get("source_clause") or "",
                )
            )
            seen_documents.add(doc_id)

        if doc_ver_pk not in seen_doc_versions:
            db.add(
                DocumentVersion(
                    id=doc_ver_pk,
                    document_id=doc_id,
                    approver=approver,
                    recorded_at=recorded_at,
                    published_at=None,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    status=status,
                    supersedes_version_id=None,
                )
            )
            seen_doc_versions.add(doc_ver_pk)

        if policy_id not in seen_policies:
            db.add(
                Policy(
                    id=policy_id,
                    title=(row.get("field_name") or policy_id)[:500],
                    policy_family=policy_family,
                )
            )
            seen_policies.add(policy_id)

        if policy_version_id not in seen_policy_versions:
            db.add(
                PolicyVersion(
                    id=policy_version_id,
                    policy_id=policy_id,
                    document_version_id=doc_ver_pk,
                    scope=scope,
                    audience=audience,
                    status=status,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    recorded_at=recorded_at,
                    owner=owner,
                    approver=approver,
                )
            )
            seen_policy_versions.add(policy_version_id)

        payload = dict(
            policy_id=policy_id,
            policy_version_id=policy_version_id,
            document_version_id=doc_ver_pk,
            field_name=row.get("field_name") or "",
            field_type=row.get("field_type") or "",
            operator=row.get("operator") or "",
            value=row.get("value") or "",
            unit=row.get("unit") or None,
            currency=row.get("currency") or None,
            approval_role=row.get("approval_role") or "",
            time_limit=row.get("time_limit") or None,
            exception_condition=row.get("exception_condition") or None,
            required_documents=row.get("required_documents") or None,
            source_clause=row.get("source_clause") or "",
            scope=scope,
            audience=audience,
            status=status,
            is_tombstoned=False,
            tombstoned_at=None,
            tombstone_batch_id=None,
            last_batch_id=batch_id,
            last_batch_timestamp=batch_timestamp,
            source_recorded_at=effective_from,
        )
        if current is None:
            field = CriticalField(id=record_id, **payload)
            db.add(field)
            return field
        for key, value in payload.items():
            setattr(current, key, value)
        return current

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

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
