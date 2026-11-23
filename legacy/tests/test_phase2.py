"""
legacy/tests/test_phase2.py
Bộ kiểm thử tự động cho Giai đoạn 2:
- CKPA-40: 7 Field cố định và hàm validate_answer
  (trả lời hợp lệ, thiếu từng trường, giải thích 99/100/250/251 từ, uncertainty_level sai, ngày sai)
- CKPA-39: Trích dẫn nguyên văn và hàm verify_citation
  (khớp nguyên văn, sai 1 ký tự, đổi dấu tiếng Việt, khác khoảng trắng/xuống dòng, sai tên tài liệu, loại toàn bộ)
- CKPA-47: 13 mã HoldReason đầy đủ thông điệp và hướng dẫn
"""

import pytest
from legacy.s4 import config
from legacy.s4.models import (
    PolicyResponse,
    ResponseStatus,
    UncertaintyLevel,
    Citation,
    validate_answer,
)
from legacy.s4.services.citation_verifier import verify_citation, verify_all_citations
from legacy.s4.services.hold_reasons import HoldReason, get_hold_info
from legacy.tests.fixtures.sample_evidence import (
    SAMPLE_CHUNK_ACCOUNT,
    SAMPLE_CHUNK_FEE,
    SAMPLE_EVIDENCE_FIXTURE,
)


def generate_vietnamese_words(n: int) -> str:
    """Tạo chuỗi tiếng Việt chuẩn gồm đúng n từ."""
    return " ".join([f"từ_{i}" for i in range(1, n + 1)])


@pytest.fixture
def valid_citation() -> Citation:
    """Tạo citation hợp lệ đối chiếu với fixture."""
    return Citation(
        document_name=SAMPLE_CHUNK_ACCOUNT.document_name,
        section=SAMPLE_CHUNK_ACCOUNT.section,
        verbatim_quote="Khách hàng cá nhân là công dân Việt Nam từ đủ 18 tuổi trở lên",
        clause_code=SAMPLE_CHUNK_ACCOUNT.clause_code,
        source_url=SAMPLE_CHUNK_ACCOUNT.source_url,
    )


@pytest.fixture
def valid_policy_response(valid_citation: Citation) -> PolicyResponse:
    """Tạo PolicyResponse hoàn toàn hợp lệ (100 từ giải thích)."""
    return PolicyResponse(
        question="Điều kiện mở tài khoản cá nhân?",
        status=ResponseStatus.SUCCESS,
        effective_date="2025-01-15",
        scope="Khách hàng cá nhân toàn hệ thống",
        short_explanation=generate_vietnamese_words(100),
        required_information="CCCD gắn chip còn hiệu lực",
        policy_owner="Khối Vận hành & Khối Bán lẻ",
        uncertainty_level=UncertaintyLevel.CAO,
        citations=[valid_citation],
    )


# ==============================================================================
# 1. KIỂM THỬ FIELD CỐ ĐỊNH & VALIDATE_ANSWER (CKPA-40)
# ==============================================================================
class TestFixedFieldsValidation:
    """Kiểm tra toàn diện hàm validate_answer."""

    def test_valid_answer_passes_validation(self, valid_policy_response: PolicyResponse):
        """Câu trả lời hợp lệ phải vượt qua kiểm tra không có lỗi nào."""
        errors = validate_answer(valid_policy_response)
        assert errors == []

    @pytest.mark.parametrize(
        "field_name",
        ["effective_date", "scope", "short_explanation", "required_information", "policy_owner"],
    )
    def test_missing_required_fields_rejected(
        self, valid_policy_response: PolicyResponse, field_name: str
    ):
        """Kiểm tra: Thiếu bất kỳ trường nào trong 5 trường bắt buộc đều bị từ chối."""
        setattr(valid_policy_response, field_name, "")
        errors = validate_answer(valid_policy_response)
        assert len(errors) > 0
        assert any("không được để trống" in err for err in errors)

    def test_explanation_boundary_99_words_rejected(self, valid_policy_response: PolicyResponse):
        """99 từ: Dưới ngưỡng tối thiểu 100 từ => Bị từ chối."""
        valid_policy_response.short_explanation = generate_vietnamese_words(99)
        errors = validate_answer(valid_policy_response)
        assert any("99 từ" in err and "giới hạn cho phép" in err for err in errors)

    def test_explanation_boundary_100_words_accepted(self, valid_policy_response: PolicyResponse):
        """100 từ: Ngưỡng tối thiểu hợp lệ => Chấp nhận."""
        valid_policy_response.short_explanation = generate_vietnamese_words(100)
        errors = validate_answer(valid_policy_response)
        assert errors == []

    def test_explanation_boundary_250_words_accepted(self, valid_policy_response: PolicyResponse):
        """250 từ: Ngưỡng tối đa hợp lệ => Chấp nhận."""
        valid_policy_response.short_explanation = generate_vietnamese_words(250)
        errors = validate_answer(valid_policy_response)
        assert errors == []

    def test_explanation_boundary_251_words_rejected(self, valid_policy_response: PolicyResponse):
        """251 từ: Vượt ngưỡng tối đa 250 từ => Bị từ chối."""
        valid_policy_response.short_explanation = generate_vietnamese_words(251)
        errors = validate_answer(valid_policy_response)
        assert any("251 từ" in err and "giới hạn cho phép" in err for err in errors)

    def test_invalid_uncertainty_level_rejected(self, valid_policy_response: PolicyResponse):
        """Mức độ chắc chắn ngoài Enum hoặc là HOLD => Bị từ chối."""
        # Trường hợp giá trị lạ
        valid_policy_response.uncertainty_level = "BAT_KY"  # type: ignore
        errors = validate_answer(valid_policy_response)
        assert any("không hợp lệ" in err for err in errors)

        # Trường hợp KHONG_XAC_DINH trong câu trả lời tự nhận thành công
        valid_policy_response.uncertainty_level = UncertaintyLevel.KHONG_XAC_DINH
        errors_hold = validate_answer(valid_policy_response)
        assert any("Không xác định / HOLD" in err for err_msg in errors_hold for err in [err_msg])

    @pytest.mark.parametrize("invalid_date", ["2025-02-30", "15-13-2025", "ngay-mai", "chua ro"])
    def test_invalid_date_format_rejected(
        self, valid_policy_response: PolicyResponse, invalid_date: str
    ):
        """Ngày hiệu lực sai định dạng hoặc không tồn tại trên lịch => Bị từ chối."""
        valid_policy_response.effective_date = invalid_date
        errors = validate_answer(valid_policy_response)
        assert any("không đúng định dạng ngày hợp lệ" in err for err in errors)

    def test_valid_vietnamese_date_accepted(self, valid_policy_response: PolicyResponse):
        """Ngày hiệu lực theo chuẩn Việt Nam DD/MM/YYYY => Chấp nhận."""
        valid_policy_response.effective_date = "31/12/2025"
        errors = validate_answer(valid_policy_response)
        assert errors == []

    def test_missing_citations_rejected(self, valid_policy_response: PolicyResponse):
        """Không có citation nào => Bị từ chối."""
        valid_policy_response.citations = []
        errors = validate_answer(valid_policy_response)
        assert any("phải có ít nhất 1 trích dẫn" in err for err in errors)


# ==============================================================================
# 2. KIỂM THỬ TRÍCH DẪN NGUYÊN VĂN (CKPA-39)
# ==============================================================================
class TestVerbatimCitationVerification:
    """Kiểm tra logic xác minh trích dẫn nguyên văn bằng code."""

    def test_exact_verbatim_match_accepted(self, valid_citation: Citation):
        """Khớp nguyên văn 100% => Hợp lệ."""
        is_valid, reason = verify_citation(valid_citation, SAMPLE_EVIDENCE_FIXTURE)
        assert is_valid is True
        assert "khớp 100%" in reason

    def test_single_character_mismatch_rejected(self, valid_citation: Citation):
        """Sai 1 ký tự (19 thay vì 18) => Bị loại bỏ."""
        valid_citation.verbatim_quote = (
            "Khách hàng cá nhân là công dân Việt Nam từ đủ 19 tuổi trở lên"
        )
        is_valid, reason = verify_citation(valid_citation, SAMPLE_EVIDENCE_FIXTURE)
        assert is_valid is False
        assert "không khớp nguyên văn từng ký tự" in reason

    def test_vietnamese_accent_change_rejected(self, valid_citation: Citation):
        """Thay đổi dấu tiếng Việt ('đũ' thay vì 'đủ') => Bị loại bỏ (Không so khớp mờ)."""
        valid_citation.verbatim_quote = (
            "Khách hàng cá nhân là công dân Việt Nam từ đũ 18 tuổi trở lên"
        )
        is_valid, reason = verify_citation(valid_citation, SAMPLE_EVIDENCE_FIXTURE)
        assert is_valid is False
        assert "không khớp nguyên văn từng ký tự" in reason

    def test_different_whitespace_and_newlines_accepted(self, valid_citation: Citation):
        """Đúng nội dung nhưng khác khoảng trắng/xuống dòng => Phải khớp sau chuẩn hóa."""
        valid_citation.verbatim_quote = (
            "Khách    hàng\n\n cá nhân là công dân\t Việt Nam từ đủ   18 tuổi trở lên"
        )
        is_valid, reason = verify_citation(valid_citation, SAMPLE_EVIDENCE_FIXTURE)
        assert is_valid is True
        assert "khớp 100%" in reason

    def test_wrong_document_name_rejected(self, valid_citation: Citation):
        """Đúng câu trích dẫn nhưng sai tên tài liệu nguồn => Bị loại bỏ."""
        valid_citation.document_name = "Văn bản số 99/Bịa-tên-nguồn"
        is_valid, reason = verify_citation(valid_citation, SAMPLE_EVIDENCE_FIXTURE)
        assert is_valid is False
        assert "Không tìm thấy văn bản" in reason

    def test_all_citations_invalid_leads_to_empty(self):
        """Khi toàn bộ citation bị sai => Danh sách hợp lệ rỗng (dẫn đến HOLD)."""
        fake_citations = [
            Citation(
                document_name="Tài liệu A",
                section="Điều 1",
                verbatim_quote="Câu nói không có thật trong nguồn",
            ),
            Citation(
                document_name="Tài liệu B",
                section="Điều 2",
                verbatim_quote="Ngoại lệ tự suy diễn",
            ),
        ]
        verified, rejections = verify_all_citations(fake_citations, SAMPLE_EVIDENCE_FIXTURE)
        assert len(verified) == 0
        assert len(rejections) == 2


# ==============================================================================
# 3. KIỂM THỬ MÃ HOLD (CKPA-47)
# ==============================================================================
class TestHoldReasons:
    """Kiểm tra 13 mã HoldReason và chi tiết thông điệp."""

    def test_all_14_hold_reasons_have_non_empty_message_and_guidance(self):
        """Mỗi mã HoldReason bắt buộc phải có thông điệp và hướng dẫn rõ ràng (14 mã)."""
        assert len(HoldReason) == 14

        for reason in HoldReason:
            info = get_hold_info(reason)
            assert info.code == reason.value
            assert len(info.message.strip()) > 0, f"Mã {reason} thiếu message"
            assert len(info.guidance.strip()) > 0, f"Mã {reason} thiếu guidance"

