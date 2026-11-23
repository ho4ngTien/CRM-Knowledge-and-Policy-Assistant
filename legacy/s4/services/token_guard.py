"""
legacy/s4/services/token_guard.py
Quản lý giới hạn Token và điều phối lượt gọi LLM an toàn (CKPA-42).
Tuân thủ:
1. Đọc mọi cấu hình DUY NHẤT từ legacy/s4/config.py.
2. Hàm estimate_tokens ước lượng bảo thủ cho tiếng Việt: max(từ * 3, ký tự / 2).
   (Lưu ý: Đây là ước lượng chủ động khi chưa có Tokenizer chính thức, dễ dàng thay thế).
3. Kiểm tra trước khi gọi: Input > 6.000 tokens => HOLD TOKEN_LIMIT_EXCEEDED.
   TUYỆT ĐỐI KHÔNG cắt gọt dữ liệu âm thầm.
4. Kiểm soát tối đa 2 lần gọi LLM mỗi package (lần 2 chỉ dùng cho retry định dạng).
   Lần thứ 3 bị chặn ngay => HOLD CALL_LIMIT_EXCEEDED.
5. Luôn truyền max_tokens = 900 vào client. Đầu ra vượt ngưỡng coi là lỗi định dạng.
"""

from typing import Optional, Tuple
from legacy.s4 import config
from legacy.s4.services.hold_reasons import HoldReason
from legacy.s4.services.llm_client import LLMClient


def estimate_tokens(text: str) -> int:
    """
    Ước lượng số lượng Token bảo thủ cho văn bản tiếng Việt.
    Công thức: max(số_từ * TOKEN_ESTIMATE_WORD_MULTIPLIER, số_ký_tự // TOKEN_ESTIMATE_CHAR_DIVISOR).
    
    Lưu ý kỹ thuật: Đây là phương pháp ước lượng bảo thủ khi chưa thống nhất
    Tokenizer chính thức từ mô hình. Được thiết kế theo dạng hàm độc lập để thay thế khi có SDK thật.
    """
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    token_by_words = words * config.TOKEN_ESTIMATE_WORD_MULTIPLIER
    token_by_chars = chars // config.TOKEN_ESTIMATE_CHAR_DIVISOR
    return max(token_by_words, token_by_chars)


class LLMGateway:
    """
    Cổng giao tiếp duy nhất kết nối với LLMClient.
    Áp dụng Token Guard và kiểm soát nghiêm ngặt số lần gọi.
    Không có bất kỳ luồng nào trong hệ thống được phép vượt qua cổng này.
    """

    def __init__(self, client: LLMClient):
        self.client: LLMClient = client
        self.call_count: int = 0

    def reset_call_count(self) -> None:
        """Đặt lại bộ đếm khi bắt đầu một package câu hỏi mới."""
        self.call_count = 0

    def execute_call(
        self,
        prompt: str,
        system_prompt: str = "",
        is_retry: bool = False
    ) -> Tuple[Optional[str], Optional[HoldReason], str]:
        """
        Thực hiện một lượt gọi LLM có kiểm soát an toàn.
        
        Args:
            prompt: Nội dung User Prompt (câu hỏi và bằng chứng).
            system_prompt: Nội dung System Prompt quy định hành vi.
            is_retry: Cờ đánh dấu lượt gọi thử lại khi gặp lỗi định dạng.
            
        Returns:
            Tuple[Optional[str], Optional[HoldReason], str]:
            (Phản hồi từ LLM, Mã HOLD nếu bị chặn, Thông điệp giải thích chi tiết)
        """
        # 1. Kiểm tra giới hạn số lần gọi (Tối đa 2 lần / package)
        if self.call_count >= config.MAX_LLM_CALLS_PER_PACKAGE:
            return (
                None,
                HoldReason.CALL_LIMIT_EXCEEDED,
                f"Đã đạt giới hạn tối đa {config.MAX_LLM_CALLS_PER_PACKAGE} lượt gọi cho package này. "
                "Lần gọi thứ 3 đã bị chặn an toàn."
            )

        # Lần gọi thứ 2 chỉ được phép khi có cờ retry định dạng
        if self.call_count == 1 and not is_retry:
            return (
                None,
                HoldReason.CALL_LIMIT_EXCEEDED,
                "Lượt gọi thứ hai chỉ được phép sử dụng cho mục đích thử lại định dạng (Retry on format error)."
            )

        # 2. Kiểm tra giới hạn Token đầu vào TRƯỚC KHI GỌI (Tối đa 6.000 input tokens)
        combined_input = f"{system_prompt}\n{prompt}"
        estimated_input_tokens = estimate_tokens(combined_input)
        if estimated_input_tokens > config.MAX_INPUT_TOKENS:
            return (
                None,
                HoldReason.TOKEN_LIMIT_EXCEEDED,
                f"Tổng số token đầu vào ước lượng ({estimated_input_tokens}) vượt quá giới hạn cho phép "
                f"({config.MAX_INPUT_TOKENS} tokens). Hệ thống từ chối cắt gọt nội dung âm thầm."
            )

        # 3. Tăng bộ đếm và gọi LLMClient với max_output_tokens cố định = 900
        self.call_count += 1
        raw_output = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=config.MAX_OUTPUT_TOKENS
        )

        # 4. Kiểm tra giới hạn đầu ra (Tối đa 900 output tokens)
        estimated_output_tokens = estimate_tokens(raw_output)
        if estimated_output_tokens > config.MAX_OUTPUT_TOKENS:
            return (
                None,
                HoldReason.INVALID_LLM_FORMAT,
                f"Đầu ra từ LLM ước lượng ({estimated_output_tokens} tokens) vượt quá giới hạn 900 tokens. "
                "Nội dung có thể bị cắt dở dang nên bị loại bỏ."
            )

        return raw_output, None, "Thành công"

