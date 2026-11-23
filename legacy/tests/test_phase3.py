"""
legacy/tests/test_phase3.py
Bộ kiểm thử tự động cho Giai đoạn 3:
- CKPA-39 (Bản vá trích dẫn): Ranh giới từ, độ dài tối thiểu (MIN_CITATION_WORDS), ngữ cảnh phủ định (NEGATION_CONTEXT_TRUNCATED)
- CKPA-41 (Prompt tiếng Việt & Bộ phân tích JSON): Ranh giới XML, bảo toàn số liệu/ngày/phủ định, parser nghiêm ngặt
- CKPA-42 (Giới hạn Token & Gateway): Ước lượng bảo thủ, chặn trước khi gọi nếu > 6.000 token, chặn lần gọi thứ 3, max_tokens=900
"""

import pytest
import json
from legacy.s4 import config
from legacy.s4.models import (
    Citation,
    EvidenceChunk,
    PolicyResponse,
    ResponseStatus,
    UncertaintyLevel,
)
from legacy.s4.services.citation_verifier import verify_citation
from legacy.s4.services.hold_reasons import HoldReason
from legacy.s4.services.prompt_builder import build_prompts
from legacy.s4.services.response_parser import parse_llm_json_response
from legacy.s4.services.token_guard import estimate_tokens, LLMGateway
from legacy.s4.services.llm_client import MockLLMClient
from legacy.tests.fixtures.sample_evidence import (
    SAMPLE_CHUNK_ACCOUNT,
    SAMPLE_CHUNK_ATM_LIMIT,
    SAMPLE_EVIDENCE_FIXTURE,
)


def generate_words(n: int) -> str:
    """Tạo chuỗi gồm n từ."""
    return " ".join([f"từ_{i}" for i in range(1, n + 1)])


# ==============================================================================
# 1. KIỂM THỬ BẢN VÁ TRÍCH DẪN (CKPA-39 - Mục 3.0)
# ==============================================================================
class TestPatchedCitationVerifier:
    """Kiểm tra bản vá ranh giới từ, độ dài tối thiểu và phủ định."""

    def test_too_short_citation_rejected(self):
        """Dưới MIN_CITATION_WORDS (4 từ) => Bị loại."""
        short_cit = Citation(
            document_name=SAMPLE_CHUNK_ACCOUNT.document_name,
            section=SAMPLE_CHUNK_ACCOUNT.section,
            verbatim_quote="Khách hàng cá",  # 3 từ
        )
        is_valid, reason = verify_citation(short_cit, SAMPLE_EVIDENCE_FIXTURE)
        assert is_valid is False
        assert "quá ngắn" in reason

    def test_middle_of_word_cut_rejected(self):
        """Cắt xén ngang giữa từ ('hách hàng' thay vì 'Khách hàng') => Bị loại."""
        cut_cit = Citation(
            document_name=SAMPLE_CHUNK_ACCOUNT.document_name,
            section=SAMPLE_CHUNK_ACCOUNT.section,
            verbatim_quote="hách hàng cá nhân là công dân",
        )
        is_valid, reason = verify_citation(cut_cit, SAMPLE_EVIDENCE_FIXTURE)
        assert is_valid is False
        assert "ranh giới từ" in reason

    def test_negation_context_truncated_rejected(self):
        """
        Nguồn: 'Khách hàng cá nhân không được phép rút quá 20 triệu VNĐ...'
        Trích bị cắt: 'được phép rút quá 20 triệu VNĐ' (cắt bỏ từ 'không')
        => Phải bị loại với mã NEGATION_CONTEXT_TRUNCATED.
        """
        truncated_cit = Citation(
            document_name=SAMPLE_CHUNK_ATM_LIMIT.document_name,
            section=SAMPLE_CHUNK_ATM_LIMIT.section,
            verbatim_quote="được phép rút quá 20 triệu VNĐ một lần",
        )
        is_valid, reason = verify_citation(truncated_cit, [SAMPLE_CHUNK_ATM_LIMIT])
        assert is_valid is False
        assert "NEGATION_CONTEXT_TRUNCATED" in reason

    def test_full_negation_quote_accepted(self):
        """Trích đủ cả cụm phủ định ('không được phép...') => Được chấp nhận."""
        full_cit = Citation(
            document_name=SAMPLE_CHUNK_ATM_LIMIT.document_name,
            section=SAMPLE_CHUNK_ATM_LIMIT.section,
            verbatim_quote="không được phép rút quá 20 triệu VNĐ một lần",
        )
        is_valid, reason = verify_citation(full_cit, [SAMPLE_CHUNK_ATM_LIMIT])
        assert is_valid is True
        assert "khớp 100%" in reason


# ==============================================================================
# 2. KIỂM THỬ PROMPT TIẾNG VIỆT (CKPA-41 - Mục 3.2)
# ==============================================================================
class TestPromptBuilder:
    """Kiểm tra việc lắp ghép Prompt tiếng Việt và ranh giới an toàn."""

    def test_prompt_contains_required_blocks_and_no_secrets(self):
        """Prompt chứa đầy đủ các khối <cau_hoi>, <bang_chung> và không chứa API key."""
        question = "Khách hàng mở tài khoản eKYC cần giấy tờ gì?"
        system_p, user_p = build_prompts(question, SAMPLE_EVIDENCE_FIXTURE)

        # Kiểm tra khối thẻ
        assert "<cau_hoi>" in user_p
        assert "</cau_hoi>" in user_p
        assert question in user_p
        assert '<bang_chung id="chunk_01"' in user_p
        assert "</bang_chung>" in user_p

        # Kiểm tra không chứa thông tin bí mật hay API key
        combined = f"{system_p}\n{user_p}".lower()
        for secret_pattern in ["sk-", "api_key=", "secret_key", "password", "bearer "]:
            assert secret_pattern not in combined

    def test_unaccented_question_preserved_verbatim(self):
        """Câu hỏi thiếu dấu được giữ nguyên vẹn 100%, không bị sửa đổi."""
        unaccented_q = "khach hang mo tai khoan ekyc han muc bao nhieu tien 1 ngay?"
        _, user_p = build_prompts(unaccented_q, SAMPLE_EVIDENCE_FIXTURE)
        assert unaccented_q in user_p

    def test_amounts_dates_and_negations_preserved(self):
        """Bảo toàn số tiền, ngày tháng và từ phủ định trong câu hỏi."""
        complex_q = (
            "Khách hàng VIP không được miễn phí thường niên 11.000 VNĐ "
            "vào ngày 15/01/2025 đúng không?"
        )
        _, user_p = build_prompts(complex_q, SAMPLE_EVIDENCE_FIXTURE)
        assert "11.000 VNĐ" in user_p
        assert "15/01/2025" in user_p
        assert "không được" in user_p


# ==============================================================================
# 3. KIỂM THỬ BỘ PHÂN TÍCH ĐẦU RA (CKPA-41 - Mục 3.3)
# ==============================================================================
class TestResponseParser:
    """Kiểm tra parser JSON nghiêm ngặt theo schema cố định."""

    def test_valid_json_response_parsed_successfully(self):
        """JSON hợp lệ chuẩn schema => Chuyển thành PolicyResponse thành công."""
        valid_json = json.dumps({
            "status": "SUCCESS",
            "short_explanation": generate_words(100),
            "required_information": "CCCD gắn chip",
            "uncertainty_level": "CAO",
            "citations": [
                {
                    "chunk_id": "chunk_01",
                    "verbatim_quote": "Khách hàng cá nhân là công dân Việt Nam từ đủ 18 tuổi trở lên"
                }
            ]
        }, ensure_ascii=False)

        response = parse_llm_json_response(valid_json, "Câu hỏi test", SAMPLE_EVIDENCE_FIXTURE)
        assert response.status == ResponseStatus.SUCCESS
        assert response.uncertainty_level == UncertaintyLevel.CAO
        assert response.effective_date == "2025-01-15"  # Trích xuất từ metadata chunk_01
        assert response.scope == "Khách hàng cá nhân toàn hệ thống"
        assert len(response.citations) == 1
        assert response.citations[0].document_name == SAMPLE_CHUNK_ACCOUNT.document_name

    def test_malformed_json_returns_invalid_format_hold(self):
        """JSON lỗi cú pháp => Trả về HOLD với mã INVALID_LLM_FORMAT."""
        malformed = "{ status: 'SUCCESS', short_explanation: ... "
        response = parse_llm_json_response(malformed, "Câu hỏi test", SAMPLE_EVIDENCE_FIXTURE)
        assert response.status == ResponseStatus.HOLD
        assert response.hold_reason_code == HoldReason.INVALID_LLM_FORMAT.value

    def test_extra_text_around_json_rejected(self):
        """Có văn bản thừa ngoài JSON => Bị từ chối (không dùng regex cứu)."""
        text_with_json = (
            "Chào bạn, dưới đây là câu trả lời:\n"
            + json.dumps({
                "status": "SUCCESS",
                "short_explanation": generate_words(100),
                "required_information": "CCCD",
                "uncertainty_level": "CAO",
                "citations": []
            })
            + "\nHy vọng thông tin hữu ích!"
        )
        response = parse_llm_json_response(text_with_json, "Câu hỏi test", SAMPLE_EVIDENCE_FIXTURE)
        assert response.status == ResponseStatus.HOLD
        assert response.hold_reason_code == HoldReason.INVALID_LLM_FORMAT.value

    def test_missing_keys_rejected(self):
        """Thiếu trường bắt buộc trong JSON => Bị từ chối."""
        missing_keys_json = json.dumps({
            "status": "SUCCESS",
            "required_information": "CCCD",
            # Thiếu short_explanation, uncertainty_level, citations
        })
        response = parse_llm_json_response(missing_keys_json, "Câu hỏi test", SAMPLE_EVIDENCE_FIXTURE)
        assert response.status == ResponseStatus.HOLD
        assert response.hold_reason_code == HoldReason.INVALID_LLM_FORMAT.value

    def test_extra_unknown_keys_rejected(self):
        """Có trường lạ ngoài schema => Bị từ chối."""
        extra_keys_json = json.dumps({
            "status": "SUCCESS",
            "short_explanation": generate_words(100),
            "required_information": "CCCD",
            "uncertainty_level": "CAO",
            "citations": [],
            "unknown_extra_field": "Hacker injection"
        })
        response = parse_llm_json_response(extra_keys_json, "Câu hỏi test", SAMPLE_EVIDENCE_FIXTURE)
        assert response.status == ResponseStatus.HOLD
        assert response.hold_reason_code == HoldReason.INVALID_LLM_FORMAT.value

    def test_invalid_uncertainty_rejected(self):
        """uncertainty_level không có trong Enum => Bị từ chối."""
        bad_uncertainty_json = json.dumps({
            "status": "SUCCESS",
            "short_explanation": generate_words(100),
            "required_information": "CCCD",
            "uncertainty_level": "RAT_CHAC_CHAN",  # Sai enum
            "citations": []
        })
        response = parse_llm_json_response(bad_uncertainty_json, "Câu hỏi test", SAMPLE_EVIDENCE_FIXTURE)
        assert response.status == ResponseStatus.HOLD
        assert response.hold_reason_code == HoldReason.INVALID_LLM_FORMAT.value

    def test_hold_signal_from_llm_mapped_to_proper_reason(self):
        """Tín hiệu HOLD chủ động từ LLM => Ánh xạ đúng HoldReason."""
        llm_hold_json = json.dumps({
            "status": "HOLD",
            "short_explanation": "",
            "required_information": "",
            "uncertainty_level": "KHONG_XAC_DINH",
            "citations": [],
            "hold_reason_code": "INSUFFICIENT_EVIDENCE"
        })
        response = parse_llm_json_response(llm_hold_json, "Câu hỏi test", SAMPLE_EVIDENCE_FIXTURE)
        assert response.status == ResponseStatus.HOLD
        assert response.hold_reason_code == HoldReason.INSUFFICIENT_EVIDENCE.value


# ==============================================================================
# 4. KIỂM THỬ GIỚI HẠN TOKEN & GATEWAY (CKPA-42 - Mục 3.4)
# ==============================================================================
class TestTokenGuardAndGateway:
    """Kiểm tra bộ đếm Token và cổng LLMGateway."""

    def test_token_estimation_conservative_formula(self):
        """Kiểm tra công thức ước lượng token: max(từ * 3, ký tự / 2)."""
        text = "Một hai ba bốn năm"  # 5 từ, 18 ký tự
        # 5 * 3 = 15; 18 // 2 = 9 => max là 15
        assert estimate_tokens(text) == 15

    def test_input_exceeds_6000_tokens_triggers_hold_and_skips_llm(self):
        """
        Ước lượng input > 6.000 tokens => Kích hoạt HOLD TOKEN_LIMIT_EXCEEDED
        và TUYỆT ĐỐI KHÔNG gọi LLM (mock_client.call_count == 0).
        """
        mock_client = MockLLMClient()
        gateway = LLMGateway(client=mock_client)

        # Tạo prompt khổng lồ: 2.100 từ * 3 = 6.300 tokens > 6.000
        huge_prompt = generate_words(2100)
        output, hold_reason, msg = gateway.execute_call(prompt=huge_prompt)

        assert output is None
        assert hold_reason == HoldReason.TOKEN_LIMIT_EXCEEDED
        assert "vượt quá giới hạn cho phép" in msg
        assert mock_client.call_count == 0  # Không có cuộc gọi mạng nào được thực hiện

    def test_call_limit_third_call_blocked(self):
        """
        Tối đa 2 cuộc gọi / package.
        Lần 1: Thành công.
        Lần 2 (is_retry=True): Thành công.
        Lần 3: Bị chặn ngay lập tức => HOLD CALL_LIMIT_EXCEEDED.
        """
        mock_client = MockLLMClient(predefined_response="{}")
        gateway = LLMGateway(client=mock_client)

        # Lần 1
        out1, reason1, _ = gateway.execute_call("Câu hỏi lần 1")
        assert out1 == "{}"
        assert reason1 is None
        assert gateway.call_count == 1

        # Lần 2 (Retry)
        out2, reason2, _ = gateway.execute_call("Câu hỏi lần 2 thử lại", is_retry=True)
        assert out2 == "{}"
        assert reason2 is None
        assert gateway.call_count == 2

        # Lần 3 (Vượt hạn mức)
        out3, reason3, msg3 = gateway.execute_call("Câu hỏi lần 3")
        assert out3 is None
        assert reason3 == HoldReason.CALL_LIMIT_EXCEEDED
        assert "Đã đạt giới hạn tối đa" in msg3
        assert mock_client.call_count == 2  # Không tăng lên 3

    def test_max_output_tokens_passed_to_client(self):
        """Kiểm tra max_tokens=900 luôn được truyền sang LLMClient."""
        mock_client = MockLLMClient(predefined_response="{}")
        gateway = LLMGateway(client=mock_client)

        gateway.execute_call("Câu hỏi kiểm tra max tokens")
        assert mock_client.last_max_tokens == 900
        assert mock_client.last_max_tokens == config.MAX_OUTPUT_TOKENS

    def test_no_silent_truncation(self):
        """Không có hành vi âm thầm cắt bớt nội dung prompt."""
        mock_client = MockLLMClient(predefined_response="{}")
        gateway = LLMGateway(client=mock_client)

        original_prompt = "Nội dung câu hỏi nguyên vẹn không bị cắt gọt bớt bất kỳ từ nào."
        gateway.execute_call(original_prompt)
        assert mock_client.last_prompt == original_prompt

