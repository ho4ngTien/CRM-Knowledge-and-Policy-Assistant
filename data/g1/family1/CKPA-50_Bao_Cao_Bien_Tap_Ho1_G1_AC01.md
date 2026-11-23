# BÁO CÁO BIÊN TẬP CORPUS HỌ 1 (`POL-001`) — `CKPA-50` (`CRM-G1-SUB04`)

- **Dự án Jira chính thức:** `CKPA` — SongNhat CRM Knowledge and Policy Assistant (`Board 2: CKPA board`)
- **Jira Issue:** `CKPA-50` (`CRM-G1-SUB04`, Sub-task của Story `CKPA-49` / `CRM-G1-ST02`, Sprint 3 - G1 Impl W1) *(tương ứng mã cũ `CKPAOLD-77` trên board cũ đã lưu trữ)*
- **GitHub Branch:**
  - Theo **Onboarding Guide v1.0 (§15):** `data/CKPA-50-curate-family1-dat01-08` *(khuyến nghị)*
  - Theo **Description import từ Excel:** `data/CRM-G1-SUB04-curate-family1-dat01-08` *(cần xác nhận nhanh với `[S1]` Hoàng Tiến trước khi push)*
- **Tiêu chí Cổng G1:** `G1-AC01`
- **RFP Traceability:** `Mục 2`, `DEL 01`, `DAT 01`, `DAT 02`, `DAT 03`, `DAT 04`, `DAT 05`, `DAT 06`, `DAT 08`, `KNW 03`, `SEC 01`, `SEC 02`, `VN 01`, `VN 03`, `VN 04`, `Annex B`, `Annex C`
- **Phạm vi dữ liệu:** **Base Scope thuần túy — 0% O1 Selected CRM Context** (đúng quyết định G0 `CKPA-5` và chứng nhận `CKPA-47` của `[P5]` Anh Khoa)
- **Người thực hiện (`[P3]`):** Trần Chí Kha (*Knowledge and data steward*)
- **Người phê duyệt (`[P2]`):** Hữu Tài (*Policy owners* — `CKPA-51`)
- **Ngày hoàn tất biên tập & đối chiếu code `develop`:** `2026-11-19` (`Asia/Ho_Chi_Minh`)

---

## 1. Danh mục Sản phẩm Bàn giao (`CKPA-50`)

1. **`Policy_Corpus_Family1.csv`** — **40 passages** (`PAS-001..PAS-010`, `PAS-031..PAS-060`), UTF-8 (no BOM), đúng **21 cột** khớp tuyệt đối `PASSAGES_CSV_COLUMNS` trong `develop/backend/src/modules/ingestion/service.py`.
2. **`Critical_Fields_Family1.csv`** — **16 critical fields** (`CF-001..CF-004`, `CF-011..CF-022`), UTF-8 (no BOM), đúng **23 cột** khớp tuyệt đối `CRITICAL_FIELDS_CSV_COLUMNS` trong `develop/backend/src/modules/ingestion/service.py`.
3. **`Source_URI_And_Checksum_Manifest_Family1.csv`** — Bảng đối soát **56/56 bản ghi** (40 passages + 16 critical fields) kèm `source_uri` mở kiểm tra được 100%, mã băm `SHA-256`, độ dài Unicode và cờ `DAT 08`.
4. **Hồ sơ nguồn tham chiếu (`sources/DOC-001`, `DOC-004`, `DOC-006`, `DOC-007`)** — Cho phép re-verify thực tế `source_uri` theo `G1-AC01` và `DAT 08`.
5. **Bộ Test Fixture lỗi tách riêng (`Test_Fixtures_Quarantine_OPS01_04/`)** — **6 passages** + **4 critical fields** tiêm lỗi bao phủ **100% nhánh lỗi** của `IngestionService._validate_row()` trên nhánh `develop` (`PASSAGE_TOO_LONG`, `MISSING_ESSENTIAL_ATTACHMENTS`, `INVALID_RECORD_ACTION`, `MISSING_CURRENCY_UNIT`, thiếu `unit`, trùng `passage_id`, sai enum `KNW 03`, và `tombstone`).

---

## 2. Tổng hợp Dữ liệu Họ 1 (*Báo giá & Phê duyệt thương mại — `POL-001`*)

| Tài liệu (`document_id`) | Lớp thẩm quyền (`DAT 03`) | Phiên bản (`document_version_id`) | Trạng thái (`KNW 03`) | Dải `passage_id` | Số đoạn | Dải `field_id` | Mục đích kiểm soát RFP |
|---|---|---|---|---|---:|---|---|
| `DOC-001` | `policy` | `VER-001` *(G0 bảo toàn)* | `effective` | `PAS-001..010` | 10 | `CF-001..004` | Giữ nguyên 100% ID/nội dung G0 (khớp 60 Dev Tasks `CKPAOLD-10`) + bổ sung chiều thứ 6 `transaction_scope` |
| `DOC-001` | `policy` | `VER-001` *(Mở rộng phụ lục)* | `effective` | `PAS-031..040` | 10 | `CF-011..015, CF-021` | Động cơ 3 pha, Ex-d (`<=3%`), Biến tần trung thế (`<=12%`), Gearbox, Tạm ứng `>=30%`, Gia hạn báo giá (`>3%` tỷ giá), Chi nhánh `HN/DN/HCM`, **1 đoạn hạn chế `SEC 01` (`PAS-039` / `CF-015` không có `reader`)**, **1 đoạn `DAT 08 = false` (`PAS-040`)** |
| `DOC-001` | `policy` | `DOC001-VER-000` | `superseded` | `PAS-041..043` | 3 | `CF-016..018` | Phiên bản lịch sử `2025-01-01..2026-11-06 08:59:59 +07:00` (test Worked Case 3 & biên giờ VN `OPS 03`) |
| `DOC-001` | `policy` | `DOC001-VER-002` | `scheduled` | `PAS-044..045` | 2 | `CF-019..020` | Phiên bản tương lai `2027-01-01 00:00:00 +07:00` (`supersedes=VER-001`; test Worked Case 4 & `OPS 03`) |
| `DOC-001` | `policy` | `DOC001-VER-001-DRAFT` / `REV` / `APP` / `WD` | `draft`, `owner_reviewed`, `approved`, `withdrawn` | `PAS-046..049` | 4 | `CF-022` (`withdrawn`) | Đủ **7/7 trạng thái `KNW 03`** để `[S3]` Yến Nhi (`CKPA-54`) & `[S4]` Quý Hải (`CKPA-56`) smoke test bộ lọc Pre-Retrieval |
| `DOC-004` | `SOP` | `DOC004-VER-001` | `effective` *(chờ `[P2]` ký tại `CKPA-51`)* | `PAS-050..054` | 5 | — | Quy trình lập phiếu chiết khấu, bảng Gross Margin `BM-KD-02`, luồng duyệt & Backup Owner (`VN 04`) |
| `DOC-006` | `customer_contract` | `DOC006-VER-001` | `effective` | `PAS-055..057` | 3 | — | Hợp đồng khung B2B xung đột chiết khấu/hiệu lực/tạm ứng -> test **Conflict Hold (`DAT 05` — Worked Case 5)** |
| `DOC-007` | `staff_note` | `DOC007-VER-001` | `effective` | `PAS-058..060` | 3 | — | Ghi chú CRM cũ tiền lệ VIP -> test **No Inferred Approval (`ANS 05` — Worked Case 6)**, 0% PII thật |
| **TỔNG HỌ 1** | **4/5 lớp `DAT 03`** | **9 phiên bản** | **Đủ 7/7 `KNW 03`** | `PAS-001..010, 031..060` | **40 / 100** | **16 / 18** | **PASS 100% (`0` lỗi)** |

---

## 3. Kết quả Tự kiểm định (`scripts/validate_corpus_g1.ps1` — Đối chiếu Live `develop` & Script `[P5]`)

- **Hợp đồng CSV & Live `develop/backend/src/modules/ingestion/service.py`:**
  - `Policy_Corpus_Family1.csv`: đúng 21/21 cột UTF-8, đối soát dự kiến khi chạy qua `IngestionService.validate_csv_bytes()`: **`Expected = 40 = Accepted 39 + Quarantined 1 (PAS-040: MISSING_ESSENTIAL_ATTACHMENTS)`**.
  - `Critical_Fields_Family1.csv`: đúng 23/23 cột UTF-8, đối soát dự kiến: **`Expected = 16 = Accepted 16 + Quarantined 0`**.
- **Tương thích Live `develop/backend/src/modules/policy/service.py` & `shared/enums.py` & SQLAlchemy Models:**
  - 100% `field_type`, `operator`, `status`, `record_action`, `audience` khớp enum `CriticalFieldType`, `ComparisonOperator`, `PolicyLifecycleStatus`, `RecordAction`, `UserRole`.
  - 100% giá trị số (`number`/`currency`/`duration`) parse sạch qua `Decimal` (`between` chuẩn định dạng `low;high`); 100% cột không vượt độ dài `String(N)` trong `knowledge/models.py` & `policy/models.py`.
- **Giới hạn RFP Mục 2 & Đủ 6 chiều `DAT 04`:** `4 <= 10` docs, `40 <= 100` passages (max `591 <= 6.000` ký tự Unicode), `16 <= 18` critical fields; 100% dòng có đủ 6 chiều `company`, `branch`, `role`, `customer_group` (`= customer_category`), `product`, `transaction_scope`.
- **Đủ 7 trạng thái `KNW 03`:** `draft (1)`, `owner_reviewed (1)`, `approved (1)`, `scheduled (2)`, `effective (31)`, `superseded (3)`, `withdrawn (1)`.
- **Quét PII theo đúng script `[P5]` Anh Khoa (`CKPA-47` / `g1_security_audit_runner.py`):** **0% PII thật (`Real PII hits: 0`)**, **0% dữ liệu O1**. Có **3 đoạn hạn chế quyền (`PAS-039, PAS-046, PAS-047` không gồm `reader`)** phục vụ kiểm thử RBAC `SEC 01`.
- **Toàn vẹn `DAT 08` & `source_uri`:** **56/56 bản ghi** khớp `SHA-256` và tồn tại tệp `source_uri` trên đĩa.

---

## 4. Lưu ý bàn giao sang `CKPA-51` (`[P2]` Hữu Tài) & `CKPA-52` (`[S2]` Quốc Hưng)

1. **Hữu Tài (`CKPA-51` — đang bị `CKPA-50` block trực tiếp):** Thẩm định & ký duyệt nội dung `Policy_Corpus_Family1.csv` (40 passages) và `Critical_Fields_Family1.csv` (16 critical fields), đặc biệt xác nhận:
   - Chuyển `DOC-004` (`SOP`) từ `owner_reviewed` (G0) lên `effective` cho G1;
   - Phê duyệt các dòng kiểm thử `superseded`, `scheduled`, `withdrawn`, `PAS-039` (restricted) và `PAS-040` (`has_essential_attachments=false` để test `DAT 08` Quarantine).
2. **Quốc Hưng (`CKPA-52` — Code 2 Bộ Validator CSV & Quarantine):** Xem mục **Cảnh báo Kỹ thuật từ code `develop`** trong `BAO_CAO_BLOCKERS_VA_VAN_DE_G1_P3.md` (đặc biệt: trùng PK `DocumentVersion.id = VER-001` tại `knowledge/models.py:31`, cột `is_tombstoned` của `CriticalField` tại `policy/models.py:61-88`, và hỗ trợ 6 chiều `DAT 04` + alias `customer_group`/`customer_category`).
