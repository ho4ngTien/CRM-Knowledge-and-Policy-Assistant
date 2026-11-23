"""
legacy/s4/models.py
Định nghĩa Data Contract (Hợp đồng dữ liệu) giữa S3 (Retrieval) và S4 (Application).
[LƯU Ý QUAN TRỌNG: ĐÂY LÀ BẢN ĐỀ XUẤT TỪ S4, CHƯA ĐƯỢC S3 XÁC NHẬN CHÍNH THỨC]

Tuân thủ chuẩn:
- CKPA-40: 7 Field dữ liệu cố định
- CKPA-39: Trích dẫn nguyên văn (có gắn chunk_id)
- CKPA-47: HOLD và Fail Visibly
- KNW 01: Mã điều khoản (clause_code) và liên kết tham chiếu gốc (source_url)
- Giai đoạn 3: Phân định ranh giới metadata S3
- Giai đoạn 4: Kiểm soát phân quyền bằng code (allowed_roles, classification_level)
"""

import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from legacy.s4 import config


class UncertaintyLevel(str, Enum):
    """Mức độ chắc chắn của câu trả lời theo chuẩn CKPA-40."""
    CAO = "Cao (Có bằng chứng xác thực)"
    TRUNG_BINH = "Trung bình (Cần lưu ý điều kiện đi kèm)"
    THAP = "Thấp (Tài liệu chỉ mang tính tham khảo)"
    KHONG_XAC_DINH = "Không xác định (Đang ở trạng thái HOLD)"

    # Giữ các alias tiếng Anh để tương thích hoàn toàn mã nguồn cũ
    HIGH = "Cao (Có bằng chứng xác thực)"
    MEDIUM = "Trung bình (Cần lưu ý điều kiện đi kèm)"
    LOW = "Thấp (Tài liệu chỉ mang tính tham khảo)"
    HOLD = "Không xác định (Đang ở trạng thái HOLD)"


class ResponseStatus(str, Enum):
    """Trạng thái xử lý câu hỏi."""
    SUCCESS = "SUCCESS"    # Trả lời thành công, đầy đủ bằng chứng
    HOLD = "HOLD"          # Dừng trả lời do thiếu căn cứ / vượt giới hạn
    REFUSAL = "REFUSAL"    # Từ chối do vi phạm an toàn / Prompt Injection


@dataclass
class Citation:
    """Trích dẫn nguyên văn từ tài liệu nguồn (CKPA-39 & KNW 01)."""
    document_name: str                  # Tên văn bản / chính sách
    section: str                        # Vị trí (Điều / Khoản / Trang)
    verbatim_quote: str                 # Nội dung trích dẫn nguyên văn
    chunk_id: Optional[str] = None      # ID tham chiếu chunk từ S3 (Giai đoạn 3)
    clause_code: Optional[str] = None   # Mã định danh điều khoản (KNW 01)
    source_url: Optional[str] = None    # Đường dẫn tham chiếu tài liệu gốc (KNW 01)
    effective_date: Optional[str] = None # Ngày hiệu lực của riêng điều khoản (nếu có)


@dataclass
class EvidenceChunk:
    """Đoạn trích xuất bằng chứng nhận từ S3 Retrieval."""
    text: str                                           # Toàn bộ nội dung trích xuất
    document_name: str                                  # Tên văn bản nguồn
    section: str                                        # Vị trí điều khoản / trang
    chunk_id: str = "chunk_01"                          # Định danh chunk duy nhất (Giai đoạn 3)
    clause_code: Optional[str] = None                   # Mã điều khoản
    source_url: Optional[str] = None                    # Link tài liệu gốc
    effective_date: Optional[str] = None                 # Ngày hiệu lực từ metadata S3
    scope: Optional[str] = None                         # Phạm vi áp dụng từ metadata S3
    policy_owner: Optional[str] = None                  # Đơn vị phụ trách từ metadata S3
    allowed_roles: Optional[List[str]] = None           # Quyền truy cập được phép (Giai đoạn 4 - Đề xuất)
    classification_level: Optional[str] = "INTERNAL"    # Cấp độ bảo mật: INTERNAL, RESTRICTED...


@dataclass
class LLMAnswerOutput:
    """Đầu ra thuần túy mà LLM được phép trả về (Task 3.1 - Giảm thiểu tối đa nguy cơ bịa đặt)."""
    short_explanation: str
    required_information: str
    uncertainty_level: UncertaintyLevel
    citations: List[dict]               # Gồm: [{"chunk_id": "...", "verbatim_quote": "..."}]
    status: ResponseStatus = ResponseStatus.SUCCESS
    hold_reason_code: Optional[str] = None


@dataclass
class PolicyResponse:
    """Cấu trúc dữ liệu đầu ra cố định hiển thị lên Workspace (CKPA-40)."""
    question: str
    status: ResponseStatus = ResponseStatus.SUCCESS
    
    # 7 trường dữ liệu cố định theo yêu cầu CKPA-40:
    effective_date: str = "Chưa có dữ liệu"
    scope: str = "Chưa xác định"
    short_explanation: str = "Chưa có dữ liệu"
    required_information: str = "Không có"
    policy_owner: str = "Chưa xác định"
    uncertainty_level: UncertaintyLevel = UncertaintyLevel.KHONG_XAC_DINH
    citations: List[Citation] = field(default_factory=list)
    
    # Dành cho CKPA-47 (HOLD và Fail Visibly) & ANS 01, ANS 06:
    hold_reason_code: Optional[str] = None # Mã lỗi định danh (e.g. HOLD_NO_EVIDENCE)
    hold_reason: Optional[str] = None      # Giải thích lý do rõ ràng
    guidance: Optional[str] = None         # Hướng dẫn người dùng khi bị HOLD
    clarifying_question: Optional[str] = None # Câu hỏi gợi ý làm rõ cố định (ANS 01, ANS 06)


def _is_valid_date_format(date_str: str) -> bool:
    """Kiểm tra ngày hợp lệ theo chuẩn YYYY-MM-DD hoặc DD/MM/YYYY."""
    cleaned = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            datetime.strptime(cleaned, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_answer(answer: PolicyResponse) -> List[str]:
    """
    Kiểm tra tính hợp lệ của câu trả lời theo yêu cầu CKPA-40.
    
    Quy tắc:
    1. Các trường bắt buộc không được rỗng: effective_date, scope, short_explanation,
       required_information, policy_owner.
    2. short_explanation có số từ nằm trong [EXPLANATION_MIN_WORDS, EXPLANATION_MAX_WORDS]
       (lấy từ legacy/s4/config.py, đếm từ sau khi chuẩn hóa Unicode tiếng Việt NFC).
    3. effective_date phải là ngày hợp lệ (YYYY-MM-DD hoặc DD/MM/YYYY).
    4. uncertainty_level phải thuộc Enum UncertaintyLevel và không được là KHONG_XAC_DINH.
    5. Phải có ít nhất 1 citation đã được xác minh.
    
    Returns:
        List[str]: Danh sách thông báo lỗi (rỗng nếu hoàn toàn hợp lệ).
    """
    errors: List[str] = []

    # 1. Kiểm tra các trường bắt buộc không rỗng
    required_fields = {
        "Ngày hiệu lực (effective_date)": answer.effective_date,
        "Phạm vi áp dụng (scope)": answer.scope,
        "Giải thích ngắn (short_explanation)": answer.short_explanation,
        "Thông tin cần bổ sung (required_information)": answer.required_information,
        "Đơn vị phụ trách (policy_owner)": answer.policy_owner,
    }
    for field_name, value in required_fields.items():
        if not value or not str(value).strip():
            errors.append(f"Trường bắt buộc '{field_name}' không được để trống.")

    # 2. Kiểm tra độ dài từ của short_explanation (100 - 250 từ)
    if answer.short_explanation and answer.short_explanation.strip():
        norm_text = unicodedata.normalize("NFC", answer.short_explanation.strip())
        word_count = len(norm_text.split())
        if word_count < config.EXPLANATION_MIN_WORDS or word_count > config.EXPLANATION_MAX_WORDS:
            errors.append(
                f"Giải thích ngắn gọn có {word_count} từ, không nằm trong giới hạn cho phép "
                f"[{config.EXPLANATION_MIN_WORDS}, {config.EXPLANATION_MAX_WORDS}] từ."
            )

    # 3. Kiểm tra tính hợp lệ của effective_date
    if answer.effective_date and answer.effective_date.strip():
        if not _is_valid_date_format(answer.effective_date):
            errors.append(
                f"Ngày hiệu lực '{answer.effective_date}' không đúng định dạng ngày hợp lệ (YYYY-MM-DD hoặc DD/MM/YYYY)."
            )

    # 4. Kiểm tra uncertainty_level
    if not isinstance(answer.uncertainty_level, UncertaintyLevel):
        errors.append(
            f"Mức độ chắc chắn '{answer.uncertainty_level}' không hợp lệ. "
            f"Chỉ chấp nhận các giá trị trong UncertaintyLevel."
        )
    elif answer.uncertainty_level in (UncertaintyLevel.KHONG_XAC_DINH, UncertaintyLevel.HOLD):
        errors.append(
            "Câu trả lời hợp lệ không thể có mức độ chắc chắn là 'Không xác định / HOLD'."
        )

    # 5. Kiểm tra ít nhất 1 citation
    if not answer.citations or len(answer.citations) == 0:
        errors.append("Câu trả lời phải có ít nhất 1 trích dẫn nguyên văn từ tài liệu nguồn đã được xác minh.")
    else:
        for idx, cit in enumerate(answer.citations, start=1):
            if not cit.verbatim_quote or not cit.verbatim_quote.strip():
                errors.append(f"Trích dẫn thứ {idx} thiếu nội dung nguyên văn (verbatim_quote).")
            if not cit.document_name or not cit.document_name.strip():
                errors.append(f"Trích dẫn thứ {idx} thiếu tên tài liệu nguồn (document_name).")
            if not cit.section or not cit.section.strip():
                errors.append(f"Trích dẫn thứ {idx} thiếu vị trí điều khoản (section).")

    return errors
