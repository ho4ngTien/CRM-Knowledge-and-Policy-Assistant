"""Retrieval domain structures and approved Vietnamese CRM glossary (VN 01)."""

from dataclasses import dataclass

# Controlled owner-approved Vietnamese CRM abbreviations & synonyms (VN 01).
VIETNAMESE_CRM_SYNONYMS: dict[str, tuple[str, ...]] = {
    "kh": ("khách hàng", "customer"),
    "bg": ("báo giá", "quotation"),
    "ck": ("chiết khấu", "discount"),
    "bh": ("bảo hành", "warranty"),
    "hđ": ("hợp đồng", "contract"),
    "cskh": ("chăm sóc khách hàng", "customer service"),
    "qlbh": ("quản lý bán hàng", "sales manager"),
    "gđkd": ("giám đốc kinh doanh", "sales director"),
}


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    """Intermediate hybrid RRF retrieval candidate prior to answer generation."""

    passage_id: str
    score: float
    matched_terms: tuple[str, ...]
