# DOC-006 — Mẫu Hợp đồng khung phân phối B2B (Kiểm thử Conflict Hold DAT 05)

- **Policy Family:** `POL-001`
- **Authority Layer (DAT 03):** `customer_contract`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-006_HDNT-B2B-SYN-2026_Framework_Contract.md`
- **Curated Passages Count:** 3
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng source_uri (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-055 | DOC006-VER-001 | Điều 4.2 Hợp đồng khung (Trang 4) — [effective]
- **Title:** [Hợp đồng khung B2B] Điều khoản chiết khấu cố định 12% cho Biến tần trung thế
- **Source Ref:** `POL-001 / HDNT-B2B-SYN-2026_v1.0.docx (HDNT-04-02)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b_key_account;product:mv_inverter;transaction_scope:contract_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Lớp thẩm quyền customer_contract (Mẫu Hợp đồng khung B2B mã HĐNT-SYN-2026 — phục vụ kiểm thử xung đột DAT 05): Điều 4.2 Hợp đồng khung quy định mức chiết khấu cố định 12% cho mọi đơn hàng Biến tần trung thế không phân biệt giá trị đơn hàng. LƯU Ý BẮT BUỘC: Điều khoản này mâu thuẫn với quy trình phê duyệt theo ngưỡng tại DOC-001 Điều 2.2–2.3; hệ thống CẤM tự kết luận Hợp đồng thắng hay Chính sách thắng mà phải kích hoạt Conflict HOLD và chuyển Commercial Policy Owner. [Dữ liệu giả lập phục vụ đồ án]

### PAS-056 | DOC006-VER-001 | Điều 5.1 Hợp đồng khung (Trang 5) — [effective]
- **Title:** [Hợp đồng khung B2B] Điều khoản hiệu lực báo giá 30 ngày (Xung đột DOC-001)
- **Source Ref:** `POL-001 / HDNT-B2B-SYN-2026_v1.0.docx (HDNT-05-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b_key_account;product:industrial;transaction_scope:contract_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Lớp thẩm quyền customer_contract (Mẫu Hợp đồng khung B2B): Điều 5.1 Hợp đồng khung ghi nhận thời hạn giữ giá báo giá 30 ngày làm việc, xung đột trực tiếp với giới hạn 15 ngày làm việc tại DOC-001 Điều 1.2 (CF-004). Theo DAT 05 (Worked Case 5), hệ thống bắt buộc HOLD kết luận thời hạn báo giá, hiển thị đồng thời cả DOC-001 và DOC-006 để Commercial Policy Owner quyết định. [Dữ liệu giả lập phục vụ đồ án]

### PAS-057 | DOC006-VER-001 | Điều 6.3 Hợp đồng khung (Trang 6) — [effective]
- **Title:** [Hợp đồng khung B2B] Điều khoản tạm ứng 15% cho đơn nhập khẩu (Xung đột Điều 4.1)
- **Source Ref:** `POL-001 / HDNT-B2B-SYN-2026_v1.0.docx (HDNT-06-03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b_key_account;product:industrial;transaction_scope:contract_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Lớp thẩm quyền customer_contract (Mẫu Hợp đồng khung B2B): Điều 6.3 Hợp đồng khung đề xuất mức tạm ứng 15% cho thiết bị đặt nhập khẩu, thấp hơn mức sàn 30% của DOC-001 Điều 4.1 (CF-014). Hệ thống không được tự cho phép áp dụng 15% mà phải chuyển trạng thái Conflict HOLD và tạo Local Referral tới Commercial Policy Owner + Legal. [Dữ liệu giả lập phục vụ đồ án]

