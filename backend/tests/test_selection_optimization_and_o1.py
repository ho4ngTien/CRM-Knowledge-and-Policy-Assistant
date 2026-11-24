"""Test suite for Selection/Hold optimization and Option O1 Customer Context readiness.

Traceability:
- RFP / SRS: WP 03, DAT 07, SEC 02, OPS 03, OPS 04, VN 01.
- Jira Task: CKPA-78 / CRM-G1-SUB22.
- AC Traceability: G1-AC03 (O1 locked in Base Scope), G1-AC05, G1-AC06, G1-AC07.
"""

from __future__ import annotations

import json
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.modules.policy.schemas import ApplicabilityCandidate
from src.modules.retrieval.service import RetrievalService
from src.modules.selection.o1_context import (
    CustomerContextO1,
    apply_o1_to_scope_dimensions,
    validate_o1_batch_caps,
    validate_o1_customer_record,
)
from src.modules.selection.schemas import ScopeDimensions
from src.modules.selection.service import SelectionService
from src.shared.auth import AuthenticatedUser, create_access_token
from src.shared.contracts import PolicyGateDecision
from src.shared.enums import AuthorityTier, PolicyLifecycleStatus, UserRole

_VN_TZ = ZoneInfo(settings.APP_TIMEZONE)


def _make_candidate(
    version_id: str,
    authority_tier: AuthorityTier = AuthorityTier.POLICY,
    status: PolicyLifecycleStatus = PolicyLifecycleStatus.EFFECTIVE,
    effective_from: date = date(2026, 1, 1),
    effective_to: date | None = None,
    scope: str = "branch=all;customer_category=all",
) -> ApplicabilityCandidate:
    """Helper to synthesize a valid ApplicabilityCandidate."""
    eff_from_dt = datetime(
        effective_from.year,
        effective_from.month,
        effective_from.day,
        tzinfo=_VN_TZ,
    )
    eff_to_dt = (
        datetime(effective_to.year, effective_to.month, effective_to.day, tzinfo=_VN_TZ)
        if effective_to
        else None
    )
    return ApplicabilityCandidate(
        version_id=version_id,
        authority_tier=authority_tier,
        status=status,
        effective_from=eff_from_dt,
        effective_to=eff_to_dt,
        scope=scope,
    )


# ---------------------------------------------------------------------------
# 1. VN 01 Query Normalization Optimization Tests
# ---------------------------------------------------------------------------

class TestVN01QueryNormalizationOptimization:
    """Validate that pre-compiled Regex optimization speeds up execution."""

    def test_vietnamese_query_normalization_semantics_preserved(self) -> None:
        """Confirm unaccented terms, abbreviations, and negations are preserved."""
        svc = RetrievalService()

        # Query containing unaccented words and CRM abbreviations
        query = (
            "cvkd chiet khau cho khach hang b2b tai chi nhanh "
            "khong duoc vuot qua 5%"
        )
        norm_query, expanded = svc.normalize_query_vi(query)

        # Semantics check: unaccented words converted to accented
        assert "chiết khấu" in norm_query
        assert "khách hàng" in norm_query

        # Negation check: 'không được' is preserved and mapped to accented form
        assert "không được" in norm_query
        negations = svc.detect_preserved_negations(query)
        assert "không được" in negations

        # Synonyms check: 'cvkd' expanded to sales roles, 'b2b' to corporate customer
        assert any("chuyên viên kinh doanh" in syn for syn in expanded)
        assert any("khách hàng doanh nghiệp" in syn for syn in expanded)

    def test_normalization_performance_benchmark(self) -> None:
        """Verify that 600 query normalizations run under 50ms (avg < 0.08ms/call)."""
        svc = RetrievalService()
        queries = [
            "chiet khau cho khach hang b2b tai chi nhanh ha noi la bao nhieu?",
            "chinh sach bao hanh thiet bi bien tan tren 50 kw quy dinh the nao?",
            "hop dong tren 500 trieu do ai phe duyet?",
            "tpkd co duoc ky bao gia khong ap dung giam gia khong?",
        ] * 150  # 600 queries

        start = time.perf_counter()
        for q in queries:
            svc.normalize_query_vi(q)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Must execute comfortably under 50ms
        assert elapsed_ms < 50.0, f"Expected < 50ms, got {elapsed_ms:.2f}ms"


# ---------------------------------------------------------------------------
# 2. Date and Conflict Hold Reinforcement Tests (OPS 03, DAT 05)
# ---------------------------------------------------------------------------

class TestDateAndConflictHoldReinforcement:
    """Validate strengthened date boundaries and conflict hold evaluations."""

    def test_reinforced_date_classification_boundaries(self) -> None:
        """Confirm valid_from and valid_to cleanly partition scheduled vs superseded policies."""
        svc = SelectionService()
        today_vn = svc.resolve_governing_date_vn(None).governing_date

        c_past = _make_candidate(
            version_id="POL-PAST-01",
            status=PolicyLifecycleStatus.SUPERSEDED,
            effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31),
            scope="branch=all;customer_category=all",
        )
        c_future = _make_candidate(
            version_id="POL-FUTURE-01",
            status=PolicyLifecycleStatus.SCHEDULED,
            effective_from=date(2027, 1, 1),
            effective_to=None,
            scope="branch=all;customer_category=all",
        )

        scope = ScopeDimensions(branch="HN")

        # Without historical / preview flags: both must be excluded on today's date
        matches_today = svc.match_scope_6dim_bulk(
            [c_past, c_future],
            scope,
            today_vn,
            allow_historical=False,
            allow_future_preview=False,
        )
        assert all(not m.matched for m in matches_today)

        # Historical query in 2025: past version becomes eligible
        hist_date = date(2025, 6, 1)
        matches_hist = svc.match_scope_6dim_bulk(
            [c_past, c_future],
            scope,
            hist_date,
            allow_historical=True,
            allow_future_preview=False,
        )
        matched_hist_ids = {m.version_id for m in matches_hist if m.matched}
        assert "POL-PAST-01" in matched_hist_ids
        assert "POL-FUTURE-01" not in matched_hist_ids

        # Future preview query in 2027: future version becomes eligible
        future_date = date(2027, 6, 1)
        matches_future = svc.match_scope_6dim_bulk(
            [c_past, c_future],
            scope,
            future_date,
            allow_historical=False,
            allow_future_preview=True,
        )
        matched_future_ids = {m.version_id for m in matches_future if m.matched}
        assert "POL-FUTURE-01" in matched_future_ids
        assert "POL-PAST-01" not in matched_future_ids

    def test_reinforced_conflict_hold_on_contract_vs_policy(self) -> None:
        """Verify DAT05 conflict trigger when contract conflicts with policy on same scope."""
        svc = SelectionService()
        gate = PolicyGateDecision(
            governing_date=date(2026, 11, 15),
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=("CONTRACT-01", "POL-01"),
            has_conflict=True,
            can_proceed=True,
            hold_reason="Contract vs policy conflict",
        )
        c_contract = _make_candidate(
            version_id="CONTRACT-01",
            authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
            status=PolicyLifecycleStatus.EFFECTIVE,
            scope="branch=hn;customer_category=b2b",
        )
        c_policy = _make_candidate(
            version_id="POL-01",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            scope="branch=hn;customer_category=b2b",
        )

        decision = svc.evaluate_hold(
            gate,
            critical_field_results=[],
            applicable_version_ids=["CONTRACT-01", "POL-01"],
            matched_candidates=[c_contract, c_policy],
        )
        assert decision.must_hold is True
        assert any(t.code == "DAT05_SOURCE_CONFLICT" for t in decision.triggers)


# ---------------------------------------------------------------------------
# 3. Option O1 Base Scope Isolation Tests (DAT 07, G1-AC03)
# ---------------------------------------------------------------------------

class TestOptionO1BaseScopeIsolation:
    """Verify that Option O1 is completely locked (fail-closed 403) in Base Scope."""

    def test_o1_setting_disabled_by_default(self) -> None:
        """settings.ENABLE_O1_CONTEXT_IMPORT must strictly be False in Base Scope."""
        assert settings.ENABLE_O1_CONTEXT_IMPORT is False

    def test_o1_import_endpoint_fails_closed_with_403(self) -> None:
        """POST /api/v1/ingestion/o1/context/import returns 403 O1_OPTION_DISABLED_IN_BASE_SCOPE."""
        client = TestClient(app)
        user = AuthenticatedUser(
            user_id="U-STEWARD-01",
            email="steward@songnhat.vn",
            roles=frozenset({UserRole.STEWARD}),
        )
        token = create_access_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/v1/ingestion/o1/context/import", headers=headers)
        assert res.status_code == 403
        assert res.json()["detail"] == "O1_OPTION_DISABLED_IN_BASE_SCOPE"

    def test_selection_layer_operates_independent_of_o1(self) -> None:
        """Selection pipeline executes cleanly without any O1 customer context."""
        svc = SelectionService()
        gate = PolicyGateDecision(
            governing_date=date(2026, 11, 15),
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=(),
            has_conflict=False,
            can_proceed=True,
        )
        result = svc.run_selection(
            candidates=[],
            dimensions=ScopeDimensions(branch="HN"),
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert result.llm_used is False
        assert result.task_id is not None


# ---------------------------------------------------------------------------
# 4. Option O1 Readiness & SEC 02 Allowlist Tests (Purchased Branch)
# ---------------------------------------------------------------------------

class TestOptionO1ReadinessAndAllowlistValidation:
    """Validate Option O1 schema, hard caps, and strict SEC 02 PII allowlist."""

    def test_valid_o1_record_passes_allowlist(self) -> None:
        """Approved CRM fields in allowlist are successfully parsed."""
        valid_payload = {
            "customer_id": "CUST-VIP-001",
            "customer_tier": "VIP",
            "industry_code": "ENERGY_SOLAR",
            "assigned_branch": "Hà Nội",
            "assigned_company": "Song Nhật",
        }
        ctx = validate_o1_customer_record(valid_payload)
        assert ctx.customer_id == "CUST-VIP-001"
        assert ctx.customer_tier == "VIP"
        assert ctx.assigned_branch == "Hà Nội"

    @pytest.mark.parametrize(
        "forbidden_key,value",
        [
            ("phone", "0901234567"),
            ("email", "customer@example.com"),
            ("cccd", "001099012345"),
            ("bank_account", "19030012345678"),
            ("salary", "50000000"),
            ("dossier", "Detailed private investigation dossier"),
        ],
    )
    def test_forbidden_pii_fields_rejected_under_sec02(
        self,
        forbidden_key: str,
        value: str,
    ) -> None:
        """Forbidden sensitive PII fields must raise ValueError under SEC 02."""
        payload: dict[str, Any] = {
            "customer_id": "CUST-002",
            "customer_tier": "B2B",
            forbidden_key: value,
        }
        with pytest.raises(ValueError, match="SEC 02 violation: forbidden PII fields"):
            validate_o1_customer_record(payload)

    def test_unapproved_extra_fields_rejected_under_sec02(self) -> None:
        """Any unapproved non-PII extra field is also rejected by allowlist."""
        payload = {
            "customer_id": "CUST-003",
            "customer_tier": "B2B",
            "custom_metadata_tag": "illegal_tag",
        }
        with pytest.raises(ValueError, match="SEC 02 allowlist violation"):
            validate_o1_customer_record(payload)

    def test_hard_caps_enforced_under_cap18_dat07(self) -> None:
        """CAP-18 batch bounds (<= 2000 init, <= 5000 retained) are strictly enforced."""
        # Valid init batch: 2,000 records
        valid_batch = [
            {"customer_id": f"C-{i}", "customer_tier": "B2B"}
            for i in range(2000)
        ]
        validate_o1_batch_caps(valid_batch, is_init=True)

        # Exceeding init batch: 2,001 records
        invalid_init_batch = [
            {"customer_id": f"C-{i}", "customer_tier": "B2B"}
            for i in range(2001)
        ]
        with pytest.raises(ValueError, match="DAT 07 / CAP-18 cap exceeded"):
            validate_o1_batch_caps(invalid_init_batch, is_init=True)


# ---------------------------------------------------------------------------
# 5. Option O1 Integration with Selection 6-Dim Scope (Workspace Readiness)
# ---------------------------------------------------------------------------

class TestOptionO1IntegrationWithSelectionScope:
    """Verify that O1 context is deterministically mapped to 6-dimension scope matching."""

    def test_o1_context_enriches_scope_dimensions_deterministically(self) -> None:
        """Unset or wildcard dimensions are automatically populated from approved O1 context."""
        context = CustomerContextO1(
            customer_id="KH-B2B-HN",
            customer_tier="b2b",
            assigned_branch="Hà Nội",
            assigned_company="Song Nhật",
        )
        # Empty initial dimensions
        raw_dims = ScopeDimensions()
        enriched = apply_o1_to_scope_dimensions(raw_dims, context)

        assert enriched.customer_category == "b2b"
        assert enriched.branch == "Hà Nội"
        assert enriched.company == "Song Nhật"

    def test_selection_pipeline_filters_correctly_with_o1_context(self) -> None:
        """Confirm that Selection matches policies matching customer's branch and tier."""
        svc = SelectionService()
        gov_date = svc.resolve_governing_date_vn(None).governing_date

        c_hn_b2b = _make_candidate(
            version_id="POL-HN-B2B",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            scope="branch=hà nội;customer_category=b2b",
        )
        c_hcm_b2c = _make_candidate(
            version_id="POL-HCM-B2C",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            scope="branch=tp.hcm;customer_category=b2c",
        )

        # Query with customer context for Hà Nội B2B
        o1_ctx = CustomerContextO1(
            customer_id="KH-01",
            customer_tier="b2b",
            assigned_branch="hà nội",
        )
        enriched_scope = apply_o1_to_scope_dimensions(ScopeDimensions(), o1_ctx)

        matches = svc.match_scope_6dim_bulk(
            [c_hn_b2b, c_hcm_b2c],
            enriched_scope,
            gov_date,
        )
        matched_ids = [m.version_id for m in matches if m.matched]

        # HN B2B must match, HCM B2C must be excluded
        assert matched_ids == ["POL-HN-B2B"]


# ---------------------------------------------------------------------------
# 6. Real 100 Questions Selection Latency Test (OPS 03, SLA)
# ---------------------------------------------------------------------------

class TestReal100QuestionsSelectionLatency:
    """Benchmark Selection execution across the full 100 Real Questions corpus."""

    def test_full_100_questions_latency_under_50ms(self) -> None:
        """Confirm that 100 questions evaluate through Selection in < 50ms (avg < 0.5ms/task)."""
        base_dir = Path(__file__).resolve().parents[2]
        dataset_path = base_dir / "data" / "eval" / "100_real_questions_clean_pii.json"
        assert dataset_path.is_file(), f"Dataset not found at {dataset_path}"

        with open(dataset_path, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 100
        svc = SelectionService()

        # Dummy candidate pool
        dummy_candidates = [
            _make_candidate(
                version_id=f"POL-TEST-{i}",
                authority_tier=AuthorityTier.POLICY,
                status=PolicyLifecycleStatus.EFFECTIVE,
                scope="branch=all;customer_category=all",
            )
            for i in range(5)
        ]

        start = time.perf_counter()
        for q in data:
            requested_d = date.fromisoformat(q["Governing_Date"])
            gov_date_res = svc.resolve_governing_date_vn(requested_d)
            scope = ScopeDimensions(branch="all", customer_category="b2b")
            svc.match_scope_6dim_bulk(
                dummy_candidates,
                scope,
                gov_date_res.governing_date,
            )

        total_elapsed_ms = (time.perf_counter() - start) * 1000
        avg_per_task_ms = total_elapsed_ms / 100

        # Entire 100 questions must run in < 50ms
        assert total_elapsed_ms < 50.0, f"Total 100 tasks took {total_elapsed_ms:.2f}ms"
        assert avg_per_task_ms < 0.5, f"Avg per task {avg_per_task_ms:.4f}ms exceeded 0.5ms bound"
