"""
legacy/s4/services/hold_reasons.py
Định nghĩa danh mục mã trạng thái HOLD (CKPA-47 & ANS 06).
Nguyên tắc Fail Visibly:
Mỗi mã lỗi đều có:
1. Thông điệp tiếng Việt minh bạch, giải thích rõ nguyên nhân.
2. Hướng dẫn hành động cụ thể cho nhân viên CRM.
3. Câu hỏi gợi ý làm rõ cố định (ANS 01, ANS 06) để nhân viên CRM có thể hỏi lại
   khách hàng hoặc làm rõ yêu cầu, tuyệt đối không để LLM tự bịa đặt.
"""

from enum import Enum
from typing import NamedTuple, Dict


class HoldInfo(NamedTuple):
    """Chi tiết thông điệp, hướng dẫn và câu hỏi làm rõ cố định của từng mã HOLD."""
    code: str
    message: str
    guidance: str
    clarifying_question: str = ""


class HoldReason(str, Enum):
    """14 mã lý do kích hoạt trạng thái HOLD theo chuẩn an toàn ngân hàng (Cập nhật Giai đoạn 4, 6)."""
    NO_EVIDENCE = "NO_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"
    ACCESS_DENIED = "ACCESS_DENIED"
    CITATION_UNVERIFIED = "CITATION_UNVERIFIED"
    INVALID_FIELDS = "INVALID_FIELDS"
    LLM_ERROR = "LLM_ERROR"
    INVALID_LLM_FORMAT = "INVALID_LLM_FORMAT"
    TOKEN_LIMIT_EXCEEDED = "TOKEN_LIMIT_EXCEEDED"
    CALL_LIMIT_EXCEEDED = "CALL_LIMIT_EXCEEDED"
    INJECTION_SUSPECTED = "INJECTION_SUSPECTED"
    EMPTY_INPUT = "EMPTY_INPUT"
    EVIDENCE_SERVICE_ERROR = "EVIDENCE_SERVICE_ERROR"
    UNGROUNDED_CONTENT = "UNGROUNDED_CONTENT"


HOLD_DETAILS: Dict[HoldReason, HoldInfo] = {
    HoldReason.NO_EVIDENCE: HoldInfo(
        code="NO_EVIDENCE",
        message="Không tìm thấy văn bản quy định hoặc bằng chứng liên quan trong kho dữ liệu chính sách.",
        guidance="Vui lòng kiểm tra lại từ khóa tìm kiếm hoặc sử dụng tính năng 'Chuyển người phụ trách' (Referral) để gửi câu hỏi tới phòng Quản lý Chính sách.",
        clarifying_question="Bạn có thể cung cấp thêm số hiệu văn bản, tên gói sản phẩm hoặc từ khóa nghiệp vụ cụ thể hơn không?"
    ),
    HoldReason.INSUFFICIENT_EVIDENCE: HoldInfo(
        code="INSUFFICIENT_EVIDENCE",
        message="Tài liệu tìm thấy không có đủ thông tin chi tiết để giải đáp trọn vẹn câu hỏi.",
        guidance="Khuyến nghị tra cứu văn bản gốc tại kho quy chế nội bộ hoặc liên hệ chuyên viên phụ trách sản phẩm.",
        clarifying_question="Bạn có thể làm rõ thêm điều kiện cụ thể hoặc đối tượng khách hàng trong tình huống này không?"
    ),
    HoldReason.SCOPE_MISMATCH: HoldInfo(
        code="SCOPE_MISMATCH",
        message="Chính sách tìm thấy không áp dụng cho đối tượng hoặc phân khúc khách hàng này.",
        guidance="Xác minh lại phân khúc khách hàng (Cá nhân, SME, Doanh nghiệp lớn) hoặc chuyển câu hỏi cho bộ phận phụ trách.",
        clarifying_question="Khách hàng thuộc phân khúc nào (Khách hàng cá nhân, Doanh nghiệp SME hay Khách hàng ưu tiên) và kênh giao dịch nào?"
    ),
    HoldReason.ACCESS_DENIED: HoldInfo(
        code="ACCESS_DENIED",
        message="Văn bản quy định yêu cầu cấp quyền bảo mật cao hơn để truy cập.",
        guidance="Liên hệ quản trị viên chính sách để được cấp quyền hoặc yêu cầu cán bộ có thẩm quyền tra cứu.",
        clarifying_question="Bạn có thể xác nhận lại thẩm quyền truy cập hoặc vai trò được phân công đối với văn bản này không?"
    ),
    HoldReason.CITATION_UNVERIFIED: HoldInfo(
        code="CITATION_UNVERIFIED",
        message="Nội dung trích dẫn không khớp nguyên văn 100% với tài liệu nguồn chính thức.",
        guidance="Hệ thống đã chặn hiển thị câu trả lời để tránh sai lệch thông tin. Vui lòng đối chiếu trực tiếp văn bản gốc.",
        clarifying_question="Bạn có thể đối chiếu trực tiếp văn bản quy định gốc lưu tại đơn vị nghiệp vụ không?"
    ),
    HoldReason.INVALID_FIELDS: HoldInfo(
        code="INVALID_FIELDS",
        message="Dữ liệu câu trả lời không đáp ứng đầy đủ cấu trúc chuẩn (thiếu trường hoặc độ dài từ sai quy định).",
        guidance="Hệ thống không công nhận câu trả lời này. Vui lòng thử lại hoặc gửi câu hỏi qua kênh Referral.",
        clarifying_question="Bạn có thể đặt lại câu hỏi rõ ràng hơn với đầy đủ thông tin bối cảnh không?"
    ),
    HoldReason.LLM_ERROR: HoldInfo(
        code="LLM_ERROR",
        message="Mô hình ngôn ngữ gặp sự cố xử lý kỹ thuật trong quá trình tổng hợp câu trả lời.",
        guidance="Vui lòng thử lại sau giây lát hoặc tra cứu sổ tay quy trình nghiệp vụ.",
        clarifying_question="Bạn có muốn thử gửi lại câu hỏi hoặc chuyển tiếp sang chuyên viên chính sách không?"
    ),
    HoldReason.INVALID_LLM_FORMAT: HoldInfo(
        code="INVALID_LLM_FORMAT",
        message="Đầu ra từ mô hình không đúng định dạng JSON chuẩn đã quy định.",
        guidance="Yêu cầu đã bị hủy để tránh hiển thị sai lệch. Vui lòng thực hiện lại câu hỏi.",
        clarifying_question="Bạn có thể đặt lại câu hỏi ngắn gọn, trực diện vào nội dung cần tra cứu không?"
    ),
    HoldReason.TOKEN_LIMIT_EXCEEDED: HoldInfo(
        code="TOKEN_LIMIT_EXCEEDED",
        message="Nội dung đầu vào hoặc tài liệu vượt quá giới hạn an toàn token cho phép.",
        guidance="Vui lòng rút gọn câu hỏi hoặc chia nhỏ tình huống cần tra cứu.",
        clarifying_question="Bạn có thể chia nhỏ tình huống này thành các câu hỏi riêng cho từng nghiệp vụ cụ thể không?"
    ),
    HoldReason.CALL_LIMIT_EXCEEDED: HoldInfo(
        code="CALL_LIMIT_EXCEEDED",
        message="Đã vượt quá số lượt gọi mô hình cho phép (tối đa 2 lần gọi mỗi yêu cầu).",
        guidance="Tạm dừng xử lý tự động. Vui lòng chuyển câu hỏi cho chuyên viên chính sách.",
        clarifying_question="Tình huống này phức tạp, bạn có muốn chuyển sang chuyên viên chính sách (Referral) để giải đáp không?"
    ),
    HoldReason.INJECTION_SUSPECTED: HoldInfo(
        code="INJECTION_SUSPECTED",
        message="Nội dung câu hỏi hoặc bằng chứng chứa chỉ dẫn vi phạm quy tắc an toàn hoặc có dấu hiệu can thiệp hệ thống.",
        guidance="Hệ thống từ chối xử lý các câu hỏi yêu cầu bỏ qua quy định, tiết lộ thông tin mật hoặc tự ý phê duyệt.",
        clarifying_question="Bạn có thể diễn đạt lại câu hỏi tập trung vào quy định nghiệp vụ ngân hàng cần tra cứu không?"
    ),
    HoldReason.EMPTY_INPUT: HoldInfo(
        code="EMPTY_INPUT",
        message="Câu hỏi đang để trống hoặc chỉ chứa khoảng trắng.",
        guidance="Vui lòng nhập nội dung câu hỏi về chính sách ngân hàng cần hỗ trợ.",
        clarifying_question="Bạn đang cần hỗ trợ tra cứu chính sách hoặc quy định nghiệp vụ nào của ngân hàng?"
    ),
    HoldReason.EVIDENCE_SERVICE_ERROR: HoldInfo(
        code="EVIDENCE_SERVICE_ERROR",
        message="Dịch vụ truy xuất bằng chứng từ kho chính sách (S3) gặp sự cố kết nối.",
        guidance="Vui lòng kiểm tra lại kết nối mạng nội bộ hoặc thử lại sau.",
        clarifying_question="Bạn có muốn thử tra cứu lại hoặc gửi yêu cầu xử lý thủ công tới chuyên viên không?"
    ),
    HoldReason.UNGROUNDED_CONTENT: HoldInfo(
        code="UNGROUNDED_CONTENT",
        message="Phát hiện số liệu, tỷ lệ phần trăm, ngày tháng hoặc mã chính sách trong câu trả lời không xuất hiện trong tài liệu nguồn.",
        guidance="Hệ thống kích hoạt HOLD để phòng ngừa rủi ro AI tự bịa đặt số liệu tài chính. Vui lòng đối chiếu văn bản gốc.",
        clarifying_question="Bạn có thể chỉ rõ hạn mức, số tiền hoặc đối tượng cụ thể cần xác minh trong văn bản gốc không?"
    ),
}


def get_hold_info(reason: HoldReason) -> HoldInfo:
    """Lấy thông điệp, hướng dẫn và câu hỏi làm rõ chi tiết theo mã HOLD."""
    return HOLD_DETAILS.get(
        reason,
        HoldInfo(
            code="HOLD_GENERAL",
            message="Yêu cầu đang tạm dừng xử lý theo quy định kiểm soát rủi ro.",
            guidance="Vui lòng tra cứu văn bản gốc hoặc sử dụng chức năng chuyển người phụ trách.",
            clarifying_question="Bạn có thể làm rõ thêm thông tin nghiệp vụ cần tra cứu không?"
        )
    )
