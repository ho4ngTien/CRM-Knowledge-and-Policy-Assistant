# DOC-009 — SOP Tiếp nhận Chứng từ & Định tuyến Bảo hành Tuyến 1 / Tuyến 2 trên CRM

- **Policy Family:** `POL-003`
- **Authority Layer (DAT 03):** `SOP`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-009_SOP-CRM-BH-01_Warranty_Intake_Routing.md`
- **Curated Passages Count:** 4
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng `source_uri` (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-089 | DOC009-VER-001 | Bước 1 (Trang 1) (Trang 1) — [effective]
- **Title:** SOP Tiếp nhận & Định tuyến Bảo hành - Bước 1: Tạo Ticket CRM & Kiểm tra 03 chứng từ
- **Source Ref:** `POL-003 / SOP-CRM-BH-01_v1.0.docx (SOP-BH-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:warranty_intake_docs`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-BH-01 Bước 1 (Lớp thẩm quyền SOP — tuân thủ DOC-003): Khi khách hàng báo hỏng thiết bị công nghiệp, CSKH mở Ticket trên CRM và kiểm tra đủ 03 chứng từ trong <= 02 giờ làm việc (CF-038): (1) Phiếu bảo hành chính hãng, (2) Ảnh Nameplate & Serial nguyên vẹn, (3) Biên bản bàn giao hoặc Hóa đơn GTGT. Thiếu bất kỳ chứng từ nào phải phản hồi yêu cầu bổ sung ngay trên ticket. [Dữ liệu giả lập phục vụ đồ án]

### PAS-090 | DOC009-VER-001 | Bước 2 (Trang 1) (Trang 1) — [effective]
- **Title:** SOP Tiếp nhận & Định tuyến Bảo hành - Bước 2: Phân luồng công suất 37 kW & Loại sự cố
- **Source Ref:** `POL-003 / SOP-CRM-BH-01_v1.0.docx (SOP-BH-02)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:tier1_internal_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-BH-01 Bước 2: Sau khi đủ 03 chứng từ hợp lệ, CSKH đối chiếu công suất định mức trên Tem Nameplate và mô tả lỗi để phân luồng trong <= 04 giờ làm việc: <= 37 kW (động cơ thường/hộp giảm tốc/phụ kiện) chuyển Tuyến 1 (Internal Tech Lead, CF-009); > 37 kW hoặc lỗi bo mạch chính hoặc Động cơ phòng nổ Ex-d chuyển Tuyến 2 (Vendor Chief Engineer, CF-010, CF-032). [Dữ liệu giả lập phục vụ đồ án]

### PAS-091 | DOC009-VER-001 | Bước 3 (Trang 2) (Trang 2) — [effective]
- **Title:** SOP Tiếp nhận & Định tuyến Bảo hành - Bước 3: Xử lý ngoại lệ rách tem Serial & Substitute Owner
- **Source Ref:** `POL-003 / SOP-CRM-BH-01_v1.0.docx (SOP-BH-03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:missing_serial_or_card_hold`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-BH-01 Bước 3 (VN 04 Substitute): Nếu tem Nameplate/Serial bị mờ/rách hoặc mất Phiếu bảo hành, CSKH đặt trạng thái HOLD và tạo Local Referral gửi Warranty Policy Owner (hoặc Phó Giám đốc Dịch vụ — Substitute Owner khi vắng mặt) phối hợp Internal Tech Lead đối chiếu số khung/lô nhập kho trong tối đa 08 giờ làm việc (CF-039). [Dữ liệu giả lập phục vụ đồ án]

### PAS-092 | DOC009-VER-001 | Bước 4 (Trang 2) (Trang 2) — [effective]
- **Title:** SOP Tiếp nhận & Định tuyến Bảo hành - Bước 4: Lưu vết chuyển tuyến & Ranh giới tư vấn
- **Source Ref:** `POL-003 / SOP-CRM-BH-01_v1.0.docx (SOP-BH-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:no_adjudication_no_repair`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-BH-01 Bước 4: Khi bàn giao ticket sang Tuyến 1 hoặc Tuyến 2, nhân viên CSKH xác nhận rõ với khách hàng rằng ticket đã được chuyển cho bộ phận kỹ thuật thẩm định; không cam kết thời gian trả máy miễn phí và không gửi sơ đồ đấu nối hay hướng dẫn tự sửa chữa cho khách hàng (ANS 07). [Dữ liệu giả lập phục vụ đồ án]

