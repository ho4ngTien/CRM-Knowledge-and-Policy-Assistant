"""Independent QA Regression Suite for CKPA-75 (CRM-G1-SUB23): G1 Gate Verification.

Traceability:
- Jira Issue : CKPA-75 (CRM-G1-SUB23) | Gate G1
- RFP IDs    : OPS 01, OPS 03, OPS 04, SEC 01, SEC 05, KNW 03, DAT 02, DAT 04, DAT 05, O1
- G1 ACs     : G1-AC02, G1-AC03, G1-AC04, G1-AC05, G1-AC06
- SoD Notice : Automated QA regression suite prepared for independent execution
               and sign-off by [S4] Quy Hai on the release patch tag.
"""

from __future__ import annotations

import csv
import hashlib
import io
import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import cast
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import Table, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.config import Settings, settings
from src.db import Base
from src.modules.ingestion.models import (
    ImportBatch,
    ImportManifest,
    ImportRecord,
    QuarantineRow,
)
from src.modules.ingestion.service import (
    MANIFEST_CSV_COLUMNS,
    IngestionService,
)
from src.modules.knowledge.models import Document, DocumentVersion, Passage
from src.modules.knowledge.schemas import PassageSummary
from src.modules.knowledge.service import KnowledgeService
from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.policy.service import PolicyService
from src.modules.retrieval.service import RetrievalService
from src.modules.selection.schemas import ScopeDimensions
from src.modules.selection.service import SelectionService
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import (
    AuthorityTier,
    BatchType,
    ComparisonOperator,
    CriticalFieldType,
    PolicyLifecycleStatus,
    UserRole,
)
from src.shared.exceptions import PolicyWithdrawn

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
REPO_ROOT = Path(__file__).resolve().parents[2]
FAMILY1 = REPO_ROOT / "data" / "g1" / "family1"


class _AsyncSessionAdapter:
    """Minimal async session adapter over an isolated in-memory SQLite Session."""

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


def _serialize_csv(headers: tuple[str, ...], rows: list[dict[str, str]]) -> bytes:
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _build_passage_manifest(rows: list[dict[str, str]]) -> bytes:
    checksum_fields = (
        "passage_id",
        "document_id",
        "document_version_id",
        "clause_ref",
        "content",
        "scope",
        "status",
    )
    manifest_rows = []
    for row in rows:
        canonical = "|".join(row.get(k, "") for k in checksum_fields)
        manifest_rows.append(
            {
                "record_type": "passage",
                "record_id": row["passage_id"],
                "sha256_checksum": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                **{
                    col: ""
                    for col in MANIFEST_CSV_COLUMNS
                    if col not in {"record_type", "record_id", "sha256_checksum"}
                },
            }
        )
    return _serialize_csv(MANIFEST_CSV_COLUMNS, manifest_rows)


def _make_users() -> dict[str, AuthenticatedUser]:
    return {
        "reader": AuthenticatedUser(
            user_id="qa-reader-01",
            email="reader@songnhat.vn",
            roles=frozenset({UserRole.READER}),
            allowed_audiences=frozenset({"reader"}),
        ),
        "policy_owner": AuthenticatedUser(
            user_id="qa-owner-01",
            email="owner@songnhat.vn",
            roles=frozenset({UserRole.POLICY_OWNER}),
            allowed_audiences=frozenset({"policy_owner"}),
        ),
        "steward": AuthenticatedUser(
            user_id="qa-steward-01",
            email="steward@songnhat.vn",
            roles=frozenset({UserRole.STEWARD}),
            allowed_audiences=frozenset({"steward"}),
        ),
        "administrator": AuthenticatedUser(
            user_id="qa-admin-01",
            email="admin@songnhat.vn",
            roles=frozenset({UserRole.ADMINISTRATOR}),
            allowed_audiences=frozenset({"administrator"}),
        ),
    }


def _make_passage(
    passage_id: str,
    status: PolicyLifecycleStatus,
    audience: list[str],
    *,
    effective_from: datetime | None = None,
    effective_to: datetime | None = None,
) -> PassageSummary:
    base_dt = datetime(2026, 11, 15, 0, 0, 0, tzinfo=VN_TZ)
    return PassageSummary(
        passage_id=passage_id,
        document_id="DOC-QA-01",
        document_version_id="DOC-QA-01-V1",
        title=f"Policy {passage_id}",
        content="Điều khoản quy định chiết khấu thương mại nội bộ Song Nhật.",
        source_ref="Quy chế thương mại 2026",
        page_number=1,
        clause_ref="Điều 2.1",
        language="vi",
        scope="company=SONGNHAT_HN;branch=all",
        audience=audience,
        status=status,
        has_essential_attachments=True,
        effective_from=effective_from or (base_dt - timedelta(days=30)),
        effective_to=effective_to,
        supersedes=None,
    )


# ==============================================================================
# SECTION 1: OPS 01 REGRESSION (500-ROW BATCH, RECONCILIATION, SLA, LKG)
# ==============================================================================


class TestOPS01IndependentRegression:
    """OPS 01 / DAT 02 independent regression for 500-row batch and LKG safety."""

    @pytest.mark.asyncio
    async def test_ops01_500_row_reconciliation_sla_and_lkg_fault_injection(self) -> None:
        """500-row batch satisfies Expected = Accepted + Quarantined, SLA << 30m, 100% LKG."""
        backend_root = str(Path(__file__).resolve().parents[1])
        if backend_root not in sys.path:
            sys.path.insert(0, backend_root)

        from scripts.benchmark_ops01_500 import OPS01_MAX_MINUTES, run_ops01_benchmark

        result = await run_ops01_benchmark()

        assert result.total_batch_rows == 500
        assert result.accepted_rows + result.quarantined_rows == result.total_batch_rows
        assert result.rejected_rows == 0
        assert result.total_minutes < OPS01_MAX_MINUTES
        assert result.passed_sla_30m is True
        assert result.lkg_quarantine_preserved is True
        assert result.lkg_failed_batch_preserved is True
        assert result.idempotent_zero_duplicates is True

    @pytest.mark.asyncio
    async def test_ops01_corrupt_row_quarantined_and_lkg_preserved(self) -> None:
        """Fault injection with checksum mismatch quarantines bad row and keeps LKG intact."""
        raw = (FAMILY1 / "Policy_Corpus_Family1.csv").read_bytes()
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        headers = tuple(reader.fieldnames or ())
        rows = list(reader)[:2]

        # Build valid manifest BEFORE mutating row 1 content to trigger checksum quarantine
        manifest_bytes = _build_passage_manifest(rows)
        rows[1]["content"] = "CORRUPTED_CONTENT_AFTER_MANIFEST"
        batch_bytes = _serialize_csv(headers, rows)

        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(
            engine,
            tables=[
                cast(Table, ImportBatch.__table__),
                cast(Table, ImportManifest.__table__),
                cast(Table, ImportRecord.__table__),
                cast(Table, QuarantineRow.__table__),
                cast(Table, Document.__table__),
                cast(Table, DocumentVersion.__table__),
                cast(Table, Passage.__table__),
            ],
        )
        ingestion_svc = IngestionService()
        with Session(engine) as session:
            db = _AsyncSessionAdapter(session)
            # Seed LKG row for rows[1]
            lkg_passage = Passage(
                id=rows[1]["passage_id"],
                document_id=rows[1]["document_id"],
                document_version_id=rows[1]["document_version_id"],
                title="LKG Title",
                content="LKG_ORIGINAL_CONTENT",
                source_ref="data/g1/source.md",
                page_number=1,
                clause_ref="Điều 1",
                language="vi",
                scope="company=SONGNHAT_HN",
                audience="reader",
                status="effective",
                has_essential_attachments=True,
                is_tombstoned=False,
            )
            session.add(lkg_passage)
            session.commit()

            report = await ingestion_svc.import_csv_bytes(
                cast(AsyncSession, db),
                batch_bytes,
                source_type="passages",
                batch_type=BatchType.DELTA,
                expected_rows=2,
                manifest_bytes=manifest_bytes,
                idempotency_key="qa-ckpa75-fault-injection",
                submitted_by="CKPA-75-QA",
                batch_timestamp=datetime(2026, 11, 24, 10, 0, tzinfo=UTC),
            )

            assert report.expected_rows == 2
            assert report.accepted_rows + report.quarantined_rows == report.expected_rows
            assert report.quarantined_rows == 1
            assert report.accepted_rows == 1

            preserved = session.get(Passage, rows[1]["passage_id"])
            assert preserved is not None
            assert preserved.content == "LKG_ORIGINAL_CONTENT"
            assert preserved.is_tombstoned is False


# ==============================================================================
# SECTION 2: SEC 01 & KNW 03 (4 RFP ROLES x 7 LIFECYCLE STATES, 0% LEAKAGE)
# ==============================================================================


class TestSEC01AndKNW03MatrixRegression:
    """SEC 01 & KNW 03 pre-retrieval RBAC × 7-state lifecycle matrix verification."""

    @pytest.mark.parametrize("role_key", ["reader", "policy_owner", "steward", "administrator"])
    def test_sec01_knw03_4_roles_x_7_lifecycle_states_zero_leakage(
        self,
        role_key: str,
    ) -> None:
        """Each of 4 RFP roles sees ONLY EFFECTIVE passages in its audience across all states."""
        retrieval_svc = RetrievalService()
        users = _make_users()
        user = users[role_key]

        # All 7 formal KNW 03 lifecycle states + 2 governance states
        all_states = [
            PolicyLifecycleStatus.DRAFT,
            PolicyLifecycleStatus.OWNER_REVIEWED,
            PolicyLifecycleStatus.APPROVED,
            PolicyLifecycleStatus.SCHEDULED,
            PolicyLifecycleStatus.EFFECTIVE,
            PolicyLifecycleStatus.SUPERSEDED,
            PolicyLifecycleStatus.WITHDRAWN,
            PolicyLifecycleStatus.QUARANTINED,
            PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
        ]
        target_audience = "reader" if role_key == "administrator" else role_key

        candidates = [
            _make_passage(f"P-{role_key}-{st.value}", st, [target_audience])
            for st in all_states
        ]

        filtered = retrieval_svc.prefilter_passages(
            user,
            candidates,
            governing_date=date(2026, 11, 15),
        )
        assert [p.passage_id for p in filtered] == [f"P-{role_key}-effective"]
        assert all(p.status == PolicyLifecycleStatus.EFFECTIVE for p in filtered)

    def test_sec01_cross_role_audience_isolation_zero_leakage(self) -> None:
        """Non-admin roles have 0% access to passages targeted at other restricted roles."""
        retrieval_svc = RetrievalService()
        users = _make_users()
        candidates = [
            _make_passage("P-AUD-READER", PolicyLifecycleStatus.EFFECTIVE, ["reader"]),
            _make_passage("P-AUD-OWNER", PolicyLifecycleStatus.EFFECTIVE, ["policy_owner"]),
            _make_passage("P-AUD-STEWARD", PolicyLifecycleStatus.EFFECTIVE, ["steward"]),
            _make_passage("P-AUD-ADMIN", PolicyLifecycleStatus.EFFECTIVE, ["administrator"]),
        ]

        for role_key, expected_id in [
            ("reader", "P-AUD-READER"),
            ("policy_owner", "P-AUD-OWNER"),
            ("steward", "P-AUD-STEWARD"),
        ]:
            filtered = retrieval_svc.prefilter_passages(
                users[role_key],
                candidates,
                governing_date=date(2026, 11, 15),
            )
            assert [p.passage_id for p in filtered] == [expected_id]

        # Administrator can view all effective audiences
        admin_filtered = retrieval_svc.prefilter_passages(
            users["administrator"],
            candidates,
            governing_date=date(2026, 11, 15),
        )
        assert len(admin_filtered) == 4
        assert not check_policy_audience(users["reader"], ["policy_owner"])
        assert not check_policy_audience(users["policy_owner"], ["steward"])
        assert not check_policy_audience(users["steward"], ["administrator"])


# ==============================================================================
# SECTION 3: SEC 05 IMMEDIATE WITHDRAWAL FAIL-CLOSED
# ==============================================================================


class TestSEC05ImmediateWithdrawalFailClosed:
    """SEC 05 immediate withdrawal fail-closed across Retrieval, Knowledge, and Selection."""

    def test_sec05_withdrawn_excluded_immediately_even_for_admin_with_all_flags(self) -> None:
        """WITHDRAWN passages are never served even with historical/preview flags and admin role."""
        retrieval_svc = RetrievalService()
        admin = _make_users()["administrator"]
        withdrawn_passage = _make_passage(
            "P-EMERGENCY-WTD",
            PolicyLifecycleStatus.WITHDRAWN,
            ["all"],
        )

        filtered = retrieval_svc.prefilter_passages(
            admin,
            [withdrawn_passage],
            governing_date=date(2026, 11, 15),
            allow_historical=True,
            allow_future_preview=True,
        )
        assert filtered == []

    @pytest.mark.asyncio
    async def test_sec05_knowledge_service_raises_policy_withdrawn_fail_closed(self) -> None:
        """Direct passage fetch on a withdrawn/tombstoned record raises PolicyWithdrawn."""
        engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(
            engine,
            tables=[
                cast(Table, Document.__table__),
                cast(Table, DocumentVersion.__table__),
                cast(Table, Passage.__table__),
            ],
        )
        knowledge_svc = KnowledgeService()
        admin = _make_users()["administrator"]

        with Session(engine) as session:
            db = _AsyncSessionAdapter(session)
            doc = Document(
                id="DOC-WTD-01",
                title="Withdrawn Commercial Policy",
                policy_family="commercial_quoting_approval",
                authority_tier="policy",
                owner="Sales Director",
                source_ref="data/g1/withdrawn.md",
            )
            ver = DocumentVersion(
                id="VER-WTD-01",
                document_id="DOC-WTD-01",
                status=PolicyLifecycleStatus.WITHDRAWN.value,
                effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
                effective_to=None,
                recorded_at=datetime(2026, 1, 1, tzinfo=VN_TZ),
            )
            passage = Passage(
                id="PAS-WTD-01",
                document_id="DOC-WTD-01",
                document_version_id="VER-WTD-01",
                title="Withdrawn Clause",
                content="Nội dung đã bị thu hồi khẩn cấp.",
                source_ref="data/g1/withdrawn.md",
                page_number=1,
                clause_ref="Điều 9",
                language="vi",
                scope="all",
                audience="all",
                status=PolicyLifecycleStatus.WITHDRAWN.value,
                has_essential_attachments=True,
                is_tombstoned=True,
            )
            session.add_all([doc, ver, passage])
            session.commit()

            with pytest.raises(PolicyWithdrawn):
                await knowledge_svc.get_passage(
                    cast(AsyncSession, db),
                    admin,
                    "PAS-WTD-01",
                    allow_historical=True,
                )

    def test_sec05_withdrawn_policy_blocked_in_selection_and_triggers_hold(self) -> None:
        """WITHDRAWN candidate is excluded by PolicyService & SelectionService -> DAT04 Hold."""
        gov_date = date(2026, 11, 15)
        policy_svc = PolicyService()
        selection_svc = SelectionService()

        withdrawn_cand = ApplicabilityCandidate(
            version_id="VER-WTD-SEL",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.WITHDRAWN,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            effective_to=None,
            scope="company=SONGNHAT_HN;branch=all",
        )
        gate = policy_svc.evaluate_policy_gate([withdrawn_cand], requested_date=gov_date)
        assert gate.applicable_version_ids == ()
        assert gate.can_proceed is False

        res = selection_svc.run_selection(
            candidates=[withdrawn_cand],
            dimensions=ScopeDimensions(company="SONGNHAT_HN"),
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=gov_date,
        )
        assert res.applicable_version_ids == []
        assert res.hold_decision.must_hold is True
        assert any(
            t.code == "DAT04_NO_APPLICABLE_VERSION"
            for t in res.hold_decision.triggers
        )


# ==============================================================================
# SECTION 4: OPS 03/04 SMOKE CHECKS & O1 BASE SCOPE LOCK
# ==============================================================================


class TestOPS03OPS04SmokeAndO1Lock:
    """OPS 03/04 smoke regression + Option O1 Base Scope default-disabled lock."""

    def test_ops03_ops04_smoke_deterministic_selection_and_conflict_hold(self) -> None:
        """Smoke check: 0% LLM deterministic threshold + conflict hold on matching scope."""
        gov_date = date(2026, 11, 15)
        policy_svc = PolicyService()
        selection_svc = SelectionService()

        # Threshold smoke
        assert selection_svc.evaluate_numeric_threshold(
            ComparisonOperator.LE, Decimal("5.0"), "5"
        ) is True
        assert selection_svc.evaluate_numeric_threshold(
            ComparisonOperator.BETWEEN, Decimal("10"), "5;15"
        ) is True
        assert selection_svc.evaluate_numeric_threshold(
            ComparisonOperator.GT, Decimal("5"), "5"
        ) is False

        # Conflict hold smoke
        c1 = ApplicabilityCandidate(
            version_id="VER-SMOKE-POL",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            effective_to=None,
            scope="company=SONGNHAT_HN;branch=HN01",
        )
        c2 = ApplicabilityCandidate(
            version_id="VER-SMOKE-CTR",
            authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            effective_to=None,
            scope="company=SONGNHAT_HN;branch=HN01",
        )
        cf = CriticalFieldItem(
            field_id="CF-SMOKE-1",
            policy_id="POL-01",
            policy_version_id="VER-SMOKE-POL",
            document_version_id="DOC-V1",
            field_name="Chiết khấu",
            field_type=CriticalFieldType.NUMBER,
            operator=ComparisonOperator.LE,
            value="5%",
            unit="%",
            currency=None,
            approval_role="sales_manager",
            time_limit="24h",
            exception_condition=None,
            required_documents=["Phiếu đề xuất"],
            source_clause="Điều 2",
            status=PolicyLifecycleStatus.EFFECTIVE,
        )
        gate = policy_svc.evaluate_policy_gate([c1, c2], requested_date=gov_date)
        res = selection_svc.run_selection(
            candidates=[c1, c2],
            dimensions=ScopeDimensions(company="SONGNHAT_HN", branch="HN01"),
            all_critical_fields=[cf],
            gate_decision=gate,
            requested_date=gov_date,
        )
        assert res.hold_decision.must_hold is True
        assert any(t.code == "DAT05_SOURCE_CONFLICT" for t in res.hold_decision.triggers)
        assert res.llm_used is False

    def test_o1_context_import_disabled_by_default_base_scope(self) -> None:
        """G1-AC03: Option O1 (ENABLE_O1_CONTEXT_IMPORT) MUST remain False in Base Scope."""
        assert settings.ENABLE_O1_CONTEXT_IMPORT is False
        assert Settings().ENABLE_O1_CONTEXT_IMPORT is False
