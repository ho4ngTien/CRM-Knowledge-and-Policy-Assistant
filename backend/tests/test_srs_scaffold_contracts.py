"""Contract and invariant tests strictly aligned with SongNhat CKPA RFP Base Scope."""

import csv
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.modules.answer.schemas import AnswerPackage, AnswerQueryRequest
from src.modules.answer.service import INTERNAL_USE_WARNING_VI, AnswerOrchestratorService
from src.modules.evaluation.schemas import EvaluationRunCreateRequest
from src.modules.evaluation.service import EvaluationService
from src.modules.ingestion.service import (
    CRITICAL_FIELDS_CSV_COLUMNS,
    PASSAGES_CSV_COLUMNS,
    IngestionService,
)
from src.modules.policy.schemas import ApplicabilityCandidate
from src.modules.policy.service import PolicyService
from src.shared.auth import AuthenticatedUser, ensure_partition_access
from src.shared.enums import (
    AnswerStatus,
    AuthorityTier,
    BatchType,
    ComparisonOperator,
    EvalPartition,
    FeedbackReason,
    PolicyLifecycleStatus,
    ReleaseGate,
    UserRole,
)
from src.shared.exceptions import AccessDenied

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_all_12_routers_mounted_and_health_contract() -> None:
    """Verify 12 Base Scope /api/v1/* module prefixes and zero O1 endpoints."""
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["mounted_modules"] == 12
    assert body["timezone"] == "Asia/Ho_Chi_Minh"
    assert body["streaming_enabled"] is False
    assert "o1_crm_context_enabled" not in body

    openapi_paths = set(app.openapi()["paths"].keys())
    expected_prefixes = (
        "identity",
        "knowledge",
        "ingestion",
        "policy",
        "retrieval",
        "answer",
        "validation",
        "referral",
        "feedback",
        "audit",
        "evaluation",
        "admin",
    )
    for prefix in expected_prefixes:
        full_prefix = f"/api/v1/{prefix}"
        assert any(p.startswith(full_prefix) for p in openapi_paths), f"Missing routes: {prefix}"

    assert "/api/v1/ingestion/o1-context" not in openapi_paths
    assert not hasattr(settings, "FEATURE_O1_CRM_CONTEXT_ENABLED")
    assert not hasattr(settings, "STORAGE_ENDPOINT")


def test_rfp_common_bid_basis_and_scope_flags() -> None:
    """Enforce RFP Common Bid Basis caps and non-streaming default."""
    assert settings.APP_TIMEZONE == "Asia/Ho_Chi_Minh"
    assert settings.ENABLE_ANSWER_STREAMING is False

    assert settings.LLM_MAX_CALLS_PER_PACKAGE == 2
    assert settings.LLM_MAX_INPUT_TOKENS == 6000
    assert settings.LLM_MAX_OUTPUT_TOKENS == 900
    assert settings.LLM_MAX_CALLS_PER_MONTH == 2000
    assert settings.ANSWER_MAX_PACKAGES_PER_MONTH == 1000
    assert settings.ANSWER_MAX_PASSAGES == 8
    assert settings.PASSAGE_MAX_CHARS == 6000
    assert settings.IMPORT_MAX_ROWS_PER_BATCH == 500
    assert settings.CORPUS_MAX_PASSAGES == 300
    assert settings.CORPUS_MAX_DOCUMENTS == 30
    assert settings.CORPUS_MAX_CRITICAL_FIELDS == 50
    assert settings.IMPORT_SNAPSHOT_STALENESS_HOURS == 25
    assert settings.CACHE_WITHDRAWAL_MAX_SECONDS == 300


def test_enum_completeness() -> None:
    """Verify exact enum sets for KNW 07 (5 reasons), KNW 03 (7+2 states), and 5 Gates."""
    assert len(FeedbackReason) == 5
    assert len(PolicyLifecycleStatus) == 9
    assert {g.value for g in ReleaseGate} == {"G0", "G1", "G2", "G3", "G4"}
    assert len(EvalPartition) == 4
    assert len(AuthorityTier) == 5
    assert len(UserRole) == 7


def test_csv_templates_and_quarantine_validators() -> None:
    """Verify UTF-8 21/23-column template headers pass and missing attachments quarantine."""
    passages_csv = REPO_ROOT / "data" / "templates" / "passages_template.csv"
    critical_csv = REPO_ROOT / "data" / "templates" / "critical_fields_template.csv"

    with passages_csv.open(encoding="utf-8-sig", newline="") as f:
        header = tuple(next(csv.reader(f)))
    assert header == PASSAGES_CSV_COLUMNS
    assert len(header) == 21

    with critical_csv.open(encoding="utf-8-sig", newline="") as f:
        header_cf = tuple(next(csv.reader(f)))
    assert header_cf == CRITICAL_FIELDS_CSV_COLUMNS
    assert len(header_cf) == 23

    svc = IngestionService()
    report_p = svc.validate_csv_bytes(
        passages_csv.read_bytes(), source_type="passages", batch_type=BatchType.FULL_SNAPSHOT
    )
    assert report_p.accepted_rows == 1
    assert report_p.quarantined_rows == 0

    report_cf = svc.validate_csv_bytes(
        critical_csv.read_bytes(),
        source_type="critical_fields",
        batch_type=BatchType.FULL_SNAPSHOT,
    )
    assert report_cf.accepted_rows == 1
    assert report_cf.quarantined_rows == 0

    broken_row = passages_csv.read_text(encoding="utf-8").replace(",true,upsert", ",false,upsert")
    quarantine_report = svc.validate_csv_bytes(
        broken_row.encode("utf-8"), source_type="passages", batch_type=BatchType.DELTA
    )
    assert quarantine_report.accepted_rows == 0
    assert quarantine_report.quarantined_rows == 1
    assert quarantine_report.quarantine_issues[0].reason_code == "MISSING_ESSENTIAL_ATTACHMENTS"


def test_base_scope_seven_part_answer_package_and_fail_closed() -> None:
    """Verify unauthenticated 401 fail-closed, Base Scope purity, and 7-part AnswerPackage."""
    client = TestClient(app)
    assert client.post("/api/v1/answer", json={"question": "Test"}).status_code == 401
    assert "selected_o1_record_id" not in AnswerQueryRequest.model_fields
    assert "selected_o1_context" not in AnswerPackage.model_fields

    user = AuthenticatedUser(
        user_id="u1",
        email="u1@songnhat.vn",
        roles=frozenset({UserRole.READER}),
    )
    orch = AnswerOrchestratorService()
    pkg = orch.build_guarded_response(
        user,
        AnswerQueryRequest(question="Báo giá chiết khấu 12%, SĐT 0901234567 cần ai duyệt?"),
    )
    assert isinstance(pkg, AnswerPackage)
    for required_field in (
        "original_question",
        "governing_date",
        "scope",
        "guidance_text",
        "verbatim_quotes",
        "citations",
        "critical_fields",
        "missing_facts",
        "hold_reason",
        "uncertainty_note",
        "referral_target",
        "internal_use_warning",
    ):
        assert hasattr(pkg, required_field)
    assert pkg.internal_use_warning == INTERNAL_USE_WARNING_VI
    assert pkg.pii_warning is not None
    assert pkg.status == AnswerStatus.HOLD

    refused = orch.build_guarded_response(
        user, AnswerQueryRequest(question="Nhờ trợ lý tư vấn thuế và pháp lý hợp đồng này")
    )
    assert refused.status == AnswerStatus.REFUSED_OUT_OF_SCOPE


def test_policy_applicability_conflict_hold_and_chinese_wall() -> None:
    """Verify DAT 05 conflict hold, deterministic threshold math, and sealed_100 Chinese Wall."""
    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    now_vn = datetime.now(tz)
    ps = PolicyService()

    assert ps.evaluate_numeric_threshold(ComparisonOperator.LE, Decimal("10"), "10") is True
    assert ps.evaluate_numeric_threshold(ComparisonOperator.LE, Decimal("10.1"), "10") is False

    conflict_res = ps.evaluate_candidates(
        [
            ApplicabilityCandidate(
                version_id="PVER-POL-1",
                authority_tier=AuthorityTier.POLICY,
                status=PolicyLifecycleStatus.EFFECTIVE,
                effective_from=now_vn - timedelta(days=5),
                scope="company:SN",
            ),
            ApplicabilityCandidate(
                version_id="PVER-CTR-1",
                authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
                status=PolicyLifecycleStatus.EFFECTIVE,
                effective_from=now_vn - timedelta(days=2),
                scope="company:SN",
            ),
        ]
    )
    assert conflict_res.has_conflict is True
    assert conflict_res.hold_reason is not None

    dev_user = AuthenticatedUser(
        user_id="dev-b1", email="b1@songnhat.vn", roles=frozenset({UserRole.STEWARD})
    )
    with pytest.raises(AccessDenied):
        ensure_partition_access(dev_user, EvalPartition.SEALED_100)

    ev_svc = EvaluationService()
    run_req = EvaluationRunCreateRequest(
        release_gate=ReleaseGate.G2,
        partition=EvalPartition.SEALED_100,
        total_cases=100,
        critical_control_errors=1,
        applicability_rate=0.96,
        grounding_rate=0.96,
        completeness_rate=0.92,
        recall_at_5=0.91,
        usefulness_rate=0.85,
        fabrication_on_unanswerable_rate=0.02,
    )
    assert len(ev_svc.check_section8_thresholds(run_req)) == 1


def test_ckpa_17_answer_package_seven_parts_and_strict_schema() -> None:
    """[CKPA-17] Verify AnswerPackage 7 parts and strict Pydantic v2 validation (fail-closed)."""
    from datetime import date

    from pydantic import ValidationError

    from src.modules.policy.schemas import CriticalFieldItem
    from src.shared.enums import CriticalFieldType

    valid_payload = {
        "answer_id": "ANS-TEST-001",
        "task_id": "TSK-001",
        "status": AnswerStatus.ANSWERED,
        # Part 1
        "original_question": "Thời hạn bảo hành đổi trả tiêu chuẩn là bao nhiêu ngày?",
        # Part 2
        "governing_date": date(2026, 11, 18),
        "timezone": "Asia/Ho_Chi_Minh",
        "scope": "company:SN;branch:all;role:all;customer_group:all;product:all",
        "is_historical": False,
        "is_future_preview": False,
        # Part 3
        "guidance_text": "Thời hạn đổi trả tiêu chuẩn là 30 ngày kể từ ngày mua hàng.",
        "verbatim_quotes": ["Đổi trả trong vòng 30 ngày đối với lỗi từ nhà sản xuất."],
        # Part 4
        "citations": [],
        # Part 5
        "critical_fields": [
            {
                "field_id": "CF-001",
                "policy_id": "POL-WAR-01",
                "policy_version_id": "PVER-01",
                "document_version_id": "DVER-01",
                "field_name": "thoi_han_doi_tra",
                "field_type": CriticalFieldType.NUMBER,
                "operator": ComparisonOperator.LE,
                "value": "30",
                "unit": "ngày",
                "approval_role": "steward",
                "source_clause": "Điều 4.1",
                "status": PolicyLifecycleStatus.EFFECTIVE,
            }
        ],
        # Part 6
        "missing_facts": [],
        "hold_reason": None,
        "uncertainty_note": None,
        # Part 7
        "referral_target": None,
        "internal_use_warning": "Lưu hành nội bộ - Không chia sẻ ra ngoài",
    }

    # Pass contract validation
    pkg = AnswerPackage.model_validate(valid_payload)
    assert pkg.answer_id == "ANS-TEST-001"
    assert len(pkg.critical_fields) == 1
    assert pkg.critical_fields[0].field_name == "thoi_han_doi_tra"

    # Strict schema: reject extra fields (e.g. Option O1 or unapproved parameters)
    forbidden_payload = valid_payload.copy()
    forbidden_payload["selected_o1_context"] = "illegal_context"
    with pytest.raises(ValidationError):
        AnswerPackage.model_validate(forbidden_payload)

    # CriticalFieldItem strict schema: reject extra fields
    invalid_cf = valid_payload["critical_fields"][0].copy()
    invalid_cf["unknown_attribute"] = "malformed"
    with pytest.raises(ValidationError):
        CriticalFieldItem.model_validate(invalid_cf)

