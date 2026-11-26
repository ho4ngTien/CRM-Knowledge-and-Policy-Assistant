"""Unit and contract tests for CKPA-91 (G2-AC01): Answer Package 100-250w, O1 & KNW 01."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.modules.answer.schemas import AnswerCitation, AnswerPackage, AnswerQueryRequest
from src.modules.answer.service import (
    AnswerOrchestratorService,
    bound_deterministic_critical_fields,
    count_vietnamese_words,
    parse_scope_dimensions_6dim,
)
from src.modules.knowledge.schemas import PassageSummary
from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.selection.o1_context import CustomerContextO1
from src.modules.validation.service import ValidationService
from src.shared.auth import AuthenticatedUser, create_access_token
from src.shared.contracts import (
    HybridQuerySpec,
    LLMGenerationRequest,
    LLMGenerationResult,
)
from src.shared.enums import (
    AnswerStatus,
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyLifecycleStatus,
    UserRole,
)
from src.shared.exceptions import AccessDenied

_VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def _sample_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id="u-ckpa91",
        email="nhi@songnhat.vn",
        roles=frozenset({UserRole.READER}),
        allowed_audiences=frozenset({"reader"}),
    )


def _sample_passage() -> PassageSummary:
    return PassageSummary(
        passage_id="PSG-91",
        document_id="DOC-001",
        document_version_id="DVER-001",
        title="Quy trình duyệt báo giá & chiết khấu",
        content="Chiết khấu tối đa 10% do Quản lý bán hàng phê duyệt trong 4 giờ làm việc.",
        source_ref="docs/POL-CRM-01.md",
        page_number=1,
        clause_ref="Điều 2.1",
        language="vi",
        scope="company:SN;branch:all",
        audience=["reader"],
        status=PolicyLifecycleStatus.EFFECTIVE,
        has_essential_attachments=True,
        effective_from=datetime.now(_VN_TZ) - timedelta(days=5),
        effective_to=None,
    )


def _sample_cf(
    field_id: str = "CF-91",
    *,
    exception_condition: str | None = None,
    value: str = "10",
) -> CriticalFieldItem:
    return CriticalFieldItem(
        field_id=field_id,
        policy_id="POL-001",
        policy_version_id="PVER-001",
        document_version_id="DVER-001",
        field_name="max_discount_pct",
        field_type=CriticalFieldType.NUMBER,
        operator=ComparisonOperator.LE,
        value=value,
        unit="%",
        approval_role="Quản lý bán hàng",
        time_limit="4 giờ làm việc",
        exception_condition=exception_condition,
        required_documents=["Phiếu đề xuất báo giá"],
        source_clause="Điều 2.1",
        status=PolicyLifecycleStatus.EFFECTIVE,
    )


class _StubRetrieval:
    def __init__(self, passages: list[PassageSummary]) -> None:
        self._passages = passages

    def compute_rrf_score(
        self,
        vector_rank: int | None,
        fts_rank: int | None,
        trgm_rank: int | None = None,
        *,
        k: int = 60,
    ) -> float:
        _ = vector_rank, fts_rank, trgm_rank, k
        return 1.0

    async def search_hybrid(
        self, user: AuthenticatedUser, spec: HybridQuerySpec
    ) -> list[PassageSummary]:
        _ = user, spec
        return list(self._passages)

    async def fetch_authoritative_passages(
        self, user: AuthenticatedUser, passage_ids: list[str], db: object | None = None
    ) -> dict[str, PassageSummary]:
        _ = user, db
        return {p.passage_id: p for p in self._passages if p.passage_id in passage_ids}


class _StubLLM:
    def __init__(self, result: LLMGenerationResult) -> None:
        self._result = result

    async def generate(self, request: LLMGenerationRequest) -> LLMGenerationResult:
        _ = request
        return self._result


class _StubAudit:
    async def check_monthly_quota(self, db: object | None = None, month_key: str | None = None):
        from src.shared.contracts import QuotaStatus

        _ = db, month_key
        return QuotaStatus(
            month_key="2026-11",
            packages_used=1,
            package_quota=1000,
            llm_calls_used=1,
            llm_call_quota=2000,
            allowed=True,
        )

    async def record_usage_meter(self, db: object | None = None, **kwargs: object) -> None:
        _ = db, kwargs

    async def record_audit_event(self, db: object | None = None, **kwargs: object) -> None:
        _ = db, kwargs


def test_parse_scope_dimensions_6dim_and_word_count() -> None:
    """Verify 6-dimension scope parsing (with customer_group alias) and word count."""
    dims = parse_scope_dimensions_6dim(
        "company:SN;branch:HN;role:sales;customer_group:b2b;product:motor;transaction_scope:quotation"
    )
    assert dims == {
        "company": "SN",
        "branch": "HN",
        "role": "sales",
        "customer_category": "b2b",
        "product": "motor",
        "transaction_scope": "quotation",
    }
    assert "transaction_scope" in AnswerQueryRequest(question="Hỏi chính sách").scope

    # 120-word Vietnamese explanation falls within 100-250 words
    guidance_120w = " ".join(["quy định chiết khấu tối đa 10 phần trăm"] * 15)
    assert 100 <= count_vietnamese_words(guidance_120w) <= 250


def test_critical_fields_bounds_no_silent_truncation() -> None:
    """Verify <= 8 entries and <= 6000 Unicode chars warning without silently mutating values."""
    many_fields = [_sample_cf(field_id=f"CF-{i}") for i in range(10)]
    bounded, warn = bound_deterministic_critical_fields(many_fields)
    assert len(bounded) == 8
    assert warn is not None and "8" in warn

    oversized_cf = _sample_cf(
        field_id="CF-LONG",
        exception_condition="X" * 6050,
    )
    kept, char_warn = bound_deterministic_critical_fields([oversized_cf])
    assert len(kept) == 1
    assert len(kept[0].exception_condition or "") == 6050
    assert char_warn is not None and "6000" in char_warn


async def test_o1_locked_in_base_scope_and_enabled_when_purchased(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """O1 context fails closed in Base Scope and enriches 6-dim scope when enabled."""
    user = _sample_user()
    orch = AnswerOrchestratorService()
    o1 = CustomerContextO1(
        customer_id="CUST-B2B-01",
        customer_tier="b2b",
        industry_code="MFG",
        assigned_branch="HN",
        assigned_company="SN",
    )

    assert settings.ENABLE_O1_CONTEXT_IMPORT is False
    with pytest.raises(AccessDenied, match="O1_OPTION_DISABLED_IN_BASE_SCOPE"):
        await orch.execute_pipeline(
            user,
            AnswerQueryRequest(question="Chiết khấu bao nhiêu?", o1_context=o1),
        )

    # HTTP endpoint also fails closed 403
    client = TestClient(app)
    token = create_access_token(user)
    res = client.post(
        "/api/v1/answer",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Chiết khấu bao nhiêu?", "o1_context": o1.model_dump()},
    )
    assert res.status_code == 403

    # When O1 is enabled, O1 record is attached and enriches 6-dim scope
    monkeypatch.setattr(settings, "ENABLE_O1_CONTEXT_IMPORT", True)
    pkg = await orch.execute_pipeline(
        user,
        AnswerQueryRequest(question="Chiết khấu bao nhiêu?", o1_context=o1),
    )
    assert pkg.o1_enabled is True
    assert pkg.o1_record == o1
    assert pkg.scope_matched_dimensions["branch"] == "HN"
    assert pkg.scope_matched_dimensions["customer_category"] == "b2b"


async def test_answered_with_conditions_and_citation_metadata() -> None:
    """Verify Answered with conditions status, 100-250w count, and citation effective_date/owner."""
    user = _sample_user()
    passage = _sample_passage()
    cf = _sample_cf(exception_condition="Khách hàng VIP cần thêm duyệt Giám đốc kinh doanh.")
    candidate = ApplicabilityCandidate(
        version_id="PVER-001",
        authority_tier=AuthorityTier.POLICY,
        status=PolicyLifecycleStatus.EFFECTIVE,
        effective_from=datetime.now(_VN_TZ) - timedelta(days=5),
        scope="company:SN",
    )
    guidance = (
        "Căn cứ quy định thương mại hiện hành ngày 26/11/2026 tại Song Nhật, mức chiết khấu "
        "tối đa 10% nằm trong thẩm quyền phê duyệt của Quản lý bán hàng với thời hạn xử lý "
        "tối đa 4 giờ làm việc. "
        + " ".join(["Nhân viên bán hàng cần đính kèm đủ hồ sơ đề xuất báo giá."] * 10)
    )
    citation = AnswerCitation(
        document_id=passage.document_id,
        document_version_id=passage.document_version_id,
        passage_id=passage.passage_id,
        title=passage.title,
        page_number=passage.page_number,
        clause_ref=passage.clause_ref,
        quoted_text=passage.content,
        evidence_url=f"/api/v1/knowledge/passages/{passage.passage_id}",
        effective_date=date(2026, 11, 1),
        owner="Lý Hữu Tài",
    )
    orch = AnswerOrchestratorService(
        retrieval_port=_StubRetrieval([passage]),
        llm_generator=_StubLLM(
            LLMGenerationResult(
                guidance_text=guidance,
                verbatim_quotes=(passage.content,),
                citations=(citation,),
                uncertainty_note="Áp dụng có điều kiện ngoại lệ với nhóm khách VIP.",
                input_tokens=150,
                output_tokens=180,
                llm_calls_used=1,
            )
        ),
        audit_meter=_StubAudit(),
    )
    pkg: AnswerPackage = await orch.execute_pipeline(
        user,
        AnswerQueryRequest(question="Chiết khấu 10% cần ai duyệt?"),
        candidates=[candidate],
        critical_fields=[cf],
    )
    assert pkg.status == AnswerStatus.ANSWERED_WITH_CONDITIONS
    assert 100 <= pkg.guidance_word_count <= 250
    assert pkg.citations[0].effective_date == date(2026, 11, 1)
    assert pkg.citations[0].owner == "Lý Hữu Tài"
    assert len(pkg.scope_matched_dimensions) == 6
    assert ValidationService().verify_final_delivery(
        user, pkg, {passage.passage_id: passage}
    ).status == AnswerStatus.ANSWERED_WITH_CONDITIONS
