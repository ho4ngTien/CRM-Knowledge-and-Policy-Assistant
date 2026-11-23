# DOC-002 — Chính sách Xử lý và Quản trị Thông tin Khách hàng CRM SongNhat (VER-000/001/002)

- **Policy Family:** `POL-002`
- **Authority Layer (DAT 03):** `policy`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-002_POL-CRM-03_Customer_Information_Handling.md`
- **Curated Passages Count:** 22
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng `source_uri` (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-011 | VER-001 | Điều 1.1–1.3 (KH-03-01..03) (Trang 1) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Mục đích & Nguyên tắc bảo mật nội bộ
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-01..03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:all_customer_data`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Mục đích và nguyên tắc xác minh, bảo mật dữ liệu khách hàng trên CRM: Đảm bảo tính chính xác, toàn vẹn và bảo mật thông tin hồ sơ khách hàng doanh nghiệp trên hệ thống CRM SongNhat. Nhân viên chỉ được ghi nhận, chỉnh sửa hoặc xác minh thông tin khi có đủ chứng từ hợp lệ; tuyệt đối không tự ý tiết lộ dữ liệu khách hàng cho bên thứ ba hoặc bộ phận không có quyền (audience) và không tự xác lập cơ sở pháp lý ngoài quy trình đã duyệt. [Dữ liệu giả lập phục vụ đồ án]

### PAS-012 | VER-001 | Điều 1.4–1.5 (KH-03-04..05) (Trang 1) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Cập nhật Email nhận hóa đơn & SĐT liên hệ
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-04..05)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:contact_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy trình cập nhật thông tin liên hệ thông thường trên CRM (Worked Case 8 & Critical Field CF-005): Khi khách hàng doanh nghiệp yêu cầu thay đổi địa chỉ Email nhận hóa đơn GTGT hoặc Số điện thoại người liên hệ qua Hotline/Email công vụ, nhân viên CRM bắt buộc phải thu thập bản quét (scan) Thông báo thay đổi thông tin có đóng dấu đỏ của doanh nghiệp khách hàng. Thẩm quyền xử lý: Chuyên viên CRM (reader / CRM Staff). Thời hạn hoàn tất (SLA): Tối đa 02 giờ làm việc kể từ khi nhận đủ chứng từ hợp lệ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-013 | VER-001 | Điều 2.1 (KH-03-06) (Trang 1) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Chứng từ thay đổi thông tin pháp lý doanh nghiệp
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-06)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:legal_entity_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Yêu cầu chứng từ gốc khi chỉnh sửa thông tin pháp lý doanh nghiệp: Mọi yêu cầu thay đổi Tên công ty, Địa chỉ trụ sở đăng ký thuế, Mã số thuế hoặc Người đại diện pháp luật trên hệ thống CRM bắt buộc phải đính kèm bản sao Giấy chứng nhận Đăng ký kinh doanh (ĐKKD) mới nhất do cơ quan đăng ký kinh doanh cấp. Không chấp nhận yêu cầu sửa thông tin pháp lý chỉ qua tin nhắn hoặc điện thoại. [Dữ liệu giả lập phục vụ đồ án]

### PAS-014 | VER-001 | Điều 2.1–2.3 (KH-03-06..08) (Trang 1) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Cập nhật pháp lý KH dưới ngưỡng 500 triệu VND
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-06..08)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:legal_update_under_500m`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phân cấp xác minh và cập nhật thông tin pháp lý cho khách hàng có tổng hợp đồng lũy kế dưới 500 triệu VND (cumulative_contract < 500.000.000 VND - Critical Field CF-006): Đối với doanh nghiệp có tổng giá trị hợp đồng lũy kế dưới 500 triệu VND yêu cầu đổi Tên công ty hoặc Người đại diện pháp luật, Chuyên viên CRM (reader / CRM Staff) trực tiếp đối chiếu bản sao Giấy ĐKKD mới nhất và cập nhật trên hệ thống. Thời hạn xử lý (SLA): Tối đa 04 giờ làm việc. [Dữ liệu giả lập phục vụ đồ án]

### PAS-015 | VER-001 | Điều 2.3 (KH-03-08) (Trang 1) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Lưu vết lịch sử chỉnh sửa hồ sơ pháp lý
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-08)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:audit_history_preservation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy định bảo toàn lịch sử khi chỉnh sửa thông tin pháp lý trên CRM (Phụ lục C RFP): Khi cập nhật tên pháp nhân hoặc đại diện pháp luật mới, hệ thống phải tạo bản ghi lịch sử thay đổi có gắn timestamp giờ Việt Nam (Asia/Ho_Chi_Minh), ID nhân viên thực hiện và mã tham chiếu chứng từ ĐKKD; tuyệt đối không ghi đè làm mất lịch sử giao dịch của các hợp đồng đã ký trước thời điểm thay đổi. [Dữ liệu giả lập phục vụ đồ án]

### PAS-016 | VER-001 | Điều 2.4 (KH-03-09) (Trang 2) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Phê duyệt cập nhật pháp lý KH trọng yếu (>= 500 triệu VND)
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-09)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:legal_update_over_500m`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Thẩm quyền phê duyệt cập nhật hồ sơ khách hàng trọng yếu (cumulative_contract >= 500.000.000 VND - Critical Field CF-007): Đối với khách hàng doanh nghiệp có tổng giá trị hợp đồng lũy kế từ 500 triệu VND trở lên, mọi yêu cầu cập nhật thông tin pháp lý và xác minh giao dịch trên CRM bắt buộc phải trình Trưởng phòng CRM (CRM Manager) phê duyệt kèm bản sao Giấy ĐKKD mới nhất và Hợp đồng liên quan. Thời hạn phê duyệt (SLA): Tối đa 04 giờ làm việc. [Dữ liệu giả lập phục vụ đồ án]

### PAS-017 | VER-001 | Điều 2.5 (KH-03-10) (Trang 2) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Phê duyệt cập nhật khẩn cấp ngoài giờ hành chính
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-10)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:after_hours_urgent_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy định xử lý yêu cầu cập nhật hồ sơ khẩn cấp ngoài giờ hành chính theo múi giờ Asia/Ho_Chi_Minh (Critical Field CF-008): Mọi yêu cầu cập nhật gấp thông tin pháp lý khách hàng phát sinh ngoài khung giờ làm việc chuẩn (sau 17:00 hoặc trước 08:00 giờ Việt Nam) để kịp xuất hóa đơn/giao hàng sáng hôm sau bắt buộc phải có xác nhận phê duyệt qua Email công vụ từ Giám đốc CRM (CRM Director) kèm đủ chứng từ ĐKKD. Thời hạn xử lý sau khi có Email duyệt: Tối đa 01 giờ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-018 | VER-001 | Điều 2.6–2.7 (KH-03-11..12) (Trang 2) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Cấm miễn trừ chứng từ VIP & Xử lý lệch dữ liệu Hợp đồng
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-11..12)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:vip_no_waiver_and_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Nguyên tắc không miễn trừ chứng từ cho khách VIP và tạm giữ khi mâu thuẫn dữ liệu Hợp đồng - CRM (DAT 05, ANS 05): Nhân viên CRM và Trợ lý AI tuyệt đối không được miễn trừ bản sao Giấy ĐKKD hoặc Thông báo dấu đỏ cho khách hàng VIP/thân thiết hay dựa trên ghi chú CRM cũ. Trường hợp thông tin Mã số thuế/Pháp nhân trên Hợp đồng đang lệch với hồ sơ CRM, bắt buộc giữ trạng thái chờ (HOLD) và chuyển Chủ sở hữu Quản trị dữ liệu CRM (CRM Data Governance) xử lý. [Dữ liệu giả lập phục vụ đồ án]

### PAS-019 | VER-001 | Điều 3.1 (KH-03-13..14) (Trang 2) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Giảm thiểu dữ liệu cá nhân (PII Minimization SEC 02)
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-13..14)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:pii_minimization`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy định tối thiểu hóa dữ liệu cá nhân khi tra cứu trên Trợ lý tri thức (SEC 02, VN 05): Trong phạm vi cơ sở (Base Scope), hệ thống không nhập hồ sơ khách hàng cá nhân. Nhân viên khi đặt câu hỏi quy trình không được dán số CCCD, tài khoản ngân hàng cá nhân hoặc danh sách dữ liệu khách hàng thô vào ô chat; hệ thống thực hiện cảnh báo/lọc PII đầu vào và từ chối các yêu cầu xin cấp quyền tiết lộ dữ liệu trái phép. [Dữ liệu giả lập phục vụ đồ án]

### PAS-020 | VER-001 | Điều 3.2 (KH-03-15) (Trang 2) — [effective]
- **Title:** Chính sách Xử lý Thông tin Khách hàng CRM - Tạm giữ khi chứng từ đính kèm bị mờ/thiếu trang
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-15)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:incomplete_scan_hold`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Kiểm soát chất lượng tài liệu xác minh đính kèm trên CRM (DAT 08): Khi bản quét Thông báo dấu đỏ hoặc Giấy chứng nhận ĐKKD do khách hàng gửi bị mờ, mất góc, thiếu trang phụ lục hoặc không đọc được thông tin đối chiếu, nhân viên CRM phải giữ yêu cầu ở trạng thái chờ (HOLD), không được tự suy đoán nội dung và yêu cầu khách hàng cung cấp lại bản quét rõ nét hoặc chuyển Trưởng bộ phận Quản trị dữ liệu CRM xác minh. [Dữ liệu giả lập phục vụ đồ án]

### PAS-061 | VER-001 | Điều 4.1 (KH-03-16) (Trang 3) — [effective]
- **Title:** Chính sách Thông tin KH - Phân nhóm Nhà máy/Đại lý & Tách mã hồ sơ
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-16)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:customer_classification`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.1 - Chuẩn hóa phân nhóm khách hàng trên CRM: Mọi khách hàng B2B mới tạo lập trên CRM phải được gắn đúng 01 mã phân nhóm chính (Nhà máy sản xuất, Đại lý phân phối hoặc Nhà thầu cơ điện) dựa trên ngành nghề trên Giấy ĐKKD. Việc chuyển đổi phân nhóm từ Đại lý sang Nhà máy hoặc ngược lại phải được CRM Manager xác nhận trong SLA 04 giờ làm việc (CF-023). [Dữ liệu giả lập phục vụ đồ án]

### PAS-062 | VER-001 | Điều 4.2 (KH-03-17) (Trang 3) — [effective]
- **Title:** Chính sách Thông tin KH - Quy trình hợp nhất hồ sơ trùng MST (Deduplication)
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-17)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:deduplication`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.2 - Xử lý trùng lặp hồ sơ khách hàng theo Mã số thuế: Khi phát hiện 02 hồ sơ CRM mang cùng Mã số thuế doanh nghiệp, nhân viên CRM không tự xóa hồ sơ cũ mà lập phiếu đề nghị hợp nhất (Merge Request) gửi CRM Data Steward đối chiếu lịch sử báo giá và bảo hành trong tối đa 08 giờ làm việc (CF-024). Hồ sơ hợp nhất phải giữ nguyên mã hợp đồng lịch sử. [Dữ liệu giả lập phục vụ đồ án]

### PAS-063 | VER-001 | Điều 4.3 (KH-03-18) (Trang 3) — [effective]
- **Title:** Chính sách Thông tin KH - Yêu cầu trích xuất hoặc xóa dữ liệu chủ thể (PDPL R02)
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-18)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:data_subject_request`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.3 - Tiếp nhận yêu cầu quyền của chủ thể dữ liệu theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 (R02): Nhân viên CRM không tự thực hiện xuất file hoặc xóa vĩnh viễn dữ liệu liên hệ cá nhân khi nhận yêu cầu từ khách hàng. Bắt buộc ghi nhận Local Referral chuyển ngay cho Privacy & Security Owner và Legal Owner xử lý trong thời hạn tối đa 24 giờ làm việc để xác định cơ sở pháp lý và nghĩa vụ lưu giữ hóa đơn (CF-025). [Dữ liệu giả lập phục vụ đồ án]

### PAS-064 | VER-001 | Điều 4.4 (KH-03-19) (Trang 4) — [effective]
- **Title:** Chính sách Thông tin KH - Thời hạn lưu giữ hồ sơ kiểm toán & bản xuất thô (Annex C)
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-19)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:data_retention`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.4 - Lưu giữ hồ sơ xác minh và bản xuất đối soát (Annex C): Bản xuất dữ liệu thô (raw exports) phục vụ đối soát chỉ giới hạn cho Reconciliation Owners và phải xóa bản sao tiện ích sau tối đa 90 ngày trừ khi có phê duyệt giữ lại (CF-026). Lịch sử trả lời và phiếu chuyển xử lý lưu tối đa 12 tháng theo mục đích đã duyệt; mọi lệnh giữ pháp lý (Legal Hold) ưu tiên hơn lịch xóa định kỳ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-065 | VER-001 | Điều 5.1 (KH-03-20) (Trang 4) — [effective]
- **Title:** [Hạn chế quyền] Chính sách Thông tin KH - Quy trình kiểm toán truy cập & khóa tài khoản bất thường
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-20-CONFIDENTIAL)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm_admin;customer_group:b2b;product:all;transaction_scope:security_incident_response`
- **Audience (SEC 01):** `policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 5.1 (Tài liệu nội bộ cấp Quản trị — KHÔNG hiển thị cho role reader theo SEC 01): Khi phát hiện nhân viên tải xuất danh sách khách hàng hàng loạt hoặc tra cứu vượt phạm vi chi nhánh được giao, Privacy & Security Owner phối hợp Administrator khóa phiên truy cập ngay lập tức (fail-closed) và lập báo cáo sự cố gửi Purchaser Sponsor trong vòng 04 giờ liên tục kể từ thời điểm phát hiện (CF-027, SEC 07). [Dữ liệu giả lập phục vụ đồ án]

### PAS-066 | VER-001 | Phụ lục B2 (KH-03-B2) (Trang 5) — [effective]
- **Title:** Chính sách Thông tin KH - Phụ lục Bảng phân quyền xuất dữ liệu đối tác (Thiếu Chú thích DAT 08)
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-B2)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:partner_data_sharing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `false`

Phụ lục B2 - Ma trận trường thông tin khách hàng được phép chia sẻ cho đơn vị vận chuyển/lắp đặt đối tác: Việc cấp quyền xem thông tin giao hàng tuân theo Bảng phân quyền đính kèm (Lưu ý: Bảng danh mục trường cho phép Allowlist và chú thích loại trừ thông tin tài chính ở cuối trang 5 chưa được đính kèm đầy đủ trong bản trích xuất này -> gắn cờ has_essential_attachments=false để kích hoạt Quarantine/HOLD theo DAT 08). [Dữ liệu giả lập phục vụ đồ án]

### PAS-067 | DOC002-VER-000 | Điều 2.1 v0.9 (Trang 1) — [superseded]
- **Title:** [Lịch sử v0.9] Chính sách Thông tin KH - Ngưỡng phê duyệt pháp lý cũ (< 300 triệu VND)
- **Source Ref:** `POL-002 / POL-CRM-03_v0.9_superseded.docx (KH-00-06)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:legal_update_under_500m`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lịch sử v0.9 (hiệu lực 01/01/2025 – 06/11/2026 08:59:59 +07:00, đã bị thay thế bởi VER-001): Trước ngày 06/11/2026, ngưỡng tổng hợp đồng lũy kế để CRM Staff tự cập nhật thông tin pháp lý là dưới 300.000.000 VND (CF-028); từ 300 triệu VND trở lên phải trình CRM Manager. Chỉ dùng cho câu hỏi lịch sử có ngày sự kiện trước 06/11/2026 09:00 +07:00 và bắt buộc gắn nhãn 'Hướng dẫn lịch sử'. [Dữ liệu giả lập phục vụ đồ án]

### PAS-068 | DOC002-VER-002 | Điều 1.4 v2.0 (Trang 1) — [scheduled]
- **Title:** [Tương lai v2.0 - Scheduled] Chính sách Thông tin KH 2027 - Rút ngắn SLA cập nhật liên hệ xuống 01 giờ
- **Source Ref:** `POL-002 / POL-CRM-03_v2.0_scheduled.docx (KH-02-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:contact_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lên lịch tương lai v2.0 (trạng thái scheduled — bắt đầu hiệu lực từ 01/01/2027 00:00:00 +07:00, thay thế VER-001): Từ 01/01/2027, SLA cập nhật Email nhận hóa đơn và SĐT liên hệ sau khi có Thông báo dấu đỏ hoặc chữ ký số hợp lệ rút ngắn từ 02 giờ xuống còn 01 giờ làm việc (CF-029). TUYỆT ĐỐI KHÔNG áp dụng cho giao dịch năm 2026. [Dữ liệu giả lập phục vụ đồ án]

### PAS-069 | DOC002-VER-001-WD | Thông báo tạm (Đã thu hồi) (Trang 1) — [withdrawn]
- **Title:** [Đã thu hồi - Withdrawn] Thông báo cho phép cập nhật Email hóa đơn qua tin nhắn nội bộ
- **Source Ref:** `POL-002 / POL-CRM-03_memo_withdrawn.docx (KH-WD-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:contact_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Trạng thái withdrawn (ĐÃ THU HỒI KHẨN CẤP theo SEC 05 / KNW 04 — CẤM sử dụng): Hướng dẫn tạm thời cho phép cập nhật email hóa đơn chỉ dựa vào ảnh chụp tin nhắn nhân viên kinh doanh đã bị thu hồi ngay lập tức do không đủ bằng chứng pháp lý xác thực từ doanh nghiệp khách hàng. Hệ thống phải chặn fail-closed mọi phản hồi tham chiếu văn bản này. [Dữ liệu giả lập phục vụ đồ án]

### PAS-070 | DOC002-VER-003-DRAFT | Dự thảo Điều 1.6 (Trang 1) — [draft]
- **Title:** [Dự thảo - Draft] Đề xuất cho phép xác thực ĐKKD qua chữ ký số điện tử USB Token
- **Source Ref:** `POL-002 / POL-CRM-03_v2.1_draft.docx (KH-DR-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:contact_update`
- **Audience (SEC 01):** `policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Bản dự thảo (trạng thái draft — CHƯA phê duyệt theo KNW 03): Đề xuất bổ sung kênh tiếp nhận Thông báo thay đổi thông tin ký số bằng USB Token doanh nghiệp thay cho bản scan đóng dấu đỏ. Bộ lọc Pre-retrieval phải chặn 100% bản ghi trạng thái draft khỏi hướng dẫn hiện hành. [Dữ liệu giả lập phục vụ đồ án]

### PAS-077 | VER-001 | Điều 4.5 (KH-03-21) (Trang 4) — [effective]
- **Title:** Chính sách Thông tin KH - Quy tắc xác minh theo Chi nhánh HN/ĐN/HCM
- **Source Ref:** `POL-002 / POL-CRM-03_v1.0.docx (KH-03-21)`
- **Scope (6-dim DAT 04):** `company:SN;branch:HN,DN,HCM;role:crm;customer_group:b2b;product:all;transaction_scope:regional_customer_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.5 - Phân quyền xử lý hồ sơ theo Chi nhánh khu vực (Miền Bắc HN, Miền Trung ĐN, Miền Nam HCM): Nhân viên CRM tại từng chi nhánh chỉ được phép cập nhật hồ sơ khách hàng thuộc phạm vi chi nhánh mình phụ trách; trường hợp doanh nghiệp có nhiều nhà máy liên vùng, quyền sửa thông tin pháp lý trụ sở chính thuộc bộ phận CRM Trung tâm (Head Office). [Dữ liệu giả lập phục vụ đồ án]

### PAS-078 | DOC002-VER-001-APP | Phụ lục C (Chờ phát hành) (Trang 1) — [approved]
- **Title:** [Approved] Bản đã duyệt chuẩn hóa biểu mẫu xác nhận đổi tài khoản ngân hàng thanh toán
- **Source Ref:** `POL-002 / POL-CRM-03_v1.2_approved.docx (KH-AP-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:bank_account_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Trạng thái approved (đã có chữ ký duyệt nhưng CHƯA đến ngày phát hành effective theo KNW 03): Quy định bổ sung xác nhận đối chiếu 02 lớp với Phòng Kế toán khi khách hàng thay đổi thông tin tài khoản thanh toán trên hồ sơ CRM. Bộ lọc Pre-retrieval phải chặn trạng thái approved không cho dùng làm quy tắc hiện hành. [Dữ liệu giả lập phục vụ đồ án]

