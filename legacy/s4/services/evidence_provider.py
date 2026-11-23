"""
legacy/s4/services/evidence_provider.py
Evidence Integration Layer (Giao diện trừu tượng và Adapter tích hợp S3).
Cung cấp:
- EvidenceProvider: Lớp trừu tượng (Interface) định nghĩa hợp đồng gọi truy xuất từ S3.
- NullEvidenceProvider: Triển khai mặc định khi S3 chưa bàn giao - luôn trả về rỗng
  để hệ thống an toàn kích hoạt trạng thái HOLD (CKPA-47).
"""

from abc import ABC, abstractmethod
from typing import List
from legacy.s4.models import Citation


class EvidenceProvider(ABC):
    """Giao diện trừu tượng tích hợp với S3 Retrieval & Policy Engine."""

    @abstractmethod
    def retrieve_evidence(self, question: str) -> List[Citation]:
        """
        Truy xuất danh sách trích dẫn bằng chứng từ kho tài liệu chính sách.
        
        Args:
            question: Câu hỏi từ nhân viên CRM.
            
        Returns:
            List[Citation]: Danh sách trích dẫn nguyên văn từ tài liệu nguồn.
        """
        pass


class NullEvidenceProvider(EvidenceProvider):
    """
    Adapter mặc định khi chưa kết nối với S3.
    Luôn trả về danh sách bằng chứng rỗng để đảm bảo hệ thống không bao giờ
    tự bịa tài liệu nguồn và kích hoạt HOLD theo đúng quy định an toàn.
    """

    def retrieve_evidence(self, question: str) -> List[Citation]:
        # Trả về rỗng: Chưa có kết nối S3 chính thức
        return []

