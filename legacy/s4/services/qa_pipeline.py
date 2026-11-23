"""
legacy/s4/services/qa_pipeline.py
Luồng điều phối xử lý một câu hỏi chính sách CRM hoàn chỉnh (Giai đoạn 4).
Tuân thủ nghiêm ngặt quy trình 8 bước:
1. input_guard: Làm sạch, kiểm tra rỗng, độ dài, thẻ giả mạo, Prompt Injection.
2. EvidenceProvider (S3): Lấy bằng chứng. Rỗng => NO_EVIDENCE, Lỗi => EVIDENCE_SERVICE_ERROR.
3. evidence_guard: Quét từng chunk bằng chứng, cách ly nếu nghi ngờ chứa chỉ dẫn độc hại.
4. Access & Scope Control: Kiểm tra phân quyền và phạm vi BẰNG CODE dựa trên metadata S3.
   (ĐỀ XUẤT CHƯA ĐƯỢC S3 XÁC NHẬN - Thiếu quyền => ACCESS_DENIED, không mặc định cho phép).
5. token_guard: Ước lượng bảo thủ input tokens. Vượt 6.000 tokens => TOKEN_LIMIT_EXCEEDED.
6. LLMGateway: Gọi LLMClient (tối đa 2 lần; lần 2 chỉ retry khi gặp INVALID_LLM_FORMAT).
7. response_parser & output_guard:
   - Parse JSON theo schema cố định.
   - Gắn metadata S3 (effective_date, scope, policy_owner).
   - verify_all_citations: Xác minh trích dẫn nguyên văn (ranh giới từ, phủ định, ngoại lệ).
   - validate_answer: Kiểm tra 7 trường cố định, độ dài 100-250 từ.
   - check_output_safety: Kiểm tra rò rỉ prompt, lộ key, URL lạ, ngôn ngữ tự duyệt, tư vấn pháp lý, số liệu lạ.
8. Kiểm tra cuối: Trả về một đối tượng PolicyResponse duy nhất. Mọi HOLD đều ghi vào hold_logs.

TUYỆT ĐỐI KHÔNG import Streamlit và không phụ thuộc giao diện người dùng.
"""

from typing import Optional, Dict, Any, List
from legacy.s4.models import PolicyResponse, ResponseStatus, UncertaintyLevel, EvidenceChunk
from legacy.s4.services.hold_reasons import HoldReason, get_hold_info
from legacy.s4.services.evidence_provider import EvidenceProvider, NullEvidenceProvider
from legacy.s4.services.llm_client import LLMClient, MockLLMClient
from legacy.s4.services.token_guard import LLMGateway, estimate_tokens
from legacy.s4.services.input_guard import validate_question, scan_evidence_chunk, sanitize_for_log
from legacy.s4.services.prompt_builder import build_prompts
from legacy.s4.services.response_parser import parse_llm_json_response
from legacy.s4.services.output_guard import check_output_safety
from legacy.s4.services.database import save_hold_log


def _record_and_return_hold(
    question: str,
    reason: HoldReason,
    custom_message: Optional[str] = None
) -> PolicyResponse:
    """Hàm phụ trợ ghi nhật ký trạng thái HOLD an toàn vào database và trả về PolicyResponse."""
    info = get_hold_info(reason)
    message = custom_message or info.message
    
    # Rút gọn câu hỏi khi ghi log để tránh lưu dữ liệu nhạy cảm
    sanitized_q = sanitize_for_log(question)
    save_hold_log(sanitized_q, message, reason_code=info.code)

    return PolicyResponse(
        question=question,
        status=ResponseStatus.HOLD,
        uncertainty_level=UncertaintyLevel.KHONG_XAC_DINH,
        hold_reason_code=info.code,
        hold_reason=message,
        guidance=info.guidance,
        clarifying_question=info.clarifying_question,
        citations=[]
    )


def check_access_permission(
    chunks: List[EvidenceChunk],
    user_context: Optional[Dict[str, Any]]
) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra quyền truy cập tài liệu bằng code dựa trên metadata.
    [LƯU Ý: ĐÂY LÀ BẢN ĐỀ XUẤT TỪ S4, CHƯA ĐƯỢC S3 XÁC NHẬN]
    
    Quy tắc an toàn:
    - Nếu user_context thiếu hoặc không có danh sách roles => ACCESS_DENIED (không mặc định cho phép).
    - Nếu chunk có quy định allowed_roles mà user không sở hữu => ACCESS_DENIED.
    """
    if not user_context or not isinstance(user_context, dict):
        return False, "Thiếu thông tin ngữ cảnh người dùng (user_context)."

    user_roles = set(user_context.get("roles", []))
    if not user_roles:
        return False, "Người dùng không có bất kỳ quyền hạn (roles) nào được ghi nhận."

    for chunk in chunks:
        if chunk.allowed_roles:
            chunk_allowed = set(chunk.allowed_roles)
            if not (user_roles & chunk_allowed):
                return (
                    False,
                    f"Người dùng không có quyền truy cập tài liệu '{chunk.document_name}' "
                    f"(Yêu cầu một trong các quyền: {sorted(list(chunk_allowed))})."
                )

    return True, None


def answer_question(
    question: str,
    user_context: Optional[Dict[str, Any]] = None,
    evidence_provider: Optional[EvidenceProvider] = None,
    llm_gateway: Optional[LLMGateway] = None
) -> PolicyResponse:
    """
    Điều phối luồng xử lý câu hỏi qua 8 bước kiểm soát an toàn nghiêm ngặt.
    """
    provider = evidence_provider or NullEvidenceProvider()
    gateway = llm_gateway or LLMGateway(client=MockLLMClient())

    # --------------------------------------------------------------------------
    # BƯỚC 1: Kiểm tra đầu vào (input_guard)
    # --------------------------------------------------------------------------
    is_valid_input, input_err, pattern_code = validate_question(question)
    if not is_valid_input:
        if pattern_code == "EMPTY_INPUT":
            return _record_and_return_hold(question, HoldReason.EMPTY_INPUT, input_err)
        elif pattern_code == "QUESTION_TOO_LONG":
            return _record_and_return_hold(question, HoldReason.TOKEN_LIMIT_EXCEEDED, input_err)
        else:
            # Các lỗi giả mạo thẻ hoặc Prompt Injection
            return _record_and_return_hold(question, HoldReason.INJECTION_SUSPECTED, input_err)

    # --------------------------------------------------------------------------
    # BƯỚC 2: Truy xuất bằng chứng từ kho chính sách (EvidenceProvider)
    # --------------------------------------------------------------------------
    try:
        chunks = provider.retrieve_evidence(question)
    except Exception as e:
        # Không bao giờ nuốt lỗi (Fail Visibly)
        return _record_and_return_hold(
            question,
            HoldReason.EVIDENCE_SERVICE_ERROR,
            f"Dịch vụ truy xuất bằng chứng S3 gặp sự cố: {str(e)}"
        )

    if not chunks:
        return _record_and_return_hold(question, HoldReason.NO_EVIDENCE)

    # --------------------------------------------------------------------------
    # BƯỚC 3: Quét dữ liệu bằng chứng không đáng tin (evidence_guard)
    # --------------------------------------------------------------------------
    for chunk in chunks:
        is_chunk_safe, chunk_err, _ = scan_evidence_chunk(chunk)
        if not is_chunk_safe:
            # Phát hiện chỉ dẫn độc hại được nhúng trong tài liệu nguồn
            return _record_and_return_hold(
                question,
                HoldReason.INJECTION_SUSPECTED,
                f"CẢNH BÁO: {chunk_err} Tài liệu đã bị cách ly ngay lập tức."
            )

    # --------------------------------------------------------------------------
    # BƯỚC 4: Kiểm tra quyền truy cập và phạm vi bằng code (Access Control)
    # --------------------------------------------------------------------------
    has_permission, perm_err = check_access_permission(chunks, user_context)
    if not has_permission:
        return _record_and_return_hold(question, HoldReason.ACCESS_DENIED, perm_err)

    # --------------------------------------------------------------------------
    # BƯỚC 5: Xây dựng Prompt và kiểm soát ngân sách Token (token_guard)
    # --------------------------------------------------------------------------
    system_prompt, user_prompt = build_prompts(question, chunks)

    # --------------------------------------------------------------------------
    # BƯỚC 6: Gọi LLM qua Cổng duy nhất LLMGateway (Tối đa 2 lần, retry khi lỗi format)
    # --------------------------------------------------------------------------
    gateway.reset_call_count()
    raw_output, call_hold_reason, call_msg = gateway.execute_call(
        prompt=user_prompt,
        system_prompt=system_prompt,
        is_retry=False
    )
    if call_hold_reason:
        return _record_and_return_hold(question, call_hold_reason, call_msg)

    # Phân tích cú pháp lần 1
    parsed_response = parse_llm_json_response(raw_output or "", question, chunks)

    # Nếu gặp lỗi định dạng JSON, cho phép thử lại lần 2 (is_retry=True)
    if (
        parsed_response.status == ResponseStatus.HOLD
        and parsed_response.hold_reason_code == HoldReason.INVALID_LLM_FORMAT.value
    ):
        raw_retry_output, retry_hold_reason, retry_msg = gateway.execute_call(
            prompt=user_prompt,
            system_prompt=system_prompt,
            is_retry=True
        )
        if retry_hold_reason:
            return _record_and_return_hold(question, retry_hold_reason, retry_msg)

        parsed_response = parse_llm_json_response(raw_retry_output or "", question, chunks)

    # Nếu sau khi gọi (kể cả đã retry) vẫn là HOLD thì kết luận HOLD
    if parsed_response.status != ResponseStatus.SUCCESS:
        if not parsed_response.clarifying_question and parsed_response.hold_reason_code:
            try:
                hr = HoldReason(parsed_response.hold_reason_code)
                parsed_response.clarifying_question = get_hold_info(hr).clarifying_question
            except Exception:
                pass
        sanitized_q = sanitize_for_log(question)
        save_hold_log(sanitized_q, parsed_response.hold_reason or "", reason_code=parsed_response.hold_reason_code or "HOLD_GENERAL")
        return parsed_response

    # --------------------------------------------------------------------------
    # BƯỚC 7: Kiểm tra an toàn đầu ra (output_guard)
    # --------------------------------------------------------------------------
    is_safe_output, output_hold, output_msg = check_output_safety(
        answer=parsed_response,
        system_prompt_text=system_prompt,
        evidence_chunks=chunks
    )
    if not is_safe_output and output_hold:
        return _record_and_return_hold(question, output_hold, output_msg)

    # --------------------------------------------------------------------------
    # BƯỚC 8: Kiểm tra cuối cùng và bàn giao kết quả (SUCCESS)
    # --------------------------------------------------------------------------
    return parsed_response

