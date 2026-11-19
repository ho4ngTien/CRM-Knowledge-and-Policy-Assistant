# DANH SÁCH CÂU HỎI MỞ CẦN LÀM RÕ (OPEN QUESTIONS)

**Dự án:** AI-06 CRM Knowledge and Policy Assistant (Group 7)  
**Vai trò:** S4 – Application + LLM Engineer  
**Thời điểm cập nhật:** 13/11/2026 (Hoàn thành Giai đoạn 5)  

---

### 1. Nhà cung cấp LLM và Mô hình chính thức
- Nhóm và ngân hàng dự kiến sử dụng mô hình LLM nào trong môi trường sản xuất (Azure OpenAI GPT-4o / GPT-4o-mini, Google Gemini 1.5 Pro / Flash, AWS Bedrock Claude, hay mô hình On-Premise nội bộ)?
- Cần thông tin về endpoint, cơ chế xác thực (API Key hay OAuth/IAM role) và hạn mức chi phí (rate limits).

### 2. Phương pháp đếm Token chính thức (CKPA-42)
- Dự án sẽ dùng thư viện tokenizer nào chính thức (ví dụ: `tiktoken` cho OpenAI, hay API đếm token riêng của model)?
- Trong giai đoạn chưa có model chính thức, S4 áp dụng công thức ước lượng bảo thủ cho tiếng Việt (`TOKEN_ESTIMATE_WORD_MULTIPLIER = 3`, `TOKEN_ESTIMATE_CHAR_DIVISOR = 2`) để đảm bảo không vượt 6.000 input tokens.

### 3. Làm rõ mã yêu cầu ANS 03 và KNW 06
- Hiện tại bảng yêu cầu của dự án chưa có mô tả chi tiết cho 2 mã:
  - **ANS 03:** Chưa có nội dung quy định.
  - **KNW 06:** Chưa có nội dung quy định.
- Đề nghị người giao việc / Product Owner cung cấp nội dung cụ thể để S4 bổ sung tiêu chí nghiệm thu.

### 4. Tài liệu kịch bản kiểm thử Annex B
- Hiện tại chưa có tài liệu chính thức về bộ dữ liệu kiểm thử Annex B (các câu hỏi test mẫu, câu hỏi bẫy ngoại lệ, câu hỏi bẻ khóa).
- Đề nghị nhóm P4 (Quality Evaluation) cung cấp tiêu chuẩn hoặc danh sách ca kiểm thử để đối chiếu, S4 cam kết không tự bịa nội dung Annex B. Chi tiết đã lập danh mục theo dõi tại [tests/ANNEX_B_CHECKLIST.md](file:///c:/Users/ACER/Desktop/crm-knowledge-and-policy-assistant/tests/ANNEX_B_CHECKLIST.md).

### 5. Tài liệu hướng dẫn ngôn ngữ và thuật ngữ VN 01
- Có bảng thuật ngữ đối chiếu Anh - Việt chuẩn của ngân hàng (Glossary) hay không (ví dụ: eKYC, CASA, Term Deposit, Overdraft, Collateral)?
- Danh sách các từ viết tắt chuyên ngành cần bảo toàn nguyên văn khi xử lý tiếng Việt thiếu dấu.

### 6. Chính sách lưu trữ dữ liệu và bảo mật SQLite (SEC 02)
- Database SQLite hiện tại (`data/app.db`) được dùng lưu trữ cục bộ trong giai đoạn phát triển cho Feedback, Referral, và HOLD logs.
- Khi triển khai thật vào hệ thống ngân hàng, chính sách lưu trữ này sẽ chuyển sang dịch vụ nào (PostgreSQL / SQL Server tập trung, hay API ghi log nội bộ) để đảm bảo tuân thủ quy định bảo mật dữ liệu khách hàng và ngân hàng?

### 7. Chế độ DEMO_MODE và Nguồn dữ liệu kiểm thử trực quan (Giai đoạn 5)
- Hệ thống hỗ trợ cờ môi trường `DEMO_MODE=1` để hiển thị thử nghiệm đầy đủ 7 trường dữ liệu và trích dẫn bằng MockLLMClient khi chưa nối S3 thực.
- Cần làm rõ: Khi demo cho các bên liên quan (Hội đồng, Ban Giám đốc), nhóm muốn dùng kịch bản dữ liệu mẫu nào để chuẩn hóa các ca kiểm thử trực quan? Mặc định `DEMO_MODE` luôn tắt (`0`).

### 8. Nguồn xác thực danh tính và phân quyền người dùng (User Role Context)
- Trong `app/main.py`, hàm `get_current_user_context()` đang tạm thời gán quyền tối thiểu `{"roles": ["CRM_STAFF"]}`.
- Cần làm rõ: Khi tích hợp thực tế, thông tin người dùng (CRM_STAFF, BRANCH_MANAGER, COMPLIANCE_OFFICER, RISK_ANALYST) sẽ được truyền từ hệ thống nào (Single Sign-On SSO qua Azure AD, Keycloak, JWT trong header, hay session CRM)?
