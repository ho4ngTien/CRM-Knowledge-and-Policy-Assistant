"""[G2][KNW05] CKPA-92 — Local Referral 3-State Service & 9 Annex B Contracts.

Acceptance criteria (G2-AC01):
- Local referral record stores: PII-free question, minimal_context, hold_reason & owner_role.
- No outbound messages, no CRM task creation, no auto-approval, 0% CRM writeback.
- Separate 3-state tracking (KNW 05): referred -> owner_responded -> closed.
- Unit + integration tests across all 9 Annex B contracts (SC-01..SC-09 / B-01..B-09):
  SC-01 / B-01  General CRM question  -> HOLD_ANS06 -> Local Referral
  SC-02 / B-02  Commercial exception  -> HOLD_ANS07 -> Local Referral
  SC-03 / B-03  Dated transaction     -> HOLD_ANS06 / HOLD_DAT05 -> Local Referral
  SC-04 / B-04  Scheduled replacement -> HOLD_DAT05 -> Local Referral
  SC-05 / B-05  Conflicting contract  -> HOLD_DAT05 -> Local Referral
  SC-06 / B-06  Old CRM note          -> HOLD_ANS07 -> Local Referral
  SC-07 / B-07  Missing footnote      -> HOLD_DAT08 -> Local Referral
  SC-08 / B-08  Data correction       -> HOLD_ANS07 -> Local Referral (0% CRM writeback)
  SC-09 / B-09  Withdrawal mid-answer -> HOLD_SEC05 -> Local Referral
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, cast
from zoneinfo import ZoneInfo

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.db import Base, get_db
from src.main import app
from src.modules.answer.schemas import AnswerCitation, AnswerQueryRequest
from src.modules.answer.service import AnswerOrchestratorService
from src.modules.knowledge.schemas import PassageSummary
from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.policy.service import PolicyService
from src.modules.referral.annex_b_handler import (
    ANNEX_B_CONTRACTS,
    AnnexBCaseId,
    AnnexBReferralHandler,
    resolve_annex_b_contract,
)
from src.modules.referral.models import LocalReferral
from src.modules.referral.schemas import (
    AnnexBReferralRequest,
    ReferralCreateRequest,
    ReferralUpdateRequest,
)
from src.modules.referral.service import ReferralService
from src.shared.auth import AuthenticatedUser, create_access_token
from src.shared.contracts import HybridQuerySpec, LLMGenerationRequest, LLMGenerationResult
from src.shared.enums import (
    AnswerStatus,
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyFamily,
    PolicyLifecycleStatus,
    ReferralStatus,
    UserRole,
)
from src.shared.exceptions import AccessDenied, PolicyNotFound, SourceConflict

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


class _AsyncSessionAdapter:
    """Wrap synchronous SQLite session as async-compatible for isolated unit/integration tests."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def execute(self, statement: Any) -> Any:
        return self.session.execute(statement)

    async def get(self, entity: Any, identity: Any) -> Any:
        return self.session.get(entity, identity)

    def add(self, entity: Any) -> None:
        self.session.add(entity)

    async def commit(self) -> None:
        self.session.commit()

    async def refresh(self, entity: Any) -> None:
        self.session.refresh(entity)


def _make_db() -> tuple[Any, _AsyncSessionAdapter]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[LocalReferral.__table__])
    session = Session(engine)
    return engine, _AsyncSessionAdapter(session)


def _reader(user_id: str = "p4-tra-my") -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=user_id,
        email=f"{user_id}@songnhat.vn",
        roles=frozenset({UserRole.READER}),
        allowed_audiences=frozenset({"reader"}),
    )


def _policy_owner(user_id: str = "p2-huu-tai") -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=user_id,
        email=f"{user_id}@songnhat.vn",
        roles=frozenset({UserRole.POLICY_OWNER}),
        allowed_audiences=frozenset({"reader", "policy_owner"}),
    )


def _steward(user_id: str = "p3-chi-kha") -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=user_id,
        email=f"{user_id}@songnhat.vn",
        roles=frozenset({UserRole.STEWARD}),
        allowed_audiences=frozenset({"reader", "steward"}),
    )


def _assert_no_crm_writeback_or_auto_action(ref: Any) -> None:
    """Assert KNW 05 non-writeback, no external dispatch, and no auto-approval invariants."""
    assert not hasattr(ref, "crm_task_id")
    assert not hasattr(ref, "crm_writeback")
    ctx = getattr(ref, "minimal_context", {}) or {}
    if "crm_writeback" in ctx:
        assert ctx["crm_writeback"] is False
    if "external_message_sent" in ctx:
        assert ctx["external_message_sent"] is False
    if "auto_approved" in ctx:
        assert ctx["auto_approved"] is False


service = ReferralService()
handler = AnnexBReferralHandler(service)


# ---------------------------------------------------------------------------
# Unit tests: KNW 05 3-state tracking, PII minimization & state guard
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_knw05_full_3state_lifecycle_and_separate_tracking() -> None:
    """KNW 05: referred -> owner_responded -> closed tracks timestamps and actors separately."""
    _, db = _make_db()
    requester = _reader()
    owner = _policy_owner()

    ref = await service.create_referral(
        cast(AsyncSession, db),
        requester,
        ReferralCreateRequest(
            task_id="TASK-KNW05-01",
            answer_package_id="ANS-KNW05-01",
            owner_role="policy_owner",
            target_owner="p2-huu-tai",
            policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
            question_summary="Báo giá thiếu phạm vi khách hàng cần chuyển xử lý.",
            minimal_context={"case_id": "SC-01", "scope": "company:SN"},
            hold_reason="HOLD_ANS06",
        ),
    )
    assert ref.status == ReferralStatus.REFERRED
    assert ref.owner_role == "policy_owner"
    assert ref.hold_reason == "HOLD_ANS06"
    assert ref.minimal_context == {"case_id": "SC-01", "scope": "company:SN"}
    assert ref.owner_responded_at is None
    assert ref.responded_by is None
    assert ref.closed_at is None
    assert ref.closed_by is None

    responded = await service.update_referral(
        cast(AsyncSession, db),
        ref.id,
        ReferralUpdateRequest(
            status=ReferralStatus.OWNER_RESPONDED,
            owner_response="Áp dụng DOC-001 VER-001 Điều 1.2 cho phân khúc b2b_enterprise.",
        ),
        owner,
    )
    assert responded.status == ReferralStatus.OWNER_RESPONDED
    assert responded.owner_response is not None
    assert responded.owner_responded_at is not None
    assert responded.responded_by == owner.user_id
    assert responded.closed_at is None

    closed = await service.update_referral(
        cast(AsyncSession, db),
        ref.id,
        ReferralUpdateRequest(
            status=ReferralStatus.CLOSED,
            resolution_note="Nhân viên đã ghi nhận hướng dẫn và đóng phiếu nội bộ.",
        ),
        owner,
    )
    assert closed.status == ReferralStatus.CLOSED
    assert closed.closed_at is not None
    assert closed.closed_by == owner.user_id
    assert closed.owner_responded_at == responded.owner_responded_at
    assert closed.responded_by == owner.user_id


@pytest.mark.asyncio
async def test_knw05_pii_sanitized_in_question_and_minimal_context() -> None:
    """SEC 02: PII (phone/email/CCCD) is redacted before persisting LocalReferral."""
    _, db = _make_db()
    ref = await service.create_referral(
        cast(AsyncSession, db),
        _reader(),
        ReferralCreateRequest(
            task_id="TASK-PII-01",
            owner_role="policy_owner",
            target_owner="p2-huu-tai",
            policy_family=PolicyFamily.CUSTOMER_INFO_HANDLING,
            question_summary="Đổi email khach@example.com SĐT 0901234567 CCCD 079090001234",
            minimal_context={"raw_note": "Liên hệ 0912345678 hoặc a@b.vn"},
            hold_reason="HOLD_ANS07",
        ),
    )
    assert "0901234567" not in ref.question_summary
    assert "khach@example.com" not in ref.question_summary
    assert "079090001234" not in ref.question_summary
    assert "[REDACTED_PHONE]" in ref.question_summary
    assert "[REDACTED_EMAIL]" in ref.question_summary
    assert "[REDACTED_ID]" in ref.question_summary
    assert "0912345678" not in str(ref.minimal_context)
    assert "a@b.vn" not in str(ref.minimal_context)


def test_knw05_requires_non_empty_owner_response_on_transition() -> None:
    """KNW 05: transitioning to owner_responded without owner_response raises ValidationError."""
    with pytest.raises(ValidationError):
        ReferralUpdateRequest(status=ReferralStatus.OWNER_RESPONDED, owner_response="  ")


@pytest.mark.asyncio
async def test_knw05_state_guard_blocks_skip_and_reverse_transitions() -> None:
    """KNW 05 guard: blocks referred->closed skip, backward transitions, and reader mutations."""
    _, db = _make_db()
    requester = _reader()
    owner = _policy_owner()

    ref = await service.create_referral(
        cast(AsyncSession, db),
        requester,
        ReferralCreateRequest(
            task_id="TASK-GUARD-01",
            owner_role="policy_owner",
            target_owner="p2-huu-tai",
            policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
            question_summary="Kiểm tra chặn nhảy cóc trạng thái.",
            hold_reason="HOLD_ANS07",
        ),
    )

    with pytest.raises(AccessDenied):
        await service.update_referral(
            cast(AsyncSession, db),
            ref.id,
            ReferralUpdateRequest(
                status=ReferralStatus.OWNER_RESPONDED,
                owner_response="Reader không có quyền ghi phản hồi owner.",
            ),
            requester,
        )

    with pytest.raises(SourceConflict, match="KNW 05 state guard"):
        await service.update_referral(
            cast(AsyncSession, db),
            ref.id,
            ReferralUpdateRequest(status=ReferralStatus.CLOSED),
            owner,
        )

    await service.update_referral(
        cast(AsyncSession, db),
        ref.id,
        ReferralUpdateRequest(
            status=ReferralStatus.OWNER_RESPONDED,
            owner_response="Owner đã phản hồi.",
        ),
        owner,
    )

    with pytest.raises(SourceConflict, match="KNW 05 state guard"):
        await service.update_referral(
            cast(AsyncSession, db),
            ref.id,
            ReferralUpdateRequest(status=ReferralStatus.REFERRED),
            owner,
        )

    await service.update_referral(
        cast(AsyncSession, db),
        ref.id,
        ReferralUpdateRequest(status=ReferralStatus.CLOSED, resolution_note="Đóng phiếu."),
        owner,
    )

    with pytest.raises(SourceConflict, match="KNW 05 state guard"):
        await service.update_referral(
            cast(AsyncSession, db),
            ref.id,
            ReferralUpdateRequest(status=ReferralStatus.REFERRED),
            owner,
        )


@pytest.mark.asyncio
async def test_knw05_not_found_and_visibility_isolation() -> None:
    """Readers only see own referrals; privileged owners see all; unknown ID raises 404."""
    _, db = _make_db()
    user_a = _reader("user-a")
    user_b = _reader("user-b")
    owner = _policy_owner()

    ref_a = await service.create_referral(
        cast(AsyncSession, db),
        user_a,
        ReferralCreateRequest(
            task_id="TASK-ISO-A",
            owner_role="policy_owner",
            target_owner="p2-huu-tai",
            policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
            question_summary="Phiếu của user A.",
            hold_reason="HOLD_ANS06",
        ),
    )

    assert await service.list_referrals(cast(AsyncSession, db), user_b) == []
    assert len(await service.list_referrals(cast(AsyncSession, db), user_a)) == 1
    assert len(await service.list_referrals(cast(AsyncSession, db), owner)) == 1

    with pytest.raises(AccessDenied):
        await service.get_referral(cast(AsyncSession, db), user_b, ref_a.id)

    with pytest.raises(PolicyNotFound):
        await service.update_referral(
            cast(AsyncSession, db),
            "REF-UNKNOWN",
            ReferralUpdateRequest(status=ReferralStatus.CLOSED),
            owner,
        )


# ---------------------------------------------------------------------------
# Handler tests across all 9 Annex B contracts (SC-01..SC-09 / B-01..B-09)
# ---------------------------------------------------------------------------


_ANNEX_B_HOLD_SCENARIOS: list[tuple[str, str, dict[str, Any], str, str]] = [
    (
        "SC-01",
        "B-01",
        {
            "question": "Trường báo giá bắt buộc khi thiếu chiều phạm vi giao dịch?",
            "answer_status": "hold",
            "missing_facts": ["transaction_scope"],
        },
        "HOLD_ANS06",
        "policy_owner",
    ),
    (
        "SC-02",
        "B-02",
        {
            "question": "Đề nghị hệ thống tự duyệt chiết khấu 18% cho đơn 1.2 tỷ VND.",
            "answer_status": "refused_out_of_scope",
            "is_auto_approve_request": True,
        },
        "HOLD_ANS07",
        "policy_owner",
    ),
    (
        "SC-03",
        "B-03",
        {
            "question": "Giao dịch bảo hành motor 3 pha cần kiểm tra nhưng thiếu ngày sự kiện.",
            "answer_status": "clarification_required",
            "missing_facts": ["event_timestamp_utc7"],
        },
        "HOLD_ANS06",
        "policy_owner",
    ),
    (
        "SC-04",
        "B-04",
        {
            "question": "Kiểm tra bản scheduled VER-002 khi chưa xác minh trạng thái xuất bản.",
            "answer_status": "hold",
            "has_contract_conflict": True,
        },
        "HOLD_DAT05",
        "steward",
    ),
    (
        "SC-05",
        "B-05",
        {
            "question": "Hợp đồng DOC-006 mâu thuẫn chính sách DOC-001 về mức chiết khấu.",
            "answer_status": "hold",
            "has_contract_conflict": True,
            "source_refs": ["DOC-001", "DOC-006"],
        },
        "HOLD_DAT05",
        "policy_owner",
    ),
    (
        "SC-06",
        "B-06",
        {
            "question": "Viện dẫn ghi chú CRM cũ DOC-007 để xin áp dụng quyền lợi cho KH khác.",
            "answer_status": "hold",
            "is_staff_note_rule_request": True,
            "source_refs": ["DOC-007"],
        },
        "HOLD_ANS07",
        "policy_owner",
    ),
    (
        "SC-07",
        "B-07",
        {
            "question": "Ngưỡng chiết khấu dự án inverter_mv thiếu bảng phụ lục đính kèm.",
            "answer_status": "hold",
            "has_essential_attachments": False,
            "source_refs": ["PAS-019"],
        },
        "HOLD_DAT08",
        "steward",
    ),
    (
        "SC-08",
        "B-08",
        {
            "question": "Yêu cầu trợ lý cập nhật trực tiếp email hóa đơn trên hồ sơ CRM.",
            "answer_status": "hold",
            "is_crm_writeback_request": True,
        },
        "HOLD_ANS07",
        "policy_owner",
    ),
    (
        "SC-09",
        "B-09",
        {
            "question": "Truy vấn bảo hành Tuyến 2 khi PAS-024/DOC-003 thu hồi giữa Tầng 4-5.",
            "answer_status": "stale",
            "is_withdrawn": True,
            "source_refs": ["PAS-024", "DOC-003"],
        },
        "HOLD_SEC05",
        "policy_owner",
    ),
]


def test_annex_b_registry_contains_all_9_contracts() -> None:
    """Verify exact 9 Annex B contracts SC-01..SC-09 and alias lookup B-01..B-09."""
    assert len(ANNEX_B_CONTRACTS) == 9
    for idx in range(1, 10):
        sc_contract = resolve_annex_b_contract(f"SC-0{idx}")
        b_contract = resolve_annex_b_contract(f"B-0{idx}")
        assert sc_contract == b_contract
        assert sc_contract.case_id == AnnexBCaseId(f"SC-0{idx}")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("case_id", "matrix_id", "kwargs", "expected_hold", "expected_owner_role"),
    _ANNEX_B_HOLD_SCENARIOS,
)
async def test_annex_b_each_scenario_creates_referral_and_completes_3_states(
    case_id: str,
    matrix_id: str,
    kwargs: dict[str, Any],
    expected_hold: str,
    expected_owner_role: str,
) -> None:
    """SC-01..SC-09: 100% Hold/exception creates Local Referral through all 3 KNW 05 states."""
    _, db = _make_db()
    requester = _reader()
    actor = _steward() if expected_owner_role == "steward" else _policy_owner()

    result = await handler.handle_case(
        cast(AsyncSession, db),
        requester,
        AnnexBReferralRequest(
            case_id=case_id,
            task_id=f"TASK-{case_id}",
            answer_package_id=f"ANS-{case_id}",
            **kwargs,
        ),
    )

    assert result.case_id == case_id
    assert result.matrix_id == matrix_id
    assert result.referral_created is True
    assert result.hold_reason == expected_hold
    assert result.owner_role == expected_owner_role
    assert result.crm_writeback_count == 0
    assert result.messages_dispatched == 0
    assert result.auto_approved is False
    assert result.referral is not None

    ref = result.referral
    assert ref.status == ReferralStatus.REFERRED
    assert ref.hold_reason == expected_hold
    assert ref.owner_role == expected_owner_role
    assert ref.minimal_context["case_id"] == case_id
    _assert_no_crm_writeback_or_auto_action(ref)

    # State 2: owner response recorded
    responded = await service.update_referral(
        cast(AsyncSession, db),
        ref.id,
        ReferralUpdateRequest(
            status=ReferralStatus.OWNER_RESPONDED,
            owner_response=f"[{case_id}] Chủ sở hữu đã rà soát {expected_hold}.",
        ),
        actor,
    )
    assert responded.status == ReferralStatus.OWNER_RESPONDED
    assert responded.owner_responded_at is not None

    # State 3: closure
    closed = await service.update_referral(
        cast(AsyncSession, db),
        ref.id,
        ReferralUpdateRequest(
            status=ReferralStatus.CLOSED,
            resolution_note=f"[{case_id}] Hoàn tất xử lý nội bộ, 0% ghi ngược CRM.",
        ),
        actor,
    )
    assert closed.status == ReferralStatus.CLOSED
    assert closed.closed_at is not None
    _assert_no_crm_writeback_or_auto_action(closed)


@pytest.mark.asyncio
async def test_annex_b_answered_case_does_not_create_spurious_referral() -> None:
    """When an Annex B query is answered cleanly (no Hold/exception), no referral is created."""
    _, db = _make_db()
    result = await handler.handle_case(
        cast(AsyncSession, db),
        _reader(),
        AnnexBReferralRequest(
            case_id="SC-01",
            task_id="TASK-CLEAN-01",
            question="Giải thích trường báo giá bắt buộc cho B2B doanh nghiệp.",
            answer_status="answered",
        ),
    )
    assert result.referral_created is False
    assert result.referral is None
    assert result.crm_writeback_count == 0


# ---------------------------------------------------------------------------
# Integration: 5-layer AnswerOrchestrator -> AnnexBReferralHandler -> HTTP API
# ---------------------------------------------------------------------------


class _StaticRetrievalStub:
    """Minimal retrieval port stub for integration testing SC-05 & SC-09 through pipeline."""

    def __init__(
        self,
        passages: list[PassageSummary],
        live_passages: dict[str, PassageSummary] | None = None,
    ) -> None:
        self._passages = passages
        self._live = (
            {p.passage_id: p for p in passages} if live_passages is None else live_passages
        )

    def compute_rrf_score(
        self,
        vector_rank: int | None,
        fts_rank: int | None,
        trgm_rank: int | None = None,
        *,
        k: int = 60,
    ) -> float:
        _ = vector_rank, fts_rank, trgm_rank, k
        return 0.0

    async def search_hybrid(
        self, user: AuthenticatedUser, spec: HybridQuerySpec
    ) -> list[PassageSummary]:
        _ = user, spec
        return list(self._passages)

    async def fetch_authoritative_passages(
        self, user: AuthenticatedUser, passage_ids: list[str], db: object | None = None
    ) -> dict[str, PassageSummary]:
        _ = user, db
        return {pid: self._live[pid] for pid in passage_ids if pid in self._live}


class _StaticLLMStub:
    def __init__(self, result: LLMGenerationResult) -> None:
        self._result = result

    async def generate(self, request: LLMGenerationRequest) -> LLMGenerationResult:
        _ = request
        return self._result


class _AllowAuditStub:
    async def check_monthly_quota(
        self, db: AsyncSession | None = None, month_key: str | None = None
    ) -> Any:
        _ = db, month_key
        from src.shared.contracts import QuotaStatus

        return QuotaStatus(
            month_key="2026-11",
            packages_used=0,
            package_quota=1000,
            llm_calls_used=0,
            llm_call_quota=2000,
            allowed=True,
        )

    async def record_usage_meter(self, db: AsyncSession | None = None, **kwargs: Any) -> None:
        _ = db, kwargs

    async def record_audit_event(self, db: AsyncSession | None = None, **kwargs: Any) -> None:
        _ = db, kwargs


@pytest.mark.asyncio
async def test_integration_pipeline_holds_feed_annex_b_handler_and_http_3_states() -> None:
    """Integration: AnswerOrchestrator HOLD/STALE feeds AnnexBHandler & HTTP 3-state API."""
    _, db = _make_db()
    reader = _reader()
    owner = _policy_owner()

    # 1. SC-05 Conflicting contract through real PolicyService + AnswerOrchestratorService
    now_vn = datetime.now(VN_TZ)
    orch = AnswerOrchestratorService(
        policy_gate=PolicyService(),
        audit_meter=_AllowAuditStub(),
    )
    sc05_pkg = await orch.execute_pipeline(
        reader,
        AnswerQueryRequest(
            task_id="TASK-INT-SC05",
            question="Hợp đồng DOC-006 giảm 20% mâu thuẫn chính sách DOC-001?",
            scope=ANNEX_B_CONTRACTS[AnnexBCaseId.SC_05].canonical_scope,
        ),
        candidates=[
            ApplicabilityCandidate(
                version_id="VER-DOC001",
                authority_tier=AuthorityTier.POLICY,
                status=PolicyLifecycleStatus.EFFECTIVE,
                effective_from=now_vn - timedelta(days=10),
                scope=ANNEX_B_CONTRACTS[AnnexBCaseId.SC_05].canonical_scope,
            ),
            ApplicabilityCandidate(
                version_id="VER-DOC006",
                authority_tier=AuthorityTier.CUSTOMER_CONTRACT,
                status=PolicyLifecycleStatus.EFFECTIVE,
                effective_from=now_vn - timedelta(days=5),
                scope=ANNEX_B_CONTRACTS[AnnexBCaseId.SC_05].canonical_scope,
            ),
        ],
    )
    assert sc05_pkg.status == AnswerStatus.HOLD

    # 2. SC-09 Withdrawal mid-answer through real 5-layer pipeline (Layer 3 -> Layer 5 withdrawn)
    effective_p = PassageSummary(
        passage_id="PAS-024",
        document_id="DOC-003",
        document_version_id="VER-003",
        title="Quy trình bảo hành Tuyến 2",
        content="Bảo hành Tuyến 2 chuyển hãng trong vòng 48 giờ.",
        source_ref="data/g1/doc003.md",
        page_number=2,
        clause_ref="Điều 2.1",
        language="vi",
        scope=ANNEX_B_CONTRACTS[AnnexBCaseId.SC_09].canonical_scope,
        audience=["reader"],
        status=PolicyLifecycleStatus.EFFECTIVE,
        has_essential_attachments=True,
        effective_from=now_vn - timedelta(days=3),
    )
    withdrawn_p = effective_p.model_copy(update={"status": PolicyLifecycleStatus.WITHDRAWN})
    cf = CriticalFieldItem(
        field_id="CF-WAR-01",
        policy_id="POL-WAR-01",
        policy_version_id="VER-003",
        document_version_id="VER-003",
        field_name="sla_hours",
        field_type=CriticalFieldType.DURATION,
        operator=ComparisonOperator.LE,
        value="48",
        unit="hours",
        approval_role="policy_owner",
        source_clause="Điều 2.1",
        status=PolicyLifecycleStatus.EFFECTIVE,
    )
    sc09_orch = AnswerOrchestratorService(
        retrieval_port=_StaticRetrievalStub([effective_p], live_passages={"PAS-024": withdrawn_p}),
        llm_generator=_StaticLLMStub(
            LLMGenerationResult(
                guidance_text="Bảo hành Tuyến 2 chuyển hãng trong vòng 48 giờ.",
                verbatim_quotes=(effective_p.content,),
                citations=(
                    AnswerCitation(
                        document_id="DOC-003",
                        document_version_id="VER-003",
                        passage_id="PAS-024",
                        title=effective_p.title,
                        page_number=2,
                        clause_ref="Điều 2.1",
                        quoted_text=effective_p.content,
                        evidence_url="/api/v1/knowledge/passages/PAS-024",
                    ),
                ),
            )
        ),
        audit_meter=_AllowAuditStub(),
    )
    sc09_pkg = await sc09_orch.execute_pipeline(
        reader,
        AnswerQueryRequest(
            task_id="TASK-INT-SC09",
            question="Quy trình bảo hành Tuyến 2 inverter_mv?",
            governing_date=date.today(),
            scope=ANNEX_B_CONTRACTS[AnnexBCaseId.SC_09].canonical_scope,
        ),
        candidates=[
            ApplicabilityCandidate(
                version_id="VER-003",
                authority_tier=AuthorityTier.POLICY,
                status=PolicyLifecycleStatus.EFFECTIVE,
                effective_from=now_vn - timedelta(days=3),
                scope=ANNEX_B_CONTRACTS[AnnexBCaseId.SC_09].canonical_scope,
            )
        ],
        critical_fields=[cf],
    )
    assert sc09_pkg.status == AnswerStatus.STALE

    # 3. Exercise HTTP API (/api/v1/referral/annex-b -> GET -> PATCH -> PATCH) with FastAPI app
    async def _override_get_db() -> Any:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    reader_token = create_access_token(reader)
    owner_token = create_access_token(owner)
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Create via /api/v1/referral/annex-b for SC-05 and SC-09
            r5 = await client.post(
                "/api/v1/referral/annex-b",
                headers={"Authorization": f"Bearer {reader_token}"},
                json={
                    "case_id": "SC-05",
                    "task_id": sc05_pkg.task_id,
                    "answer_package_id": sc05_pkg.answer_id,
                    "question": sc05_pkg.original_question,
                    "scope": sc05_pkg.scope,
                    "answer_status": sc05_pkg.status.value,
                    "has_contract_conflict": True,
                },
            )
            assert r5.status_code == 201
            b5 = r5.json()
            assert b5["referral_created"] is True
            assert b5["hold_reason"] == "HOLD_DAT05"
            assert b5["crm_writeback_count"] == 0
            ref_id = b5["referral"]["id"]

            r9 = await client.post(
                "/api/v1/referral/annex-b",
                headers={"Authorization": f"Bearer {reader_token}"},
                json={
                    "case_id": "SC-09",
                    "task_id": sc09_pkg.task_id,
                    "answer_package_id": sc09_pkg.answer_id,
                    "question": sc09_pkg.original_question,
                    "scope": sc09_pkg.scope,
                    "answer_status": sc09_pkg.status.value,
                    "is_withdrawn": True,
                },
            )
            assert r9.status_code == 201
            assert r9.json()["hold_reason"] == "HOLD_SEC05"

            # Reader forbidden from PATCH transition
            forbidden = await client.patch(
                f"/api/v1/referral/{ref_id}",
                headers={"Authorization": f"Bearer {reader_token}"},
                json={"status": "owner_responded", "owner_response": "Unauthorized"},
            )
            assert forbidden.status_code == 403

            # Owner cannot skip referred -> closed (409 SOURCE_CONFLICT)
            skip = await client.patch(
                f"/api/v1/referral/{ref_id}",
                headers={"Authorization": f"Bearer {owner_token}"},
                json={"status": "closed"},
            )
            assert skip.status_code == 409

            # Owner records response -> owner_responded
            step2 = await client.patch(
                f"/api/v1/referral/{ref_id}",
                headers={"Authorization": f"Bearer {owner_token}"},
                json={
                    "status": "owner_responded",
                    "owner_response": "Ưu tiên DOC-001 VER-001 sau rà soát Legal Owner.",
                },
            )
            assert step2.status_code == 200
            assert step2.json()["status"] == "owner_responded"
            assert step2.json()["responded_by"] == owner.user_id

            # Owner closes referral -> closed
            step3 = await client.patch(
                f"/api/v1/referral/{ref_id}",
                headers={"Authorization": f"Bearer {owner_token}"},
                json={"status": "closed", "resolution_note": "Đã xử lý xong, không ghi CRM."},
            )
            assert step3.status_code == 200
            assert step3.json()["status"] == "closed"
            assert step3.json()["closed_by"] == owner.user_id

            # Fetch single referral confirms final closed state
            fetched = await client.get(
                f"/api/v1/referral/{ref_id}",
                headers={"Authorization": f"Bearer {reader_token}"},
            )
            assert fetched.status_code == 200
            assert fetched.json()["status"] == "closed"
    finally:
        app.dependency_overrides.clear()
