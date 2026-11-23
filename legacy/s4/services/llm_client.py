"""
legacy/s4/services/llm_client.py
LLM Integration Layer: Lớp trừu tượng và Mock Client kết nối LLM.
Tuân thủ nguyên tắc an toàn:
- Không hardcode API Key hay nhà cung cấp thật.
- Cung cấp MockLLMClient để kiểm thử offline an toàn, không tốn chi phí và không phụ thuộc mạng.
- Hỗ trợ giới hạn max_output_tokens mặc định 900 theo CKPA-42.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMClient(ABC):
    """Giao diện trừu tượng kết nối mô hình ngôn ngữ lớn (LLM)."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 900
    ) -> str:
        """
        Gửi yêu cầu tạo phản hồi tới LLM.
        
        Args:
            prompt: Nội dung prompt kèm dữ liệu câu hỏi và bằng chứng.
            system_prompt: System prompt quy định hành vi và định dạng đầu ra.
            max_tokens: Giới hạn token đầu ra (mặc định tối đa 900 theo CKPA-42).
            
        Returns:
            str: Chuỗi văn bản phản hồi từ LLM (thường là định dạng JSON cố định).
        """
        pass


class MockLLMClient(LLMClient):
    """
    Mock Client phục vụ kiểm thử tự động và chạy offline.
    Không gọi bất kỳ dịch vụ mạng nào.
    """

    def __init__(self, predefined_response: Optional[str] = None):
        self.predefined_response = predefined_response or "{}"
        self.call_count: int = 0
        self.last_prompt: Optional[str] = None
        self.last_system_prompt: Optional[str] = None
        self.last_max_tokens: Optional[int] = None

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 900
    ) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        self.last_system_prompt = system_prompt
        self.last_max_tokens = max_tokens
        return self.predefined_response

