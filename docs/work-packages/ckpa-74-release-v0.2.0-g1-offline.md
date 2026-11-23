# BÁO CÁO HỢP NHẤT & ĐÓNG BĂNG BẢN PHÁT HÀNH `v0.2.0-g1-offline` (CKPA-74 — DEL 02 G1 OFFLINE CORE)

- **Mã Jira:** `CKPA-74` (`CRM-G1-SUB22`) | **Parent Epic:** `CKPA-44` | **Story liên quan:** `CKPA-73` (`CRM-G1-ST08`)
- **Mở khóa (Blocks):** `CKPA-75` (`CRM-G1-SUB23` — S4 Kiểm định độc lập OPS 01/03/04 & SEC 01/05 trên hộp đen)
- **Tiêu chí Cổng G1:** `G1-AC02`, `G1-AC03`, `G1-AC04`, `G1-AC05`, `G1-AC06`
- **Truy vết RFP:** `WP 02`, `WP 03`, `DEL 02`, `Mục 9 (G1)`
- **Assignee / Lead:** `[S1]` Hoàng Tiến (Named Lead) | **Reporter / Nghiệm thu:** `[P1]` Mỹ Vân (Purchaser Sponsor)
- **Phối hợp (RACI):** `[S2]` Quốc Hưng, `[S3]` Yến Nhi, `[S5]` Ngọc Duy
- **Release Tag:** `v0.2.0-g1-offline` (gắn trên nhánh `develop`)
- **Ngày đóng băng:** `2026-11-24`

---

## 1. Danh sách PR / Nhánh WP 02 & WP 03 đã Hợp nhất vào `develop`

Toàn bộ các nhánh tính năng (`feat/`, `data/`, `ops/`) của Sprint 3–4 đã vượt qua kiểm duyệt ngang hàng (`[S1]` + peer Build, tuân thủ tách vai SoD — **không dùng `[S4]` trên PR `feat/`**) và được hợp nhất sạch vào `develop` (`Open PRs = 0`):

| PR | Nhánh nguồn | Commit Merge | Mã Jira | Phạm vi bàn giao |
| :---: | :--- | :---: | :---: | :--- |
| **#18** | `data/CKPA-50-curate-family1-dat01-08` | `a5a6a14` | `CKPA-50` | Corpus Họ 1, SHA-256 manifest, quarantine fixtures |
| **#20** | `feat/CRM-G1-SUB07-rbac-7states-knw03-filter` | `375a5c4` | `CKPA-54` | Pre-retrieval RBAC 4 vai trò (`SEC 01`) & 7 trạng thái `KNW 03` |
| **#23** | `feat/CRM-G1-SUB14-date-6dim-lookup-conflict-hold` | `b2d2f19` | `CKPA-63` | Governing Date `UTC+7` (`OPS 03`), 6 chiều `DAT 04`, Critical Field Lookup & Hold (`DAT 05/06/08`, `OPS 04`) |
| **#25** | `ops/CKPA-46-g1-sec06-dung-moi-truong-test-tach-prod-iam-4-vai` | `7a7e154` | `CKPA-46` | Môi trường Test tách Prod (`SEC 06`) & IAM 4 vai trò |
| **#26** | `feat/CKPA-52-code-csv-validators-and-quarantine` | `09e7cf4` | `CKPA-52` | 2 Bộ CSV Validators cơ sở (21 & 23 cột) & Quarantine |
| **#27** | `data/CKPA-58-curate-family2-3-ceilings` | `9a45bc6` | `CKPA-58` | Full Corpus 3 Họ (11 tài liệu, 96 đoạn, 40 trường) & SHA-256 manifest |
| **#28** | `feat/CKPA-59-code-doi-soat-tombstone-thu-hoi` | `52a0c4c` | `CKPA-59` | Đối soát full-snapshot, Tombstone, Immediate Withdrawal (commit trước ack, fail-closed) & khóa `O1` mặc định (`403`) |
| **#29** | `ops/CKPA-60-g1-ops01-benchmark-500-dong-lkg` | `7eeb87b` | `CKPA-60` | Benchmark `OPS 01` 500 dòng (`0.3738s` ≤ 30p) & bảo toàn LKG 100% |

---

## 2. Kết quả Kiểm chứng Chất lượng trước khi Đóng băng (Pre-Freeze Verification)

| Kiểm tra | Lệnh thực thi | Kết quả |
| :--- | :--- | :---: |
| Backend Lint | `cd backend && python -m ruff check .` | **PASS** (`All checks passed!`) |
| Backend Typecheck | `cd backend && python -m mypy src` | **PASS** (`no issues found in 75 source files`) |
| Backend Test Suite | `cd backend && APP_ENV=test python -m pytest -q` | **PASS** (`100 passed, 1 warning in 1.33s`) |
| Worker Syntax | `python -m compileall -q worker/src` | **PASS** |
| CSV Contract Templates | Kiểm tra header `passages_template.csv` & `critical_fields_template.csv` | **PASS** (`21` & `23` cột UTF-8) |
| G1 Full Corpus Ceilings | Kiểm tra `data/g1/full/Policy_Corpus_G1_Full.csv` & `Critical_Fields_G1_Full.csv` | **PASS** (`11/30` tài liệu, `96/300` đoạn, `40/50` trường) |
| Base Scope Boundary (`O1`) | `ENABLE_O1_CONTEXT_IMPORT=false` | **PASS** (từ chối `403 O1_OPTION_DISABLED_IN_BASE_SCOPE`) |

---

## 3. Quy định Đóng băng & Bàn giao Hộp đen cho Kiểm định Độc lập (`CKPA-75`)

1. **Chính sách đóng băng nhánh (Code Freeze Policy):**
   - Kể từ thời điểm gắn tag `v0.2.0-g1-offline`, `[S2]` Quốc Hưng và `[S3]` Yến Nhi **không được phép** sửa trực tiếp hoặc ghi đè tag.
   - Mọi lỗi phát sinh trong quá trình kiểm định độc lập của `[S4]` Quý Hải (`CKPA-64`, `CKPA-75`) hoặc kiểm toán bảo mật của `[P5]` Anh Khoa (`CKPA-70`, `CKPA-79`) phải đi qua luồng sửa lỗi chính thức (`CKPA-72` / `CKPA-76` Swarming), review bởi `[S1]` và tạo bản vá delta cho `[S4]` retest.
2. **Đóng gói & Triển khai trên môi trường Test (`SEC 06`):**
   - Checkout đúng tag `v0.2.0-g1-offline` trên môi trường Test tách Prod (`APP_ENV=test`, `ENABLE_O1_CONTEXT_IMPORT=false`).
   - Chạy migration Alembic (`alembic upgrade head`) và nạp Full Corpus G1 (`data/g1/full/`).
3. **Ranh giới độc lập SoD (`Mục 8`):**
   - `[S4]` Quý Hải thực thi `CKPA-75` trên bản build `v0.2.0-g1-offline` theo cơ chế hộp đen; `[S2]`/`[S3]` tuyệt đối không tiếp cận `sealed-eval-repo`.
