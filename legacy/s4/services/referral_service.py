"""
legacy/s4/services/referral_service.py
Dịch vụ xử lý chuyển câu hỏi đến chuyên viên chính sách (Referral Service).
Chỉ ghi nhận cục bộ, không gửi email, không gọi mạng.
"""

from typing import List, Dict, Any
from legacy.s4.services.database import save_referral, get_recent_referrals
from legacy.s4.services.input_guard import sanitize_for_log


def submit_referral(
    question: str,
    reason: str,
    policy_owner: str = "",
    status: str = "Mới tạo",
) -> bool:
    """
    Tiếp nhận yêu cầu chuyển chuyên viên từ UI, rút gọn nội dung và lưu cục bộ.
    """
    sanitized_q = sanitize_for_log(question)
    return save_referral(
        question=sanitized_q,
        reason=reason,
        policy_owner=policy_owner,
        status=status,
    )


def list_recent_referrals(limit: int = 10) -> List[Dict[str, Any]]:
    """Truy vấn danh sách yêu cầu chuyển gần nhất để hiển thị."""
    return get_recent_referrals(limit=limit)
