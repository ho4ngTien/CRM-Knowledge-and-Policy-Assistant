"""Retrieval domain structures and approved Vietnamese CRM glossary (VN 01, ANS 02)."""

from dataclasses import dataclass

# Controlled owner-approved Vietnamese CRM abbreviations, roles, and synonyms (VN 01 / ANS 02).
# Handed over from P4 (CKPA-55) to S3 for query normalization and expansion.
VIETNAMESE_CRM_SYNONYMS: dict[str, tuple[str, ...]] = {
    # Customer and Market Segment
    "kh": ("khách hàng", "customer", "người mua", "đối tác"),
    "khtt": ("khách hàng thân thiết", "loyal customer", "vip customer"),
    "b2b": ("doanh nghiệp với doanh nghiệp", "khách hàng doanh nghiệp", "corporate customer"),
    "b2c": ("doanh nghiệp với người tiêu dùng", "khách hàng cá nhân", "retail customer"),
    
    # Commercial & Quotation (POL-CRM-01)
    "bg": ("báo giá", "bảng báo giá", "quotation", "quote"),
    "qbg": ("quy trình báo giá", "quy định báo giá", "quotation procedure"),
    "ck": ("chiết khấu", "giảm giá", "tỷ lệ chiết khấu", "discount", "rebate"),
    "hd": ("hợp đồng", "hợp đồng kinh tế", "hợp đồng nguyên tắc", "contract", "agreement"),
    "hđ": ("hợp đồng", "hợp đồng kinh tế", "hợp đồng nguyên tắc", "contract", "agreement"),
    "po": ("đơn đặt hàng", "lệnh đặt mua", "purchase order"),
    "vat": ("thuế giá trị gia tăng", "thuế gtgt", "value added tax"),
    "gtgt": ("giá trị gia tăng",),
    
    # Approval Roles & Governance
    "cvkd": ("chuyên viên kinh doanh", "nhân viên bán hàng", "sales executive", "sales rep"),
    "tpkd": ("trưởng phòng kinh doanh", "sales manager"),
    "gdkd": ("giám đốc kinh doanh", "sales director"),
    "gđkd": ("giám đốc kinh doanh", "sales director"),
    "gdcn": ("giám đốc chi nhánh", "branch manager", "branch director"),
    "gđcn": ("giám đốc chi nhánh", "branch manager", "branch director"),
    "tgd": ("tổng giám đốc", "general director", "ceo"),
    "tgđ": ("tổng giám đốc", "general director", "ceo"),
    "qlbh": ("quản lý bán hàng", "sales supervisor"),
    
    # Warranty & Service Support (POL-CRM-02)
    "cskh": ("chăm sóc khách hàng", "dịch vụ khách hàng", "customer service", "customer support"),
    "bh": ("bảo hành", "chính sách bảo hành", "phiếu bảo hành", "warranty"),
    "bd": ("bảo dưỡng", "bảo trì định kỳ", "maintenance"),
    "bđ": ("bảo dưỡng", "bảo trì định kỳ", "maintenance"),
    "cvdv": ("cố vấn dịch vụ", "service advisor"),
    "ktv": ("kỹ thuật viên", "thợ kỹ thuật", "technician"),
    "scc": ("sửa chữa chung", "general repair"),
    "ds": ("đồng sơn", "sơn và gò hàn", "body and paint"),
    "đs": ("đồng sơn", "sơn và gò hàn", "body and paint"),
    
    # Inventory & Warehouse
    "bo": ("đơn hàng chờ", "hàng đặt trước chưa lưu kho", "back order"),
    "stock": ("hàng tồn kho", "hàng lưu kho sẵn có", "available inventory"),
    
    # Legal, Identity & Compliance
    "mst": ("mã số thuế", "tax code"),
    "cccd": ("căn cước công dân", "định danh cá nhân", "citizen identity"),
    "cmnd": ("chứng minh nhân dân", "identity card"),
    "nd": ("nghị định", "decree"),
    "nđ": ("nghị định", "decree"),
    "tt": ("thông tư", "circular"),
    "qd": ("quyết định", "decision"),
    "qđ": ("quyết định", "decision"),
    "sla": ("cam kết thời gian giải quyết", "cam kết dịch vụ", "service level agreement"),
    "sop": ("quy trình chuẩn", "quy trình vận hành tiêu chuẩn", "standard operating procedure"),
    "pii": (
        "thông tin định danh cá nhân",
        "dữ liệu cá nhân",
        "personally identifiable information",
    ),
}

# Vietnamese negation terms that MUST BE PRESERVED during normalization (ANS 02, ANS 07).
# Stripping negations causes severe polarity inversion and is strictly prohibited.
VIETNAMESE_NEGATIONS: tuple[str, ...] = (
    "không",
    "chưa",
    "chẳng",
    "miễn",
    "ngoại trừ",
    "ngoài",
    "không được",
    "cấm",
    "loại trừ",
    "không áp dụng",
    "vắng mặt",
    "thiếu",
    "từ chối",
    "hủy",
)

# Unaccented Vietnamese common queries mapping to standard accented forms (VN 01 Profile)
VIETNAMESE_UNACCENT_MAPPINGS: dict[str, str] = {
    "chiet khau": "chiết khấu",
    "bao gia": "báo giá",
    "hop dong": "hợp đồng",
    "khach hang": "khách hàng",
    "bao hanh": "bảo hành",
    "bao duong": "bảo dưỡng",
    "co van dich vu": "cố vấn dịch vụ",
    "chuyen vien kinh doanh": "chuyên viên kinh doanh",
    "truong phong kinh doanh": "trưởng phòng kinh doanh",
    "giam doc kinh doanh": "giám đốc kinh doanh",
    "giam doc chi nhanh": "giám đốc chi nhánh",
    "tong giam doc": "tổng giám đốc",
    "dong co 3 pha": "động cơ công nghiệp 3 pha",
    "dong co phong no": "động cơ phòng nổ",
    "bien tan": "biến tần trung thế",
    "bien tan trung the": "biến tần trung thế",
    "bo truyen dong": "bộ truyền động bánh răng",
    "phu tung": "phụ tùng thay thế",
    "hoa don gtgt": "hóa đơn giá trị gia tăng",
    "thue vat": "thuế giá trị gia tăng",
    "ma so thue": "mã số thuế",
    "doi tra hang": "đổi trả hàng",
    "sua chua chung": "sửa chữa chung",
    "dong son": "đồng sơn",
    "bien ban giam dinh": "biên bản giám định hiện trường",
    "to trinh": "tờ trình phê duyệt",
    "tam ung": "tạm ứng thanh toán",
    "dat coc": "đặt cọc hợp đồng",
    "thu hoi": "thu hồi chính sách",
    "hieu luc": "ngày hiệu lực",
    "het han": "hết hạn hiệu lực",
}

# Technical and bilingual CRM product terms
VIETNAMESE_TECHNICAL_TERMS: dict[str, str] = {
    "motor 3 pha": "Động cơ công nghiệp 3 pha",
    "inverter": "Biến tần trung thế",
    "gearbox": "Bộ truyền động bánh răng",
    "explosion proof motor": "Động cơ phòng nổ",
    "spare parts": "Phụ tùng thay thế",
    "back order": "Đơn hàng đặt phụ tùng không dự trữ (BO)",
    "stock inventory": "Hàng dự trữ lưu kho (Stock)",
    "quotation": "Bảng báo giá",
    "discount rate": "Tỷ lệ chiết khấu thương mại",
    "down payment": "Tiền đặt cọc / tạm ứng",
    "warranty claim": "Yêu cầu bảo hành / khiếu nại bảo hành",
    "inspection report": "Biên bản giám định hiện trường",
    "tombstone": "Đánh dấu xóa mềm / thu hồi bản ghi",
    "quarantine": "Hàng đợi cách ly lỗi schema / thiếu phụ lục",
    "hold": "Tạm dừng xuất kết luận do xung đột thẩm quyền / điều khoản",
    "referral": "Chuyển tiếp lên cấp thẩm quyền phê duyệt cao hơn",
}


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    """Intermediate hybrid RRF retrieval candidate prior to answer generation."""

    passage_id: str
    score: float
    matched_terms: tuple[str, ...]
