"""
app/config.py
NƠI DUY NHẤT chứa toàn bộ các thông số cấu hình và giới hạn an toàn của S4:
- Giới hạn Token và lượt gọi LLM (CKPA-42)
- Giới hạn độ dài từ giải thích ngắn (100 - 250 từ)
- Giới hạn độ dài tối thiểu của trích dẫn (MIN_CITATION_WORDS)
- Giới hạn độ dài câu hỏi tối đa (MAX_QUESTION_CHARS - Đề xuất Giai đoạn 4)
- Hệ số ước lượng Token bảo thủ cho tiếng Việt
- Phiên bản cấu hình và Prompt
"""

# 1. Giới hạn cuộc gọi LLM và Token (CKPA-42, CKPA-7 / Gate G0)
MAX_LLM_CALLS_PER_PACKAGE: int = 2
MAX_INPUT_TOKENS: int = 6000
MAX_OUTPUT_TOKENS: int = 900
LLM_MAX_CALLS_PER_MONTH: int = 2000
ENABLE_ANSWER_STREAMING: bool = False
# O1 (Reasoning model) loại trừ khỏi Base Scope theo SRS §2.3; Base Scope dùng gpt-4o với streaming=false.

# 2. Giới hạn độ dài nội dung giải thích ngắn (Quy định bổ sung Giai đoạn 1)
EXPLANATION_MIN_WORDS: int = 100
EXPLANATION_MAX_WORDS: int = 250

# 3. Giới hạn độ dài tối thiểu của trích dẫn nguyên văn (Giai đoạn 3 - Đề xuất, chưa chốt)
MIN_CITATION_WORDS: int = 4

# 4. Giới hạn ký tự câu hỏi đầu vào (Giai đoạn 4 - Đề xuất, chưa chốt)
MAX_QUESTION_CHARS: int = 1000

# 5. Hệ số ước lượng Token bảo thủ cho tiếng Việt (khi chưa có Tokenizer chính thức)
TOKEN_ESTIMATE_WORD_MULTIPLIER: int = 3
TOKEN_ESTIMATE_CHAR_DIVISOR: int = 2

# 6. Phiên bản hệ thống và Prompt (Phục vụ truy vết và kiểm soát thay đổi)
PROMPT_VERSION: str = "v1.1"
CONFIG_VERSION: str = "1.2.0"
