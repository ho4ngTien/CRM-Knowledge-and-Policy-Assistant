# CÂU HỎI THỐNG NHẤT HỢP ĐỒNG TÍCH HỢP VỚI S3 (RETRIEVAL & POLICY ENGINE)

**Người gửi:** S4 (Application + LLM Engineer)  
**Người nhận:** S3 (Retrieval & Policy Engine)  
**Mục tiêu:** Thống nhất giao diện dữ liệu (Data Contract) và hành vi lỗi giữa S3 và S4 theo chuẩn WP04.

---

### 1. Định dạng bằng chứng (Evidence / Chunk Schema)
- S3 sẽ trả về bằng chứng dưới cấu trúc nào (Python `dataclass`, `dict`, hay Pydantic model)?
- Mỗi đoạn trích dẫn (chunk) gồm những trường thông tin cụ thể nào? Hiện tại S4 đang đề xuất:
  - `document_name`: Tên văn bản / chính sách (Ví dụ: *"Quy định mở tài khoản số 123/2025/QĐ-TGĐ"*).
  - `section`: Vị trí (Ví dụ: *"Điều 4, Khoản 2, Trang 5"*).
  - `verbatim_quote`: Nội dung trích dẫn nguyên văn không chỉnh sửa.
  - `clause_code`: Mã định danh điều khoản (KNW 01) nếu có.
  - `source_url` / `reference_link`: Đường dẫn nội bộ hoặc link tới tài liệu gốc.
  - `effective_date`: Ngày hiệu lực của riêng điều khoản nếu khác ngày hiệu lực của toàn văn bản.

### 2. Thông tin Ngày hiệu lực (Effective Date) và Phạm vi (Scope)
- S3 sẽ trích xuất sẵn `effective_date` và `scope` ở cấp độ văn bản hay S4 phải tổng hợp từ các chunks?
- Khi một chính sách có nhiều phiên bản (cũ và mới thay thế), S3 lọc phiên bản mới nhất như thế nào?

### 3. Kiểm tra quyền truy cập (Access Control / Authorization)
- Việc kiểm tra quyền truy cập tài liệu mật/nội bộ do S3 lọc trước khi trả bằng chứng, hay S4 phải nhận thêm cờ phân quyền (`classification_level`, `allowed_roles`) để lọc bằng code?
- Nguyên tắc: Không để LLM tự quyết định quyền truy cập.

### 4. Link tham chiếu gốc và Mã điều khoản (KNW 01)
- Kho tài liệu của S3 có sẵn URL nội bộ (hoặc đường dẫn mạng nội bộ) tới file PDF/Docx gốc không?
- Định dạng mã điều khoản (`clause_code`) theo quy ước nào của ngân hàng?

### 5. Cách S3 phản hồi khi không tìm thấy hoặc xảy ra lỗi
- Khi không có tài liệu liên quan, S3 trả về danh sách rỗng (`[]`) hay raise Exception?
- Khi dịch vụ S3 gặp sự cố kỹ thuật (timeout, lỗi vector DB), định dạng mã lỗi trả về là gì để S4 hiển thị lý do HOLD phù hợp (Fail Visibly)?


### 6. Metadata quản trị và Ranh giới trách nhiệm (Cập nhật Giai đoạn 3)
- **Đơn vị phụ trách chính sách (`policy_owner`):** S3 có cung cấp trường này trong metadata của tài liệu không (ví dụ: *"Khối Quản trị Rủi ro"*, *"Khối Bán lẻ"*), hay S4 phải tra cứu qua bảng ánh xạ riêng?
- **Phạm vi (`scope`) và Ngày hiệu lực (`effective_date`):** S3 gắn ở cấp văn bản hay từng điều khoản con? Trường hợp văn bản có nhiều sửa đổi bổ sung từng điều khoản, S3 có cung cấp ngày hiệu lực riêng của điều khoản đó không?
- **Giới hạn kích thước chunk (Chunk Token Budget):** Để đảm bảo tổng input prompt không vượt quá giới hạn an toàn **6.000 input tokens** (CKPA-42), S3 dự kiến trả về tối đa bao nhiêu chunks cho mỗi câu hỏi và mỗi chunk dài tối đa bao nhiêu từ/tokens?
