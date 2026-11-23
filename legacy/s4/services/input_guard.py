"""
legacy/s4/services/input_guard.py
Lớp bảo vệ dữ liệu đầu vào chống Prompt Injection (CKPA-43 & ANS 08).
Quy tắc:
1. Coi toàn bộ câu hỏi và tài liệu truy xuất là DỮ LIỆU KHÔNG ĐÁNG TIN.
2. Chuẩn hóa NFC, loại ký tự điều khiển, ký tự ẩn zero-width, giới hạn độ dài ký tự.
3. Chặn chuỗi giả mạo thẻ XML ranh giới: </cau_hoi>, <bang_chung...
4. Phát hiện các mẫu tấn công tiếng Việt (có dấu và không dấu) và tiếng Anh:
   - Bỏ qua/quên hướng dẫn
   - Đổi vai trò / Jailbreak (DAN, hacker, admin...)
   - Đòi tiết lộ System Prompt / API Key / Mật khẩu
   - Đòi truy cập web / chạy lệnh hệ điều hành
   - Ép AI tự ý phê duyệt ngoại lệ (chỉ được hướng dẫn quy trình)
   - Ép bỏ qua đối chiếu nguồn
5. Chống chặn nhầm (False Positive): Cho phép câu hỏi nghiệp vụ hợp lệ chứa từ "ngoại lệ",
   "mật khẩu khách hàng", "xác thực".
6. Quét chunk bằng chứng của S3; nếu chunk độc hại => Cách ly ngay và báo cáo minh bạch.
"""

import re
import unicodedata
from typing import List, Tuple, Optional
from legacy.s4 import config
from legacy.s4.models import EvidenceChunk

# Ký tự zero-width ẩn cần loại bỏ
ZERO_WIDTH_CHARS = set("\u200b\u200c\u200d\ufeff")

# Danh sách mẫu phát hiện Prompt Injection (regex)
INJECTION_RULES = [
    # 1. Bỏ qua hướng dẫn / quy tắc
    (
        "IGNORE_INSTRUCTIONS",
        re.compile(
            r"\b(bỏ qua|quên|hủy bỏ|ignore|disregard|forget)\s+(toàn bộ|mọi|tất cả|all)?\s*(hướng dẫn|chỉ dẫn|lệnh|quy tắc|instructions|rules)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(bo qua|quen|huy bo|ignore|disregard|forget)\s+(toan bo|moi|tat ca|all)?\s*(huong dan|chi dan|lenh|quy tac|instructions|rules)\b",
            re.IGNORECASE
        ),
    ),
    # 2. Đổi vai trò / Jailbreak
    (
        "ROLE_CHANGE",
        re.compile(
            r"\b(bạn là|you are now|act as|đóng vai)\s+(quản trị viên|hacker|admin|chuyên gia không giới hạn|dan|root)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(ban la|you are now|act as|dong vai)\s+(quan tri vien|hacker|admin|chuyen gia khong gioi han|dan|root)\b",
            re.IGNORECASE
        ),
    ),
    # 3. Đòi tiết lộ System Prompt / API Key / Mật khẩu
    (
        "LEAK_SECRETS",
        re.compile(
            r"\b(tiết lộ|cho tôi biết|cho tôi|cho xem|cho xin|cho|đưa|hiện|in ra|xem|đọc|cung cấp|lấy|show|reveal|display|get|print)\s+(?:ngay\s+|luôn\s+|thấy\s+)?(system\s*prompt|hướng dẫn hệ thống|cấu hình hệ thống|api[_\s-]?key|mật khẩu hệ thống|token xác thực|secret[_\s-]?key|khóa bí mật)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(tiet lo|cho toi biet|cho toi|cho xem|cho xin|cho|dua|hien|in ra|xem|doc|cung cap|lay|show|reveal|display|get|print)\s+(?:ngay\s+|luon\s+|thay\s+)?(system\s*prompt|huong dan he thong|cau hinh he thong|api[_\s-]?key|mat khau he thong|token xac thuc|secret[_\s-]?key|khoa bi mat)\b",
            re.IGNORECASE
        ),
    ),
    # 4. Đòi truy cập web / Chạy lệnh
    (
        "WEB_OR_EXEC",
        re.compile(
            r"\b(truy cập|search|tìm trên|browse|fetch|curl)\s+(web|internet|google|trang web|url)\b|\b(chạy lệnh|execute command|run shell|thực thi lệnh)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(truy cap|search|tim tren|browse|fetch|curl)\s+(web|internet|google|trang web|url)\b|\b(chay lenh|execute command|run shell|thuc thi lenh)\b",
            re.IGNORECASE
        ),
    ),
    # 5. Ép phê duyệt ngoại lệ tự động (ANS 05)
    (
        "FORCE_APPROVAL",
        re.compile(
            r"\b(phê duyệt luôn|duyệt luôn|tự phê duyệt|chấp nhận luôn ngoại lệ|bỏ qua điều kiện và duyệt|approve exception)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(phe duyet luon|duyet luon|tu phe duyet|chap nhan luon ngoai le|bo qua dieu kien va duyet|approve exception)\b",
            re.IGNORECASE
        ),
    ),
    # 6. Ép bỏ qua kiểm tra nguồn
    (
        "SKIP_VERIFICATION",
        re.compile(
            r"\b(bỏ qua kiểm tra nguồn|không cần bằng chứng|skip verification|không cần dẫn chứng|không cần trích dẫn)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(bo qua kiem tra nguon|khong can bang chung|skip verification|khong can dan chung|khong can trich dan)\b",
            re.IGNORECASE
        ),
    ),
]


def strip_vietnamese_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để phát hiện các câu hỏi cố tình viết không dấu."""
    # Thay thế thủ công ký tự đ/Đ trước khi phân rã NFD
    res = text.replace("đ", "d").replace("Đ", "D")
    nfd = unicodedata.normalize("NFD", res)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def clean_control_chars(text: str) -> str:
    """Loại bỏ ký tự điều khiển và zero-width characters."""
    filtered = []
    for c in text:
        if c in ZERO_WIDTH_CHARS:
            continue
        # Cho phép ký tự in được và \n, \t, \r
        if ord(c) < 32 and c not in "\n\t\r":
            continue
        filtered.append(c)
    return "".join(filtered)


def collapse_spaced_characters(text: str) -> str:
    """
    Phát hiện các chuỗi ký tự đơn cách nhau rồi ghép lại để quét (chống Spaced Character Evasion).
    Không làm thay đổi khoảng trắng của câu bình thường.
    """
    if not text:
        return ""
    res = text
    pattern = re.compile(r'(?<=\b[a-zA-Z0-9À-ỹà-ỹ])\x20(?=[a-zA-Z0-9À-ỹà-ỹ]\b)')
    prev = None
    while prev != res:
        prev = res
        res = pattern.sub('', res)
    return " ".join(res.split())


def sanitize_for_log(text: str, max_chars: int = 100) -> str:
    """
    Rút gọn câu hỏi và che thông tin định danh cá nhân nhạy cảm (PII) trước khi ghi log (SEC 02).
    LƯU Ý KỸ THUẬT: Đây là cơ chế lọc heuristic đề xuất từ S4 để phòng ngừa rò rỉ dữ liệu,
    chưa được nhóm và chuyên gia an ninh ngân hàng chốt chính thức.
    """
    clean = " ".join(text.strip().split())
    # 1. Che chuỗi giống số thẻ tín dụng / ghi nợ (16 số liên tiếp hoặc 4 nhóm 4 chữ số)
    clean = re.sub(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b", "[ĐÃ_CHE_SỐ_THẺ]", clean)
    # 2. Che chuỗi giống số CCCD (12 chữ số) hoặc CMND (9 chữ số)
    clean = re.sub(r"\b\d{12}\b", "[ĐÃ_CHE_CCCD]", clean)
    clean = re.sub(r"\b\d{9}\b", "[ĐÃ_CHE_CMND]", clean)

    if len(clean) > max_chars:
        return f"{clean[:max_chars]}... [BẢN RÚT GỌN ĐỂ LOG]"
    return clean


def validate_question(question: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Kiểm tra câu hỏi đầu vào của người dùng.
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
        (Hợp lệ hay không, Lý do lỗi nếu có, Mã định danh vi phạm)
    """
    if not question or not question.strip():
        return False, "Câu hỏi rỗng hoặc chỉ chứa khoảng trắng.", "EMPTY_INPUT"

    # 1. Làm sạch ký tự ẩn và ký tự điều khiển
    cleaned = clean_control_chars(question)
    norm_nfc = unicodedata.normalize("NFC", cleaned)

    # 2. Giới hạn độ dài ký tự câu hỏi
    if len(norm_nfc) > config.MAX_QUESTION_CHARS:
        return (
            False,
            f"Câu hỏi quá dài ({len(norm_nfc)} ký tự), vượt quá giới hạn an toàn {config.MAX_QUESTION_CHARS} ký tự.",
            "QUESTION_TOO_LONG"
        )

    # 3. Chặn chuỗi giả mạo thẻ ranh giới XML
    forgery_tags = ["</cau_hoi>", "<cau_hoi>", "<bang_chung", "</bang_chung>"]
    for tag in forgery_tags:
        if tag.lower() in norm_nfc.lower():
            return (
                False,
                f"Phát hiện ký tự giả mạo thẻ phân định ranh giới XML hệ thống: '{tag}'.",
                "TAG_FORGERY"
            )

    # 4. Quét mẫu Prompt Injection trên cả bản có dấu và không dấu
    # Đồng thời quét bản đã gộp chuỗi ký tự đơn cách nhau (Spaced Character Evasion)
    unaccented = strip_vietnamese_accents(norm_nfc)
    collapsed_nfc = collapse_spaced_characters(norm_nfc)
    collapsed_unaccented = strip_vietnamese_accents(collapsed_nfc)

    for rule_name, pat_accent, pat_unaccent in INJECTION_RULES:
        if (
            pat_accent.search(norm_nfc)
            or pat_unaccent.search(unaccented)
            or pat_accent.search(collapsed_nfc)
            or pat_unaccent.search(collapsed_unaccented)
        ):
            return (
                False,
                f"Nội dung câu hỏi chứa chỉ dẫn vi phạm quy tắc an toàn (Mã phát hiện: {rule_name}).",
                rule_name
            )

    return True, None, None


def scan_evidence_chunk(chunk: EvidenceChunk) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Kiểm tra từng chunk bằng chứng do S3 cung cấp.
    Coi dữ liệu bằng chứng cũng là DỮ LIỆU KHÔNG ĐÁNG TIN (Task 4.2).
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
        (An toàn hay không, Lý do cách ly, Mã vi phạm)
    """
    text = chunk.text
    # 1. Kiểm tra giả mạo ranh giới
    forgery_tags = ["</bang_chung>", "<bang_chung", "</cau_hoi>"]
    for tag in forgery_tags:
        if tag.lower() in text.lower():
            return (
                False,
                f"Phát hiện tài liệu nguồn chứa thẻ giả mạo ranh giới: '{tag}' (Chunk ID: {chunk.chunk_id}).",
                "CHUNK_TAG_FORGERY"
            )

    # 2. Quét injection nhúng trong tài liệu (bao gồm cả biến thể ký tự đơn cách nhau)
    norm_nfc = unicodedata.normalize("NFC", text)
    unaccented = strip_vietnamese_accents(norm_nfc)
    collapsed_nfc = collapse_spaced_characters(norm_nfc)
    collapsed_unaccented = strip_vietnamese_accents(collapsed_nfc)

    for rule_name, pat_accent, pat_unaccent in INJECTION_RULES:
        if (
            pat_accent.search(norm_nfc)
            or pat_unaccent.search(unaccented)
            or pat_accent.search(collapsed_nfc)
            or pat_unaccent.search(collapsed_unaccented)
        ):
            return (
                False,
                f"Phát hiện chỉ dẫn độc hại được nhúng trong tài liệu '{chunk.document_name}' "
                f"(Chunk ID: {chunk.chunk_id}, Mã: {rule_name}).",
                rule_name
            )

    return True, None, None

