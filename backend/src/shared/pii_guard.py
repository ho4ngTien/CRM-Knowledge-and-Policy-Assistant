"""PII detection & data minimization helpers for Base Scope (SEC 02)."""

import re
from dataclasses import dataclass

_PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?84|0)(?:\d[\s.-]?){8,10}(?!\d)")
_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_ID_PATTERN = re.compile(r"\b\d{9}\b|\b\d{12}\b")


@dataclass(frozen=True, slots=True)
class PIIScanResult:
    """Summary of suspected personal identifiers found in a free-text query."""

    has_suspected_pii: bool
    detected_categories: list[str]
    redacted_preview: str
    warning_message_vi: str


def scan_query_for_pii(text: str) -> PIIScanResult:
    """Detect common VN phone numbers, emails, and national IDs before LLM transmission."""
    categories: list[str] = []
    redacted = text

    if _PHONE_PATTERN.search(redacted):
        categories.append("phone_number")
        redacted = _PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)

    if _EMAIL_PATTERN.search(redacted):
        categories.append("email")
        redacted = _EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)

    if _ID_PATTERN.search(redacted):
        categories.append("national_or_tax_id")
        redacted = _ID_PATTERN.sub("[REDACTED_ID]", redacted)

    warning = (
        "Cảnh báo SEC 02: Không nhập thông tin định danh khách hàng (SĐT, email, CCCD/MST) "
        "vào câu hỏi; hệ thống chỉ cần mô tả tình huống và phạm vi chính sách."
        if categories
        else ""
    )
    return PIIScanResult(
        has_suspected_pii=bool(categories),
        detected_categories=categories,
        redacted_preview=redacted,
        warning_message_vi=warning,
    )
