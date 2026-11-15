"""Verified AnswerPackage orchestrator (ANS 01-08, KNW 01-04, Common Bid Basis bounds)."""

import uuid

from src.config import settings
from src.modules.answer.schemas import AnswerPackage, AnswerQueryRequest
from src.modules.policy.service import PolicyService
from src.shared.auth import AuthenticatedUser
from src.shared.enums import AnswerStatus
from src.shared.pii_guard import scan_query_for_pii

INTERNAL_USE_WARNING_VI = (
    "Hướng dẫn làm việc nội bộ — nhân viên phải kiểm tra hoàn cảnh, nguồn hiện hành và thẩm quyền "
    "trước khi hành động; không thay thế phê duyệt hay thực thi."
)

_OUT_OF_SCOPE_MARKERS: tuple[tuple[str, str], ...] = (
    ("pháp lý", "Tư vấn pháp lý nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("luật", "Tư vấn pháp lý nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("thuế", "Tư vấn thuế nằm ngoài phạm vi trợ lý (ANS 07)."),
    ("duyệt bảo hành", "Hệ thống không tự phê duyệt bảo hành; chuyển Policy Owner."),
    ("duyệt chiết khấu", "Hệ thống không tự phê duyệt chiết khấu; chuyển cấp có thẩm quyền."),
    ("sửa chữa thiết bị", "Hướng dẫn sửa chữa/an toàn thiết bị nằm ngoài phạm vi (ANS 07)."),
)


class AnswerOrchestratorService:
    """Produces non-streamed, post-validated 7-part AnswerPackages bounded by RFP limits."""

    def __init__(self) -> None:
        self._policy_service = PolicyService()

    def build_guarded_response(
        self,
        user: AuthenticatedUser,
        request: AnswerQueryRequest,
        *,
        is_regenerate: bool = False,
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

        action_note = "Tạo lại gói trả lời" if is_regenerate else "Khung điều phối hợp đồng 7 phần"
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
                f"{action_note}: chưa có bằng chứng chính sách hợp lệ được nạp cho câu hỏi này; "
                "hệ thống HOLD kết luận và không dùng trí nhớ mô hình để suy đoán."
            ),
            verbatim_quotes=[],
            citations=[],
            critical_fields=[],
            missing_facts=["Cần nguồn chính sách/SOP hiệu lực đã kiểm chứng cho phạm vi đã chọn."],
            hold_reason="Insufficient verified curated evidence; fail-closed HOLD enforced.",
            uncertainty_note="Vui lòng bổ sung ngày giao dịch/phạm vi hoặc tạo Local Referral.",
            referral_target="policy_owner",
            internal_use_warning=INTERNAL_USE_WARNING_VI,
            pii_warning=pii_scan.warning_message_vi or None,
            snapshot_age_hours=None,
            llm_calls_used=0,
        )

    def _detect_out_of_scope(self, question: str) -> str | None:
        lowered = question.lower()
        for keyword, reason in _OUT_OF_SCOPE_MARKERS:
            if keyword in lowered:
                return reason
        return None
