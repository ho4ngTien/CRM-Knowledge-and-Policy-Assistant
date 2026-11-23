"""
legacy/s4/services/prompt_builder.py
Xây dựng Prompt tiếng Việt có phiên bản (CKPA-41).
Tuân thủ:
- ANS 01: Hỗ trợ nhân viên CRM.
- VN 01: Bảo toàn nguyên vẹn câu hỏi, kể cả không dấu, số tiền, ngày tháng, phủ định.
- Ranh giới rõ ràng: <cau_hoi> và <bang_chung id="...">.
- Không chứa bất kỳ API Key, mật khẩu hay thông tin xác thực nào trong prompt.
"""

from pathlib import Path
from typing import List, Tuple
from legacy.s4 import config
from legacy.s4.models import EvidenceChunk

BASE_DIR = Path(__file__).resolve().parents[2]
PROMPTS_DIR = BASE_DIR / "prompts"


def get_system_prompt() -> str:
    """Đọc System Prompt tiếng Việt có phiên bản."""
    prompt_file = PROMPTS_DIR / f"system_prompt_vi_{config.PROMPT_VERSION}.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    # Fallback an toàn nếu chưa tìm thấy file
    return (
        "Bạn là Trợ lý AI Tra cứu Chính sách NỘI BỘ CRM. "
        "Chỉ sử dụng thông tin trong khối bằng chứng. Trả JSON theo schema quy định."
    )


def get_user_template() -> str:
    """Đọc template ghép câu hỏi và bằng chứng."""
    template_file = PROMPTS_DIR / f"user_template_vi_{config.PROMPT_VERSION}.md"
    if template_file.exists():
        return template_file.read_text(encoding="utf-8")
    return (
        "<cau_hoi>\n{question}\n</cau_hoi>\n\n"
        "<danh_sach_bang_chung>\n{evidence_blocks}\n</danh_sach_bang_chung>"
    )


def format_evidence_blocks(evidence_chunks: List[EvidenceChunk]) -> str:
    """Định dạng các khối bằng chứng có ranh giới rõ ràng."""
    if not evidence_chunks:
        return "(Không có bằng chứng nào được cung cấp)"

    blocks = []
    for idx, chunk in enumerate(evidence_chunks, start=1):
        cid = chunk.chunk_id or f"chunk_{idx:02d}"
        doc = chunk.document_name.strip()
        sec = chunk.section.strip()
        text = chunk.text.strip()
        block = (
            f'<bang_chung id="{cid}" doc="{doc}" section="{sec}">\n'
            f"{text}\n"
            f"</bang_chung>"
        )
        blocks.append(block)
    return "\n\n".join(blocks)


def build_prompts(
    question: str,
    evidence_chunks: List[EvidenceChunk]
) -> Tuple[str, str]:
    """
    Ghép System Prompt và User Prompt.
    
    Quy tắc:
    - Bảo toàn câu hỏi gốc (không cắt bớt, không tự thêm dấu, không sửa số liệu).
    - Đặt câu hỏi và bằng chứng vào đúng ranh giới XML tags.
    - Tuyệt đối không để lộ thông tin xác thực.
    
    Returns:
        Tuple[str, str]: (system_prompt, user_prompt)
    """
    system_prompt = get_system_prompt()
    user_template = get_user_template()

    evidence_blocks = format_evidence_blocks(evidence_chunks)
    
    # Ghép câu hỏi nguyên vẹn không chỉnh sửa
    user_prompt = user_template.replace("{question}", question)
    user_prompt = user_prompt.replace("{evidence_blocks}", evidence_blocks)

    return system_prompt, user_prompt

