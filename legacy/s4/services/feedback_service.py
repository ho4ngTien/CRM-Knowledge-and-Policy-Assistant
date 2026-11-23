"""
legacy/s4/services/feedback_service.py
Dịch vụ xử lý phản hồi từ người dùng (Feedback Service).
Đóng vai trò lớp đệm trung gian giữa UI và tầng lưu trữ.
"""

from typing import List, Dict, Any, Optional
from legacy.s4.services.database import (
    save_feedback,
    get_recent_feedbacks,
    VALID_FEEDBACK_TYPES,
)
from legacy.s4.services.input_guard import sanitize_for_log


def get_valid_feedback_types() -> set[str]:
    """Trả về tập hợp các nhóm phản hồi chuẩn được phép."""
    return set(VALID_FEEDBACK_TYPES)


def submit_feedback(
    question: str,
    feedback_type: Optional[str] = None,
    comment: str = "",
    is_helpful: Optional[bool] = None,
    flag_missing_exception: bool = False,
    flag_unfounded_claim: bool = False,
) -> bool:
    """
    Tiếp nhận phản hồi từ UI, làm sạch câu hỏi và lưu vào hệ thống.
    """
    sanitized_q = sanitize_for_log(question)
    return save_feedback(
        question=sanitized_q,
        feedback_type=feedback_type,
        comment=comment,
        is_helpful=is_helpful,
        flag_missing_exception=flag_missing_exception,
        flag_unfounded_claim=flag_unfounded_claim,
    )


def list_recent_feedbacks(limit: int = 10) -> List[Dict[str, Any]]:
    """Truy vấn danh sách phản hồi gần nhất phục vụ kiểm tra."""
    return get_recent_feedbacks(limit=limit)
