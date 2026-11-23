# KIẾN TRÚC AN TOÀN VÀ PHÒNG THỦ HỆ THỐNG S4 (SAFETY ARCHITECTURE)

**Dự án:** AI-06 CRM Knowledge and Policy Assistant (Group 7)  
**Vai trò:** S4 – Application + LLM Engineer (Gói công việc WP04)  
**Tiêu chuẩn áp dụng:** CKPA-43, ANS 05, ANS 06, ANS 07, ANS 08, KNW 02, CKPA-47.

---

## 1. Nguyên tắc An toàn Cốt lõi
Hệ thống tuân thủ nguyên tắc **Phòng thủ đa tầng (Defense in Depth)** và **Thất bại minh bạch (Fail Visibly)**:
1. **Dữ liệu không đáng tin cậy:** Mọi câu hỏi của nhân viên và cả tài liệu bằng chứng nhận từ S3 đều được xử lý như dữ liệu không đáng tin (Untrusted Data).
2. **Không có công cụ tự do / Không truy cập web:** Mô hình LLM hoàn toàn không được cấp tool gọi ra ngoài mạng hoặc thực thi lệnh shell.
3. **Không tự quyết định quyền truy cập:** Toàn bộ việc kiểm tra quyền và phân khúc phạm vi tài liệu được thực hiện **BẰNG CODE** trước khi gửi tới LLM.
4. **Không âm thầm cắt bớt nội dung:** Khi vượt ngân sách Token, hệ thống kích hoạt HOLD minh bạch thay vì tự ý cắt bỏ câu hỏi hay bằng chứng.
5. **Chỉ dùng nội bộ (KNW 02):** Hệ thống không có chức năng xuất/gửi nội dung cho khách hàng; không tư vấn pháp lý và không hứa hẹn với khách (ANS 07).

---

## 2. Thứ tự 8 Lớp Bảo vệ trong Luồng xử lý (`legacy/s4/services/qa_pipeline.py`)

| Bước | Lớp bảo vệ | Trách nhiệm xử lý | Mã trạng thái HOLD khi vi phạm |
| :---: | :--- | :--- | :--- |
| **1** | **Input Guard** | Làm sạch ký tự ẩn, kiểm tra độ dài tối đa (`MAX_QUESTION_CHARS`), chặn giả mạo thẻ XML (`</cau_hoi>`), quét mẫu Prompt Injection tiếng Việt (có dấu & không dấu) và tiếng Anh. | `EMPTY_INPUT`<br>`TOKEN_LIMIT_EXCEEDED`<br>`INJECTION_SUSPECTED` |
| **2** | **Evidence Provider** | Nhận kết quả từ S3. Nếu không có dữ liệu => HOLD. Nếu S3 gặp sự cố kỹ thuật/timeout => Báo cáo lỗi trung thực, không nuốt lỗi. | `NO_EVIDENCE`<br>`EVIDENCE_SERVICE_ERROR` |
| **3** | **Evidence Guard** | Quét dữ liệu bằng chứng do S3 cung cấp. Nếu phát hiện chỉ dẫn độc hại được nhúng trong tài liệu nguồn => Cách ly ngay chunk độc hại và cảnh báo. | `INJECTION_SUSPECTED` |
| **4** | **Access & Scope Control** | Kiểm tra quyền truy cập (`allowed_roles`, `classification_level`) của người dùng BẰNG CODE dựa trên metadata S3. Thiếu quyền => Từ chối truy cập. | `ACCESS_DENIED` |
| **5** | **Token Guard** | Ước lượng bảo thủ Token đầu vào. Nếu vượt 6.000 tokens => Chặn trước khi gọi LLM để bảo toàn ngân sách. | `TOKEN_LIMIT_EXCEEDED` |
| **6** | **LLMGateway** | Giới hạn tối đa 2 lần gọi / package (lần 2 chỉ dùng khi retry lỗi định dạng JSON). Cố định `max_tokens = 900`. Lần gọi thứ 3 bị chặn ngay. | `CALL_LIMIT_EXCEEDED`<br>`INVALID_LLM_FORMAT` |
| **7** | **Response Parser & Verifier** | - Parse JSON nghiêm ngặt (từ chối văn bản thừa và khóa lạ).<br>- Gắn metadata S3 vào câu trả lời.<br>- `verify_all_citations`: Kiểm tra trích dẫn nguyên văn (ranh giới từ, tiền tố phủ định, hậu tố ngoại lệ).<br>- `validate_answer`: Kiểm tra 7 trường cố định, độ dài 100-250 từ. | `INVALID_LLM_FORMAT`<br>`CITATION_UNVERIFIED`<br>`INVALID_FIELDS` |
| **8** | **Output Guard** | - Kiểm tra rò rỉ System Prompt.<br>- Kiểm tra chuỗi nhạy cảm (API key, Bearer, mật khẩu).<br>- Kiểm tra URL lạ không nằm trong metadata S3.<br>- Kiểm tra ngôn ngữ tự phê duyệt hoặc hứa hẹn với khách (ANS 05, 07).<br>- Kiểm tra tư vấn pháp lý trái thẩm quyền (ANS 07).<br>- `check_explanation_grounding`: Kiểm tra số tiền, tỷ lệ %, ngày, mã quy định trong giải thích bắt buộc phải có trong bằng chứng. | `INJECTION_SUSPECTED`<br>`UNGROUNDED_CONTENT` |

---

## 3. Các Giới hạn Kỹ thuật đã biết (Known Limitations)

> [!WARNING]
> Hệ thống áp dụng các quy tắc nghiêm ngặt nhưng **KHÔNG THỂ khẳng định an toàn tuyệt đối 100%**. Dưới đây là các giới hạn kỹ thuật cần được người vận hành và chuyên viên CRM lưu ý:

1. **Bộ lọc mẫu Injection dựa trên từ khóa và Regex:** Mặc dù đã hỗ trợ cả tiếng Việt có dấu, không dấu, tiếng Anh và cơ chế gộp ký tự đơn cách nhau (`collapse_spaced_characters` chống Spaced Character Evasion), kỹ thuật lọc mẫu từ khóa chỉ là một lớp phòng ngự cú pháp heuristic bề mặt. Kẻ tấn công tinh vi có thể sử dụng các biến thể ngôn ngữ mới, ẩn dụ ngữ nghĩa, prompt injection nhiều tầng (multi-turn / indirect injection) hoặc kỹ thuật mã hóa (encoding) chưa được bao phủ trong danh mục từ điển regex. Bộ lọc KHÔNG thể thay thế hoàn toàn mô hình phân loại an toàn chuyên dụng (Safety Classifier) hoặc cơ chế LLM-as-a-judge trong môi trường sản xuất thực tế. Mọi yêu cầu nhạy cảm liên quan đến khóa bí mật (`api_key`, `token`) được bảo vệ bằng quy tắc ghép động từ yêu cầu để tránh chặn nhầm câu hỏi nghiệp vụ hợp lệ chứa từ "mật khẩu", "token" hay "API".
2. **Quy tắc kiểm tra phủ định và ngoại lệ mang tính Heuristic:** Bộ kiểm tra `NEGATION_CONTEXT_TRUNCATED` và `EXCEPTION_CONTEXT_TRUNCATED` hoạt động bằng cách quét từ khóa trong phạm vi câu lân cận. Phương pháp này ngăn chặn rất tốt việc cắt xén câu chữ thô bạo, nhưng không thể thay thế hoàn toàn khả năng đọc hiểu ngữ nghĩa phức tạp của con người.
3. **Môi trường kiểm thử của prototype:** Các thử nghiệm trong tài liệu này dùng `MockLLMClient` và kịch bản giả lập (`legacy/tests/fixtures/`); nội dung không mô tả backend runtime hiện tại.
4. **Bộ kiểm thử Annex B:** Chưa có tài liệu kịch bản đánh giá chính thức Annex B từ nhóm P4. Các kịch bản hiện tại được S4 tự thiết kế nhằm bao phủ các tình huống biên kỹ thuật theo hợp đồng giao việc.

