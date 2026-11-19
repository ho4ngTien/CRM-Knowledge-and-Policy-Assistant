# BÁO CÁO HIỆN TRẠNG DỰ ÁN S4 (XÁC MINH VÀ HIỆU CHỈNH TRUNG THỰC)

**Dự án:** AI-06 CRM Knowledge and Policy Assistant (Group 7)  
**Vai trò:** S4 – Application + LLM Engineer (Gói công việc WP04)  
**Thời điểm đánh giá:** 13/11/2026 (Hiệu chỉnh Giai đoạn 5B)  
**Nhánh Git:** `feature/s4-complete`  
**Yêu cầu tham chiếu:** [docs/REQUIREMENTS_S4.md](file:///c:/Users/ACER/Desktop/crm-knowledge-and-policy-assistant/docs/REQUIREMENTS_S4.md) | [docs/SAFETY.md](file:///c:/Users/ACER/Desktop/crm-knowledge-and-policy-assistant/docs/SAFETY.md) | [docs/HANDOVER.md](file:///c:/Users/ACER/Desktop/crm-knowledge-and-policy-assistant/docs/HANDOVER.md) | [docs/S4_README.md](file:///c:/Users/ACER/Desktop/crm-knowledge-and-policy-assistant/docs/S4_README.md)

---

## 1. Môi trường và Công cụ thực tế
- **Hệ điều hành:** Windows
- **Python:** `3.14.10`
- **Streamlit:** `1.67.0`
- **Pytest:** `9.2.0`
- **SQLite:** 3.50.4 (Data `data/app.db` được bảo vệ bằng `.gitignore`, không đưa lên Git)
- **Git Branch:** `feature/s4-complete`

---

## 2. Phân định rõ ràng: Đã hoàn thành (với Mock) vs Chưa kiểm chứng thực tế

> [!IMPORTANT]
> **Tuyên bố trung thực về phạm vi hoàn thành:**  
> S4 **KHÔNG tuyên bố hoàn thành 100% toàn diện toàn bộ dự án**. S4 chỉ hoàn thành phần kiến trúc code ứng dụng, các bộ lọc an toàn và đã kiểm thử tự động nội bộ bằng Mock / Fixtures. Nhiều hạng mục trọng yếu phụ thuộc vào các nhóm khác và môi trường ngân hàng thực tế hiện **CHƯA ĐƯỢC KIỂM CHỨNG**.

### A. CÁC HẠNG MỤC ĐÃ XONG (Đã kiểm thử tự động bằng Mock / Fixture cục bộ)
1. **Kiến trúc phân tầng và bảo vệ UI:**
   - Đã loại bỏ hoàn toàn việc import trực tiếp `sqlite3`, `llm_client`, `evidence_provider`, hoặc `database` tại tầng UI (`app/main.py` và `app/components/*.py`).
   - Mọi thao tác lưu trữ và điều phối được đóng gói qua các dịch vụ trung gian: `system_service`, `feedback_service`, `referral_service`, `policy_service`.
   - Có kiểm thử quét cây cú pháp trừu tượng (AST scan) tự động trong `tests/test_phase5_ui.py`.
2. **Quy trình xử lý khép kín 8 bước (qa_pipeline):**
   - Đã cài đặt `qa_pipeline.py` với luồng tuần tự: Input Guard -> Evidence Provider -> Evidence Guard -> Access Control -> Token Guard -> LLMGateway -> Response Parser & Verifier -> Output Guard -> Kết quả/HOLD.
   - Đã tái cấu trúc `PolicyService` thành thin wrapper chuyển tiếp trực tiếp sang pipeline (Single-path processing).
   - Đã đồng bộ mã Jira chính thức CKPA-44 cho tính năng Chặn streaming khi chưa kiểm tra nguồn và quyền.
3. **Bộ lọc an toàn và chống Prompt Injection:**
   - `input_guard.py`: 6 nhóm quy tắc chống injection (hỗ trợ tiếng Việt có dấu, không dấu và tiếng Anh), phát hiện giả mạo thẻ ranh giới XML, quét và cô lập chunk độc hại.
   - `output_guard.py`: Chặn số liệu lạ không có trong tài liệu (Grounding check), chặn ngôn từ tự ý phê duyệt, tư vấn kiện tụng, rò rỉ system prompt, lộ API key/Bearer/password=.
   - `citation_verifier.py`: Xác minh trích dẫn nguyên văn chuẩn hóa NFC, bắt buộc ranh giới từ, chặn trích dẫn bị cắt ngữ cảnh phủ định phía trước hoặc ngoại lệ phía sau.
4. **Cấu trúc dữ liệu và Mã HOLD:**
   - Định dạng 7 trường cố định `PolicyResponse`, kiểm tra độ dài giải thích 100-250 từ.
   - 14 mã `HoldReason` định danh rõ ràng, thông báo tiếng Việt có hướng dẫn xử lý và ghi log rút gọn an toàn vào SQLite.
5. **Giao diện Workspace và Hỗ trợ tương tác (Streamlit):**
   - Đã kiểm thử tương tác tự động thành công bằng `streamlit.testing.v1.AppTest` cho 5 kịch bản: câu hỏi rỗng (cảnh báo), câu hỏi bình thường với NullEvidenceProvider (HOLD NO_EVIDENCE), câu hỏi injection (HOLD INJECTION_SUSPECTED), gửi Feedback, tạo Referral.
   - Banner nội bộ KNW 02 và hỗ trợ cờ `DEMO_MODE=1` hiển thị banner cảnh báo dữ liệu giả lập.

---

### B. CÁC HẠNG MỤC CHƯA KIỂM CHỨNG TRÊN MÔI TRƯỜNG THỰC TẾ
Các hạng mục sau đây hiện **CHƯA THỂ KIỂM CHỨNG** do phụ thuộc vào hạ tầng bên ngoài và sự phối hợp từ các nhóm khác (xem chi tiết tại [docs/OPEN_QUESTIONS.md](file:///c:/Users/ACER/Desktop/crm-knowledge-and-policy-assistant/docs/OPEN_QUESTIONS.md)):
1. **Mô hình LLM thật (Real LLM Provider):** Hiện tại toàn bộ hệ thống chỉ chạy qua `MockLLMClient`. Chưa từng kết nối hoặc kiểm định độ trễ, chi phí, format với Azure OpenAI, Google Gemini hay LLM nội bộ thực tế.
2. **Dịch vụ tìm kiếm tài liệu thật (S3 / Vector Search thật):** Mặc định hệ thống dùng `NullEvidenceProvider` (trả về rỗng). Chưa có kết nối API thật tới hệ sinh thái S3 để đo độ chính xác trích xuất chunk.
3. **Bộ đếm Token thật (Real Tokenizer):** Hiện chỉ dùng công thức ước lượng bảo thủ cho tiếng Việt (`TOKEN_ESTIMATE_WORD_MULTIPLIER = 3`, `TOKEN_ESTIMATE_CHAR_DIVISOR = 2`). Chưa có thư viện tokenizer chuẩn theo từng model.
4. **Xác thực và Vai trò người dùng thật (Real SSO / IAM):** Hàm `get_current_user_context()` tại UI đang gán cố định `{"roles": ["CRM_STAFF"]}`. Chưa tích hợp hệ thống xác thực tập trung (Active Directory, Keycloak, JWT).
5. **Bộ kịch bản kiểm thử Annex B chính thức:** Chưa có tài liệu Annex B từ Product Owner hoặc nhóm P4. Các bài kiểm thử hiện tại hoàn toàn là bài test code nội bộ do S4 tự viết.
6. **Bộ từ điển thuật ngữ ngân hàng VN 01:** Chưa có bảng Glossary chính thức từ nhóm P3 để bảo toàn nguyên văn các thuật ngữ viết tắt tiếng Việt/Anh.
7. **Nội dung yêu cầu ANS 03 và KNW 06:** Nhóm chưa cung cấp mô tả chi tiết cho 2 mã yêu cầu này.
8. **Chính sách lưu trữ cơ sở dữ liệu sản xuất (SEC 02):** Hiện tại dùng SQLite cục bộ (`data/app.db`); chưa tích hợp cơ sở dữ liệu tập trung an ninh cao (PostgreSQL / SQL Server) cho môi trường production.
