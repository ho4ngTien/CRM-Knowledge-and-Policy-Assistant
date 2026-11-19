# MA TRẬN TRUY VẾT YÊU CẦU – TRIỂN KHAI – KIỂM THỬ (TRACEABILITY MATRIX)

**Dự án:** AI-06 CRM Knowledge and Policy Assistant (Group 7)  
**Vai trò:** S4 – Application + LLM Engineer (Gói công việc WP04)  
**Thời điểm cập nhật:** 13/11/2026 (Hoàn thành Giai đoạn 6B)  
**Quy ước trạng thái:** Chỉ sử dụng 4 trạng thái theo đúng yêu cầu kiểm định:  
- **Đã xong (mock):** Đã hoàn thành mã nguồn và đã vượt qua kiểm thử tự động nội bộ bằng Mock / Fixtures.  
- **Một phần:** Đã triển khai khung hoặc logic ban đầu nhưng chưa hoàn thiện đầy đủ.  
- **Chưa làm:** Chưa có mã nguồn triển khai.  
- **Chưa kiểm chứng (cần S3/LLM/Annex B):** Mã nguồn đã sẵn sàng nhưng chưa thể kiểm định vì phụ thuộc đối tác bên ngoài (S3 thật, LLM thật, SSO thật, kịch bản Annex B).  

---

## 1. Bảng ma trận truy vết chi tiết

| Mã yêu cầu | Mô tả yêu cầu chính thức | Tệp triển khai | Tệp / Tên bài kiểm thử tiêu biểu | Trạng thái kỹ thuật |
| :--- | :--- | :--- | :--- | :--- |
| **ANS 01** | Hỗ trợ tác vụ CRM, làm rõ câu hỏi khi thông tin chưa đủ | `app/services/hold_reasons.py`<br>`app/models.py`<br>`app/services/qa_pipeline.py` | `tests/test_phase6_integration.py`::`TestAllFourteenHoldReasonsEndToEnd` | **Đã xong (mock)** |
| **ANS 03** | *Chưa có mô tả yêu cầu chính thức trong tài liệu dự án; cần nhóm xác nhận* | Chưa triển khai | Chưa có bài test | **Chưa có mô tả yêu cầu** |
| **ANS 05** | Ngoại lệ: Chỉ giải thích lộ trình và bằng chứng cần có; KHÔNG suy ra phê duyệt từ độ quan trọng của khách hay tiền lệ | `app/services/output_guard.py`<br>`app/services/citation_verifier.py`<br>`prompts/system_prompt_vi_v1.1.md` | `tests/test_phase6_integration.py`::`test_mock_llm_attempting_approval_triggers_hold` | **Đã xong (mock)** |
| **ANS 06** | Thiếu bằng chứng: Kích hoạt HOLD kèm câu hỏi làm rõ gợi ý cố định; KHÔNG dùng kiến thức nền hay web | `app/services/qa_pipeline.py`<br>`app/services/hold_reasons.py`<br>`app/components/policy_display.py` | `tests/test_phase6_integration.py`::`test_hold_2_no_evidence` | **Đã xong (mock)** |
| **ANS 07** | Ranh giới: KHÔNG tư vấn pháp lý, khởi kiện; KHÔNG hứa hẹn bồi thường với khách hàng | `app/services/output_guard.py`<br>`prompts/system_prompt_vi_v1.1.md` | `tests/test_phase4.py`::`test_output_prohibited_legal_advice_rejected` | **Đã xong (mock)** |
| **ANS 08** | Chống Prompt Injection trong câu hỏi, trong tài liệu trích xuất S3 và trong đầu ra mô hình | `app/services/input_guard.py`<br>`app/services/output_guard.py` | `tests/test_phase6_integration.py`::`TestSecurityInjectionIntegration` | **Đã xong (mock)** |
| **KNW 01** | Evidence: hiển thị câu hỏi, ngày áp dụng, phạm vi (scope), điều khoản (clause), link tới tham chiếu gốc | `app/models.py`<br>`app/components/policy_display.py` | `tests/test_phase6_integration.py`::`test_happy_path_returns_seven_fields_and_verified_citations` | **Đã xong (mock)** |
| **KNW 02** | Chỉ sử dụng nội bộ ngân hàng, KHÔNG xuất / gửi / tải tài liệu cho khách hàng | `app/main.py`<br>`app/components/policy_display.py` | `tests/test_phase5_ui.py`::`test_zero_forbidden_imports_in_entire_ui_ast` | **Đã xong (mock)** |
| **KNW 05** | Referral: chuyển tiếp câu hỏi tới người phụ trách chính sách, bản ghi lưu cục bộ (KHÔNG gửi email, KHÔNG tạo CRM task) | `app/services/referral_service.py`<br>`app/components/referral_modal.py` | `tests/test_phase5_ui.py`::`TestReferralService`<br>`tests/test_phase6_integration.py`::`test_referral_local_only_blocks_network_calls` | **Đã xong (mock)** |
| **KNW 06** | *Chưa có mô tả yêu cầu chính thức trong tài liệu dự án; cần nhóm xác nhận* | Chưa triển khai | Chưa có bài test | **Chưa có mô tả yêu cầu** |
| **KNW 07** | Feedback: thu thập đánh giá từ CRM theo phân loại lý do (5 nhóm chuẩn + 2 cờ bổ sung: thiếu ngoại lệ, khẳng định không căn cứ) | `app/services/feedback_service.py`<br>`app/components/feedback_form.py` | `tests/test_phase5_ui.py`::`TestFeedbackService`<br>`tests/test_phase6_integration.py`::`test_feedback_persisted_with_version_and_flags` | **Đã xong (mock)** |
| **VN 01** | Bảo toàn nguyên vẹn tiếng Việt không dấu, số tiền, ngày tháng, phủ định trong prompt và kết quả | `app/services/prompt_builder.py`<br>`app/services/input_guard.py` | `tests/test_phase6_integration.py`::`test_vietnamese_unaccented_amounts_dates_negations_preserved` | **Đã xong (mock)** |
| **OPS 02** | Thuộc phân hệ S5: Thời gian phản hồi xử lý (Mục tiêu p95 <= 25s toàn hệ thống) | `app/services/qa_pipeline.py` | `tests/test_phase6_integration.py`::`test_internal_pipeline_latency_under_target` | **Một phần** *(Chỉ đo overhead nội bộ < 1s; toàn bộ luồng thuộc trách nhiệm S5)* |
| **SEC 02** | Thuộc phân hệ S5: Chính sách lưu trữ dữ liệu và bảo mật PII (Che số CMND/CCCD/thẻ khi ghi nhật ký) | `app/services/input_guard.py`<br>`app/services/database.py` | `tests/test_phase6_integration.py`::`TestPIISanitizationHeuristic` | **Một phần** *(Heuristic regex đề xuất; chính sách PII toàn diện thuộc trách nhiệm S5, cần nhóm xác nhận)* |
| **WP04** | Gói công việc S4: Workspace, trích dẫn nguyên văn, 7 field, prompt tiếng Việt, token limit, anti-injection, referral, feedback, hold, fail visibly, ghi phiên bản | Toàn bộ thư mục `app/` và `prompts/` | Toàn bộ 154 bài test tự động nội bộ | **Đã xong (mock), chưa kiểm chứng với S3/LLM thật** |
| **CKPA-38** | Workspace giao diện làm việc chính cho CRM | `app/main.py`<br>`app/services/system_service.py` | `tests/test_phase5_ui.py`::`TestAppTestEndToEnd` | **Đã xong (mock)** |
| **CKPA-39** | Trích dẫn nguyên văn, phân biệt với giải thích; vá ngữ cảnh phủ định và ngoại lệ | `app/services/citation_verifier.py`<br>`app/components/policy_display.py` | `tests/test_phase3.py`::`TestPatchedCitationVerifier`<br>`tests/test_phase4.py`::`TestPatchedExceptionContextVerifier` | **Đã xong (mock)** |
| **CKPA-40** | 7 trường dữ liệu cố định trong PolicyResponse và hàm validate_answer | `app/models.py` | `tests/test_phase2.py`::`TestFixedFieldsValidation` | **Đã xong (mock)** |
| **CKPA-41** | Prompt tiếng Việt v1.1 phân tách thẻ XML và Bộ phân tích cú pháp JSON nghiêm ngặt | `prompts/system_prompt_vi_v1.1.md`<br>`app/services/response_parser.py` | `tests/test_phase3.py`::`TestResponseParser` | **Đã xong (mock)** |
| **CKPA-42** | Giới hạn Token (<= 6.000 in, 900 out) và giới hạn số lượt gọi LLM (tối đa 2 lần) | `app/config.py`<br>`app/services/token_guard.py` | `tests/test_phase3.py`::`TestTokenGuardAndGateway`<br>`tests/test_phase6_integration.py`::`TestTokenAndCallLimitsIntegration` | **Đã xong (mock)** |
| **CKPA-43** | Chống Prompt Injection đa ngôn ngữ (Việt có/không dấu, Anh) và bảo vệ bằng chứng | `app/services/input_guard.py`<br>`app/services/qa_pipeline.py` | `tests/test_phase4.py`::`TestInputGuard`<br>`tests/test_phase6_integration.py`::`TestSecurityInjectionIntegration` | **Đã xong (mock)** |
| **CKPA-44** | Chặn streaming khi chưa kiểm tra nguồn và quyền truy cập (Đã xác nhận chính thức từ Jira) | `app/services/qa_pipeline.py` | `tests/test_phase6_integration.py`::`test_pipeline_returns_complete_object_never_generator` | **Đã xong (mock)** |
| **CKPA-45** | Chức năng Referral cục bộ (SQLite) | `app/services/referral_service.py`<br>`app/components/referral_modal.py` | `tests/test_phase6_integration.py`::`test_referral_local_only_blocks_network_calls` | **Đã xong (mock)** |
| **CKPA-46** | Chức năng Feedback 5 nhóm lỗi + 2 cờ bổ sung | `app/services/feedback_service.py`<br>`app/components/feedback_form.py` | `tests/test_phase6_integration.py`::`test_feedback_persisted_with_version_and_flags` | **Đã xong (mock)** |
| **CKPA-47** | Trạng thái TẠM DỪNG (HOLD) và Fail Visibly với 14 mã lỗi định danh | `app/services/hold_reasons.py`<br>`app/components/policy_display.py` | `tests/test_phase6_integration.py`::`TestAllFourteenHoldReasonsEndToEnd` | **Đã xong (mock)** |

---

## 2. Báo cáo xác minh đặc biệt

### 2.1. Xác minh rà soát ANS 01 và ANS 06 (Câu hỏi làm rõ khi HOLD)
- **Hiện trạng trước Giai đoạn 6:** Kết quả HOLD chỉ có `hold_reason` (lý do) và `guidance` (hướng dẫn hành động), chưa có trường câu hỏi gợi ý làm rõ cụ thể cho nhân viên CRM.
- **Bổ sung kỹ thuật tại Giai đoạn 6:**
  - Đã thêm trường `clarifying_question: Optional[str] = None` vào `PolicyResponse` và `HoldInfo`.
  - Đã cấu hình câu hỏi làm rõ chuẩn hóa, cố định cho toàn bộ 14 mã HOLD (ví dụ: `NO_EVIDENCE` gợi ý hỏi thêm số hiệu văn bản/gói sản phẩm; `SCOPE_MISMATCH` gợi ý hỏi phân khúc khách hàng).
  - Tuyệt đối không để LLM tự bịa đặt câu hỏi làm rõ khi chưa có căn cứ.
  - Đã có test kiểm định tại `tests/test_phase6_integration.py`::`TestAllFourteenHoldReasonsEndToEnd`.

### 2.2. Xác minh rà soát KNW 02 (Chỉ dùng nội bộ ngân hàng)
- **Kết quả quét mã nguồn tự động:** Đã quét toàn bộ thư mục `app/` để tìm các từ khóa liên quan đến xuất dữ liệu ra ngoài: `st.download_button`, `send_email`, `export`, `smtp`, `crm_task`.
- **Kết luận:** **100% KHÔNG TỒN TẠI** bất kỳ nút bấm tải xuống, hàm xuất dữ liệu, gửi email tự động hay tạo CRM task tự động nào. Mọi thông tin chỉ hiển thị trực tiếp trên giao diện màn hình nhân viên CRM và có banner cố định: *"CHỈ DÙNG NỘI BỘ — Không gửi nội dung này cho khách hàng"*.

### 2.3. Báo cáo về hai mã ANS 03 và KNW 06
- **Trạng thái:** **Chưa có mô tả yêu cầu trong tài liệu dự án; cần nhóm xác nhận**.
- **Giải trình trung thực:** Nhóm chưa cung cấp tài liệu mô tả chi tiết nghiệp vụ cho 2 mã này. S4 tuyệt đối không suy đoán hay tự gán ghép tính năng khi chưa có văn bản chính thức.
