# DOC-005 — SOP Xác minh Chứng từ & Cập nhật Hồ sơ Khách hàng trên CRM

- **Policy Family:** `POL-002`
- **Authority Layer (DAT 03):** `SOP`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-005_SOP-CRM-KH-01_Customer_Verification_Update.md`
- **Curated Passages Count:** 4
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng `source_uri` (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-071 | DOC005-VER-001 | Bước 1 (Trang 1) (Trang 1) — [effective]
- **Title:** SOP Xác minh & Cập nhật Hồ sơ KH CRM - Bước 1: Tiếp nhận & Phân loại chứng từ
- **Source Ref:** `POL-002 / SOP-CRM-KH-01_v1.0.docx (SOP-KH-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:customer_intake_verification`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-KH-01 Bước 1 (Lớp thẩm quyền SOP — tuân thủ DOC-002): Khi nhận yêu cầu sửa thông tin khách hàng, nhân viên CRM phân loại ngay 02 nhóm: (a) Thông tin liên hệ (Email hóa đơn/SĐT) yêu cầu Thông báo đóng dấu đỏ; (b) Thông tin pháp lý (Tên công ty/MST/Địa chỉ thuế/Đại diện pháp luật) yêu cầu Giấy chứng nhận ĐKKD mới nhất. Từ chối tiếp nhận qua lời nói hoặc tin nhắn không chứng từ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-072 | DOC005-VER-001 | Bước 2 (Trang 1) (Trang 1) — [effective]
- **Title:** SOP Xác minh & Cập nhật Hồ sơ KH CRM - Bước 2: Đối chiếu Cổng thông tin Quốc gia & Ngưỡng 500 triệu
- **Source Ref:** `POL-002 / SOP-CRM-KH-01_v1.0.docx (SOP-KH-02)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:legal_entity_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-KH-01 Bước 2: Nhân viên CRM đối chiếu Mã số thuế và tên pháp nhân trên bản scan ĐKKD với trạng thái hoạt động hợp lệ, đồng thời kiểm tra tổng giá trị hợp đồng lũy kế của khách hàng: nếu < 500 triệu VND thì tự thực hiện (CF-006); nếu >= 500 triệu VND thì lập phiếu trình CRM Manager duyệt kèm hợp đồng liên quan (CF-007). [Dữ liệu giả lập phục vụ đồ án]

### PAS-073 | DOC005-VER-001 | Bước 3 (Trang 2) (Trang 2) — [effective]
- **Title:** SOP Xác minh & Cập nhật Hồ sơ KH CRM - Bước 3: Kiểm tra khung giờ hành chính & Duyệt khẩn cấp
- **Source Ref:** `POL-002 / SOP-CRM-KH-01_v1.0.docx (SOP-KH-03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:after_hours_urgent_update`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-KH-01 Bước 3: Mọi yêu cầu cập nhật pháp lý phát sinh trong giờ hành chính (08:00–17:00 giờ Việt Nam, thứ Hai đến thứ Sáu) theo SLA 04 giờ làm việc. Nếu phát sinh ngoài khung giờ 08:00–17:00 +07:00 cần xử lý gấp để xuất hóa đơn, nhân viên CRM bắt buộc chờ Email công vụ phê duyệt từ Giám đốc CRM (CF-008) rồi mới cập nhật trong <= 01 giờ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-074 | DOC005-VER-001 | Bước 4 (Trang 2) (Trang 2) — [effective]
- **Title:** SOP Xác minh & Cập nhật Hồ sơ KH CRM - Bước 4: Ghi nhật ký thay đổi & Substitute Owner
- **Source Ref:** `POL-002 / SOP-CRM-KH-01_v1.0.docx (SOP-KH-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b;product:all;transaction_scope:audit_history_preservation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-KH-01 Bước 4 (VN 04 Substitute): Sau khi cập nhật, hệ thống tự động lưu bản ghi lịch sử gồm mã nhân viên, thời điểm UTC+7 và mã file chứng từ đính kèm. Trường hợp CRM Manager vắng mặt, Phó phòng Quản trị Dữ liệu CRM (Deputy CRM Manager — Substitute Owner) thực hiện phê duyệt thay thế cho hồ sơ >= 500 triệu VND theo Ma trận Thẩm quyền đã ký. [Dữ liệu giả lập phục vụ đồ án]

