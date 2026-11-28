"""Focused contracts for CSV validation, manifest checksums, and durable staging."""

import csv
import hashlib
import io
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.db import Base
from src.modules.answer.models import AnswerCitationRecord, AnswerPackageRecord
from src.modules.ingestion.models import (
    ImportBatch,
    ImportManifest,
    ImportRecord,
    QuarantineRow,
)
from src.modules.ingestion.service import (
    MANIFEST_CSV_COLUMNS,
    PASSAGES_CSV_COLUMNS,
    CorpusCeilingExceeded,
    IdempotencyKeyConflict,
    IngestionService,
    StaleBatchRejected,
)
from src.modules.knowledge.models import ChangeImpactReport, Document, DocumentVersion, Passage
from src.modules.policy.models import CriticalField, Policy, PolicyVersion
from src.shared.enums import BatchType, PolicyFamily

REPO_ROOT = Path(__file__).resolve().parents[2]
FAMILY1 = REPO_ROOT / "data" / "g1" / "family1"
SERVICE = IngestionService()
_CHANGE_IMPACT_TABLES = [
    AnswerPackageRecord.__table__,
    AnswerCitationRecord.__table__,
    ChangeImpactReport.__table__,
]


class _AsyncSessionAdapter:
    """Expose the async operations used by the service over an isolated SQLite session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    async def get(self, entity, identity):
        return self.session.get(entity, identity)

    def add(self, entity) -> None:
        self.session.add(entity)

    def add_all(self, entities) -> None:
        self.session.add_all(entities)

    async def commit(self) -> None:
        self.session.commit()


def _read_csv(raw_bytes: bytes) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(raw_bytes.decode("utf-8-sig")))
    return list(reader.fieldnames or []), list(reader)


def _serialize_csv(headers: tuple[str, ...], rows: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _manifest_for(rows: list[dict[str, str]], source_type: str) -> bytes:
    record_type = "passage" if source_type == "passages" else "critical_field"
    checksum_fields = (
        (
            "passage_id",
            "document_id",
            "document_version_id",
            "clause_ref",
            "content",
            "scope",
            "status",
        )
        if source_type == "passages"
        else (
            "field_id",
            "policy_id",
            "policy_version_id",
            "field_type",
            "operator",
            "value",
            "unit",
            "currency",
            "approval_role",
            "status",
        )
    )
    manifest_rows = []
    for row in rows:
        canonical = "|".join(row.get(key, "") for key in checksum_fields)
        manifest_rows.append(
            {
                "record_type": record_type,
                "record_id": row[checksum_fields[0]],
                "sha256_checksum": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                **{
                    column: ""
                    for column in MANIFEST_CSV_COLUMNS
                    if column not in {"record_type", "record_id", "sha256_checksum"}
                },
            }
        )
    return _serialize_csv(MANIFEST_CSV_COLUMNS, manifest_rows)


def test_family1_csvs_reconcile_against_manifest() -> None:
    manifest = (FAMILY1 / "Source_URI_And_Checksum_Manifest_Family1.csv").read_bytes()
    passages = SERVICE.validate_csv_bytes(
        (FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes(),
        source_type="passages",
        batch_type=BatchType.FULL_SNAPSHOT,
        expected_rows=40,
        manifest_bytes=manifest,
    )
    critical_fields = SERVICE.validate_csv_bytes(
        (FAMILY1 / "Critical_Fields_Family1.csv").read_bytes(),
        source_type="critical_fields",
        batch_type=BatchType.FULL_SNAPSHOT,
        expected_rows=16,
        manifest_bytes=manifest,
    )

    assert (
        passages.expected_rows,
        passages.accepted_rows,
        passages.quarantined_rows,
        passages.quarantine_issues[0].reason_code,
        passages.quarantine_issues[0].record_id,
    ) == (40, 39, 1, "MISSING_ESSENTIAL_ATTACHMENTS", "PAS-040")
    assert (
        critical_fields.expected_rows,
        critical_fields.accepted_rows,
        critical_fields.quarantined_rows,
    ) == (16, 16, 0)


def test_validator_quarantines_missing_fields_duplicates_and_bad_checksum() -> None:
    _, rows = _read_csv((FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes())
    rows[0]["title"] = ""
    rows[1]["passage_id"] = rows[0]["passage_id"]
    rows[2]["content"] = "tampered content"
    raw_bytes = _serialize_csv(PASSAGES_CSV_COLUMNS, rows)
    original_manifest = (FAMILY1 / "Source_URI_And_Checksum_Manifest_Family1.csv").read_bytes()

    report = SERVICE.validate_csv_bytes(
        raw_bytes,
        source_type="passages",
        batch_type=BatchType.DELTA,
        manifest_bytes=original_manifest,
    )
    reasons = {issue.reason_code for issue in report.quarantine_issues}
    assert "MISSING_REQUIRED_FIELD" in reasons
    assert "DUPLICATE_RECORD_ID" in reasons
    assert "CHECKSUM_MISMATCH" in reasons
    assert report.expected_rows == report.accepted_rows + report.quarantined_rows


def test_validator_quarantines_invalid_numeric_type() -> None:
    headers, rows = _read_csv((FAMILY1 / "Critical_Fields_Family1.csv").read_bytes())
    rows[0]["value"] = "not-a-number"
    report = SERVICE.validate_csv_bytes(
        _serialize_csv(tuple(headers), rows),
        source_type="critical_fields",
        batch_type=BatchType.DELTA,
    )

    reason_codes = {issue.reason_code for issue in report.quarantine_issues}
    assert "INVALID_NUMERIC_VALUE" in reason_codes
    assert report.expected_rows == report.accepted_rows + report.quarantined_rows


def test_validates_utf8_and_reconciles_invalid_row_fixtures() -> None:
    invalid_encoding = SERVICE.validate_csv_bytes(
        b"\xff",
        source_type="passages",
        batch_type=BatchType.DELTA,
    )
    assert invalid_encoding.quarantine_issues[0].reason_code == "INVALID_UTF8_ENCODING"

    fixture_path = (
        REPO_ROOT / "data" / "g1" / "fixtures" / "Quarantine_CriticalFields_Fixtures_G1.csv"
    )
    fixture_report = SERVICE.validate_csv_bytes(
        fixture_path.read_bytes(),
        source_type="critical_fields",
        batch_type=BatchType.DELTA,
    )
    reason_codes = {issue.reason_code for issue in fixture_report.quarantine_issues}
    assert "MISSING_CURRENCY_UNIT" in reason_codes
    assert "MISSING_REQUIRED_UNIT" in reason_codes
    assert "INVALID_RECORD_ACTION" in reason_codes
    assert fixture_report.accepted_rows + fixture_report.quarantined_rows == 4


def test_passage_fixtures_cover_size_attachment_enum_and_tombstone_rules() -> None:
    fixture_path = REPO_ROOT / "data" / "g1" / "fixtures" / "Quarantine_Passages_Fixtures_G1.csv"
    report = SERVICE.validate_csv_bytes(
        fixture_path.read_bytes(),
        source_type="passages",
        batch_type=BatchType.DELTA,
    )
    reason_codes = {issue.reason_code for issue in report.quarantine_issues}
    assert {
        "PASSAGE_TOO_LONG",
        "MISSING_ESSENTIAL_ATTACHMENTS",
        "INVALID_STATUS",
        "INVALID_RECORD_ACTION",
    }.issubset(reason_codes)
    assert report.expected_rows == report.accepted_rows + report.quarantined_rows == 6
    assert report.accepted_rows == 2


@pytest.mark.asyncio
async def test_import_persists_accepted_rows_manifest_and_quarantine() -> None:
    raw_bytes = (FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes()
    critical_fields_bytes = (FAMILY1 / "Critical_Fields_Family1.csv").read_bytes()
    manifest_bytes = (FAMILY1 / "Source_URI_And_Checksum_Manifest_Family1.csv").read_bytes()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Policy.__table__,
        PolicyVersion.__table__,
        CriticalField.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Passage.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        report = await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="passages",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=40,
            manifest_bytes=manifest_bytes,
            idempotency_key="test-family1-passages",
            submitted_by="CKPA-52",
        )

        assert report.imported_rows == 39
        assert report.quarantined_rows == 1
        assert session.scalar(select(func.count()).select_from(ImportRecord)) == 39
        assert session.scalar(select(func.count()).select_from(QuarantineRow)) == 1
        quarantined = session.scalar(select(QuarantineRow))
        import_manifest = session.get(ImportManifest, report.batch_id)
        assert quarantined.record_id == "PAS-040"
        assert import_manifest.expected_rows == 40
        assert import_manifest.accepted_rows + import_manifest.quarantined_rows == 40

        critical_report = await SERVICE.import_csv_bytes(
            db,
            critical_fields_bytes,
            source_type="critical_fields",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=16,
            manifest_bytes=manifest_bytes,
            idempotency_key="test-family1-critical-fields",
            submitted_by="CKPA-52",
        )
        assert critical_report.expected_rows == critical_report.imported_rows == 16
        assert critical_report.quarantined_rows == 0
        assert session.scalar(select(func.count()).select_from(ImportRecord)) == 55
        assert session.scalar(select(func.count()).select_from(QuarantineRow)) == 1

        repeated = await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="passages",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=40,
            manifest_bytes=manifest_bytes,
            idempotency_key="test-family1-passages",
            submitted_by="CKPA-52",
        )
        assert repeated.batch_id == report.batch_id
        assert session.scalar(select(func.count()).select_from(ImportRecord)) == 55


@pytest.mark.asyncio
async def test_import_rejects_idempotency_key_reuse_with_different_content() -> None:
    raw_bytes = (FAMILY1 / "Critical_Fields_Family1.csv").read_bytes()
    manifest_bytes = (FAMILY1 / "Source_URI_And_Checksum_Manifest_Family1.csv").read_bytes()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Passage.__table__,
        Policy.__table__,
        PolicyVersion.__table__,
        CriticalField.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="critical_fields",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=16,
            manifest_bytes=manifest_bytes,
            idempotency_key="already-used",
            submitted_by="CKPA-52",
        )

        with pytest.raises(IdempotencyKeyConflict):
            await SERVICE.import_csv_bytes(
                db,
                raw_bytes,
                source_type="critical_fields",
                batch_type=BatchType.FULL_SNAPSHOT,
                expected_rows=16,
                manifest_bytes=manifest_bytes + b"\n",
                idempotency_key="already-used",
                submitted_by="CKPA-52",
            )


@pytest.mark.asyncio
async def test_full_snapshot_partial_apply_and_quarantined_lkg_is_preserved() -> None:
    headers, rows = _read_csv((FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes())
    rows[0]["content"] = "accepted replacement"
    rows[1]["has_essential_attachments"] = "false"
    raw_bytes = _serialize_csv(tuple(headers), rows)
    manifest = _manifest_for(rows, "passages")

    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Passage.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        original = Passage(
            id=rows[1]["passage_id"],
            document_id="DOC-OLD",
            document_version_id="VER-OLD",
            title="last-known-good",
            content="preserved",
            source_ref="data/g1/old.md",
            page_number=1,
            clause_ref="OLD",
            language="vi",
            scope="company:SN",
            audience="reader",
            status="effective",
            has_essential_attachments=True,
            is_tombstoned=False,
        )
        session.add(original)
        session.commit()

        report = await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="passages",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=len(rows),
            manifest_bytes=manifest,
            idempotency_key="partial-full-snapshot",
            submitted_by="CKPA-59",
            batch_timestamp=datetime(2026, 11, 23, 10, 0, tzinfo=UTC),
        )

        preserved = session.get(Passage, rows[1]["passage_id"])
        assert report.accepted_rows + report.quarantined_rows == report.expected_rows
        assert report.quarantined_rows >= 1
        assert preserved is not None
        assert preserved.content == "preserved"
        assert preserved.is_tombstoned is False


@pytest.mark.asyncio
async def test_stale_batch_is_rejected_before_authoritative_apply() -> None:
    raw_bytes = (FAMILY1 / "Critical_Fields_Family1.csv").read_bytes()
    manifest_bytes = (FAMILY1 / "Source_URI_And_Checksum_Manifest_Family1.csv").read_bytes()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Policy.__table__,
        PolicyVersion.__table__,
        CriticalField.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="critical_fields",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=16,
            manifest_bytes=manifest_bytes,
            idempotency_key="current-batch",
            submitted_by="CKPA-59",
            batch_timestamp=datetime(2026, 11, 23, 10, 0, tzinfo=UTC),
        )

        with pytest.raises(StaleBatchRejected):
            await SERVICE.import_csv_bytes(
                db,
                raw_bytes,
                source_type="critical_fields",
                batch_type=BatchType.FULL_SNAPSHOT,
                expected_rows=16,
                manifest_bytes=manifest_bytes,
                idempotency_key="stale-batch",
                submitted_by="CKPA-59",
                batch_timestamp=datetime(2026, 11, 23, 9, 0, tzinfo=UTC),
            )


@pytest.mark.asyncio
async def test_delta_missing_rows_are_not_tombstoned() -> None:
    headers, rows = _read_csv((FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes())
    raw_bytes = _serialize_csv(tuple(headers), rows[:1])
    manifest = _manifest_for(rows[:1], "passages")

    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Passage.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        existing = Passage(
            id="PAS-MISSING",
            document_id="DOC-001",
            document_version_id="VER-001",
            title="must remain active",
            content="active",
            source_ref="data/g1/source.md",
            page_number=1,
            clause_ref="OLD",
            language="vi",
            scope="company:SN",
            audience="reader",
            status="effective",
            has_essential_attachments=True,
            is_tombstoned=False,
        )
        session.add(existing)
        session.commit()

        await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="passages",
            batch_type=BatchType.DELTA,
            expected_rows=1,
            manifest_bytes=manifest,
            idempotency_key="delta-no-auto-tombstone",
            submitted_by="CKPA-59",
            batch_timestamp=datetime(2026, 11, 23, 10, 0, tzinfo=UTC),
        )

        remaining = session.get(Passage, "PAS-MISSING")
        assert remaining is not None
        assert remaining.is_tombstoned is False


def test_higher_version_compares_numeric_tuples() -> None:
    assert SERVICE._higher_version("v1.10", "v1.2") is True
    assert SERVICE._higher_version("v1.2", "v1.10") is False
    assert SERVICE._higher_version("DOC-002:VER-010", "DOC-002:VER-002") is True
    assert SERVICE._higher_version("beta", "alpha") is True


def test_composed_document_version_id_stays_within_database_limit() -> None:
    long_prefix = f"DOC-{'a' * 80}"
    long_version = f"VER-{'b' * 80}"

    composed = SERVICE._compose_document_version_id(long_prefix, long_version)
    other = SERVICE._compose_document_version_id(long_prefix, f"{long_version}x")
    already_composed = SERVICE._compose_document_version_id("", f"DOC:{long_version}")

    assert len(composed) <= 64
    assert composed == SERVICE._compose_document_version_id(long_prefix, long_version)
    assert composed != other
    assert len(already_composed) <= 64


@pytest.mark.asyncio
async def test_composite_doc_version_id_prevents_cross_document_collision() -> None:
    headers, rows = _read_csv((FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes())
    row_a = dict(rows[0])
    row_a["passage_id"] = "PAS-COL-1"
    row_a["document_id"] = "DOC-001"
    row_a["document_version_id"] = "VER-001"
    row_b = dict(rows[0])
    row_b["passage_id"] = "PAS-COL-2"
    row_b["document_id"] = "DOC-002"
    row_b["document_version_id"] = "VER-001"
    row_b["title"] = "Chính sách Bảo mật Thông tin Khách hàng"
    batch_rows = [row_a, row_b]
    raw_bytes = _serialize_csv(tuple(headers), batch_rows)
    manifest = _manifest_for(batch_rows, "passages")

    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Passage.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="passages",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=2,
            manifest_bytes=manifest,
            idempotency_key="composite-doc-ver-test",
            submitted_by="steward-1",
            batch_timestamp=datetime(2026, 11, 24, 10, 0, tzinfo=UTC),
        )
        p1 = session.get(Passage, "PAS-COL-1")
        p2 = session.get(Passage, "PAS-COL-2")
        doc1 = session.get(Document, "DOC-001")
        doc2 = session.get(Document, "DOC-002")
        assert p1 is not None and p2 is not None
        assert p1.document_version_id == "DOC-001:VER-001"
        assert p2.document_version_id == "DOC-002:VER-001"
        assert session.get(DocumentVersion, "DOC-001:VER-001") is not None
        assert session.get(DocumentVersion, "DOC-002:VER-001") is not None
        assert doc1 is not None and doc1.policy_family == PolicyFamily.COMMERCIAL_QUOTING_APPROVAL
        assert doc2 is not None and doc2.policy_family == PolicyFamily.CUSTOMER_INFO_HANDLING


@pytest.mark.asyncio
async def test_full_snapshot_tombstones_omitted_document_passages() -> None:
    headers, rows = _read_csv((FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes())
    raw_bytes = _serialize_csv(tuple(headers), rows[:1])
    manifest = _manifest_for(rows[:1], "passages")

    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Passage.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        omitted = Passage(
            id="PAS-OMITTED-DOC",
            document_id="DOC-REMOVED",
            document_version_id="DOC-REMOVED:VER-001",
            title="removed document passage",
            content="old content",
            source_ref="data/g1/removed.md",
            page_number=1,
            clause_ref="OLD",
            language="vi",
            scope="company:SN",
            audience="reader",
            status="effective",
            has_essential_attachments=True,
            is_tombstoned=False,
        )
        session.add(omitted)
        session.commit()

        await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="passages",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=1,
            manifest_bytes=manifest,
            idempotency_key="full-snapshot-omitted-doc",
            submitted_by="steward-1",
            batch_timestamp=datetime(2026, 11, 24, 11, 0, tzinfo=UTC),
        )
        tombstoned = session.get(Passage, "PAS-OMITTED-DOC")
        assert tombstoned is not None
        assert tombstoned.is_tombstoned is True
        assert tombstoned.status == "withdrawn"


@pytest.mark.asyncio
async def test_critical_field_import_creates_parent_policy_and_policy_version() -> None:
    raw_bytes = (FAMILY1 / "Critical_Fields_Family1.csv").read_bytes()
    manifest_bytes = (FAMILY1 / "Source_URI_And_Checksum_Manifest_Family1.csv").read_bytes()
    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Policy.__table__,
        PolicyVersion.__table__,
        CriticalField.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        await SERVICE.import_csv_bytes(
            db,
            raw_bytes,
            source_type="critical_fields",
            batch_type=BatchType.FULL_SNAPSHOT,
            expected_rows=16,
            manifest_bytes=manifest_bytes,
            idempotency_key="cf-parent-fk-test",
            submitted_by="steward-1",
            batch_timestamp=datetime(2026, 11, 24, 12, 0, tzinfo=UTC),
        )
        policy = session.get(Policy, "POL-001")
        policy_version = session.get(PolicyVersion, "PV-001")
        cf = session.get(CriticalField, "CF-001")
        assert policy is not None
        assert policy.policy_family == PolicyFamily.COMMERCIAL_QUOTING_APPROVAL
        assert policy_version is not None
        assert policy_version.policy_id == "POL-001"
        assert policy_version.document_version_id == "POL-001:VER-001"
        assert cf is not None
        assert cf.document_version_id == "POL-001:VER-001"


@pytest.mark.asyncio
async def test_enforce_corpus_ceiling_rejects_over_limit_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from src.config import settings

    monkeypatch.setattr(settings, "CORPUS_MAX_PASSAGES", 2)
    headers, rows = _read_csv((FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes())
    raw_bytes = _serialize_csv(tuple(headers), rows[:3])
    manifest = _manifest_for(rows[:3], "passages")

    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables = [
        ImportBatch.__table__,
        ImportManifest.__table__,
        ImportRecord.__table__,
        QuarantineRow.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        Passage.__table__,
    ]
    Base.metadata.create_all(engine, tables=[*tables, *_CHANGE_IMPACT_TABLES])
    with Session(engine) as session:
        db = _AsyncSessionAdapter(session)
        with pytest.raises(CorpusCeilingExceeded):
            await SERVICE.import_csv_bytes(
                db,
                raw_bytes,
                source_type="passages",
                batch_type=BatchType.FULL_SNAPSHOT,
                expected_rows=3,
                manifest_bytes=manifest,
                idempotency_key="ceiling-reject-test",
                submitted_by="steward-1",
                batch_timestamp=datetime(2026, 11, 24, 13, 0, tzinfo=UTC),
                enforce_corpus_ceiling=True,
            )
        assert session.scalar(select(func.count()).select_from(Passage)) == 0
