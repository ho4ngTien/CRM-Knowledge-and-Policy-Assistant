"""
legacy/s4/services/output_guard.py
Lớp kiểm tra an toàn đầu ra (CKPA-43; ANS 05, 06, 07, KNW 02).
Chức năng:
1. check_explanation_grounding: Kiểm tra số tiền, tỷ lệ %, ngày tháng, mã chính sách
   trong lời giải thích bắt buộc phải xuất hiện trong bằng chứng của S3.
   Nếu xuất hiện giá trị lạ => Kích hoạt HOLD UNGROUNDED_CONTENT.
2. check_output_safety:
   - Phát hiện rò rỉ System Prompt.
   - Phát hiện chuỗi bí mật/API key/Bearer token.
   - Phát hiện URL lạ không nằm trong metadata S3.
   - Phát hiện ngôn ngữ tự phê duyệt hoặc hứa hẹn với khách (ANS 05, 07).
   - Phát hiện tư vấn pháp lý trái thẩm quyền (ANS 07).
"""

import re
import unicodedata
from typing import List, Tuple, Optional, Set
from legacy.s4.models import PolicyResponse, EvidenceChunk
from legacy.s4.services.hold_reasons import HoldReason

# Các cụm từ phê duyệt hoặc cam kết quyền lợi bị cấm (ANS 05, 07)
PROHIBITED_APPROVAL_PHRASES = [
    "đã được phê duyệt",
    "chắc chắn được chấp thuận",
    "chắc chắn được duyệt",
    "cam kết với khách",
    "ngân hàng cam kết",
    "bạn có thể báo khách rằng",
    "được chấp thuận luôn",
]

# Các cụm từ tư vấn pháp lý bị cấm (ANS 07)
PROHIBITED_LEGAL_PHRASES = [
    "bạn nên khởi kiện",
    "khách hàng nên khởi kiện",
    "tư vấn pháp lý cho",
    "thắng kiện",
    "khởi kiện ra tòa",
]

# Mẫu chuỗi nhạy cảm / API Key / Mật khẩu
SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9_\-]{20,}", re.IGNORECASE),
    re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{15,}", re.IGNORECASE),
    re.compile(r"password\s*=\s*\S+", re.IGNORECASE),
    re.compile(r"api[_\-]?key\s*=\s*\S+", re.IGNORECASE),
]


def normalize_numeric_string(s: str) -> str:
    """Chuẩn hóa chuỗi số (thay dấu phẩy phân cách hàng nghìn thành dấu chấm)."""
    return re.sub(r"(\d+),(\d{3})", r"\1.\2", s)


def extract_grounding_values(text: str) -> Set[str]:
    """
    Trích xuất mọi giá trị số tiền, tỷ lệ %, ngày tháng, và mã chữ-số.
    """
    norm_text = unicodedata.normalize("NFC", text)
    values: Set[str] = set()

    # 1. Số tiền / Con số có đơn vị hoặc phân cách (ví dụ 20.000.000, 20 triệu, 11.000 VNĐ)
    money_pattern = re.compile(
        r"\b\d{1,3}(?:[.,]\d{3})+(?:\s*(?:VNĐ|VND|đồng|triệu|nghìn|tỷ))?\b|\b\d+\s*(?:VNĐ|VND|đồng|triệu|nghìn|tỷ)\b",
        re.IGNORECASE
    )
    for m in money_pattern.finditer(norm_text):
        values.add(m.group(0).strip())

    # 2. Tỷ lệ phần trăm (ví dụ: 5%, 10.5%)
    pct_pattern = re.compile(r"\b\d+(?:[.,]\d+)?\s*%\b")
    for m in pct_pattern.finditer(norm_text):
        values.add(m.group(0).strip())

    # 3. Ngày tháng (ví dụ: 15/01/2025, 2025-01-15, 15-01-2025)
    date_pattern = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b")
    for m in date_pattern.finditer(norm_text):
        values.add(m.group(0).strip())

    # 4. Mã chính sách chữ-số (ví dụ POL-ACC-01, 01/2025/QĐ-NH)
    code_pattern = re.compile(r"\b[A-Z0-9]+(?:-[A-Z0-9]+)+\b|\b\d{1,4}/\d{4}/[A-ZĐ]+(?:-[A-ZĐ]+)*\b")
    for m in code_pattern.finditer(norm_text):
        values.add(m.group(0).strip())

    return values


def check_explanation_grounding(
    explanation: str,
    evidence_chunks: List[EvidenceChunk]
) -> Tuple[bool, Optional[str]]:
    """
    Kiểm tra xem mọi giá trị số liệu, ngày tháng, mã chính sách trong giải thích
    có xuất hiện trong tài liệu bằng chứng S3 hay không.
    
    Quy tắc:
    - Nếu phát hiện giá trị trong giải thích không có trong bằng chứng => Trả về False.
    """
    if not explanation or not explanation.strip():
        return True, None

    # Ghép toàn bộ nội dung text và metadata của các chunk
    corpus_parts = []
    for chunk in evidence_chunks:
        corpus_parts.append(chunk.text)
        corpus_parts.append(chunk.document_name)
        corpus_parts.append(chunk.section)
        if chunk.clause_code:
            corpus_parts.append(chunk.clause_code)
        if chunk.effective_date:
            corpus_parts.append(chunk.effective_date)

    combined_corpus = unicodedata.normalize("NFC", " ".join(corpus_parts))
    normalized_corpus = normalize_numeric_string(combined_corpus)

    explanation_values = extract_grounding_values(explanation)

    for val in explanation_values:
        norm_val = normalize_numeric_string(val)
        # So khớp giá trị nguyên bản hoặc giá trị đã chuẩn hóa dấu phân cách
        if (val not in combined_corpus) and (norm_val not in normalized_corpus):
            return (
                False,
                f"Giá trị số liệu hoặc mã '{val}' không xuất hiện trong tài liệu bằng chứng được cấp."
            )

    return True, None


def check_output_safety(
    answer: PolicyResponse,
    system_prompt_text: str,
    evidence_chunks: List[EvidenceChunk]
) -> Tuple[bool, Optional[HoldReason], str]:
    """
    Kiểm tra an toàn toàn diện cho câu trả lời đầu ra.
    
    Returns:
        Tuple[bool, Optional[HoldReason], str]: (An toàn hay không, Mã HOLD nếu vi phạm, Lý do chi tiết)
    """
    explanation_lower = answer.short_explanation.lower()

    # 1. Kiểm tra rò rỉ System Prompt (trích đoạn >= 50 ký tự từ system prompt)
    clean_sys = re.sub(r"\s+", " ", system_prompt_text.strip().lower())
    # Quét các cửa sổ 50 ký tự trong system prompt
    chunk_size = 50
    if len(clean_sys) >= chunk_size:
        for i in range(0, min(len(clean_sys) - chunk_size, 500), 20):
            window = clean_sys[i : i + chunk_size]
            if len(window) == chunk_size and window in explanation_lower:
                return (
                    False,
                    HoldReason.INJECTION_SUSPECTED,
                    "Phát hiện đầu ra chứa trích đoạn trực tiếp từ System Prompt nội bộ."
                )

    # 2. Kiểm tra chuỗi thông tin xác thực / API Key / Mật khẩu
    for pat in SECRET_PATTERNS:
        if pat.search(answer.short_explanation):
            return (
                False,
                HoldReason.INJECTION_SUSPECTED,
                "Phát hiện đầu ra chứa mẫu thông tin xác thực, khóa bí mật hoặc mật khẩu."
            )

    # 3. Kiểm tra URL lạ không nằm trong metadata S3
    url_pattern = re.compile(r"https?://[^\s)\]\"'>]+", re.IGNORECASE)
    allowed_urls = set()
    for c in evidence_chunks:
        if c.source_url:
            allowed_urls.add(c.source_url.strip().lower())

    for found_url in url_pattern.findall(answer.short_explanation):
        if found_url.lower() not in allowed_urls:
            return (
                False,
                HoldReason.INJECTION_SUSPECTED,
                f"Phát hiện đường dẫn URL lạ không thuộc nguồn tài liệu được xác thực: {found_url}"
            )

    # 4. Kiểm tra ngôn ngữ tự phê duyệt hoặc cam kết quyền lợi (ANS 05, 07)
    for phrase in PROHIBITED_APPROVAL_PHRASES:
        if phrase in explanation_lower:
            return (
                False,
                HoldReason.INJECTION_SUSPECTED,
                f"Đầu ra vi phạm quy tắc an toàn: Sử dụng ngôn ngữ tự ý phê duyệt hoặc cam kết ('{phrase}')."
            )

    # 5. Kiểm tra tư vấn pháp lý trái thẩm quyền (ANS 07)
    for phrase in PROHIBITED_LEGAL_PHRASES:
        if phrase in explanation_lower:
            return (
                False,
                HoldReason.INJECTION_SUSPECTED,
                f"Đầu ra vi phạm quy tắc an toàn: Có dấu hiệu tư vấn pháp lý hoặc định hướng khởi kiện ('{phrase}')."
            )

    # 6. Kiểm tra giá trị trong lời giải thích (Grounding check)
    is_grounded, grounding_err = check_explanation_grounding(answer.short_explanation, evidence_chunks)
    if not is_grounded:
        return (
            False,
            HoldReason.UNGROUNDED_CONTENT,
            grounding_err or "Phát hiện nội dung số liệu không có căn cứ từ tài liệu nguồn."
        )

    return True, None, "Đầu ra đáp ứng đầy đủ tiêu chuẩn an toàn."

