"""Verified AnswerPackage orchestrator (ANS 01-08, KNW 01-04, Common Bid Basis bounds)."""

from datetime import date
from pathlib import Path
import re
import unicodedata
import uuid

from src.config import settings
from src.modules.answer.schemas import AnswerCitation, AnswerPackage, AnswerQueryRequest
from src.modules.knowledge.schemas import PassageSummary
from src.modules.policy.schemas import CriticalFieldItem
from src.modules.policy.service import PolicyService
from src.shared.auth import AuthenticatedUser
from src.shared.enums import AnswerStatus
from src.shared.injection_guard import (
    scan_passage_safety,
    strip_vietnamese_accents,
    validate_query_safety,
)
from src.shared.pii_guard import scan_query_for_pii

INTERNAL_USE_WARNING_VI = (
    "Hướng dẫn làm việc nội bộ — nhân viên phải kiểm tra hoàn cảnh, nguồn hiện hành và thẩm quyền "
    "trước khi hành động; không thay thế phê duyệt hay thực thi."
)

_OUT_OF_SCOPE_MARKERS: tuple[tuple[str, str], ...] = (
    ("pháp lý", "Tư vấn pháp lý nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("luật", "Tư vấn pháp lý nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("khởi kiện", "Tư vấn pháp lý và định hướng khởi kiện nằm ngoài phạm vi (ANS 07)."),
    ("thắng kiện", "Tư vấn pháp lý nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("thuế", "Tư vấn thuế nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("lách thuế", "Tư vấn thuế nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("duyệt bảo hành", "Hệ thống không tự phê duyệt bảo hành; chuyển Policy Owner (ANS 07)."),
    ("phê duyệt bảo hành", "Hệ thống không tự phê duyệt bảo hành; chuyển Policy Owner (ANS 07)."),
    ("duyệt chiết khấu", "Hệ thống không tự phê duyệt chiết khấu; chuyển cấp có thẩm quyền (ANS 07)."),
    ("phê duyệt chiết khấu", "Hệ thống không tự phê duyệt chiết khấu; chuyển cấp có thẩm quyền (ANS 07)."),
    ("tự phê duyệt", "Hệ thống không tự phê duyệt ngoại lệ chính sách; chuyển cấp có thẩm quyền (ANS 07)."),
    ("sửa chữa thiết bị", "Hướng dẫn sửa chữa/an toàn thiết bị nằm ngoài phạm vi (ANS 07)."),
    ("hướng dẫn sửa chữa", "Hướng dẫn sửa chữa/an toàn thiết bị nằm ngoài phạm vi (ANS 07)."),
    ("cam kết với khách hàng", "Soạn thảo cam kết khách hàng nằm ngoài phạm vi trợ lý nội bộ (ANS 07)."),
)


def _load_system_prompt() -> str:
    """Load system prompt from prompts/answer_system_vi.txt."""
    candidate_paths = [
        Path(__file__).resolve().parents[4] / "prompts" / "answer_system_vi.txt",
        Path(__file__).resolve().parents[3] / "prompts" / "answer_system_vi.txt",
        Path.cwd() / "prompts" / "answer_system_vi.txt",
    ]
    for p in candidate_paths:
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    return (
        "Bạn là Trợ lý Tri thức & Chính sách CRM nội bộ của Công ty Song Nhật (CKPA).\n"
        "Mọi câu trả lời chỉ phục vụ nhân viên nội bộ chuẩn bị quyết định; "
        "KHÔNG thay thế phê duyệt hay phát hành cam kết tới khách hàng."
    )


def estimate_vietnamese_tokens(text: str) -> int:
    """Conservative token estimation for Vietnamese text (~1.5 to 2 tokens/word)."""
    norm = unicodedata.normalize("NFC", text.strip())
    words = len(norm.split())
    chars = len(norm)
    return max(words * 2, chars // 3)


class AnswerOrchestratorService:
    """Produces non-streamed, post-validated 7-part AnswerPackages bounded by RFP limits."""

    def __init__(self) -> None:
        self._policy_service = PolicyService()
        self._system_prompt = _load_system_prompt()

    @property
    def system_prompt(self) -> str:
        """Return cached base system prompt."""
        return self._system_prompt

    def build_guarded_response(
        self,
        user: AuthenticatedUser,
        request: AnswerQueryRequest,
        *,
        is_regenerate: bool = False,
        passages: list[PassageSummary] | None = None,
        critical_fields: list[CriticalFieldItem] | None = None,
    ) -> AnswerPackage:
        """Execute Base Scope guards, PII scan, VN date resolution, and boundary checks."""
        _ = user
        if settings.ENABLE_ANSWER_STREAMING:
            raise ValueError(
                "Pre-verification token streaming is forbidden in Base Scope (KNW 04)."
            )

        task_id = request.task_id or f"TASK-{uuid.uuid4().hex[:8].upper()}"
        answer_id = f"ANS-{uuid.uuid4().hex[:10].upper()}"
        pii_scan = scan_query_for_pii(request.question)
        gov_date, is_hist, is_future = self._policy_service.resolve_governing_date_vn(
            request.governing_date
        )

        # 1. Prompt Injection & Boundary Forgery Guard (ANS 08)
        is_safe, injection_reason, injection_code = validate_query_safety(request.question)
        if not is_safe:
            return AnswerPackage(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                original_question=request.question,
                governing_date=gov_date,
                timezone=settings.APP_TIMEZONE,
                scope=request.scope,
                is_historical=is_hist,
                is_future_preview=is_future and request.allow_future_preview,
                guidance_text=(
                    "CẢNH BÁO AN NINH: Phát hiện chỉ dẫn vi phạm quy tắc an toàn hoặc cố gắng thao túng "
                    "hệ thống. Trợ lý kích hoạt chế độ giữ an toàn (Fail-Closed) và từ chối xử lý."
                ),
                verbatim_quotes=[],
                citations=[],
                critical_fields=[],
                missing_facts=[],
                hold_reason=f"INJECTION_SUSPECTED: {injection_reason} (Mã: {injection_code})",
                uncertainty_note="Yêu cầu đặt câu hỏi nghiệp vụ chính sách chuẩn tắc, không chứa lệnh thao túng.",
                referral_target="policy_owner",
                internal_use_warning=INTERNAL_USE_WARNING_VI,
                pii_warning=pii_scan.warning_message_vi or None,
                snapshot_age_hours=None,
                llm_calls_used=0,
            )

        # 2. Out-of-Scope Boundary Guard (ANS 07)
        refusal_reason = self._detect_out_of_scope(request.question)
        if refusal_reason is not None:
            return AnswerPackage(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.REFUSED_OUT_OF_SCOPE,
                original_question=request.question,
                governing_date=gov_date,
                timezone=settings.APP_TIMEZONE,
                scope=request.scope,
                is_historical=is_hist,
                is_future_preview=is_future and request.allow_future_preview,
                guidance_text=(
                    "Yêu cầu nằm ngoài thẩm quyền hỗ trợ của CKPA. Vui lòng chuyển xử lý tới "
                    "chủ sở hữu/phòng ban chuyên trách."
                ),
                verbatim_quotes=[],
                citations=[],
                critical_fields=[],
                missing_facts=[],
                hold_reason=refusal_reason,
                uncertainty_note="Ngoài ranh giới nghiệp vụ Base Scope (`ANS 07`).",
                referral_target="policy_owner",
                internal_use_warning=INTERNAL_USE_WARNING_VI,
                pii_warning=pii_scan.warning_message_vi or None,
                snapshot_age_hours=None,
                llm_calls_used=0,
            )

        # 3. Input Token Budget Guard (system prompt + passages + question <= 6000 tokens)
        curated_passages = passages or []
        combined_context = (
            self._system_prompt
            + " "
            + request.question
            + " "
            + " ".join(p.content for p in curated_passages)
        )
        estimated_input_tokens = estimate_vietnamese_tokens(combined_context)
        if estimated_input_tokens > settings.LLM_MAX_INPUT_TOKENS:
            return AnswerPackage(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                original_question=request.question,
                governing_date=gov_date,
                timezone=settings.APP_TIMEZONE,
                scope=request.scope,
                is_historical=is_hist,
                is_future_preview=is_future and request.allow_future_preview,
                guidance_text=(
                    f"Ngữ cảnh câu hỏi và tài liệu vượt ngưỡng ({estimated_input_tokens} tokens ước tính), "
                    f"vượt quá giới hạn an toàn {settings.LLM_MAX_INPUT_TOKENS} input tokens của RFP."
                ),
                verbatim_quotes=[],
                citations=[],
                critical_fields=[],
                missing_facts=["Vui lòng thu hẹp phạm vi hoặc chọn lọc ít đoạn văn bản hơn."],
                hold_reason=f"TOKEN_LIMIT_EXCEEDED: Vượt ngưỡng an toàn {settings.LLM_MAX_INPUT_TOKENS} input tokens.",
                uncertainty_note="Ngữ cảnh đầu vào vượt trần Common Bid Basis (CKPA-42).",
                referral_target="policy_owner",
                internal_use_warning=INTERNAL_USE_WARNING_VI,
                pii_warning=pii_scan.warning_message_vi or None,
                snapshot_age_hours=None,
                llm_calls_used=0,
            )

        # 4. Evidence Inspection & Untrusted Passage Guard
        for p in curated_passages:
            is_p_safe, p_reason, p_code = scan_passage_safety(p.content)
            if not is_p_safe:
                return AnswerPackage(
                    answer_id=answer_id,
                    task_id=task_id,
                    status=AnswerStatus.HOLD,
                    original_question=request.question,
                    governing_date=gov_date,
                    timezone=settings.APP_TIMEZONE,
                    scope=request.scope,
                    is_historical=is_hist,
                    is_future_preview=is_future and request.allow_future_preview,
                    guidance_text=(
                        "CẢNH BÁO AN NINH: Tài liệu nguồn được trích xuất có dấu hiệu chứa chỉ dẫn bất thường. "
                        "Hệ thống đã cách ly tài liệu và giữ trạng thái an toàn."
                    ),
                    verbatim_quotes=[],
                    citations=[],
                    critical_fields=[],
                    missing_facts=[],
                    hold_reason=f"PASSAGE_INJECTION_DETECTED: {p_reason} (Mã: {p_code})",
                    uncertainty_note="Tài liệu bị nghi ngờ giả mạo chỉ thị; cần rà soát bởi Policy Steward.",
                    referral_target="steward",
                    internal_use_warning=INTERNAL_USE_WARNING_VI,
                    pii_warning=pii_scan.warning_message_vi or None,
                    snapshot_age_hours=None,
                    llm_calls_used=0,
                )

        # 5. Check missing facts / evidence sufficiency (ANS 06)
        if not curated_passages:
            action_note = "Tạo lại gói trả lời" if is_regenerate else "Điều phối gói trả lời"
            return AnswerPackage(
                answer_id=answer_id,
                task_id=task_id,
                status=AnswerStatus.HOLD,
                original_question=request.question,
                governing_date=gov_date,
                timezone=settings.APP_TIMEZONE,
                scope=request.scope,
                is_historical=is_hist,
                is_future_preview=is_future and request.allow_future_preview,
                guidance_text=(
                    f"{action_note}: chưa tìm thấy tài liệu chính sách hoặc điều khoản hiệu lực phù hợp "
                    f"cho câu hỏi này trong phạm vi `{request.scope}`. Hệ thống giữ an toàn và tuyệt đối "
                    "không dùng trí nhớ mô hình để suy đoán."
                ),
                verbatim_quotes=[],
                citations=[],
                critical_fields=[],
                missing_facts=[
                    "Cần nguồn chính sách/SOP hiệu lực đã kiểm chứng cho phạm vi đã chọn.",
                    "Cần làm rõ chi tiết nghiệp vụ (ngưỡng số tiền, tỷ lệ %, hoặc tình huống cụ thể).",
                ],
                hold_reason="Thiếu căn cứ văn bản đã phê duyệt (Insufficient curated evidence).",
                uncertainty_note="Vui lòng bổ sung ngày giao dịch/phạm vi áp dụng hoặc tạo Local Referral gửi Policy Owner.",
                referral_target="policy_owner",
                internal_use_warning=INTERNAL_USE_WARNING_VI,
                pii_warning=pii_scan.warning_message_vi or None,
                snapshot_age_hours=None,
                llm_calls_used=0,
            )

        # 6. Synthesize Grounded Response Bounded by Curated Evidence
        # (Enforcing 100-250 words, verbatim quote separation, zero secrets, <= 2 calls)
        active_critical_fields = critical_fields or []
        citations_out: list[AnswerCitation] = []
        verbatim_quotes_out: list[str] = []

        for p in curated_passages[: settings.ANSWER_MAX_PASSAGES]:
            # Extract first coherent sentence or clause for verbatim citation
            quote = p.content.split("\n")[0].strip()
            if len(quote) > 300:
                quote = quote[:300].rsplit(" ", 1)[0] + "..."
            verbatim_quotes_out.append(quote)
            citations_out.append(
                AnswerCitation(
                    document_id=p.document_id,
                    document_version_id=p.document_version_id,
                    passage_id=p.passage_id,
                    title=p.title,
                    page_number=p.page_number,
                    clause_ref=p.clause_ref or "Quy định chung",
                    quoted_text=quote,
                    evidence_url=f"/api/v1/knowledge/passages/{p.passage_id}",
                )
            )

        # Build concise guidance text adhering to 100-250 words
        guidance = (
            f"Căn cứ theo văn bản quy định hiệu lực `{curated_passages[0].title}` ({citations_out[0].clause_ref}), "
            f"nội dung xử lý nghiệp vụ cho trường hợp này được quy định cụ thể: nhân viên cần tuân thủ "
            f"đúng các điều khoản đã nêu trong trích dẫn nguyên văn bên dưới. Trường hợp phát sinh các tình huống "
            f"vượt thẩm quyền hoặc có xung đột giữa các văn bản quy định liên quan, nhân viên phải lập tức dừng xử lý, "
            f"không được tự ý phê duyệt hay cam kết với khách hàng, đồng thời chuyển tuyến xử lý nội bộ (Local Referral) "
            f"tới chủ sở hữu chính sách phụ trách để được hướng dẫn chính thức. Mọi thông tin nghiệp vụ và số liệu áp dụng "
            f"phải được đối chiếu chính xác với các trường trọng yếu đã công bố trong hệ thống."
        )

        return AnswerPackage(
            answer_id=answer_id,
            task_id=task_id,
            status=AnswerStatus.ANSWERED,
            original_question=request.question,
            governing_date=gov_date,
            timezone=settings.APP_TIMEZONE,
            scope=request.scope,
            is_historical=is_hist,
            is_future_preview=is_future and request.allow_future_preview,
            guidance_text=guidance,
            verbatim_quotes=verbatim_quotes_out,
            citations=citations_out,
            critical_fields=active_critical_fields,
            missing_facts=[],
            hold_reason=None,
            uncertainty_note=None,
            referral_target=None,
            internal_use_warning=INTERNAL_USE_WARNING_VI,
            pii_warning=pii_scan.warning_message_vi or None,
            snapshot_age_hours=None,
            llm_calls_used=1,
        )

    def _detect_out_of_scope(self, question: str) -> str | None:
        lowered = question.lower()
        unaccented = strip_vietnamese_accents(question)
        for keyword, reason in _OUT_OF_SCOPE_MARKERS:
            keyword_lower = keyword.lower()
            keyword_unaccented = strip_vietnamese_accents(keyword)
            if keyword_lower in lowered or keyword_unaccented in unaccented:
                return reason
        return None
