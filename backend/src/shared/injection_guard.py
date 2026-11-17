"""Prompt Injection and untrusted input isolation guard (ANS 08, CKPA-43)."""

import re
import unicodedata

ZERO_WIDTH_CHARS = set("\u200b\u200c\u200d\ufeff")

_VIETNAMESE_ACCENT_MAP = {
    "à": "a", "á": "a", "ả": "a", "ã": "a", "ạ": "a",
    "ă": "a", "ằ": "a", "ắ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
    "â": "a", "ầ": "a", "ấ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
    "è": "e", "é": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
    "ê": "e", "ề": "e", "ế": "e", "ể": "e", "ễ": "e", "ệ": "e",
    "ì": "i", "í": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
    "ò": "o", "ó": "o", "ỏ": "o", "õ": "o", "ọ": "o",
    "ô": "o", "ồ": "o", "ố": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
    "ơ": "o", "ờ": "o", "ớ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
    "ù": "u", "ú": "u", "ủ": "u", "ũ": "u", "ụ": "u",
    "ư": "u", "ừ": "u", "ứ": "u", "ử": "u", "ữ": "u", "ự": "u",
    "ỳ": "y", "ý": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
    "đ": "d",
}


def strip_vietnamese_accents(text: str) -> str:
    """Normalize and convert Vietnamese accented characters to ASCII equivalents."""
    norm = unicodedata.normalize("NFC", text.lower())
    return "".join(_VIETNAMESE_ACCENT_MAP.get(c, c) for c in norm)


def clean_control_chars(text: str) -> str:
    """Strip zero-width characters and unusual control characters while keeping standard whitespace."""
    filtered = [c for c in text if c not in ZERO_WIDTH_CHARS]
    cleaned = "".join(filtered)
    return "".join(c for c in cleaned if unicodedata.category(c)[0] != "C" or c in "\n\r\t")


def collapse_spaced_characters(text: str) -> str:
    """Collapse sequences like 'a d m i n' into 'admin' to thwart spaced obfuscation."""
    tokens = text.split()
    result: list[str] = []
    i = 0
    while i < len(tokens):
        if len(tokens[i]) == 1 and tokens[i].isalnum():
            single_run = [tokens[i]]
            j = i + 1
            while j < len(tokens) and len(tokens[j]) == 1 and tokens[j].isalnum():
                single_run.append(tokens[j])
                j += 1
            if len(single_run) >= 3:
                result.append("".join(single_run))
                i = j
                continue
        result.append(tokens[i])
        i += 1
    return " ".join(result)


INJECTION_RULES: list[tuple[str, re.Pattern[str], re.Pattern[str]]] = [
    # 1. Ignore instructions / rules / override
    (
        "IGNORE_INSTRUCTIONS",
        re.compile(
            r"(bỏ\s*qua|bo\s*qua|boqua|quên|quen|hủy\s*bỏ|huy\s*bo|ignore|disregard|forget).*?(hướng\s*dẫn|huong\s*dan|huongdan|chỉ\s*dẫn|chi\s*dan|lệnh|lenh|quy\s*tắc|quy\s*tac|instructions|rules|prompts)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(ignore|disregard|forget)\s*(all\s*)?(previous\s*|prior\s*)?(instructions|rules|prompts)",
            re.IGNORECASE,
        ),
    ),
    # 2. Role change / Jailbreak
    (
        "ROLE_CHANGE",
        re.compile(
            r"\b(bạn\s*là|ban\s*la|you\s+are\s+now|act\s+as|đóng\s*vai|dong\s*vai)\s+(?:a\s+|an\s+|the\s+)?(?:system\s+)?(quản\s*trị\s*viên|quan\s*tri\s*vien|hacker|admin|administrator|chuyên\s*gia\s*không\s*giới\s*hạn|dan|root)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(ban\s*la|you\s+are\s+now|act\s+as|dong\s*vai)\s+(?:a\s+|an\s+|the\s+)?(?:system\s+)?(quan\s*tri\s*vien|hacker|admin|administrator|chuyen\s*gia\s*khong\s*gioi\s*han|dan|root)\b",
            re.IGNORECASE,
        ),
    ),
    # 3. Leak system prompt / secrets
    (
        "LEAK_SECRETS",
        re.compile(
            r"\b(tiết\s*lộ|cho\s*tôi\s*biết|cho\s*tôi|cho\s*xem|cho\s*xin|cho|đưa|hiện|in\s*ra|xem|đọc|cung\s*cấp|lấy|show|reveal|display|get|print)\s+(?:ngay\s+|luôn\s+|thấy\s+)?(system\s*prompt|hướng\s*dẫn\s*hệ\s*thống|cấu\s*hình\s*hệ\s*thống|api[_\s-]?key|mật\s*khẩu\s*hệ\s*thống|token\s*xác\s*thực|secret[_\s-]?key|khóa\s*bí\s*mật)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(tiet\s*lo|cho\s*toi\s*biet|cho\s*toi|cho\s*xem|cho\s*xin|cho|dua|hien|in\s*ra|xem|doc|cung\s*cap|lay|show|reveal|display|get|print)\s+(?:ngay\s+|luon\s+|thay\s+)?(system\s*prompt|huong\s*dan\s*he\s*thong|cau\s*hinh\s*he\s*thong|api[_\s-]?key|mat\s*khau\s*he\s*thong|token\s*xac\s*thuc|secret[_\s-]?key|khoa\s*bi\s*mat)\b",
            re.IGNORECASE,
        ),
    ),
    # 4. Web access or Shell execution
    (
        "WEB_OR_EXEC",
        re.compile(
            r"\b(truy\s*cập|search|tìm\s*trên|browse|fetch|curl)\s+(web|internet|google|trang\s*web|url)\b|\b(chạy\s*lệnh|execute\s*command|run\s*shell|thực\s*thi\s*lệnh)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(truy\s*cap|search|tim\s*tren|browse|fetch|curl)\s+(web|internet|google|trang\s*web|url)\b|\b(chay\s*lenh|execute\s*command|run\s*shell|thuc\s*thi\s*lenh)\b",
            re.IGNORECASE,
        ),
    ),
    # 5. Force auto approval without human authority (ANS 05)
    (
        "FORCE_APPROVAL",
        re.compile(
            r"\b(phê\s*duyệt\s*luôn|duyệt\s*luôn|tự\s*phê\s*duyệt|chấp\s*nhận\s*ngoại\s*lệ\s*này\s*ngay|không\s*cần\s*chuyển)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(phe\s*duyet\s*luon|duyet\s*luon|tu\s*phe\s*duyet|chap\s*nhan\s*ngoai\s*le\s*nay\s*ngay|khong\s*can\s*chuyen)\b",
            re.IGNORECASE,
        ),
    ),
    # 6. Bypass verification
    (
        "BYPASS_CHECK",
        re.compile(
            r"\b(bỏ\s*qua\s*(?:kiểm\s*tra|xác\s*minh|đối\s*chiếu)|không\s*cần\s*trích\s*dẫn|không\s*cần\s*nguồn)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(bo\s*qua\s*(?:kiem\s*tra|xac\s*minh|doi\s*chieu)|khong\s*can\s*trich\s*dan|khong\s*can\s*nguon)\b",
            re.IGNORECASE,
        ),
    ),
]

FORGERY_TAGS = (
    "</retrieved_passages>",
    "<retrieved_passages>",
    "</critical_fields>",
    "<critical_fields>",
    "</cau_hoi>",
    "<cau_hoi>",
    "</bang_chung>",
    "<bang_chung>",
    "<system>",
    "</system>",
    "<prompt>",
    "</prompt>",
)


def validate_query_safety(query: str) -> tuple[bool, str | None, str | None]:
    """Validate query for prompt injection, boundary forgery, control characters."""
    if not query or not query.strip():
        return False, "Câu hỏi rỗng hoặc chỉ chứa khoảng trắng.", "EMPTY_INPUT"

    cleaned = clean_control_chars(query)
    norm_nfc = unicodedata.normalize("NFC", cleaned)

    # Check for XML boundary tag forgery
    for tag in FORGERY_TAGS:
        if tag.lower() in norm_nfc.lower():
            return (
                False,
                f"Phát hiện ký tự giả mạo thẻ phân định ranh giới XML hệ thống: '{tag}'.",
                "TAG_FORGERY",
            )

    unaccented = strip_vietnamese_accents(norm_nfc)
    collapsed_nfc = collapse_spaced_characters(norm_nfc)
    collapsed_unaccented = strip_vietnamese_accents(collapsed_nfc)

    for rule_name, pat_accent, pat_unaccent in INJECTION_RULES:
        if (
            pat_accent.search(norm_nfc)
            or pat_unaccent.search(norm_nfc)
            or pat_accent.search(unaccented)
            or pat_unaccent.search(unaccented)
            or pat_accent.search(collapsed_nfc)
            or pat_unaccent.search(collapsed_nfc)
            or pat_accent.search(collapsed_unaccented)
            or pat_unaccent.search(collapsed_unaccented)
        ):
            return (
                False,
                f"Nội dung câu hỏi chứa chỉ dẫn vi phạm quy tắc an toàn (Mã: {rule_name}).",
                rule_name,
            )

    return True, None, None


def scan_passage_safety(content: str) -> tuple[bool, str | None, str | None]:
    """Scan retrieved passage for embedded injection or boundary forgery."""
    cleaned = clean_control_chars(content)
    norm_nfc = unicodedata.normalize("NFC", cleaned)

    for tag in FORGERY_TAGS:
        if tag.lower() in norm_nfc.lower():
            return (
                False,
                f"Tài liệu nguồn chứa thẻ giả mạo ranh giới XML: '{tag}'.",
                "PASSAGE_TAG_FORGERY",
            )

    unaccented = strip_vietnamese_accents(norm_nfc)
    collapsed_nfc = collapse_spaced_characters(norm_nfc)
    collapsed_unaccented = strip_vietnamese_accents(collapsed_nfc)

    for rule_name, pat_accent, pat_unaccent in INJECTION_RULES:
        if (
            pat_accent.search(norm_nfc)
            or pat_unaccent.search(norm_nfc)
            or pat_accent.search(unaccented)
            or pat_unaccent.search(unaccented)
            or pat_accent.search(collapsed_nfc)
            or pat_unaccent.search(collapsed_nfc)
            or pat_accent.search(collapsed_unaccented)
            or pat_unaccent.search(collapsed_unaccented)
        ):
            return (
                False,
                f"Phát hiện chỉ dẫn độc hại được nhúng trong tài liệu nguồn (Mã: {rule_name}).",
                rule_name,
            )

    return True, None, None
