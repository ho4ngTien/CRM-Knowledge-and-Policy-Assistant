# DOC-008 — Phụ lục Bảo vệ Dữ liệu Khách hàng B2B DPA-B2B-SYN-2026 (Kiểm thử xung đột DAT 05)

- **Policy Family:** `POL-002`
- **Authority Layer (DAT 03):** `customer_contract`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-008_DPA-B2B-SYN-2026_Customer_Data_Addendum.md`
- **Curated Passages Count:** 2
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng `source_uri` (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-075 | DOC008-VER-001 | Điều 3.2 Phụ lục DPA (Trang 2) — [effective]
- **Title:** [Phụ lục DPA Hợp đồng B2B] Điều khoản xóa dữ liệu trong 15 ngày (Xung đột Annex C)
- **Source Ref:** `POL-002 / DPA-B2B-SYN-2026_v1.0.docx (DPA-03-02)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b_key_account;product:all;transaction_scope:contract_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Lớp thẩm quyền customer_contract (Phụ lục Bảo vệ dữ liệu DPA-B2B-SYN-2026 — kiểm thử xung đột DAT 05): Điều 3.2 Phụ lục DPA khách hàng yêu cầu xóa toàn bộ dữ liệu liên hệ và nhật ký giao dịch trong vòng 15 ngày sau khi chấm dứt đơn hàng, mâu thuẫn với lịch lưu giữ tối đa 12 tháng của DOC-002 Điều 4.4 và nghĩa vụ lưu giữ hóa đơn kế toán. BẮT BUỘC HOLD và chuyển CRM Data Governance Owner + Legal Owner quyết định. [Dữ liệu giả lập phục vụ đồ án]

### PAS-076 | DOC008-VER-001 | Điều 4.1 Phụ lục DPA (Trang 3) — [effective]
- **Title:** [Phụ lục DPA Hợp đồng B2B] Yêu cầu cập nhật liên hệ qua Email cá nhân không dấu đỏ (Xung đột DOC-002)
- **Source Ref:** `POL-002 / DPA-B2B-SYN-2026_v1.0.docx (DPA-04-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:crm;customer_group:b2b_key_account;product:all;transaction_scope:contract_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Lớp thẩm quyền customer_contract (Phụ lục DPA-B2B-SYN-2026): Điều 4.1 ghi nhận khách hàng đề xuất chấp nhận email thông báo từ người phụ trách mua hàng mà không cần Thông báo đóng dấu đỏ. Điều khoản này xung đột trực tiếp với DOC-002 Điều 1.4–1.5 (CF-005). Theo DAT 05, hệ thống không được tự cho phép bỏ dấu đỏ mà phải HOLD và chuyển CRM Data Governance Owner phân xử. [Dữ liệu giả lập phục vụ đồ án]

