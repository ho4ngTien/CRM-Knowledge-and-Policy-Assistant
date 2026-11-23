# BÁO CÁO BIÊN TẬP FULL CORPUS 3 HỌ CHÍNH SÁCH GATE G1 (`CKPA-58` / `CRM-G1-SUB10`)

- **Dự án:** SongNhat CRM Knowledge and Policy Assistant (`SCRM` / `CKPA`)
- **Jira Sub-task:** `CKPA-58` (`CRM-G1-SUB10`) | **Parent Story:** `CKPA-57` (`CRM-G1-ST04`) — Sprint 4 - G1 Impl W2
- **Tiêu chí Cổng G1:** `G1-AC01` (`Mục 2`, `DEL 01`, `DAT 01`, `DAT 04`, `DAT 06`, `DAT 08`, `KNW 03`, `SEC 01`, `SEC 02`, `Annex C`)
- **Assignee / Người biên tập:** `[P3]` Trần Chí Kha (Knowledge and Data Steward)
- **Người thẩm định / Phê duyệt:** `[P2]` Hữu Tài (Policy Owner — `CKPA-62`)
- **Phạm vi:** Base Scope thuần túy (**0% O1**, **0% PII thật**), nối tiếp gói Họ 1 đã duyệt tại `CKPA-50` / `CKPA-51`.
- **Thời điểm đối soát:** `2026-11-22 05:30 (+07)` (`Asia/Ho_Chi_Minh`)

---

## 1. Tổng hợp Quy mô & Đối soát `Expected = Accepted + Quarantined`

Toàn bộ gói Full Corpus 3 Họ tuân thủ chặt chẽ trần RFP Mục 2 (không tự bịa quy tắc để ép đủ trần):

| Hạng mục | Thực tế (`CKPA-58`) | Trần RFP (Mục 2) | Đối soát `IngestionService` (`DAT 02` / `DAT 08`) |
|---|---:|---:|---|
| **Tài liệu nguồn (`DOC-001..DOC-011`)** | **11** | `<= 30` | Phủ đủ **5/5 lớp thẩm quyền `DAT 03`** (`policy`, `SOP`, `manufacturer_terms`, `customer_contract`, `staff_note`) |
| **Passages (`Policy_Corpus_G1_Full.csv`)** | **96** | `<= 300` | `Expected = 96 = 93 Accepted + 3 Quarantined` (`PAS-040`, `PAS-066`, `PAS-082` cố ý `has_essential_attachments=false`) |
| **Critical Fields (`Critical_Fields_G1_Full.csv`)** | **40** | `<= 50` | `Expected = 40 = 40 Accepted + 0 Quarantined` (100% pass kiểu dữ liệu `Decimal`/enum/đơn vị/tiền tệ) |
| **Manifest SHA-256 & `source_uri`** | **136** | `= 96 + 40` | **136/136** `source_uri_exists = true`, **0** hash mismatch |
| **Độ dài tối đa đoạn văn bản** | **591 chars** | `<= 6.000` | 100% không cắt cụt âm thầm |
| **Bản ghi hạn chế quyền (`SEC 01` — không có `reader`)** | **7** | `>= 1` | Kiểm thử Pre-Retrieval RBAC trên cả 3 họ chính sách |
| **Quét PII thật (`CKPA-47` regex)** | **0 hits** | `0` | Đạt 100% `SEC 02` / `SEC 06` |

---

## 2. Phân bổ 11 Tài liệu Nguồn (`DOC-001..DOC-011`) theo 3 Họ & 5 Lớp `DAT 03`

| Mã Tài liệu | Họ Chính sách | Lớp `DAT 03` | Số Passages | Đường dẫn `source_uri` (Repo-relative) |
|---|---|---|---:|---|
| `DOC-001` | `POL-001` (Báo giá & Phê duyệt TM) | `policy` | 29 | `data/g1/sources/DOC-001_POL-CRM-01_Quotation_Commercial_Approval.md` |
| `DOC-004` | `POL-001` | `SOP` | 5 | `data/g1/sources/DOC-004_SOP-CRM-QBG-01_Discount_GrossMargin.md` |
| `DOC-006` | `POL-001` | `customer_contract` | 3 | `data/g1/sources/DOC-006_HDNT-B2B-SYN-2026_Framework_Contract.md` |
| `DOC-007` | `POL-001` | `staff_note` | 3 | `data/g1/sources/DOC-007_CRM-STAFF-NOTES-SYN_Quotation_History.md` |
| `DOC-002` | `POL-002` (Xử lý Thông tin KH) | `policy` | 22 | `data/g1/sources/DOC-002_POL-CRM-03_Customer_Information_Handling.md` |
| `DOC-005` | `POL-002` | `SOP` | 4 | `data/g1/sources/DOC-005_SOP-CRM-KH-01_Customer_Verification_Update.md` |
| `DOC-008` | `POL-002` | `customer_contract` | 2 | `data/g1/sources/DOC-008_DPA-B2B-SYN-2026_Customer_Data_Addendum.md` |
| `DOC-003` | `POL-003` (Định tuyến Dịch vụ/BH) | `policy` | 20 | `data/g1/sources/DOC-003_POL-CRM-02_Warranty_and_Service_Routing.md` |
| `DOC-009` | `POL-003` | `SOP` | 4 | `data/g1/sources/DOC-009_SOP-CRM-BH-01_Warranty_Intake_Routing.md` |
| `DOC-010` | `POL-003` | `manufacturer_terms` | 2 | `data/g1/sources/DOC-010_OEM-TERMS-SYN-2026_Manufacturer_Warranty_Terms.md` |
| `DOC-011` | `POL-003` | `staff_note` | 2 | `data/g1/sources/DOC-011_CRM-STAFF-NOTES-BH_Warranty_History.md` |

---

## 3. Tương thích Ngược & Kiểm soát Đặc thù RFP

1. **Bảo toàn 100% khóa ngoại G0 & Họ 1:** Giữ nguyên toàn bộ `PAS-001..030` và `CF-001..010` (G0) cùng `PAS-031..060` và `CF-011..022` (Họ 1 `CKPA-50`), nâng cấp bổ sung đủ chiều thứ 6 `transaction_scope` trên 100% dòng để đáp ứng đủ 6 chiều `DAT 04` (`company`, `branch`, `role`, `customer_group`, `product`, `transaction_scope`) mà không làm gãy bất kỳ tham chiếu nào của 60 Dev Tasks / 200 Real Tasks.
2. **Đủ 7/7 trạng thái `KNW 03`:** `draft`, `owner_reviewed`, `approved`, `scheduled`, `effective`, `superseded`, `withdrawn` — phủ đầy đủ trên các họ để kiểm thử bộ lọc Pre-Retrieval và ngày hiệu lực `UTC+7` (`OPS 03`).
3. **3 ca kiểm thử `DAT 08` Quarantine/Hold:** `PAS-040` (Họ 1 — Phụ lục B1), `PAS-066` (Họ 2 — Phụ lục B2), `PAS-082` (Họ 3 — Phụ lục B3).
4. **Kiểm thử `DAT 05` Conflict Hold:** `DOC-006` (HĐ khung B2B Họ 1), `DOC-008` (Phụ lục DPA Họ 2), `DOC-010` (Điều khoản Hãng OEM > 30 kW vs 37 kW Họ 3).

---

## 4. Tự kiểm định & Bàn giao Bước tiếp theo

- Đã chạy `powershell -NoProfile -ExecutionPolicy Bypass -File data/g1/scripts/validate_g1_repo.ps1`: **PASS 100% (0 errors, 136/136 SHA-256 & `source_uri`, 0 Real PII hits)**.
- **Mở khóa cho:**
  - **`[P2]` Hữu Tài (`CKPA-62`):** Thẩm định & ký duyệt nội dung Họ 2–3, 6 chiều `DAT 04` và đáp án chuẩn Hold.
  - **`[S2]` Quốc Hưng (`CKPA-57`/`CKPA-59`) & `[S5]` Ngọc Duy (`CKPA-60`):** Nạp Full Corpus 3 Họ vào pipeline đối soát & benchmark `OPS 01` (`<= 30 phút`).
  - **`[P4]` Trà My (`CKPA-66`):** Có thể đối chiếu lại `source_uri_inspection_log.csv` từ `PENDING_CURATION` sang `VERIFIED_ACCESSIBLE` cho `DOC-002..DOC-011`.
