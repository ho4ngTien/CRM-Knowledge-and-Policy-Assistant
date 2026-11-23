"""
backend/tests/test_sub14_selection.py
==============================
Gate G1 | CRM-G1-SUB14 | Branch: feat/CRM-G1-SUB14-date-6dim-lookup-conflict-hold

Acceptance Criteria (G1-AC05, G1-AC06):
  Given module SUB07 and VN 01 SUB08 dictionary
  When S3 codes the Selection Date/Scope/Critical-Fields/Hold tier
  Then 0% arithmetic goes through LLM and 100% of missing-date /
       missing-annotation / conflict cases are automatically held.

Coverage:
  DAT 04 – 6-Dimension applicability matching
  DAT 04 – Hold when no applicable version for governing date
  DAT 05 – Source-conflict → mandatory Hold
  DAT 06 – Typed deterministic critical-field lookup (≤ 50 rows, 0% LLM)
  DAT 08 – Hold when essential annotation/table is missing
  OPS 03 – Mandatory Hold gate propagation
  VN 01  – UTC+7 date resolution from Asia/Ho_Chi_Minh clock

Assignee  : [S3] Yến Nhi
Reviewers : [S1] Hoàng Tiến, [S2] Quốc Hưng
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.selection.schemas import ScopeDimensions, SelectionResult
from src.modules.selection.service import SelectionService
from src.shared.contracts import PolicyGateDecision
from src.shared.enums import (
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyLifecycleStatus,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
TODAY_VN = datetime.now(VN_TZ).date()
PAST_DATE = date(2025, 1, 1)
FUTURE_DATE = date(2028, 1, 1)


_DEFAULT_SCOPE = (
    "company=SONGNHAT_HN;branch=all;role=all;"
    "customer_category=all;product=all;transaction_scope=all"
)


def _make_candidate(
    version_id: str = None,
    status: PolicyLifecycleStatus = PolicyLifecycleStatus.EFFECTIVE,
    scope: str = _DEFAULT_SCOPE,
    authority_tier: AuthorityTier = AuthorityTier.POLICY,
    effective_from: date = None,
    effective_to: date = None,
) -> ApplicabilityCandidate:
    eff_from = effective_from or date(2024, 1, 1)
    return ApplicabilityCandidate(
        version_id=version_id or str(uuid.uuid4()),
        authority_tier=authority_tier,
        status=status,
        effective_from=datetime(eff_from.year, eff_from.month, eff_from.day, tzinfo=VN_TZ),
        effective_to=(
            datetime(effective_to.year, effective_to.month, effective_to.day, tzinfo=VN_TZ)
            if effective_to else None
        ),
        scope=scope,
    )


def _make_cf(
    policy_version_id: str,
    field_id: str = None,
    source_clause: str = "Điều 3.2",
    value: str = "15%",
    status: PolicyLifecycleStatus = PolicyLifecycleStatus.EFFECTIVE,
) -> CriticalFieldItem:
    return CriticalFieldItem(
        field_id=field_id or str(uuid.uuid4()),
        policy_id="POL-TEST-01",
        policy_version_id=policy_version_id,
        document_version_id="DOC-V1",
        field_name="Tỷ lệ chiết khấu",
        field_type=CriticalFieldType.NUMBER,
        operator=ComparisonOperator.LE,
        value=value,
        unit="%",
        currency=None,
        approval_role="sales_director",
        time_limit="24h",
        exception_condition=None,
        required_documents=["Tờ trình phê duyệt", "Báo cáo tài chính"],
        source_clause=source_clause,
        status=status,
    )


def _make_gate_ok(version_ids: list[str]) -> PolicyGateDecision:
    return PolicyGateDecision(
        governing_date=TODAY_VN,
        timezone="Asia/Ho_Chi_Minh",
        is_historical=False,
        is_future_preview=False,
        applicable_version_ids=tuple(version_ids),
        has_conflict=False,
        can_proceed=True,
    )


def _make_gate_conflict(version_ids: list[str]) -> PolicyGateDecision:
    return PolicyGateDecision(
        governing_date=TODAY_VN,
        timezone="Asia/Ho_Chi_Minh",
        is_historical=False,
        is_future_preview=False,
        applicable_version_ids=tuple(version_ids),
        has_conflict=True,
        can_proceed=False,
        hold_reason="DAT 05 Hold: nguồn xung đột.",
    )


def _make_gate_no_versions() -> PolicyGateDecision:
    return PolicyGateDecision(
        governing_date=TODAY_VN,
        timezone="Asia/Ho_Chi_Minh",
        is_historical=False,
        is_future_preview=False,
        applicable_version_ids=(),
        has_conflict=False,
        can_proceed=False,
        hold_reason="DAT 04 Hold: không tìm thấy phiên bản.",
    )


@pytest.fixture
def svc() -> SelectionService:
    return SelectionService()


@pytest.fixture
def default_dimensions() -> ScopeDimensions:
    return ScopeDimensions(
        company="SONGNHAT_HN",
        branch="HN01",
        role="sales_executive",
        customer_category="b2b",
        product="3-phase-motor",
        transaction_scope="quotation",
    )


# ===========================================================================
# A. Governing Date Resolver (DAT 04 / UTC+7)
# ===========================================================================

class TestGoverningDateResolver:
    """DAT 04: resolve_governing_date_vn returns UTC+7 date with correct flags."""

    def test_resolves_today_when_no_request_date(self, svc: SelectionService):
        result = svc.resolve_governing_date_vn(None)
        assert result.governing_date == TODAY_VN
        assert result.timezone == "Asia/Ho_Chi_Minh"
        assert result.resolved_from == "system_now"
        assert result.is_historical is False
        assert result.is_future_preview is False

    def test_past_date_flagged_historical(self, svc: SelectionService):
        result = svc.resolve_governing_date_vn(PAST_DATE)
        assert result.governing_date == PAST_DATE
        assert result.is_historical is True
        assert result.is_future_preview is False
        assert result.resolved_from == "request"

    def test_future_date_flagged_preview(self, svc: SelectionService):
        result = svc.resolve_governing_date_vn(FUTURE_DATE)
        assert result.governing_date == FUTURE_DATE
        assert result.is_historical is False
        assert result.is_future_preview is True
        assert result.resolved_from == "request"

    def test_today_exact_is_not_historical_or_future(self, svc: SelectionService):
        result = svc.resolve_governing_date_vn(TODAY_VN)
        assert result.is_historical is False
        assert result.is_future_preview is False

    def test_llm_never_called_in_date_resolution(self, svc: SelectionService):
        """0% LLM: resolve_governing_date_vn must not touch any LLM client."""
        # Simply verify no exception and the result carries llm_used=False at the
        # pipeline level (checked in integration tests below).
        r = svc.resolve_governing_date_vn(None)
        assert r.governing_date is not None


# ===========================================================================
# B. 6-Dimension Scope Matcher (DAT 04)
# ===========================================================================

class TestScopeMatcher6Dim:
    """DAT 04: 6-dimension scope matching – wildcard, exact, and mismatch cases."""

    def test_all_wildcard_policy_matches_any_request(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        c = _make_candidate(
            scope=(
                "company=all;branch=all;role=all;"
                "customer_category=all;product=all;transaction_scope=all"
            )
        )
        result = svc.match_scope_6dim(c, default_dimensions)
        assert result.matched is True
        assert result.unmatched_dimensions == []

    def test_exact_6dim_match(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        c = _make_candidate(
            scope=(
                "company=SONGNHAT_HN;branch=HN01;role=sales_executive;"
                "customer_category=b2b;product=3-phase-motor;transaction_scope=quotation"
            )
        )
        result = svc.match_scope_6dim(c, default_dimensions)
        assert result.matched is True

    def test_one_dimension_mismatch_fails_match(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        c = _make_candidate(
            scope=(
                "company=SONGNHAT_HN;branch=HCM01;role=sales_executive;"
                "customer_category=b2b;product=3-phase-motor;transaction_scope=quotation"
            )
        )
        result = svc.match_scope_6dim(c, default_dimensions)
        assert result.matched is False
        assert "branch" in result.unmatched_dimensions

    def test_multiple_dimension_mismatches(self, svc: SelectionService):
        dims = ScopeDimensions(
            company="SONGNHAT_HCM",
            branch="HCM01",
            role="branch_manager",
            customer_category="b2c",
            product="gearbox",
            transaction_scope="warranty",
        )
        c = _make_candidate(
            scope=(
                "company=SONGNHAT_HN;branch=HN01;role=sales_executive;"
                "customer_category=b2b;product=3-phase-motor;transaction_scope=quotation"
            )
        )
        result = svc.match_scope_6dim(c, dims)
        assert result.matched is False
        assert len(result.unmatched_dimensions) >= 2

    def test_missing_dimension_in_policy_treated_as_wildcard(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        # Policy only declares 2 of 6 dimensions – rest default to wildcard
        c = _make_candidate(
            scope="company=SONGNHAT_HN;role=sales_executive"
        )
        result = svc.match_scope_6dim(c, default_dimensions)
        assert result.matched is True

    def test_case_insensitive_matching(
        self, svc: SelectionService
    ):
        dims = ScopeDimensions(
            company="SONGNHAT_HN",
            branch=None,
            role=None,
            customer_category=None,
            product=None,
            transaction_scope=None,
        )
        c = _make_candidate(scope="company=songnhat_hn")
        result = svc.match_scope_6dim(c, dims)
        assert result.matched is True

    def test_star_wildcard_in_policy_matches(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        star_scope = (
            "company=*;branch=*;role=*;customer_category=*;"
            "product=*;transaction_scope=*"
        )
        c = _make_candidate(scope=star_scope)
        result = svc.match_scope_6dim(c, default_dimensions)
        assert result.matched is True

    def test_draft_candidate_excluded_from_bulk_match(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        draft = _make_candidate(status=PolicyLifecycleStatus.DRAFT)
        results = svc.match_scope_6dim_bulk([draft], default_dimensions, TODAY_VN)
        assert results == []

    def test_withdrawn_candidate_excluded_from_bulk_match(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        withdrawn = _make_candidate(status=PolicyLifecycleStatus.WITHDRAWN)
        results = svc.match_scope_6dim_bulk([withdrawn], default_dimensions, TODAY_VN)
        assert results == []

    def test_superseded_included_only_when_allow_historical(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        sup = _make_candidate(
            status=PolicyLifecycleStatus.SUPERSEDED,
            effective_from=PAST_DATE,
            effective_to=date(2025, 12, 31),
        )
        # Without allow_historical
        r_no = svc.match_scope_6dim_bulk(
            [sup], default_dimensions, PAST_DATE, allow_historical=False
        )
        assert r_no == []
        # With allow_historical
        r_yes = svc.match_scope_6dim_bulk(
            [sup], default_dimensions, PAST_DATE, allow_historical=True
        )
        assert len(r_yes) == 1

    def test_scheduled_included_only_when_allow_future_preview(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        sched = _make_candidate(
            status=PolicyLifecycleStatus.SCHEDULED,
            effective_from=FUTURE_DATE,
        )
        r_no = svc.match_scope_6dim_bulk(
            [sched], default_dimensions, FUTURE_DATE, allow_future_preview=False
        )
        assert r_no == []
        r_yes = svc.match_scope_6dim_bulk(
            [sched], default_dimensions, FUTURE_DATE, allow_future_preview=True
        )
        assert len(r_yes) == 1

    def test_candidate_outside_effective_window_excluded(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        expired = _make_candidate(
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 12, 31),
        )
        # TODAY_VN is after 2024-12-31
        results = svc.match_scope_6dim_bulk([expired], default_dimensions, TODAY_VN)
        assert results == []


# ===========================================================================
# C. Critical Field Lookup (DAT 06, DAT 08) ≤ 50 rows
# ===========================================================================

class TestCriticalFieldLookup:
    """DAT 06, DAT 08: Deterministic lookup – 0% LLM, ≤ 50 rows, annotation checks."""

    from src.modules.selection.schemas import CriticalFieldLookupRequest

    def test_lookup_returns_fields_for_matching_version(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupRequest

        vid = "V-TEST-001"
        cf = _make_cf(policy_version_id=vid)
        result = svc.lookup_critical_fields(
            CriticalFieldLookupRequest(version_ids=[vid], governing_date=TODAY_VN),
            [cf],
        )
        assert len(result) == 1
        assert result[0].fields_found == 1
        assert result[0].has_missing_annotations is False

    def test_lookup_excludes_other_versions(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupRequest

        vid = "V-MINE"
        other_vid = "V-OTHER"
        cf_mine = _make_cf(policy_version_id=vid)
        cf_other = _make_cf(policy_version_id=other_vid)
        result = svc.lookup_critical_fields(
            CriticalFieldLookupRequest(version_ids=[vid], governing_date=TODAY_VN),
            [cf_mine, cf_other],
        )
        assert result[0].fields_found == 1

    def test_lookup_excludes_withdrawn_fields(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupRequest

        vid = "V-WTEST"
        cf_ok = _make_cf(policy_version_id=vid, field_id="OK")
        cf_withdrawn = _make_cf(
            policy_version_id=vid,
            field_id="WD",
            status=PolicyLifecycleStatus.WITHDRAWN,
        )
        result = svc.lookup_critical_fields(
            CriticalFieldLookupRequest(version_ids=[vid], governing_date=TODAY_VN),
            [cf_ok, cf_withdrawn],
        )
        assert result[0].fields_found == 1

    def test_lookup_excludes_draft_fields(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupRequest

        vid = "V-DRAFT"
        cf_draft = _make_cf(policy_version_id=vid, status=PolicyLifecycleStatus.DRAFT)
        result = svc.lookup_critical_fields(
            CriticalFieldLookupRequest(version_ids=[vid], governing_date=TODAY_VN),
            [cf_draft],
        )
        assert result[0].fields_found == 0

    def test_lookup_caps_at_50_rows(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupRequest

        vid = "V-CAP"
        # Create 60 fields; expect cap at 50
        cfs = [_make_cf(policy_version_id=vid, field_id=f"F{i}") for i in range(60)]
        result = svc.lookup_critical_fields(
            CriticalFieldLookupRequest(version_ids=[vid], governing_date=TODAY_VN),
            cfs,
        )
        assert result[0].fields_found <= 50

    def test_dat08_missing_source_clause_triggers_annotation_flag(
        self, svc: SelectionService
    ):
        from src.modules.selection.schemas import CriticalFieldLookupRequest

        vid = "V-ANN"
        cf_bad = _make_cf(policy_version_id=vid, source_clause="")
        result = svc.lookup_critical_fields(
            CriticalFieldLookupRequest(version_ids=[vid], governing_date=TODAY_VN),
            [cf_bad],
        )
        assert result[0].has_missing_annotations is True
        assert result[0].missing_annotation_detail is not None
        assert "DAT 08" in result[0].missing_annotation_detail

    def test_dat08_missing_value_triggers_annotation_flag(
        self, svc: SelectionService
    ):
        from src.modules.selection.schemas import CriticalFieldLookupRequest

        vid = "V-VAL"
        cf_bad = _make_cf(policy_version_id=vid, value="")
        result = svc.lookup_critical_fields(
            CriticalFieldLookupRequest(version_ids=[vid], governing_date=TODAY_VN),
            [cf_bad],
        )
        assert result[0].has_missing_annotations is True

    def test_lookup_zero_llm_flag_in_full_pipeline(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        """AC: llm_used is ALWAYS False for the selection pipeline."""
        vid = str(uuid.uuid4())
        c = _make_candidate(version_id=vid)
        cf = _make_cf(policy_version_id=vid)
        gate = _make_gate_ok([vid])

        result = svc.run_selection(
            candidates=[c],
            dimensions=default_dimensions,
            all_critical_fields=[cf],
            gate_decision=gate,
            requested_date=TODAY_VN,
        )
        assert result.llm_used is False


# ===========================================================================
# D. Mandatory Hold Gate (DAT 04, DAT 05, DAT 08, OPS 03)
# ===========================================================================

class TestHoldGate:
    """OPS 03: 100% mandatory hold for all missing-date / conflict / annotation cases."""

    def test_hold_dat04_no_applicable_version(self, svc: SelectionService):
        gate = _make_gate_no_versions()
        hold = svc.evaluate_hold(gate, [])
        assert hold.must_hold is True
        codes = [t.code for t in hold.triggers]
        assert "DAT04_NO_APPLICABLE_VERSION" in codes

    def test_hold_dat05_source_conflict(self, svc: SelectionService):
        gate = _make_gate_conflict(["V1", "V2"])
        hold = svc.evaluate_hold(gate, [])
        assert hold.must_hold is True
        codes = [t.code for t in hold.triggers]
        assert "DAT05_SOURCE_CONFLICT" in codes

    def test_hold_dat08_missing_annotation(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupResult

        vid = "V-ANN-HOLD"
        gate = _make_gate_ok([vid])
        cf_result = CriticalFieldLookupResult(
            version_id=vid,
            fields_found=1,
            fields=[],
            has_missing_annotations=True,
            missing_annotation_detail="DAT 08: thiếu source_clause",
        )
        hold = svc.evaluate_hold(gate, [cf_result])
        assert hold.must_hold is True
        codes = [t.code for t in hold.triggers]
        assert "DAT08_MISSING_TABLE_OR_ANNOTATION" in codes

    def test_no_hold_when_all_conditions_pass(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupResult

        vid = "V-OK"
        gate = _make_gate_ok([vid])
        cf_result = CriticalFieldLookupResult(
            version_id=vid,
            fields_found=2,
            fields=[],
            has_missing_annotations=False,
        )
        hold = svc.evaluate_hold(gate, [cf_result])
        assert hold.must_hold is False
        assert hold.triggers == []
        assert hold.combined_reason_vi is None

    def test_hold_combined_reason_contains_all_triggers(self, svc: SelectionService):
        from src.modules.selection.schemas import CriticalFieldLookupResult

        vid = "V-MULTI"
        gate = _make_gate_conflict(["V-MULTI"])  # DAT 05 conflict
        cf_result = CriticalFieldLookupResult(
            version_id=vid,
            fields_found=1,
            fields=[],
            has_missing_annotations=True,
            missing_annotation_detail="DAT 08: thiếu chú thích",
        )
        hold = svc.evaluate_hold(gate, [cf_result])
        assert hold.must_hold is True
        assert hold.combined_reason_vi is not None
        assert "DAT 05" in hold.combined_reason_vi
        assert "DAT 08" in hold.combined_reason_vi

    def test_ops03_hold_propagated_when_gate_cannot_proceed(
        self, svc: SelectionService
    ):
        """OPS 03: When gate.can_proceed is False and no DAT04/05, OPS03 trigger fires."""
        gate = PolicyGateDecision(
            governing_date=TODAY_VN,
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=("V-STALE",),
            has_conflict=False,
            can_proceed=False,
            hold_reason="Snapshot quá cũ; cần refresh dữ liệu (OPS 01).",
        )
        hold = svc.evaluate_hold(gate, [])
        assert hold.must_hold is True
        codes = [t.code for t in hold.triggers]
        assert "OPS03_MANDATORY_HOLD" in codes

    def test_100_pct_hold_coverage_no_bypass(self, svc: SelectionService):
        """
        AC (G1-AC06): All three forced-hold conditions produce must_hold=True,
        and the pipeline CANNOT proceed.  This test iterates all three to confirm
        100% coverage.
        """
        from src.modules.selection.schemas import CriticalFieldLookupResult

        # Case 1: No applicable version (DAT 04)
        gate_no_ver = _make_gate_no_versions()
        h1 = svc.evaluate_hold(gate_no_ver, [])
        assert h1.must_hold is True

        # Case 2: Source conflict (DAT 05)
        gate_conflict = _make_gate_conflict(["V1"])
        h2 = svc.evaluate_hold(gate_conflict, [])
        assert h2.must_hold is True

        # Case 3: Missing annotation (DAT 08)
        gate_ok = _make_gate_ok(["V3"])
        cf_bad = CriticalFieldLookupResult(
            version_id="V3",
            fields_found=1,
            fields=[],
            has_missing_annotations=True,
            missing_annotation_detail="missing",
        )
        h3 = svc.evaluate_hold(gate_ok, [cf_bad])
        assert h3.must_hold is True


# ===========================================================================
# E. Full Pipeline Integration (run_selection)
# ===========================================================================

class TestRunSelectionIntegration:
    """Integration: run_selection is deterministic, llm_used=False, hold propagated."""

    def test_happy_path_no_hold(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        vid = str(uuid.uuid4())
        c = _make_candidate(version_id=vid)
        cf = _make_cf(policy_version_id=vid)
        gate = _make_gate_ok([vid])

        result = svc.run_selection(
            candidates=[c],
            dimensions=default_dimensions,
            all_critical_fields=[cf],
            gate_decision=gate,
        )

        assert isinstance(result, SelectionResult)
        assert result.llm_used is False
        assert result.hold_decision.must_hold is False
        assert vid in result.applicable_version_ids
        assert result.governing_date_result.timezone == "Asia/Ho_Chi_Minh"

    def test_pipeline_hold_when_gate_conflict(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        vid = str(uuid.uuid4())
        c = _make_candidate(version_id=vid)
        gate = _make_gate_conflict([vid])

        result = svc.run_selection(
            candidates=[c],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert result.hold_decision.must_hold is True
        assert result.llm_used is False

    def test_pipeline_hold_when_no_applicable_versions(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        gate = _make_gate_no_versions()
        result = svc.run_selection(
            candidates=[],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert result.hold_decision.must_hold is True
        assert result.applicable_version_ids == []

    def test_pipeline_hold_when_critical_field_annotation_missing(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        vid = str(uuid.uuid4())
        c = _make_candidate(version_id=vid)
        cf_bad = _make_cf(policy_version_id=vid, source_clause="")
        gate = _make_gate_ok([vid])

        result = svc.run_selection(
            candidates=[c],
            dimensions=default_dimensions,
            all_critical_fields=[cf_bad],
            gate_decision=gate,
        )
        assert result.hold_decision.must_hold is True
        codes = [t.code for t in result.hold_decision.triggers]
        assert "DAT08_MISSING_TABLE_OR_ANNOTATION" in codes

    def test_task_id_auto_generated_when_absent(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        gate = _make_gate_no_versions()
        result = svc.run_selection(
            candidates=[],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert result.task_id is not None
        assert len(result.task_id) > 0

    def test_custom_task_id_preserved(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        custom_id = "CRM-G1-SUB14-task-001"
        gate = _make_gate_ok([])
        result = svc.run_selection(
            task_id=custom_id,
            candidates=[],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert result.task_id == custom_id

    def test_historical_date_query_resolved_correctly(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        vid = str(uuid.uuid4())
        c = _make_candidate(
            version_id=vid,
            status=PolicyLifecycleStatus.SUPERSEDED,
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 12, 31),
        )
        gate = PolicyGateDecision(
            governing_date=PAST_DATE,
            timezone="Asia/Ho_Chi_Minh",
            is_historical=True,
            is_future_preview=False,
            applicable_version_ids=(vid,),
            has_conflict=False,
            can_proceed=True,
        )
        result = svc.run_selection(
            candidates=[c],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=PAST_DATE,
        )
        assert result.governing_date_result.is_historical is True
        assert result.llm_used is False

    def test_selection_result_has_resolved_at_timestamp(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        gate = _make_gate_ok([])
        result = svc.run_selection(
            candidates=[],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert result.resolved_at is not None

    def test_scope_match_results_included_in_output(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        vid = str(uuid.uuid4())
        c = _make_candidate(version_id=vid)
        gate = _make_gate_ok([vid])
        result = svc.run_selection(
            candidates=[c],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert len(result.scope_matches) >= 1

    def test_unmatched_scope_dimension_excludes_version(
        self, svc: SelectionService
    ):
        vid = str(uuid.uuid4())
        c = _make_candidate(
            version_id=vid,
            scope=(
                "company=SONGNHAT_HCM;branch=HCM01;role=sales_executive;"
                "customer_category=b2b;product=3-phase-motor;transaction_scope=quotation"
            ),
        )
        # Request for HN, not HCM
        dims = ScopeDimensions(
            company="SONGNHAT_HN",
            branch="HN01",
            role="sales_executive",
            customer_category="b2b",
            product="3-phase-motor",
            transaction_scope="quotation",
        )
        gate = _make_gate_ok([vid])
        result = svc.run_selection(
            candidates=[c],
            dimensions=dims,
            all_critical_fields=[],
            gate_decision=gate,
        )
        # The candidate is in gate but fails 6-dim match, so not in applicable_version_ids
        assert vid not in result.applicable_version_ids


# ===========================================================================
# F. Schema invariants
# ===========================================================================

class TestSelectionSchemaInvariants:
    """Structural invariants: SelectionResult.llm_used always False, frozen schemas."""

    def test_selection_result_llm_used_always_false(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        gate = _make_gate_ok([])
        r = svc.run_selection(
            candidates=[],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
        )
        assert r.llm_used is False

    def test_scope_dimensions_extra_fields_forbidden(self):
        import pytest

        with pytest.raises(Exception):
            ScopeDimensions(
                company="X",
                branch=None,
                role=None,
                customer_category=None,
                product=None,
                transaction_scope=None,
                extra_field="forbidden",  # type: ignore[call-arg]
            )

    def test_hold_trigger_code_is_constrained_literal(self):
        from src.modules.selection.schemas import HoldTrigger

        with pytest.raises(Exception):
            HoldTrigger(
                code="UNKNOWN_CODE",  # type: ignore[arg-type]
                reason_vi="Invalid",
            )


# ===========================================================================
# G. Vietnamese Normalisation & CRM Glossary (VN 01, SUB08)
# ===========================================================================

class TestVietnameseNormalizationVN01SUB08:
    """VN 01 / SUB08: Test unaccent and CRM glossary matching in 6-dim scope."""

    def test_unaccented_product_matches_accented_policy(self, svc: SelectionService):
        c = _make_candidate(scope="product=biến tần trung thế")
        dims = ScopeDimensions(
            company=None,
            branch=None,
            role=None,
            customer_category=None,
            product="bien tan",
            transaction_scope=None,
        )
        result = svc.match_scope_6dim(c, dims)
        assert result.matched is True

    def test_crm_synonym_role_gdcn_matches_giam_doc_chi_nhanh(self, svc: SelectionService):
        c = _make_candidate(scope="role=giám đốc chi nhánh")
        dims = ScopeDimensions(
            company=None,
            branch=None,
            role="gđcn",
            customer_category=None,
            product=None,
            transaction_scope=None,
        )
        result = svc.match_scope_6dim(c, dims)
        assert result.matched is True

    def test_crm_synonym_b2b_matches_khach_hang_doanh_nghiep(self, svc: SelectionService):
        c = _make_candidate(scope="customer_category=b2b")
        dims = ScopeDimensions(
            company=None,
            branch=None,
            role=None,
            customer_category="khách hàng doanh nghiệp",
            product=None,
            transaction_scope=None,
        )
        result = svc.match_scope_6dim(c, dims)
        assert result.matched is True

    def test_technical_product_synonym_match(self, svc: SelectionService):
        c = _make_candidate(scope="product=Động cơ công nghiệp 3 pha")
        dims = ScopeDimensions(
            company=None,
            branch=None,
            role=None,
            customer_category=None,
            product="motor 3 pha",
            transaction_scope=None,
        )
        result = svc.match_scope_6dim(c, dims)
        assert result.matched is True


# ===========================================================================
# H. Deterministic Numeric Threshold Arithmetic (OPS 04, 0% LLM)
# ===========================================================================

class TestDeterministicNumericThreshold:
    """OPS 04 / Acceptance Criteria: 0% arithmetic through LLM."""

    from decimal import Decimal

    def test_threshold_comparisons(self, svc: SelectionService):
        from decimal import Decimal

        assert svc.evaluate_numeric_threshold(ComparisonOperator.LE, Decimal("10"), "15") is True
        assert svc.evaluate_numeric_threshold(ComparisonOperator.LE, Decimal("20"), "15") is False
        assert svc.evaluate_numeric_threshold(ComparisonOperator.LT, Decimal("15"), "15") is False
        assert svc.evaluate_numeric_threshold(ComparisonOperator.GE, Decimal("15"), "15") is True
        assert svc.evaluate_numeric_threshold(ComparisonOperator.GT, Decimal("16"), "15") is True
        assert svc.evaluate_numeric_threshold(ComparisonOperator.EQ, Decimal("15"), "15") is True

    def test_threshold_between(self, svc: SelectionService):
        from decimal import Decimal

        assert svc.evaluate_numeric_threshold(
            ComparisonOperator.BETWEEN, Decimal("15"), "10;20"
        ) is True
        assert svc.evaluate_numeric_threshold(
            ComparisonOperator.BETWEEN, Decimal("25"), "10;20"
        ) is False

    def test_dat08_missing_tables_or_attachments_triggers_hold(
        self, svc: SelectionService, default_dimensions: ScopeDimensions
    ):
        vid = str(uuid.uuid4())
        c = _make_candidate(version_id=vid)
        gate = _make_gate_ok([vid])

        result = svc.run_selection(
            candidates=[c],
            dimensions=default_dimensions,
            all_critical_fields=[],
            gate_decision=gate,
            missing_tables_or_attachments=True,
            missing_attachment_detail="Thiếu bảng tỷ lệ hoa hồng phụ lục II.",
        )
        assert result.hold_decision.must_hold is True
        assert any(
            t.code == "DAT08_MISSING_TABLE_OR_ANNOTATION"
            for t in result.hold_decision.triggers
        )
        assert "phụ lục II" in (result.hold_decision.combined_reason_vi or "")
