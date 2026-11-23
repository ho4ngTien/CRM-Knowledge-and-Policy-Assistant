"""
legacy/s4/services/citation_verifier.py
Module kiểm tra trích dẫn nguyên văn bằng code (CKPA-39 - Bản vá Giai đoạn 4).
Quy tắc kiểm định nghiêm ngặt:
1. Chuẩn hóa chuỗi bằng Unicode NFC và gộp các khoảng trắng/dòng mới liền kề thành 1 khoảng trắng đơn.
2. KHÔNG bỏ dấu, KHÔNG đổi chữ hoa/thường, KHÔNG so khớp mờ (no fuzzy match).
3. Độ dài tối thiểu: Phải có ít nhất MIN_CITATION_WORDS (legacy/s4/config.py).
4. Ranh giới từ: Đoạn trích phải bắt đầu và kết thúc ở ranh giới từ trong nguồn, không cắt giữa từ.
5. Kiểm soát ngữ cảnh phủ định (Tiền tố): Nếu câu nguồn ngay trước đoạn trích chứa từ phủ định
   mà đoạn trích bị cắt bỏ mất => loại với lý do NEGATION_CONTEXT_TRUNCATED.
6. Kiểm soát vế ngoại lệ/điều kiện (Hậu tố - Giai đoạn 4): Nếu câu nguồn ngay sau đoạn trích
   chứa vế ngoại lệ/điều kiện (trừ khi, ngoại trừ, ngoại lệ, tuy nhiên, chỉ khi, nếu không...)
   mà đoạn trích không bao gồm => loại với lý do EXCEPTION_CONTEXT_TRUNCATED.
   (Lưu ý kỹ thuật: Đây là các lớp bảo vệ heuristic, không đảm bảo tuyệt đối).
7. Tên tài liệu (document_name) và vị trí (section) phải khớp chính xác với chunk đó.
8. Citation không đạt yêu cầu bị loại bỏ hoàn toàn, tuyệt đối không chỉnh sửa nội dung nguồn.
"""

import re
import unicodedata
from typing import List, Tuple
from legacy.s4 import config
from legacy.s4.models import Citation, EvidenceChunk

# Danh mục từ/cụm từ phủ định tiếng Việt phổ biến (Heuristic vế trước)
NEGATION_WORDS = [
    "không",
    "chưa",
    "chẳng",
    "cấm",
    "không được",
    "tuyệt đối không",
    "trừ khi",
    "ngoại trừ",
]

# Danh mục từ/cụm từ ngoại lệ và điều kiện đi kèm (Heuristic vế sau - Giai đoạn 4)
EXCEPTION_PHRASES = [
    "trừ khi",
    "ngoại trừ",
    "ngoại lệ",
    "tuy nhiên",
    "chỉ khi",
    "nếu không",
    "trừ trường hợp",
]

# Ký tự phân tách ranh giới từ hợp lệ
BOUNDARY_CHARS = set(" \t\n\r.,;:!?()[]{}'\"/\\-_+=")


def normalize_whitespace_nfc(text: str) -> str:
    """Chuẩn hóa Unicode dạng NFC và gộp toàn bộ khoảng trắng, ký tự xuống dòng."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", text)
    return " ".join(norm.strip().split())


def _is_word_boundary(text: str, index: int) -> bool:
    """Kiểm tra chỉ số index trong text có nằm ở ranh giới từ hay không."""
    if index <= 0 or index >= len(text):
        return True
    return text[index - 1] in BOUNDARY_CHARS or text[index] in BOUNDARY_CHARS


def _find_sentence_start(text: str, match_start: int) -> int:
    """Tìm vị trí bắt đầu câu (sau dấu chấm, chấm than, hỏi, chấm phẩy gần nhất)."""
    sentence_delimiters = ".!?;:\n"
    pos = match_start - 1
    while pos >= 0:
        if text[pos] in sentence_delimiters:
            return pos + 1
        pos -= 1
    return 0


def _find_sentence_end(text: str, match_end: int) -> int:
    """Tìm vị trí kết thúc câu (trước dấu chấm, chấm than, hỏi gần nhất)."""
    sentence_delimiters = ".!?\n"
    pos = match_end
    length = len(text)
    while pos < length:
        if text[pos] in sentence_delimiters:
            return pos
        pos += 1
    return length


def _check_negation_truncation(prefix_in_sentence: str, norm_quote: str) -> bool:
    """
    Kiểm tra xem prefix trước đoạn trích có chứa từ phủ định mà đoạn trích bị cắt mất không.
    Trả về True nếu bị cắt bỏ ngữ cảnh phủ định (nguy cơ đảo nghĩa).
    """
    prefix_lower = prefix_in_sentence.lower()
    quote_lower = norm_quote.lower()

    for neg in NEGATION_WORDS:
        pattern = r"(?<!\w)" + re.escape(neg) + r"(?!\w)"
        if re.search(pattern, prefix_lower):
            if not re.search(pattern, quote_lower):
                return True
    return False


def _check_exception_truncation(suffix_in_sentence: str, norm_quote: str) -> bool:
    """
    Kiểm tra xem suffix sau đoạn trích trong cùng câu có chứa vế ngoại lệ/điều kiện mà đoạn trích bị cắt mất không.
    Trả về True nếu bị cắt bỏ vế ngoại lệ (nguy cơ hiểu sai phạm vi).
    """
    suffix_lower = suffix_in_sentence.lower()
    quote_lower = norm_quote.lower()

    for phrase in EXCEPTION_PHRASES:
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        if re.search(pattern, suffix_lower):
            if not re.search(pattern, quote_lower):
                return True
    return False


def verify_citation(citation: Citation, evidence_chunks: List[EvidenceChunk]) -> Tuple[bool, str]:
    """
    Xác minh một trích dẫn có xuất hiện nguyên văn trong các chunk bằng chứng hay không.
    
    Args:
        citation: Trích dẫn cần kiểm tra.
        evidence_chunks: Danh sách các đoạn văn bản nguồn do S3 cung cấp.
        
    Returns:
        Tuple[bool, str]: (Hợp lệ hay không, Lý do giải thích chi tiết)
    """
    if not citation.verbatim_quote or not citation.verbatim_quote.strip():
        return False, "Nội dung trích dẫn rỗng."

    if not evidence_chunks:
        return False, "Không có bằng chứng nào từ S3 để đối chiếu."

    norm_quote = normalize_whitespace_nfc(citation.verbatim_quote)
    norm_doc = normalize_whitespace_nfc(citation.document_name)
    norm_sec = normalize_whitespace_nfc(citation.section)

    # 1. Kiểm tra độ dài tối thiểu của trích dẫn (MIN_CITATION_WORDS)
    quote_words = norm_quote.split()
    if len(quote_words) < config.MIN_CITATION_WORDS:
        return (
            False,
            f"Đoạn trích dẫn quá ngắn ({len(quote_words)} từ). "
            f"Yêu cầu tối thiểu {config.MIN_CITATION_WORDS} từ để đảm bảo ngữ cảnh."
        )

    matched_doc_and_section = False
    had_negation_truncation = False
    had_exception_truncation = False
    cut_middle_of_word = False

    for chunk in evidence_chunks:
        chunk_doc = normalize_whitespace_nfc(chunk.document_name)
        chunk_sec = normalize_whitespace_nfc(chunk.section)

        # Kiểm tra khớp tài liệu và vị trí điều khoản
        if norm_doc == chunk_doc and norm_sec == chunk_sec:
            matched_doc_and_section = True
            norm_chunk_text = normalize_whitespace_nfc(chunk.text)

            start_pos = 0
            while True:
                idx = norm_chunk_text.find(norm_quote, start_pos)
                if idx == -1:
                    break
                end_idx = idx + len(norm_quote)

                # 2. Kiểm tra ranh giới từ (không cắt giữa từ)
                start_boundary = (idx == 0) or _is_word_boundary(norm_chunk_text, idx)
                end_boundary = (end_idx == len(norm_chunk_text)) or _is_word_boundary(norm_chunk_text, end_idx)

                if not (start_boundary and end_boundary):
                    cut_middle_of_word = True
                    start_pos = idx + 1
                    continue

                # 3. Kiểm tra ngữ cảnh phủ định phía trước trong cùng câu (NEGATION_CONTEXT_TRUNCATED)
                sentence_start = _find_sentence_start(norm_chunk_text, idx)
                prefix_in_sentence = norm_chunk_text[sentence_start:idx]

                if _check_negation_truncation(prefix_in_sentence, norm_quote):
                    had_negation_truncation = True
                    start_pos = idx + 1
                    continue

                # 4. Kiểm tra vế ngoại lệ / điều kiện phía sau trong cùng câu (EXCEPTION_CONTEXT_TRUNCATED)
                sentence_end = _find_sentence_end(norm_chunk_text, end_idx)
                suffix_in_sentence = norm_chunk_text[end_idx:sentence_end]

                if _check_exception_truncation(suffix_in_sentence, norm_quote):
                    had_exception_truncation = True
                    start_pos = idx + 1
                    continue

                # Đạt mọi tiêu chí kiểm định khắt khe
                return True, "Trích dẫn nguyên văn khớp 100% với tài liệu nguồn (đạt chuẩn ranh giới và ngữ cảnh)."

    if not matched_doc_and_section:
        return (
            False,
            f"Không tìm thấy văn bản '{citation.document_name}' tại vị trí '{citation.section}' trong kho bằng chứng được cấp."
        )

    if had_negation_truncation:
        return (
            False,
            "Đoạn trích bị cắt bỏ ngữ cảnh phủ định trong câu nguồn (NEGATION_CONTEXT_TRUNCATED). "
            "Trích dẫn có nguy cơ làm đảo lộn ý nghĩa chính sách."
        )

    if had_exception_truncation:
        return (
            False,
            "Đoạn trích bị cắt bỏ vế ngoại lệ hoặc điều kiện đi kèm phía sau trong câu nguồn (EXCEPTION_CONTEXT_TRUNCATED). "
            "Trích dẫn có nguy cơ làm hiểu sai phạm vi áp dụng."
        )

    if cut_middle_of_word:
        return (
            False,
            "Đoạn trích bị cắt ngang giữa từ, không tuân thủ ranh giới từ trong tài liệu nguồn."
        )

    return (
        False,
        f"Tài liệu '{citation.document_name}' và điều khoản '{citation.section}' tồn tại "
        f"nhưng nội dung trích dẫn không khớp nguyên văn từng ký tự với tài liệu nguồn."
    )


def verify_all_citations(
    citations: List[Citation],
    evidence_chunks: List[EvidenceChunk]
) -> Tuple[List[Citation], List[str]]:
    """
    Xác minh toàn bộ danh sách trích dẫn.
    Loại bỏ các trích dẫn giả lập hoặc sai lệch, giữ lại các trích dẫn nguyên văn hợp lệ.
    
    Returns:
        Tuple[List[Citation], List[str]]: (Danh sách trích dẫn hợp lệ, Danh sách lý do bị loại bỏ)
    """
    verified: List[Citation] = []
    rejections: List[str] = []

    for cit in citations:
        is_valid, reason = verify_citation(cit, evidence_chunks)
        if is_valid:
            verified.append(cit)
        else:
            rejections.append(f"Loại bỏ trích dẫn [{cit.document_name} - {cit.section}]: {reason}")

    return verified, rejections
