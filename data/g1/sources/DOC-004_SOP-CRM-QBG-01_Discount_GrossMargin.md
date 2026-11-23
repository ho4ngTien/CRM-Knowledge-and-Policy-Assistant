# DOC-004 — SOP Lập phiếu đề xuất chiết khấu và bảng tính Gross Margin trên CRM

- **Policy Family:** `POL-001`
- **Authority Layer (DAT 03):** `SOP`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-004_SOP-CRM-QBG-01_Discount_GrossMargin.md`
- **Curated Passages Count:** 5
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng source_uri (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-050 | DOC004-VER-001 | Bước 1 (Trang 1) (Trang 1) — [effective]
- **Title:** SOP Lập phiếu đề xuất chiết khấu trên CRM - Bước 1: Tạo mã phiếu & Kiểm tra MST
- **Source Ref:** `POL-001 / SOP-CRM-QBG-01_v1.0.docx (SOP-QBG-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:mid_tier_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-QBG-01 Bước 1 (Lớp thẩm quyền SOP — phải tuân thủ ngưỡng của DOC-001): Khi tạo Phiếu đề xuất chiết khấu trên CRM cho mức > 5%, nhân viên kinh doanh chọn đúng Mã cơ hội (Opportunity ID), xác minh hồ sơ khách hàng đã đủ MST, ĐKKD và Phân nhóm khách hàng (Nhà máy / Đại lý). Không tạo phiếu nếu thiếu thông tin định danh doanh nghiệp. [Dữ liệu giả lập phục vụ đồ án]

### PAS-051 | DOC004-VER-001 | Bước 2 (Trang 1) (Trang 1) — [effective]
- **Title:** SOP Lập phiếu đề xuất chiết khấu - Bước 2: Đính kèm Bảng tính Gross Margin
- **Source Ref:** `POL-001 / SOP-CRM-QBG-01_v1.0.docx (SOP-QBG-02)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:mid_tier_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-QBG-01 Bước 2: Đối với mọi đề xuất chiết khấu từ trên 5% đến 15% (CF-002), nhân viên bắt buộc điền đủ Bảng tính biên lợi nhuận dự kiến (Gross Margin Sheet mẫu BM-KD-02) gồm giá vốn tham chiếu, chi phí vận chuyển dự kiến và tỷ lệ chiết khấu đề xuất. Phiếu thiếu BM-KD-02 sẽ bị từ chối tự động ở bước rà soát của Sales Manager. [Dữ liệu giả lập phục vụ đồ án]

### PAS-052 | DOC004-VER-001 | Bước 3 (Trang 2) (Trang 2) — [effective]
- **Title:** SOP Lập phiếu đề xuất chiết khấu - Bước 3: Luồng trình duyệt Sales Manager / Sales Director
- **Source Ref:** `POL-001 / SOP-CRM-QBG-01_v1.0.docx (SOP-QBG-03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:discount_approval_workflow`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-QBG-01 Bước 3: Sau khi đính kèm chứng từ trên CRM, nhân viên bấm gửi duyệt theo đúng cấp thẩm quyền: <= 5% & < 500 triệu VND tự xác nhận (SLA 2 giờ); > 5% đến 15% & < 1 tỷ VND gửi Sales Manager (SLA 4 giờ); > 15% hoặc >= 1 tỷ VND gửi Sales Director kèm Tờ trình ngoại lệ và Hợp đồng dự thảo (SLA 48 giờ). Trợ lý AI chỉ hướng dẫn luồng, không thay mặt gửi hay duyệt phiếu. [Dữ liệu giả lập phục vụ đồ án]

### PAS-053 | DOC004-VER-001 | Bước 4 (Trang 2) (Trang 2) — [effective]
- **Title:** SOP Lập phiếu đề xuất chiết khấu - Bước 4: Lưu vết phê duyệt & Chống sửa báo giá sau duyệt
- **Source Ref:** `POL-001 / SOP-CRM-QBG-01_v1.0.docx (SOP-QBG-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:post_approval_control`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-QBG-01 Bước 4: Sau khi cấp có thẩm quyền phê duyệt trên hệ thống CRM, báo giá được khóa phiên bản PDF gửi khách hàng. Mọi thay đổi về số lượng, mã thiết bị hoặc tỷ lệ chiết khấu sau khi duyệt bắt buộc phải hủy bản cũ và mở luồng duyệt mới từ đầu; nghiêm cấm chỉnh sửa tay file PDF ngoài hệ thống CRM. [Dữ liệu giả lập phục vụ đồ án]

### PAS-054 | DOC004-VER-001 | Bước 5 (Trang 3) (Trang 3) — [effective]
- **Title:** SOP Lập phiếu đề xuất chiết khấu - Xử lý khi vượt SLA phê duyệt hoặc vắng mặt Owner
- **Source Ref:** `POL-001 / SOP-CRM-QBG-01_v1.0.docx (SOP-QBG-05)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:escalation_substitute`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

SOP-QBG-01 Bước 5 (Substitute Owner - VN 04): Trường hợp Sales Director đi công tác hoặc phiếu quá 75% thời hạn SLA (36 giờ đối với mốc 48 giờ), hệ thống quy trình nội bộ chuyển cấp phê duyệt dự phòng cho Phó Giám đốc Kinh doanh (Deputy Sales Director - Backup Owner 1) theo Ma trận Thẩm quyền đã ký duyệt. [Dữ liệu giả lập phục vụ đồ án]

