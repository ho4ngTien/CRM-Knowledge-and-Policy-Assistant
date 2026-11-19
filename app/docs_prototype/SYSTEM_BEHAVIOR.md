# Tài liệu Hành vi Hệ thống – CRM Knowledge & Policy Assistant
**Phiên bản cấu hình:** 1.2.0 | **Phiên bản prompt:** v1.1  
**Mục đích:** Tài liệu nội bộ, dành cho nhân viên CRM và quản trị viên.  
**Phạm vi:** Chỉ dùng nội bộ. Không chia sẻ với khách hàng.

---

## 1. Hệ thống làm gì và KHÔNG làm gì

### ✅ Hệ thống CÓ THỂ làm

| Chức năng | Chi tiết |
|---|---|
| Tra cứu chính sách | Tìm kiếm văn bản quy định trong kho dữ liệu nội bộ theo câu hỏi nghiệp vụ |
| Trích dẫn nguyên văn | Hiển thị đoạn văn bản gốc từ tài liệu chính sách, kèm nguồn gốc |
| Giải thích ngắn | Cung cấp giải thích 100–250 từ bằng tiếng Việt dựa trên văn bản gốc |
| Làm rõ câu hỏi | Hỏi lại nhân viên CRM khi câu hỏi thiếu thông tin hoặc không rõ phạm vi |
| Chuyển người phụ trách | Ghi nhận yêu cầu referral cục bộ khi hệ thống không thể trả lời |
| Nhận phản hồi | Ghi nhận đánh giá của nhân viên CRM về chất lượng câu trả lời |
| Hiển thị trạng thái HOLD | Thông báo rõ ràng lý do không thể trả lời và hướng dẫn hành động tiếp theo |

### ❌ Hệ thống KHÔNG làm

| Điều cấm | Lý do |
|---|---|
| **Tư vấn pháp lý** | Ngoài phạm vi ANS 07 – không có thẩm quyền pháp lý |
| **Hứa hẹn với khách hàng** | Hệ thống chỉ tra cứu, không cam kết thay mặt ngân hàng |
| **Tự suy ra phê duyệt** | ANS 05 – không được suy ra phê duyệt từ tiền lệ hay tầm quan trọng khách hàng |
| **Dùng bộ nhớ ngoài văn bản gốc** | ANS 06 – chỉ dùng bằng chứng đã nạp vào, không dùng web hay kiến thức nội tại LLM |
| **Gọi công cụ ngoài hệ thống** | ANS 08 – không có tool tự do, không gọi API bên ngoài |
| **Xuất/tải xuống dữ liệu chính sách** | KNW 02 – chỉ dùng nội bộ, không có chức năng export |
| **Gửi email / tạo CRM task** | KNW 05 – yêu cầu cấm tạo CRM task hoặc gửi email; chỉ ghi nhận referral cục bộ |
| **Streaming chưa kiểm chứng** | Toàn bộ nội dung phải qua bộ lọc output_guard trước khi hiển thị |

---

## 2. Luồng xử lý một câu hỏi (8 bước)

```
Nhân viên CRM nhập câu hỏi
        │
        ▼
[Bước 1] KIỂM TRA ĐẦU VÀO (input_guard)
         • Câu hỏi rỗng? → HOLD: EMPTY_INPUT
         • Vượt giới hạn token (ước lượng)? → HOLD: TOKEN_LIMIT_EXCEEDED
         • Dấu hiệu prompt injection? → HOLD: INJECTION_SUSPECTED
        │
        ▼
[Bước 2] TÌM KIẾM BẰNG CHỨNG (evidence_provider / S3)
         • Truy xuất các đoạn văn bản chính sách liên quan
         • Lỗi kết nối? → HOLD: EVIDENCE_SERVICE_ERROR
         • Không tìm thấy? → HOLD: NO_EVIDENCE
        │
        ▼
[Bước 3] KIỂM TRA BẰNG CHỨNG (citation_verifier)
         • Xác minh phạm vi áp dụng → không khớp? HOLD: SCOPE_MISMATCH
         • Quyền truy cập? → không đủ quyền: HOLD: ACCESS_DENIED
         • Bằng chứng quá ít? → HOLD: INSUFFICIENT_EVIDENCE
        │
        ▼
[Bước 4] KIỂM TRA TOKEN ĐẦU VÀO TỔNG HỢP
         • Tính tổng token (câu hỏi + prompt + bằng chứng)
         • Vượt MAX_INPUT_TOKENS (6 000)? → HOLD: TOKEN_LIMIT_EXCEEDED
        │
        ▼
[Bước 5] GỌI MÔ HÌNH NGÔN NGỮ (LLMGateway)
         • Gọi tối đa 2 lần (MAX_LLM_CALLS_PER_PACKAGE)
         • Vượt giới hạn lượt gọi? → HOLD: CALL_LIMIT_EXCEEDED
         • Lỗi mô hình? → HOLD: LLM_ERROR
         • Phản hồi không phải JSON hợp lệ (sau 2 lần)? → HOLD: INVALID_LLM_FORMAT
        │
        ▼
[Bước 6] PHÂN TÍCH VÀ KIỂM TRA CẤU TRÚC (json_response_parser + validate_answer)
         • Phân tích JSON 7 trường cố định
         • Trường bắt buộc rỗng / uncertainty_level sai / ngày không hợp lệ?
           → HOLD: INVALID_FIELDS
         • Không có citation đã xác minh? → HOLD: CITATION_UNVERIFIED
        │
        ▼
[Bước 7] KIỂM TRA NỘI DUNG ĐẦU RA (output_guard)
         • Số tiền/phần trăm/ngày/mã chính sách không xuất hiện trong văn bản gốc?
           → HOLD: UNGROUNDED_CONTENT
         • Câu trả lời chứa cụm phê duyệt bị cấm?
           → HOLD (OUTPUT_PROHIBITED_APPROVAL)
         • Rò rỉ system prompt hoặc chuỗi nhạy cảm (API key, Bearer, password)?
           → HOLD (OUTPUT_SYSTEM_PROMPT_LEAK)
        │
        ▼
[Bước 8] HIỂN THỊ KẾT QUẢ
         Kết quả ANSWER gồm 7 trường:
         effective_date | scope | short_explanation | required_information
         policy_owner | uncertainty_level | citations (trích dẫn nguyên văn)
```

> [!NOTE]
> Ở **mọi bước**, nếu phát hiện vi phạm, hệ thống kích hoạt HOLD ngay lập tức, **không tiến hành bước tiếp theo**, và ghi nhật ký vào bảng `hold_logs`.

---

## 3. Phân biệt ANSWER và HOLD

| Trạng thái | Ý nghĩa | Hiển thị cho nhân viên |
|---|---|---|
| **ANSWER** | Hệ thống đã tra cứu được và câu trả lời qua tất cả kiểm tra | 7 trường đầy đủ + trích dẫn nguyên văn |
| **HOLD** | Hệ thống không đủ điều kiện trả lời | Thông báo lý do + hướng dẫn + câu hỏi làm rõ |

### Bảng 14 mã HOLD

| # | Mã HOLD | Ý nghĩa | Nhân viên CRM nên làm gì |
|---|---|---|---|
| 1 | `NO_EVIDENCE` | Không tìm thấy văn bản liên quan | Kiểm tra lại từ khóa; dùng Referral |
| 2 | `INSUFFICIENT_EVIDENCE` | Tài liệu không đủ chi tiết | Tra cứu văn bản gốc; liên hệ chuyên viên sản phẩm |
| 3 | `SCOPE_MISMATCH` | Chính sách không áp dụng cho phân khúc này | Xác minh lại phân khúc khách hàng |
| 4 | `ACCESS_DENIED` | Văn bản yêu cầu quyền truy cập cao hơn | Liên hệ quản trị viên chính sách |
| 5 | `CITATION_UNVERIFIED` | Trích dẫn không khớp với văn bản gốc | Dùng Referral; đối chiếu văn bản gốc |
| 6 | `INVALID_FIELDS` | Câu trả lời thiếu trường bắt buộc hoặc giá trị sai | Thử lại; nếu vẫn HOLD → báo cáo lỗi hệ thống |
| 7 | `LLM_ERROR` | Mô hình ngôn ngữ gặp sự cố | Thử lại; nếu vẫn HOLD → báo cáo lỗi hệ thống |
| 8 | `INVALID_LLM_FORMAT` | Mô hình không trả về định dạng hợp lệ sau 2 lần thử | Thử đặt lại câu hỏi ngắn gọn hơn |
| 9 | `TOKEN_LIMIT_EXCEEDED` | Câu hỏi hoặc tài liệu quá dài | Rút ngắn câu hỏi hoặc chia nhỏ tình huống |
| 10 | `CALL_LIMIT_EXCEEDED` | Vượt 2 lượt gọi mô hình tối đa | Chuyển sang Referral cho chuyên viên chính sách |
| 11 | `INJECTION_SUSPECTED` | Phát hiện dấu hiệu can thiệp hệ thống | Đặt lại câu hỏi thuần nghiệp vụ, không chứa chỉ dẫn kỹ thuật |
| 12 | `EMPTY_INPUT` | Câu hỏi trống | Nhập nội dung câu hỏi |
| 13 | `EVIDENCE_SERVICE_ERROR` | Lỗi kết nối kho chính sách (S3) | Kiểm tra mạng nội bộ; thử lại hoặc dùng Referral |
| 14 | `UNGROUNDED_CONTENT` | Số liệu trong câu trả lời không có trong tài liệu gốc | Đối chiếu văn bản gốc; dùng Referral |

---

## 4. Trích dẫn nguyên văn và giải thích AI

### Trích dẫn nguyên văn (`citations`)
- Là **đoạn sao chép nguyên xi** từ tài liệu chính sách gốc, **không chỉnh sửa**.
- Mỗi trích dẫn kèm: tên tài liệu nguồn, ngày hiệu lực, phạm vi, điều khoản (clause).
- Hệ thống từ chối trích dẫn nếu:
  - Bị cắt giữa từ (không ở ranh giới từ)
  - Ngắn hơn 4 từ (`MIN_CITATION_WORDS = 4` – giá trị đề xuất, chưa được nhóm chốt)
  - Phần đứng trước hoặc sau trong cùng câu chứa từ phủ định / điều kiện ngoại lệ mà đoạn trích không bao gồm (heuristic, không phải quy tắc tuyệt đối)

### Giải thích AI (`short_explanation`)
- Là phần do mô hình AI soạn thảo, **độ dài 100–250 từ** (tiếng Việt).
- **Chỉ dùng thông tin có trong văn bản gốc đã nạp vào.** Mọi số tiền, phần trăm, ngày tháng, mã chính sách phải xuất hiện trong bằng chứng.
- Nếu giải thích chứa thông tin không xác minh được → kích hoạt HOLD `UNGROUNDED_CONTENT`.

> [!IMPORTANT]
> Nhân viên CRM **nên đọc trích dẫn nguyên văn** là nguồn chính thức, không chỉ dựa vào giải thích AI.

---

## 5. Quy tắc ngoại lệ (ANS 05)

Hệ thống **không tự suy ra phê duyệt**. Cụ thể:
- Không được lấy tiền lệ trường hợp cũ làm bằng chứng phê duyệt mới.
- Không được lấy tầm quan trọng của khách hàng (VIP, doanh số cao) làm lý do ngoại lệ.
- Nếu câu hỏi liên quan đến lộ trình ngoại lệ: hệ thống **chỉ giải thích lộ trình đó là gì và bằng chứng cần có**, không xác nhận hay phủ nhận kết quả.
- Câu trả lời có cụm từ phê duyệt bị cấm (vd: "đã được phê duyệt", "tôi xác nhận phê duyệt") → kích hoạt HOLD.

---

## 6. Giới hạn token và lượt gọi

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Token đầu vào tối đa | 6 000 | Ước lượng bảo thủ (chưa có tokenizer chính thức) |
| Token đầu ra tối đa | 900 | Giới hạn mỗi lần gọi mô hình |
| Lượt gọi mô hình tối đa | 2 | Mỗi câu hỏi (thử lại 1 lần nếu JSON lỗi) |
| Hệ số ước lượng token | ×3 từ / ÷2 ký tự | Dùng cho tiếng Việt khi chưa có tokenizer thật |

---

## 7. Chống Prompt Injection (ANS 08)

Hệ thống phát hiện và từ chối (HOLD: `INJECTION_SUSPECTED`) khi câu hỏi hoặc bằng chứng chứa:
- Chỉ dẫn ghi đè vai trò hệ thống (vd: "ignore all previous instructions", "bỏ qua quy định", "giả vờ là...")
- Yêu cầu tiết lộ system prompt hoặc thông tin nội bộ
- Yêu cầu thực hiện hành động bên ngoài phạm vi tra cứu chính sách

**Hạn chế đã biết:**
- Đây là phát hiện theo danh sách mẫu (heuristic). Nhóm chưa chọn công cụ guardrail; đây là câu hỏi mở cần thảo luận trước khi vận hành thực tế.
- Các biến thể mới của tấn công injection có thể chưa được phát hiện.
- Nhân viên nên báo cáo khi thấy câu trả lời bất thường qua chức năng Feedback.

---

## 8. Phản hồi (Feedback - KNW 07)

**Nhân viên CRM có thể đánh giá**: Hữu ích / Không hữu ích / Cần xem xét lại.

**Thông tin được lưu trong cơ sở dữ liệu nội bộ:**
- Câu hỏi (đã che thông tin nhận dạng cá nhân: số CCCD, CMND, số thẻ)
- Loại phản hồi (5 nhóm lý do chuẩn + 2 cờ bổ sung: thiếu ngoại lệ, khẳng định không căn cứ)
- Nhận xét tùy chọn
- Thời gian ghi nhận
- Phiên bản prompt và cấu hình tại thời điểm đó

**KHÔNG được lưu hay gửi đi:**
- Thông tin định danh cá nhân của khách hàng (đã được che)
- Phản hồi KHÔNG được gửi ra ngoài hệ thống, chỉ lưu nội bộ SQLite

---

## 9. Chuyển người phụ trách (Referral - KNW 05)

Khi hệ thống kích hoạt HOLD hoặc nhân viên đánh giá câu trả lời chưa đủ, nhân viên có thể dùng chức năng **"Chuyển người phụ trách"**:
- Điền tên người phụ trách và lý do
- Hệ thống ghi nhận vào bảng `referrals` (chỉ lưu cục bộ)
- **Quy định bắt buộc:** Tuyệt đối KHÔNG gửi email, KHÔNG tạo CRM task tự động.

---

## 10. Phạm vi nội bộ (KNW 02)

> [!CAUTION]
> Hệ thống này chỉ dành cho **nhân viên CRM nội bộ**. Không được:
> - Cho khách hàng trực tiếp sử dụng
> - Chia sẻ câu trả lời của hệ thống với khách hàng mà không có xác minh thủ công
> - Dùng câu trả lời làm căn cứ pháp lý thay thế văn bản gốc

---

## 11. Các giả định chưa được xác nhận

Các hạng mục dưới đây **chưa xác định, cần nhóm xác nhận** trước khi triển khai thực tế:

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Hợp đồng dữ liệu S3 (định dạng chunk, metadata) | Chưa kiểm chứng | Cần phân hệ Retrieval xác nhận |
| Nhà cung cấp LLM và tokenizer chính thức | Chưa kiểm chứng | Chưa xác định, cần nhóm xác nhận |
| Phân quyền người dùng (SSO/IAM) | Chưa kiểm chứng | Chưa xác định, cần nhóm xác nhận |
| Bảng thuật ngữ tiếng Việt ngành ngân hàng (VN 01) | Chưa làm | Cần phân hệ nghiệp vụ bổ sung |
| Đo lường thời gian phản hồi toàn hệ thống (OPS 02) | Một phần | Thuộc phân hệ S5 theo tài liệu yêu cầu |
| Chính sách lưu giữ dữ liệu và PII thật (SEC 02) | Một phần | Thuộc phân hệ S5 theo tài liệu yêu cầu |
| Bảo mật cơ sở dữ liệu production | Chưa kiểm chứng | Chưa xác định, cần nhóm xác nhận |
| Lựa chọn công cụ guardrail | Câu hỏi mở | Nhóm chưa chọn công cụ guardrail |
| CKPA-44: Chặn streaming khi chưa kiểm tra | Đã triển khai code | Đã xác nhận chính thức từ Jira: Chặn streaming khi chưa kiểm tra nguồn và quyền |
| Annex B – kiểm tra bảo mật chính thức | Chưa kiểm chứng | Cần thực hiện độc lập trên hệ thống hoàn chỉnh |

---

*Tài liệu cập nhật: Giai đoạn 6B – Sửa sai sót báo cáo Giai đoạn 6*  
*Người phụ trách: S4 (Application + LLM Engineer)*
