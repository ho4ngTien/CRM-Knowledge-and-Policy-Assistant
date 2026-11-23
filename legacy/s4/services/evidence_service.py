"""
legacy/s4/services/evidence_service.py
Evidence Integration Layer: Tiếp nhận kết quả truy xuất và bằng chứng từ S3.
Nếu chưa có bằng chứng xác thực từ S3, tuân thủ nguyên tắc HOLD (CKPA-47) - không tự bịa nguồn.
"""

from typing import List, Optional
from legacy.s4.models import Citation


class EvidenceService:
    """Service tích hợp với S3 (Retrieval & Policy Engine)."""

    def __init__(self):
        # Khi S3 hoàn thiện, sẽ kết nối trực tiếp với hàm search/retrieval của S3 tại đây
        pass

    def retrieve_evidence(self, question: str) -> List[Citation]:
        """
        Truy xuất các đoạn trích dẫn nguyên văn liên quan từ kho tài liệu.
        Quy tắc an toàn VI.1 & VI.2: Không tự tạo chính sách giả lập kết quả thật.
        Nếu không có tài liệu nguồn chính thức, trả về danh sách rỗng để kích hoạt HOLD.
        """
        # Mẫu tích hợp chuẩn: Trả về danh sách trích dẫn nguồn
        # Khi S3 bàn giao hàm retrieval, ta sẽ gọi s3.retrieve(question) ở đây.
        return []

