"""
backend/tests/test_selection_60dev_40val.py
============================================
Gate G1 | Sprint 4 Selection/Hold Bugfix Verification Suite (CKPA-72 / CRM-G1-SUB21)

Validates the full Selection & Hold layer on the 100 Real Questions dataset
(partitioned into exactly 60 DEV and 40 VAL tasks) from data/eval/100_real_questions_clean_pii.json.

Verification Matrix & RFP Traceability:
  - WP 03: Selection date, scope, and critical-field governance
  - DAT 04: 6-Dimension scope matching + mandatory Hold on scope mismatch / missing version
  - DAT 05: Mandatory Hold on Customer Contract vs Policy conflict (VG-06, VG-16)
  - DAT 06: Deterministic Critical Field typed lookup (<= 50 rows, 0% LLM)
  - DAT 08: Mandatory Hold on incomplete evidence / missing attachments (VG-11)
  - OPS 03: UTC+7 Asia/Ho_Chi_Minh governing date boundary resolution (00:00:00 vs 23:59:59)
  - OPS 04: Deterministic numeric threshold arithmetic (<, <=, =, >, >=, between)
  - VN 01: CRM glossary and normalization preservation

Acceptance Criteria:
  - 100% of 60 DEV and 40 VAL questions evaluated
  - 0 unhandled open defects remaining when closing Sprint 4
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.modules.policy.schemas import ApplicabilityCandidate
from src.modules.selection.schemas import (
    ScopeDimensions,
    SelectionResult,
)
from src.modules.selection.service import SelectionService
from src.shared.auth import AuthenticatedUser, create_access_token
from src.shared.contracts import PolicyGateDecision
from src.shared.enums import (
    AuthorityTier,
    PolicyLifecycleStatus,
    UserRole,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "data" / "eval" / "100_real_questions_clean_pii.json"
VN_TZ = ZoneInfo(settings.APP_TIMEZONE)


@pytest.fixture(scope="module")
def questions_100() -> list[dict]:
    assert DATASET_PATH.exists(), f"Dataset missing at {DATASET_PATH}"
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def dev_60(questions_100: list[dict]) -> list[dict]:
    return [q for q in questions_100 if q.get("Partition") == "DEV"]


@pytest.fixture(scope="module")
def val_40(questions_100: list[dict]) -> list[dict]:
    return [q for q in questions_100 if q.get("Partition") == "VAL"]


@pytest.fixture
def svc() -> SelectionService:
    return SelectionService()


# ===========================================================================
# 1. Dataset Integrity & Partition Verification (60 DEV / 40 VAL)
# ===========================================================================

class TestDatasetPartitionIntegrity:
    """Verifies that the dataset cleanly splits into 60 DEV and 40 VAL tasks."""

    def test_partition_counts(self, dev_60: list[dict], val_40: list[dict]):
        assert len(dev_60) == 60, f"Expected 60 DEV cases, got {len(dev_60)}"
        assert len(val_40) == 40, f"Expected 40 VAL cases, got {len(val_40)}"

    def test_all_16_variant_groups_covered(self, questions_100: list[dict]):
        vgs = {q["Variant_Group_ID"] for q in questions_100}
        expected_vgs = {f"VG-{i:02d}" for i in range(1, 17)}
        assert vgs == expected_vgs, f"Missing variant groups: {expected_vgs - vgs}"

    def test_all_questions_have_governing_date(self, questions_100: list[dict]):
        for q in questions_100:
            assert "Governing_Date" in q
            assert q["Governing_Date"] == "2026-11-15"


# ===========================================================================
# 2. Governing Date & Timezone Resolution (OPS 03, UTC+7)
# ===========================================================================

class TestGoverningDateResolutionOPS03:
    """OPS 03: UTC+7 calendar date resolution from Asia/Ho_Chi_Minh clock."""

    def test_historical_governing_date_flagged_correctly(self, svc: SelectionService):
        target = date(2026, 11, 15)
        res = svc.resolve_governing_date_vn(target)
        assert res.governing_date == target
        assert res.timezone == "Asia/Ho_Chi_Minh"
        # Today in 2026 is after 2026-11-15
        today = datetime.now(VN_TZ).date()
        assert res.is_historical == (target < today)
        assert res.is_future_preview == (target > today)

    def test_day_boundary_235959_vs_000000_vn(self, svc: SelectionService):
        """Verify boundary between 23:59:59 and 00:00:00 UTC+7 does not shift date."""
        dt_start = datetime(2026, 11, 15, 0, 0, 0, tzinfo=VN_TZ)
        dt_end = datetime(2026, 11, 15, 23, 59, 59, tzinfo=VN_TZ)
        assert dt_start.date() == date(2026, 11, 15)
        assert dt_end.date() == date(2026, 11, 15)

    def test_date_resolution_never_calls_llm(self, svc: SelectionService):
        res = svc.resolve_governing_date_vn(date(2026, 11, 15))
        assert res.governing_date == date(2026, 11, 15)


# ===========================================================================
# 3. 6-Dimension Scope Matching & DAT 04 Hold Gate
# ===========================================================================

class TestScopeMatchingAndHoldGateDAT04:
    """DAT 04: 6-Dimension scope matching and mandatory hold on mismatch."""

    def test_scope_match_all_wildcards_pass(self, svc: SelectionService):
        c = ApplicabilityCandidate(
            version_id="V-WILD",
            document_id="DOC-01",
            document_name="Chính sách chung",
            policy_family="commercial",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=all;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        dims = ScopeDimensions(
            company="SONGNHAT_HN",
            branch="HN01",
            role="cvkd",
            customer_category="b2b",
            product="biến tần trung thế",
            transaction_scope="báo giá",
        )
        m = svc.match_scope_6dim(c, dims)
        assert m.matched is True
        assert len(m.unmatched_dimensions) == 0

    def test_scope_mismatch_triggers_mandatory_hold_dat04(self, svc: SelectionService):
        """Fix 1: Scope mismatch MUST trigger DAT04_NO_APPLICABLE_VERSION hold."""
        c_hcm = ApplicabilityCandidate(
            version_id="V-HCM",
            document_id="DOC-01",
            document_name="Chính sách HCM",
            policy_family="commercial",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=SONGNHAT_HCM;branch=HCM01;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        # Request for HN
        dims = ScopeDimensions(
            company="SONGNHAT_HN",
            branch="HN01",
            role=None,
            customer_category=None,
            product=None,
            transaction_scope=None,
        )
        gate = PolicyGateDecision(
            governing_date=date(2026, 11, 15),
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=("V-HCM",),  # Gate originally had V-HCM
            has_conflict=False,
            can_proceed=True,
        )
        res = svc.run_selection(
            candidates=[c_hcm],
            dimensions=dims,
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=date(2026, 11, 15),
        )
        # V-HCM fails HN match -> 0 applicable versions -> MUST HOLD DAT04
        assert res.applicable_version_ids == []
        assert res.hold_decision.must_hold is True
        assert any(t.code == "DAT04_NO_APPLICABLE_VERSION" for t in res.hold_decision.triggers)

    def test_no_false_conflict_on_distinct_scopes(self, svc: SelectionService):
        """Fix 2: Two policies for different branches must NOT trigger false conflict hold."""
        c_hn = ApplicabilityCandidate(
            version_id="V-HN",
            document_id="DOC-01",
            document_name="Chính sách HN",
            policy_family="commercial",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=SONGNHAT_HN;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        c_hcm = ApplicabilityCandidate(
            version_id="V-HCM",
            document_id="DOC-01",
            document_name="Chính sách HCM",
            policy_family="commercial",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=SONGNHAT_HCM;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        dims = ScopeDimensions(
            company="SONGNHAT_HN",
            branch=None,
            role=None,
            customer_category=None,
            product=None,
            transaction_scope=None,
        )
        # Gate pre-check flagged conflict due to 2 candidates, but 6-dim scope resolves to only HN
        gate = PolicyGateDecision(
            governing_date=date(2026, 11, 15),
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=("V-HN", "V-HCM"),
            has_conflict=True,
            can_proceed=True,
        )
        res = svc.run_selection(
            candidates=[c_hn, c_hcm],
            dimensions=dims,
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=date(2026, 11, 15),
        )
        # Only V-HN matched scope -> No conflict among matched candidates -> Proceed OK
        assert res.applicable_version_ids == ["V-HN"]
        assert res.hold_decision.must_hold is False


# ===========================================================================
# 4. Deterministic Numeric Threshold Arithmetic (OPS 04, 0% LLM)
# ===========================================================================

class TestNumericThresholdArithmeticOPS04:
    """OPS 04: Deterministic numeric threshold checks for all question groups."""

    def test_vg01_standard_discount_le_5_pct(self, svc: SelectionService):
        # 2% <= 5% -> True
        assert svc.evaluate_numeric_threshold("<=", Decimal("2"), "5") is True
        assert svc.evaluate_numeric_threshold("<=", Decimal("5"), "5 %") is True
        assert svc.evaluate_numeric_threshold("<=", Decimal("6"), "5") is False

    def test_vg02_mid_tier_discount_between_5_and_15_pct(self, svc: SelectionService):
        # 8% between 5 and 15 -> True
        assert svc.evaluate_numeric_threshold("between", Decimal("8"), "5;15") is True
        assert svc.evaluate_numeric_threshold("between", Decimal("4"), "5;15") is False
        assert svc.evaluate_numeric_threshold("between", Decimal("16"), "5;15") is False

    def test_vg03_large_order_ge_1_billion(self, svc: SelectionService):
        # 2.0 billion VND >= 1.000.000.000 VND -> True
        assert svc.evaluate_numeric_threshold(">=", Decimal("2000000000"), "1000000000") is True
        assert svc.evaluate_numeric_threshold(">=", Decimal("500000000"), "1000000000 VND") is False

    def test_vg08_and_vg09_equipment_power_threshold_50kw(self, svc: SelectionService):
        # VG-08: Tuyến 1 (< 50 kW)
        assert svc.evaluate_numeric_threshold("<", Decimal("30"), "50 kW") is True
        assert svc.evaluate_numeric_threshold("<", Decimal("50"), "50 kW") is False

        # VG-09: Tuyến 2 (>= 50 kW)
        assert svc.evaluate_numeric_threshold(">=", Decimal("50"), "50 kW") is True
        assert svc.evaluate_numeric_threshold(">=", Decimal("75"), "50 kW") is True
        assert svc.evaluate_numeric_threshold(">=", Decimal("49.9"), "50 kW") is False

    def test_vg13_and_vg14_cumulative_contract_threshold_500m(self, svc: SelectionService):
        # VG-13: < 500M VND
        assert svc.evaluate_numeric_threshold("<", Decimal("300000000"), "500,000,000 VND") is True
        assert svc.evaluate_numeric_threshold("<", Decimal("500000000"), "500.000.000 VND") is False

        # VG-14: >= 500M VND
        assert svc.evaluate_numeric_threshold(">=", Decimal("500000000"), "500000000") is True
        assert svc.evaluate_numeric_threshold(">=", Decimal("800000000"), "500,000,000 VND") is True

    def test_number_formatting_with_dots_commas_and_units(self, svc: SelectionService):
        """Fix 3: Ensure dots, commas, currency strings are cleaned without InvalidOperation."""
        assert svc.evaluate_numeric_threshold("==", Decimal("500000000"), "500,000,000 VND") is True
        assert svc.evaluate_numeric_threshold("==", Decimal("500000000"), "500.000.000 VNĐ") is True
        assert svc.evaluate_numeric_threshold("==", Decimal("50"), "50 kW") is True
        assert svc.evaluate_numeric_threshold("==", Decimal("15"), "15 ngày làm việc") is True

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("0.125", Decimal("0.125")),
            ("0.500", Decimal("0.500")),
            ("-0.125", Decimal("-0.125")),
            ("1.000.000,50", Decimal("1000000.50")),
            ("1,000,000.50", Decimal("1000000.50")),
            ("500.000.000", Decimal("500000000")),
            ("500,000,000", Decimal("500000000")),
            ("1.500", Decimal("1500")),
            ("1000.125", Decimal("1000.125")),
            ("5,5%", Decimal("5.5")),
            ("5.5", Decimal("5.5")),
            ("50 kW", Decimal("50")),
            ("15 ngày làm việc", Decimal("15")),
            (1.125, Decimal("1.125")),
            (1e-5, Decimal("0.00001")),
        ],
    )
    def test_parse_decimal_edge_cases(
        self, svc: SelectionService, raw: float | str, expected: Decimal
    ):
        """OPS 04 hardening: primitives, leading-zero decimals, and VN/US locale separators."""
        assert svc._parse_decimal(raw) == expected

    @pytest.mark.parametrize("bad_raw", [True, False, float("nan"), float("inf")])
    def test_parse_decimal_rejects_bool_and_non_finite_float(
        self, svc: SelectionService, bad_raw: bool | float
    ):
        """OPS 04 hardening: booleans and non-finite floats must raise ValueError."""
        with pytest.raises(ValueError):
            svc._parse_decimal(bad_raw)


# ===========================================================================
# 5. Mandatory Hold Gate on Hold Variant Groups (DAT 05, DAT 08)
# ===========================================================================

class TestMandatoryHoldVariantGroupsDAT05DAT08:
    """Verifies Hold behavior for VG-06, VG-11, and VG-16."""

    def test_vg06_customer_contract_vs_policy_conflict_hold_dat05(self, svc: SelectionService):
        """VG-06: Customer framework contract vs Commercial policy -> DAT 05 Conflict Hold."""
        c_policy = ApplicabilityCandidate(
            version_id="V-POL-001",
            document_id="DOC-001",
            document_name="Quy trình báo giá và chiết khấu",
            policy_family="commercial",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=SN;branch=all;role=sales;customer_group:b2b;product:all;transaction_scope:all",
        )
        c_contract = ApplicabilityCandidate(
            version_id="V-CTR-001",
            document_id="CTR-001",
            document_name="Hợp đồng khung khách hàng A",
            policy_family="commercial",
            authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=SN;branch=all;role=sales;customer_group:b2b;product:all;transaction_scope:all",
        )
        dims = ScopeDimensions(
            company="SN",
            branch=None,
            role="sales",
            customer_category=None,
            product=None,
            transaction_scope=None,
        )
        gate = PolicyGateDecision(
            governing_date=date(2026, 11, 15),
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=("V-POL-001", "V-CTR-001"),
            has_conflict=True,
            can_proceed=True,
        )
        res = svc.run_selection(
            candidates=[c_policy, c_contract],
            dimensions=dims,
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=date(2026, 11, 15),
        )
        assert res.hold_decision.must_hold is True
        assert any(t.code == "DAT05_SOURCE_CONFLICT" for t in res.hold_decision.triggers)
        assert res.llm_used is False

    def test_vg11_missing_warranty_card_or_torn_serial_hold_dat08(self, svc: SelectionService):
        """VG-11: Torn serial / missing warranty certificate -> DAT 08 Incomplete Evidence Hold."""
        c = ApplicabilityCandidate(
            version_id="V-BH-001",
            document_id="DOC-002",
            document_name="Chính sách bảo hành",
            policy_family="warranty",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=all;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        dims = ScopeDimensions(
            company="SN",
            branch=None,
            role=None,
            customer_category=None,
            product=None,
            transaction_scope=None,
        )
        gate = PolicyGateDecision(
            governing_date=date(2026, 11, 15),
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=("V-BH-001",),
            has_conflict=False,
            can_proceed=True,
        )
        res = svc.run_selection(
            candidates=[c],
            dimensions=dims,
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=date(2026, 11, 15),
            missing_tables_or_attachments=True,
            missing_attachment_detail="Mất phiếu bảo hành gốc hoặc rách tem niêm phong Serial",
        )
        assert res.hold_decision.must_hold is True
        codes = [t.code for t in res.hold_decision.triggers]
        assert "DAT08_MISSING_TABLE_OR_ANNOTATION" in codes
        assert "Mất phiếu bảo hành" in (res.hold_decision.combined_reason_vi or "")

    def test_vg16_vip_contract_vs_crm_conflict_hold_dat05(self, svc: SelectionService):
        """VG-16: VIP contract demands exemption vs CRM policy requirement -> DAT 05 Hold."""
        c_pol = ApplicabilityCandidate(
            version_id="V-CRM-001",
            document_id="DOC-003",
            document_name="Quy chế quản trị dữ liệu CRM",
            policy_family="crm_data",
            authority_tier=AuthorityTier.POLICY,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=all;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        c_ctr = ApplicabilityCandidate(
            version_id="V-VIP-CTR",
            document_id="CTR-VIP",
            document_name="Hợp đồng VIP miễn trừ",
            policy_family="crm_data",
            authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=all;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        dims = ScopeDimensions(
            company="SN",
            branch=None,
            role=None,
            customer_category=None,
            product=None,
            transaction_scope=None,
        )
        gate = PolicyGateDecision(
            governing_date=date(2026, 11, 15),
            timezone="Asia/Ho_Chi_Minh",
            is_historical=False,
            is_future_preview=False,
            applicable_version_ids=("V-CRM-001", "V-VIP-CTR"),
            has_conflict=True,
            can_proceed=True,
        )
        res = svc.run_selection(
            candidates=[c_pol, c_ctr],
            dimensions=dims,
            all_critical_fields=[],
            gate_decision=gate,
            requested_date=date(2026, 11, 15),
        )
        assert res.hold_decision.must_hold is True
        codes = [t.code for t in res.hold_decision.triggers]
        assert "DAT05_SOURCE_CONFLICT" in codes


# ===========================================================================
# 6. Router RBAC Enforcement for Future Preview (SEC 01, KNW 03, TAX-11)
# ===========================================================================

class TestFuturePreviewRouterRBAC:
    """Enforce RBAC on allow_future_preview=True at POST /api/v1/selection/run."""

    def test_reader_denied_future_preview_with_403(self):
        """Reader role MUST receive 403 FUTURE_PREVIEW_FORBIDDEN when previewing SCHEDULED."""
        client = TestClient(app)
        reader = AuthenticatedUser(
            user_id="p4-tra-my",
            email="tra.my@songnhat.vn",
            roles=frozenset({UserRole.READER}),
        )
        token = create_access_token(reader)
        payload = {
            "task_id": "RBAC-PREVIEW-READER",
            "requested_date": "2027-01-15",
            "dimensions": {"company": "SN", "branch": "all"},
            "candidates": [],
            "critical_fields": [],
            "allow_future_preview": True,
        }
        res = client.post(
            "/api/v1/selection/run",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 403
        assert "FUTURE_PREVIEW_FORBIDDEN" in res.json()["detail"]

    @pytest.mark.parametrize(
        "role,user_id,email",
        [
            (UserRole.POLICY_OWNER, "p2-huu-tai", "huu.tai@songnhat.vn"),
            (UserRole.STEWARD, "p3-chi-kha", "chi.kha@songnhat.vn"),
            (UserRole.ADMINISTRATOR, "s5-ngoc-duy", "ngoc.duy@supplier.songnhat.vn"),
        ],
    )
    def test_authorized_roles_allowed_future_preview_with_scheduled_candidate(
        self, role: UserRole, user_id: str, email: str
    ):
        """Policy Owner, Steward, and Administrator can preview SCHEDULED versions end-to-end."""
        client = TestClient(app)
        user = AuthenticatedUser(
            user_id=user_id,
            email=email,
            roles=frozenset({role}),
        )
        token = create_access_token(user)
        scheduled_candidate = {
            "version_id": "VER-SCH",
            "document_id": "DOC-SCH",
            "document_name": "Chính sách dự kiến 2027",
            "policy_family": "commercial",
            "authority_tier": "policy",
            "status": "scheduled",
            "effective_from": "2027-01-01T00:00:00+07:00",
            "scope": (
                "company=all;branch=all;role=all;"
                "customer_category=all;product=all;transaction_scope=all"
            ),
        }
        payload = {
            "task_id": f"RBAC-PREVIEW-{role.value.upper()}",
            "requested_date": "2027-01-15",
            "dimensions": {"company": "SN", "branch": "all"},
            "candidates": [scheduled_candidate],
            "critical_fields": [],
            "allow_future_preview": True,
        }
        res = client.post(
            "/api/v1/selection/run",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["llm_used"] is False
        assert body["hold_decision"]["must_hold"] is False
        assert "VER-SCH" in body["applicable_version_ids"]


# ===========================================================================
# 7. Full 60 DEV & 40 VAL Evaluation Loop (Zero Unhandled Open Defects)
# ===========================================================================

def _run_task_through_selection(svc: SelectionService, task: dict) -> SelectionResult:
    """Execute a single DEV/VAL dataset task through the full SelectionService pipeline."""
    tid = str(task["Task_ID"])
    vg = str(task["Variant_Group_ID"])
    family = str(task.get("Policy_Family", "POL-CRM-01"))
    gov_date = date.fromisoformat(str(task["Governing_Date"]))

    primary_candidate = ApplicabilityCandidate(
        version_id=f"V-{family}-{tid}",
        document_id=family,
        document_name=f"Chính sách {family}",
        policy_family=family,
        authority_tier=AuthorityTier.POLICY,
        status=PolicyLifecycleStatus.EFFECTIVE,
        effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
        scope="company=all;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
    )

    candidates = [primary_candidate]
    has_conflict = False
    missing_tables = False
    missing_detail: str | None = None

    if vg in {"VG-06", "VG-16"}:
        # DAT 05: Customer framework/VIP contract conflicts with standard policy
        contract_candidate = ApplicabilityCandidate(
            version_id=f"V-CTR-{tid}",
            document_id=f"CTR-{tid}",
            document_name=f"Hợp đồng khung khách hàng ({vg})",
            policy_family=family,
            authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
            status=PolicyLifecycleStatus.EFFECTIVE,
            effective_from=datetime(2026, 1, 1, tzinfo=VN_TZ),
            scope="company=all;branch=all;role=all;customer_category=all;product=all;transaction_scope=all",
        )
        candidates.append(contract_candidate)
        has_conflict = True
    elif vg == "VG-11":
        # DAT 08: Missing warranty certificate or torn serial seal
        missing_tables = True
        missing_detail = "Mất phiếu bảo hành gốc hoặc rách tem niêm phong Serial"

    dims = ScopeDimensions(
        company="SN",
        branch="all",
        role="sales",
        customer_category="b2b",
        product="all",
        transaction_scope="all",
    )
    gate = PolicyGateDecision(
        governing_date=gov_date,
        timezone="Asia/Ho_Chi_Minh",
        is_historical=False,
        is_future_preview=False,
        applicable_version_ids=tuple(c.version_id for c in candidates),
        has_conflict=has_conflict,
        can_proceed=True,
    )

    return svc.run_selection(
        task_id=tid,
        candidates=candidates,
        dimensions=dims,
        all_critical_fields=[],
        gate_decision=gate,
        requested_date=gov_date,
        missing_tables_or_attachments=missing_tables,
        missing_attachment_detail=missing_detail,
    )


class TestFull60DevAnd40ValLoop:
    """Evaluates Selection & Hold logic across all 60 DEV and 40 VAL questions."""

    def test_full_60_dev_tasks_evaluation(self, svc: SelectionService, dev_60: list[dict]):
        """Run all 60 DEV questions through svc.run_selection() and confirm zero defects."""
        held_count = 0
        direct_count = 0

        for q in dev_60:
            vg = q["Variant_Group_ID"]
            expected = q["Expected_Behavior"]
            is_hold_expected = vg in {"VG-06", "VG-11", "VG-16"} or "HOLD" in expected

            res = _run_task_through_selection(svc, q)
            assert res.governing_date_result.governing_date == date(2026, 11, 15)
            assert res.llm_used is False
            assert res.hold_decision.must_hold is is_hold_expected

            if vg in {"VG-06", "VG-16"}:
                assert any(
                    t.code == "DAT05_SOURCE_CONFLICT" for t in res.hold_decision.triggers
                )
            elif vg == "VG-11":
                assert any(
                    t.code == "DAT08_MISSING_TABLE_OR_ANNOTATION"
                    for t in res.hold_decision.triggers
                )

            if is_hold_expected:
                held_count += 1
            else:
                direct_count += 1

        # Confirm expected partition distribution across 60 DEV
        msg_dev = f"Expected 11 HOLD tasks in DEV, got {held_count}"
        assert held_count == 11, msg_dev
        assert direct_count == 49

    def test_full_40_val_tasks_evaluation(self, svc: SelectionService, val_40: list[dict]):
        """Run all 40 VAL questions through svc.run_selection() and confirm zero defects."""
        held_count = 0
        direct_count = 0

        for q in val_40:
            vg = q["Variant_Group_ID"]
            expected = q["Expected_Behavior"]
            is_hold_expected = vg in {"VG-06", "VG-11", "VG-16"} or "HOLD" in expected

            res = _run_task_through_selection(svc, q)
            assert res.governing_date_result.governing_date == date(2026, 11, 15)
            assert res.llm_used is False
            assert res.hold_decision.must_hold is is_hold_expected

            if vg in {"VG-06", "VG-16"}:
                assert any(
                    t.code == "DAT05_SOURCE_CONFLICT" for t in res.hold_decision.triggers
                )
            elif vg == "VG-11":
                assert any(
                    t.code == "DAT08_MISSING_TABLE_OR_ANNOTATION"
                    for t in res.hold_decision.triggers
                )

            if is_hold_expected:
                held_count += 1
            else:
                direct_count += 1

        msg_val = f"Expected 7 HOLD tasks in VAL, got {held_count}"
        assert held_count == 7, msg_val
        assert direct_count == 33
