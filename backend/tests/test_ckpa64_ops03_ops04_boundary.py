"""Independent QA Boundary Test Suite for CKPA-64 (CRM-G1-SUB15): OPS 03 & OPS 04.

Traceability:
- Jira Issue : CKPA-64 (CRM-G1-SUB15) | Gate G1
- RFP IDs    : OPS 03, OPS 04, DAT 04, DAT 05, DAT 06, DAT 08, VN 01
- G1 ACs     : G1-AC05, G1-AC06
- SoD Notice : Automated QA suite prepared for independent execution and sign-off
               by [S4] Quy Hai on the release patch tag.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.policy.service import PolicyService
from src.modules.selection.schemas import ScopeDimensions
from src.modules.selection.service import SelectionService
from src.shared.contracts import PolicyGateDecision
from src.shared.enums import (
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyLifecycleStatus,
)

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
_BASE_SCOPE = (
    "company=SONGNHAT_HN;branch=HN01;role=sales_executive;"
    "customer_category=b2b;product=3-phase-motor;transaction_scope=quotation"
)


def _dims(
    *,
    company: str | None = "SONGNHAT_HN",
    branch: str | None = "HN01",
    role: str | None = "sales_executive",
    customer_category: str | None = "b2b",
    product: str | None = "3-phase-motor",
    transaction_scope: str | None = "quotation",
) -> ScopeDimensions:
    return ScopeDimensions(
        company=company,
        branch=branch,
        role=role,
        customer_category=customer_category,
        product=product,
        transaction_scope=transaction_scope,
    )


def _candidate(
    *,
    version_id: str | None = None,
    status: PolicyLifecycleStatus = PolicyLifecycleStatus.EFFECTIVE,
    authority_tier: AuthorityTier = AuthorityTier.POLICY,
    effective_from: datetime,
    effective_to: datetime | None = None,
    scope: str = _BASE_SCOPE,
) -> ApplicabilityCandidate:
    return ApplicabilityCandidate(
        version_id=version_id or f"VER-{uuid.uuid4().hex[:8]}",
        authority_tier=authority_tier,
        status=status,
        effective_from=effective_from,
        effective_to=effective_to,
        scope=scope,
    )


def _critical_field(
    *,
    policy_version_id: str,
    field_id: str = "CF-QA-01",
    operator: ComparisonOperator = ComparisonOperator.LE,
    value: str = "5",
    unit: str | None = "%",
    source_clause: str = "Điều 4.1",
    status: PolicyLifecycleStatus = PolicyLifecycleStatus.EFFECTIVE,
) -> CriticalFieldItem:
    return CriticalFieldItem(
        field_id=field_id,
        policy_id="POL-COMM-01",
        policy_version_id=policy_version_id,
        document_version_id="DOC-V1",
        field_name="Hạn mức chiết khấu",
        field_type=CriticalFieldType.NUMBER,
        operator=operator,
        value=value,
        unit=unit,
        currency=None,
        approval_role="sales_manager",
        time_limit="24h",
        exception_condition=None,
        required_documents=["Phiếu đề xuất chiết khấu"],
        source_clause=source_clause,
        status=status,
    )


def _gate_ok(governing_date: date, version_ids: list[str]) -> PolicyGateDecision:
    return PolicyGateDecision(
        governing_date=governing_date,
        timezone="Asia/Ho_Chi_Minh",
        is_historical=False,
        is_future_preview=False,
        applicable_version_ids=tuple(version_ids),
        has_conflict=False,
        can_proceed=True,
    )


@pytest.fixture
def selection_svc() -> SelectionService:
    return SelectionService()


@pytest.fixture
def policy_svc() -> PolicyService:
    return PolicyService()


# ==============================================================================
# SECTION 1: OPS 03 BOUNDARIES (VN TIMEZONE, ROLLOVER, HISTORICAL, FUTURE, HOLD)
# ==============================================================================


class TestOPS03DateAndLifecycleBoundaries:
    """OPS 03 / DAT 04 boundary verification for Asia/Ho_Chi_Minh date resolution."""

    def test_ops03_vn_midnight_235959_vs_000000_handoff(
        self,
        selection_svc: SelectionService,
        policy_svc: PolicyService,
    ) -> None:
        """23:59:59+07:00 ends on day D; 00:00:00+07:00 starts on day D+1 without overlap."""
        v_old = _candidate(
            version_id="VER-NOV14",
            effective_from=datetime(2026, 11, 1, 0, 0, 0, tzinfo=VN_TZ),
            effective_to=datetime(2026, 11, 14, 23, 59, 59, tzinfo=VN_TZ),
        )
        v_new = _candidate(
            version_id="VER-NOV15",
            effective_from=datetime(2026, 11, 15, 0, 0, 0, tzinfo=VN_TZ),
            effective_to=datetime(2026, 11, 30, 23, 59, 59, tzinfo=VN_TZ),
        )
        candidates = [v_old, v_new]

        gate_nov14 = policy_svc.evaluate_policy_gate(
            candidates,
            requested_date=date(2026, 11, 14),
        )
        assert gate_nov14.applicable_version_ids == ("VER-NOV14",)
        assert gate_nov14.has_conflict is False
        assert gate_nov14.can_proceed is True

        gate_nov15 = policy_svc.evaluate_policy_gate(
            candidates,
            requested_date=date(2026, 11, 15),
        )
        assert gate_nov15.applicable_version_ids == ("VER-NOV15",)
        assert gate_nov15.has_conflict is False
        assert gate_nov15.can_proceed is True

        res_nov15 = selection_svc.run_selection(
            candidates=candidates,
            dimensions=_dims(),
            all_critical_fields=[_critical_field(policy_version_id="VER-NOV15")],
            gate_decision=gate_nov15,
            requested_date=date(2026, 11, 15),
        )
        assert res_nov15.applicable_version_ids == ["VER-NOV15"]
        assert res_nov15.hold_decision.must_hold is False
        assert res_nov15.llm_used is False

    def test_ops03_utc_to_vn_date_rollover_165959z_vs_170000z(
        self,
        selection_svc: SelectionService,
        policy_svc: PolicyService,
    ) -> None:
        """16:59:59Z maps to 23:59:59+07:00 (day D); 17:00:00Z maps to 00:00:00+07:00 (day D+1)."""
        # 2026-11-14T16:59:59Z == 2026-11-14T23:59:59+07:00
        # 2026-11-14T17:00:00Z == 2026-11-15T00:00:00+07:00
        v_before_rollover = _candidate(
            version_id="VER-UTC-PRE",
            effective_from=datetime(2026, 11, 1, 0, 0, 0, tzinfo=UTC),
            effective_to=datetime(2026, 11, 14, 16, 59, 59, tzinfo=UTC),
        )
        v_after_rollover = _candidate(
            version_id="VER-UTC-POST",
            effective_from=datetime(2026, 11, 14, 17, 0, 0, tzinfo=UTC),
            effective_to=datetime(2026, 11, 30, 16, 59, 59, tzinfo=UTC),
        )
        candidates = [v_before_rollover, v_after_rollover]

        # On 2026-11-14 (VN): only VER-UTC-PRE is active
        gate_14 = policy_svc.evaluate_policy_gate(
            candidates,
            requested_date=date(2026, 11, 14),
        )
        assert gate_14.applicable_version_ids == ("VER-UTC-PRE",)
        assert gate_14.has_conflict is False

        # On 2026-11-15 (VN): only VER-UTC-POST is active
        gate_15 = policy_svc.evaluate_policy_gate(
            candidates,
            requested_date=date(2026, 11, 15),
        )
        assert gate_15.applicable_version_ids == ("VER-UTC-POST",)
        assert gate_15.has_conflict is False

        sel_15 = selection_svc.run_selection(
            candidates=candidates,
            dimensions=_dims(),
            all_critical_fields=[_critical_field(policy_version_id="VER-UTC-POST")],
            gate_decision=gate_15,
            requested_date=date(2026, 11, 15),
        )
        assert sel_15.governing_date_result.timezone == "Asia/Ho_Chi_Minh"
        assert sel_15.applicable_version_ids == ["VER-UTC-POST"]
        assert sel_15.hold_decision.must_hold is False

    def test_ops03_backdated_historical_superseded_allowed_vs_excluded(
        self,
        selection_svc: SelectionService,
    ) -> None:
        """SUPERSEDED version is allowed for historical date only when allow_historical=True."""
        hist_date = date(2025, 6, 15)
        superseded = _candidate(
            version_id="VER-2025-SUP",
            status=PolicyLifecycleStatus.SUPERSEDED,
            effective_from=datetime(2025, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            effective_to=datetime(2025, 12, 31, 23, 59, 59, tzinfo=VN_TZ),
        )
        cf_sup = _critical_field(
            policy_version_id="VER-2025-SUP",
            status=PolicyLifecycleStatus.SUPERSEDED,
        )
        gate = PolicyGateDecision(
            governing_date=hist_date,
            timezone="Asia/Ho_Chi_Minh",
            is_historical=True,
            is_future_preview=False,
            applicable_version_ids=("VER-2025-SUP",),
            has_conflict=False,
            can_proceed=True,
        )

        # Historical allowed -> SUPERSEDED selected
        res_allowed = selection_svc.run_selection(
            candidates=[superseded],
            dimensions=_dims(),
            all_critical_fields=[cf_sup],
            gate_decision=gate,
            requested_date=hist_date,
            allow_historical=True,
        )
        assert res_allowed.governing_date_result.is_historical is True
        assert res_allowed.applicable_version_ids == ["VER-2025-SUP"]
        assert res_allowed.hold_decision.must_hold is False
        assert res_allowed.llm_used is False

        # Historical disallowed -> SUPERSEDED excluded -> DAT04 Hold
        res_excluded = selection_svc.run_selection(
            candidates=[superseded],
            dimensions=_dims(),
            all_critical_fields=[cf_sup],
            gate_decision=gate,
            requested_date=hist_date,
            allow_historical=False,
        )
        assert res_excluded.applicable_version_ids == []
        assert res_excluded.hold_decision.must_hold is True
        assert any(
            t.code == "DAT04_NO_APPLICABLE_VERSION"
            for t in res_excluded.hold_decision.triggers
        )

    def test_ops03_scheduled_future_version_excluded_when_preview_disabled(
        self,
        selection_svc: SelectionService,
        policy_svc: PolicyService,
    ) -> None:
        """Critical Gate #4 (TAX-11): SCHEDULED version MUST be excluded if preview=False."""
        future_date = date(2028, 6, 1)
        scheduled = _candidate(
            version_id="VER-2028-SCH",
            status=PolicyLifecycleStatus.SCHEDULED,
            effective_from=datetime(2028, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            effective_to=None,
        )
        cf_sch = _critical_field(
            policy_version_id="VER-2028-SCH",
            status=PolicyLifecycleStatus.SCHEDULED,
        )

        # Layer 2 gate with default allow_future_preview=False
        gate_blocked = policy_svc.evaluate_policy_gate(
            [scheduled],
            requested_date=future_date,
            allow_future_preview=False,
        )
        assert gate_blocked.applicable_version_ids == ()
        assert gate_blocked.can_proceed is False

        # Selection layer with allow_future_preview=False -> mandatory Hold
        res_blocked = selection_svc.run_selection(
            candidates=[scheduled],
            dimensions=_dims(),
            all_critical_fields=[cf_sch],
            gate_decision=gate_blocked,
            requested_date=future_date,
            allow_future_preview=False,
        )
        assert res_blocked.applicable_version_ids == []
        assert res_blocked.hold_decision.must_hold is True
        assert any(
            t.code == "DAT04_NO_APPLICABLE_VERSION"
            for t in res_blocked.hold_decision.triggers
        )

        # Explicit allow_future_preview=True permits preview
        gate_preview = policy_svc.evaluate_policy_gate(
            [scheduled],
            requested_date=future_date,
            allow_future_preview=True,
        )
        res_preview = selection_svc.run_selection(
            candidates=[scheduled],
            dimensions=_dims(),
            all_critical_fields=[cf_sch],
            gate_decision=gate_preview,
            requested_date=future_date,
            allow_future_preview=True,
        )
        assert res_preview.applicable_version_ids == ["VER-2028-SCH"]
        assert res_preview.hold_decision.must_hold is False

    def test_ops03_missing_governing_date_and_no_applicable_version_hold(
        self,
        selection_svc: SelectionService,
        policy_svc: PolicyService,
    ) -> None:
        """Missing date uses VN clock; no matching version triggers DAT04 Hold."""
        # Candidate expired in 2024 so it cannot cover today's VN date
        expired = _candidate(
            version_id="VER-EXPIRED-2024",
            effective_from=datetime(2024, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            effective_to=datetime(2024, 12, 31, 23, 59, 59, tzinfo=VN_TZ),
        )
        gate = policy_svc.evaluate_policy_gate([expired], requested_date=None)
        assert gate.can_proceed is False
        assert gate.applicable_version_ids == ()

        res = selection_svc.run_selection(
            candidates=[expired],
            dimensions=_dims(),
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=None,
        )
        assert res.governing_date_result.resolved_from == "system_now"
        assert res.governing_date_result.timezone == "Asia/Ho_Chi_Minh"
        assert res.applicable_version_ids == []
        assert res.hold_decision.must_hold is True
        assert any(
            t.code == "DAT04_NO_APPLICABLE_VERSION"
            for t in res.hold_decision.triggers
        )
        assert res.llm_used is False

    def test_ops03_coverage_gap_between_versions_triggers_dat04_hold(
        self,
        selection_svc: SelectionService,
        policy_svc: PolicyService,
    ) -> None:
        """A governing date inside a gap between effective windows MUST trigger DAT04 Hold."""
        v1 = _candidate(
            version_id="VER-Q1",
            effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            effective_to=datetime(2026, 3, 31, 23, 59, 59, tzinfo=VN_TZ),
        )
        v2 = _candidate(
            version_id="VER-Q3",
            effective_from=datetime(2026, 7, 1, 0, 0, 0, tzinfo=VN_TZ),
            effective_to=datetime(2026, 9, 30, 23, 59, 59, tzinfo=VN_TZ),
        )
        gap_date = date(2026, 5, 15)
        gate = policy_svc.evaluate_policy_gate([v1, v2], requested_date=gap_date)
        res = selection_svc.run_selection(
            candidates=[v1, v2],
            dimensions=_dims(),
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=gap_date,
        )
        assert res.applicable_version_ids == []
        assert res.hold_decision.must_hold is True
        assert any(
            t.code == "DAT04_NO_APPLICABLE_VERSION"
            for t in res.hold_decision.triggers
        )


# ==============================================================================
# SECTION 2: OPS 04 BOUNDARIES (DECIMAL THRESHOLDS, DAT 08 HOLD, DAT 05 CONFLICT)
# ==============================================================================


class TestOPS04DeterministicThresholdAndHoldBoundaries:
    """OPS 04 / DAT 05 / DAT 06 / DAT 08 deterministic verification (0% LLM)."""

    @pytest.mark.parametrize(
        ("operator", "actual", "target", "expected"),
        [
            # LE (<=) exact <, =, >
            (ComparisonOperator.LE, Decimal("4.9999"), "5", True),
            (ComparisonOperator.LE, Decimal("5.0000"), "5", True),
            (ComparisonOperator.LE, Decimal("5.0001"), "5", False),
            # LT (<) exact <, =, >
            (ComparisonOperator.LT, Decimal("49.9999"), "50", True),
            (ComparisonOperator.LT, Decimal("50.0000"), "50", False),
            (ComparisonOperator.LT, Decimal("50.0001"), "50", False),
            # GE (>=) exact <, =, >
            (ComparisonOperator.GE, Decimal("499999999.99"), "500000000", False),
            (ComparisonOperator.GE, Decimal("500000000.00"), "500000000", True),
            (ComparisonOperator.GE, Decimal("500000000.01"), "500000000", True),
            # GT (>) exact <, =, >
            (ComparisonOperator.GT, Decimal("999999999.99"), "1000000000", False),
            (ComparisonOperator.GT, Decimal("1000000000.00"), "1000000000", False),
            (ComparisonOperator.GT, Decimal("1000000000.01"), "1000000000", True),
            # EQ (==) exact <, =, >
            (ComparisonOperator.EQ, Decimal("14.9999"), "15", False),
            (ComparisonOperator.EQ, Decimal("15.0000"), "15", True),
            (ComparisonOperator.EQ, Decimal("15.0001"), "15", False),
            # BETWEEN inclusive lower/upper and just-outside boundaries
            (ComparisonOperator.BETWEEN, Decimal("4.9999"), "5;15", False),
            (ComparisonOperator.BETWEEN, Decimal("5.0000"), "5;15", True),
            (ComparisonOperator.BETWEEN, Decimal("10.0000"), "5;15", True),
            (ComparisonOperator.BETWEEN, Decimal("15.0000"), "5;15", True),
            (ComparisonOperator.BETWEEN, Decimal("15.0001"), "5;15", False),
        ],
    )
    def test_ops04_decimal_thresholds_exact_lt_eq_gt(
        self,
        selection_svc: SelectionService,
        policy_svc: PolicyService,
        operator: ComparisonOperator,
        actual: Decimal,
        target: str,
        expected: bool,
    ) -> None:
        """All 6 deterministic operators match exact <, =, > Decimal boundaries (0% LLM)."""
        assert selection_svc.evaluate_numeric_threshold(operator, actual, target) is expected
        assert policy_svc.evaluate_numeric_threshold(operator, actual, target) is expected

    def test_ops04_formatted_vietnamese_currency_and_unit_strings(
        self,
        selection_svc: SelectionService,
    ) -> None:
        """SelectionService parses formatted VND thousand separators and unit suffixes."""
        assert selection_svc.evaluate_numeric_threshold(
            ComparisonOperator.GE,
            Decimal("500000000"),
            "500.000.000 VND",
        ) is True
        assert selection_svc.evaluate_numeric_threshold(
            ComparisonOperator.LT,
            Decimal("499999999"),
            "500,000,000 VND",
        ) is True
        assert selection_svc.evaluate_numeric_threshold(
            ComparisonOperator.GE,
            Decimal("50"),
            "50 kW",
        ) is True
        assert selection_svc.evaluate_numeric_threshold(
            ComparisonOperator.LE,
            Decimal("5.0"),
            "5%",
        ) is True

    def test_ops04_missing_footnote_clause_triggers_dat08_hold(
        self,
        selection_svc: SelectionService,
    ) -> None:
        """Missing source_clause (footnote/citation) on critical field triggers DAT08 Hold."""
        gov_date = date(2026, 11, 15)
        cand = _candidate(
            version_id="VER-MISSING-FOOTNOTE",
            effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
        )
        cf_no_clause = _critical_field(
            policy_version_id="VER-MISSING-FOOTNOTE",
            source_clause="   ",
        )
        res = selection_svc.run_selection(
            candidates=[cand],
            dimensions=_dims(),
            all_critical_fields=[cf_no_clause],
            gate_decision=_gate_ok(gov_date, ["VER-MISSING-FOOTNOTE"]),
            requested_date=gov_date,
        )
        assert res.hold_decision.must_hold is True
        assert any(
            t.code == "DAT08_MISSING_TABLE_OR_ANNOTATION"
            for t in res.hold_decision.triggers
        )
        assert res.llm_used is False

    def test_ops04_missing_unit_or_attachment_triggers_dat08_hold(
        self,
        selection_svc: SelectionService,
    ) -> None:
        """Missing unit/footnote/essential attachment flag triggers DAT08 Hold."""
        gov_date = date(2026, 11, 15)
        cand = _candidate(
            version_id="VER-MISSING-ATT",
            effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
        )
        cf_no_unit = _critical_field(
            policy_version_id="VER-MISSING-ATT",
            unit=None,
            value="",
        )
        res_empty_val = selection_svc.run_selection(
            candidates=[cand],
            dimensions=_dims(),
            all_critical_fields=[cf_no_unit],
            gate_decision=_gate_ok(gov_date, ["VER-MISSING-ATT"]),
            requested_date=gov_date,
        )
        assert res_empty_val.hold_decision.must_hold is True
        assert any(
            t.code == "DAT08_MISSING_TABLE_OR_ANNOTATION"
            for t in res_empty_val.hold_decision.triggers
        )

        # Valid critical field, but missing essential appendix table / unit footnote
        cf_valid = _critical_field(policy_version_id="VER-MISSING-ATT")
        res_missing_att = selection_svc.run_selection(
            candidates=[cand],
            dimensions=_dims(),
            all_critical_fields=[cf_valid],
            gate_decision=_gate_ok(gov_date, ["VER-MISSING-ATT"]),
            requested_date=gov_date,
            missing_tables_or_attachments=True,
            missing_attachment_detail="Thiếu Phụ lục 02 bảng đơn vị tính và chú thích chiết khấu.",
        )
        assert res_missing_att.hold_decision.must_hold is True
        assert any(
            t.code == "DAT08_MISSING_TABLE_OR_ANNOTATION"
            for t in res_missing_att.hold_decision.triggers
        )
        assert res_missing_att.llm_used is False

    def test_ops04_contract_vs_policy_conflict_same_scope_triggers_dat05_hold(
        self,
        selection_svc: SelectionService,
        policy_svc: PolicyService,
    ) -> None:
        """Customer contract vs policy on matching 6-dim scope MUST trigger DAT05 Hold."""
        gov_date = date(2026, 11, 15)
        c_policy = _candidate(
            version_id="VER-POL-COMM",
            authority_tier=AuthorityTier.POLICY,
            effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            scope=_BASE_SCOPE,
        )
        c_contract = _candidate(
            version_id="VER-CONTRACT-VIP",
            authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
            effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            scope=_BASE_SCOPE,
        )

        gate = policy_svc.evaluate_policy_gate(
            [c_policy, c_contract],
            requested_date=gov_date,
        )
        assert gate.has_conflict is True
        assert gate.can_proceed is False

        res = selection_svc.run_selection(
            candidates=[c_policy, c_contract],
            dimensions=_dims(),
            all_critical_fields=[
                _critical_field(policy_version_id="VER-POL-COMM", field_id="CF-1"),
                _critical_field(policy_version_id="VER-CONTRACT-VIP", field_id="CF-2"),
            ],
            gate_decision=gate,
            requested_date=gov_date,
        )
        assert res.hold_decision.must_hold is True
        assert any(
            t.code == "DAT05_SOURCE_CONFLICT"
            for t in res.hold_decision.triggers
        )
        assert res.llm_used is False

    def test_ops04_disjoint_branch_scopes_do_not_trigger_false_conflict(
        self,
        selection_svc: SelectionService,
    ) -> None:
        """Policy for HN01 and contract for HCM02 MUST NOT trigger false DAT05 conflict."""
        gov_date = date(2026, 11, 15)
        c_hn = _candidate(
            version_id="VER-HN01",
            authority_tier=AuthorityTier.POLICY,
            effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            scope="company=SONGNHAT_HN;branch=HN01;customer_category=b2b",
        )
        c_hcm = _candidate(
            version_id="VER-HCM02",
            authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
            effective_from=datetime(2026, 1, 1, 0, 0, 0, tzinfo=VN_TZ),
            scope="company=SONGNHAT_HN;branch=HCM02;customer_category=b2b",
        )
        res = selection_svc.run_selection(
            candidates=[c_hn, c_hcm],
            dimensions=_dims(branch="HN01"),
            all_critical_fields=[_critical_field(policy_version_id="VER-HN01")],
            gate_decision=_gate_ok(gov_date, ["VER-HN01", "VER-HCM02"]),
            requested_date=gov_date,
        )
        assert res.applicable_version_ids == ["VER-HN01"]
        assert res.hold_decision.must_hold is False
        assert not any(
            t.code == "DAT05_SOURCE_CONFLICT"
            for t in res.hold_decision.triggers
        )
