# YÊU CẦU CHÍNH THỨC S4 – AI-06 CRM KNOWLEDGE AND POLICY ASSISTANT (GROUP 7)

**Vai trò:** S4 – Application + LLM Engineer  
**Gói công việc:** WP04 (Giai đoạn trọng tâm: Tuần 3-6, G1 & G2)  
**Phạm vi:** Workspace, trích dẫn nguyên văn, field cố định; prompt tiếng Việt; giới hạn token; chống prompt injection; không stream chưa kiểm; referral cục bộ; feedback; hold và fail visibly.

---

## 1. Danh mục Mã yêu cầu S4 phụ trách

| Mã yêu cầu | Tên yêu cầu | Mô tả chi tiết & Ranh giới |
| :--- | :--- | :--- |
| **ANS 01** | **Intent** | Hỗ trợ tác vụ CRM, làm rõ câu hỏi khi người dùng đưa ra câu hỏi chưa rõ ràng. |
| **ANS 05** | **Exceptions** | Chỉ giải thích lộ trình ngoại lệ và bằng chứng cần có; **KHÔNG** suy ra phê duyệt từ độ quan trọng của khách hàng hay tiền lệ. |
| **ANS 06** | **Missing evidence** | Khi thiếu căn cứ, hỏi làm rõ hoặc chuyển HOLD; **KHÔNG** dùng bộ nhớ của model hay truy cập web để tự bù đắp thông tin. |
| **ANS 07** | **Boundaries** | **KHÔNG** tư vấn pháp lý, **KHÔNG** hứa hẹn/cam kết quyền lợi với khách hàng. |
| **ANS 08** | **Robustness** | Chống Prompt Injection, không cung cấp tool tự do cho LLM, xem dữ liệu đầu vào là không đáng tin. |
| **KNW 01** | **Evidence** | Hiển thị câu hỏi, ngày áp dụng, phạm vi, điều khoản (`clause_code`), và link/tham chiếu tới nguồn gốc. |
| **KNW 02** | **Internal use** | Hệ thống chỉ dùng nội bộ nhân viên CRM, **KHÔNG** có chức năng xuất/gửi trực tiếp nội dung cho khách hàng. |
| **KNW 05** | **Referral** | Bản ghi chuyển tiếp cục bộ (SQLite), không tự gửi email hay tạo CRM task. |
| **KNW 07** | **Feedback** | Phân loại lý do phản hồi với 5 nhóm chuẩn, hỗ trợ cờ đánh dấu đặc thù. |
| **VN 01** | **Language** | Xử lý Unicode tiếng Việt, câu hỏi thiếu dấu, thuật ngữ CRM Anh - Việt, bảo toàn nguyên vẹn tên chính sách, mã văn bản, số tiền, ngày tháng, đơn vị tính, nội dung phủ định. |
| **ANS 03** | *(Chưa có nội dung)* | **CHƯA CÓ nội dung mô tả**. Không đoán nội dung; ghi nhận vào `docs/OPEN_QUESTIONS.md` để xác nhận với người giao việc. |
| **KNW 06** | *(Chưa có nội dung)* | **CHƯA CÓ nội dung mô tả**. Không đoán nội dung; ghi nhận vào `docs/OPEN_QUESTIONS.md` để xác nhận với người giao việc. |

---

## 2. Mã yêu cầu hỗ trợ (Phối hợp liên vai trò)
- **OPS 02:** Độ trễ p95 <= 25 giây, hỗ trợ tối thiểu 5 người dùng đồng thời (vai trò S5 phụ trách chính, S4 tối ưu hiệu năng gọi LLM và xử lý luồng).
- **SEC 02:** Không nhập hay lưu trữ dữ liệu định danh khách hàng thật (PII) ở môi trường base/cục bộ.
- **DEL 02:** Phối hợp với S3 (S3 phụ trách Working Core Retrieval).

---

## 3. Quy định bổ sung bắt buộc
1. **Độ dài phần giải thích ngắn:** 
   - Dao động trong khoảng **100 đến 250 từ** (`EXPLANATION_MIN_WORDS = 100`, `EXPLANATION_MAX_WORDS = 250`).
   - Phải kiểm tra bằng code. Nếu nằm ngoài khoảng này, **không được hiển thị như câu trả lời hợp lệ** (phải chuyển HOLD hoặc đánh dấu cảnh báo rõ ràng).
2. **Đánh dấu chất lượng trên Workspace:**
   - Người dùng được phép gắn cờ: **"Thiếu ngoại lệ"** (`flag_missing_exception`) và **"Khẳng định không có căn cứ"** (`flag_unfounded_claim`).
3. **Liên kết tham chiếu nguồn:**
   - Hiển thị link hoặc đường dẫn tham chiếu tới văn bản nguồn gốc trong phần trích dẫn (`source_url` / `reference_link`).
4. **Kiểm soát Streaming:**
   - **Tuyệt đối không stream** nội dung ra giao diện khi chưa hoàn tất kiểm tra nguồn và quyền truy cập cuối cùng.
5. **Các điều cấm:**
   - Cấm tự chấm điểm câu trả lời của mình (việc đánh giá chất lượng thuộc thẩm quyền P4).
   - Cấm tinh chỉnh/tối ưu dựa trên 100 task đánh giá kín (sealed tasks).
   - Cấm dùng kết quả đánh giá của P4 ngoài mục đích sửa lỗi trong quá trình phát triển.
   - Chưa có tài liệu Annex B: Tuyệt đối không tự bịa nội dung test Annex B.

