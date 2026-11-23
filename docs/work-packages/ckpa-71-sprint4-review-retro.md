# BIÊN BẢN SPRINT 4 REVIEW, RETROSPECTIVE, PR AUDIT & BẢNG GIỜ CÔNG TUẦN 2 (CKPA-71)

- **Mã Jira:** `CKPA-71` (`CRM-G1-SUB20`) | **Parent Epic:** `CKPA-44` | **Story liên quan:** `CKPA-69` (`CRM-G1-ST07`)
- **Mở khóa (Blocks):** `CKPA-72` (`CRM-G1-SUB21` — Bugfix Selection/Hold cuối Sprint 4), `CKPA-74` (`v0.2.0-g1-offline`)
- **Phụ thuộc đầu vào:** `CKPA-70` (`CRM-G1-SUB19` — đang `In Progress` / Reopened), `CKPA-64` (`CRM-G1-SUB15` — đang `To Do`)
- **Tiêu chí Cổng G1:** `G1-AC03`, `G1-AC04`, `G1-AC07`
- **Truy vết RFP:** `Mục 10 (W2)`, `Mục 11 (Hours by role/week)`, `SEC 01`, `SEC 05`, `DAT 01–08`, `OPS 01/03/04`, `Scrum Events`
- **Vai trò tham gia:** `[S1]` Hoàng Tiến (Named Lead / SM — tổng hợp Review, PR Audit, Sổ giờ W2 & Retro), `[P1]` Mỹ Vân (PO / Nghiệm thu), cùng đại diện 10 vai trò (`P1–P5`, `S1–S5`)
- **Ngày lập & xác minh trên `develop`:** `2026-11-24` (commit `7eeb87b`)
- **Trạng thái biên bản:** **Bản v1.0 (Bổ sung trước — ghi nhận rõ các mục Carry-over chờ `CKPA-70` & `CKPA-64`)**

---

## 1. Tổng hợp Duyệt PR Kỹ thuật & Xác minh CI Nhánh `develop` (S1 + Peer Build, Tuân thủ SoD)

Toàn bộ các nhánh tính năng (`feat/`, `data/`, `ops/`) của Sprint 4 đã được `[S1]` Hoàng Tiến cùng peer Build (`[S2]`/`[S3]`) kiểm tra và hợp nhất vào `develop` (tuyệt đối **không dùng `[S4]` Quý Hải** trên PR nhánh `feat/` theo quy tắc SoD Mục 8 & Mục 11):

| PR | Nhánh / Commit | Mã Jira | Tác giả | Nội dung chính | Kết quả Review |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **#23** | `feat/CRM-G1-SUB14-date-6dim-lookup-conflict-hold` (`b2d2f19`) | `CKPA-63` | `[S3]` Yến Nhi | Governing Date `UTC+7`, 6-Scope Matcher `DAT 04`, Critical Field Lookup (≤ 50), Conflict/Date/DAT08 Hold | **Merged / PASS** |
| **#27** | `data/CKPA-58-curate-family2-3-ceilings` (`9a45bc6`) | `CKPA-58` | `[P3]` Chí Kha | Full Corpus 3 Họ (**11 tài liệu** ≤ 30, **96 đoạn** ≤ 300, **40 trường** ≤ 50), SHA-256 manifest 7 nguồn | **Merged / PASS** |
| **#28** | `feat/CKPA-59-code-doi-soat-tombstone-thu-hoi` (`52a0c4c`) | `CKPA-59` | `[S2]` Quốc Hưng | Full-snapshot reconciliation (`Expected = Accepted + Quarantined`), Tombstone, Immediate Withdrawal commit-trước-ack & fail-closed, chặn `O1` mặc định (`403`) | **Merged / PASS** |
| **#29** | `ops/CKPA-60-g1-ops01-benchmark-500-dong-lkg` (`7eeb87b`) | `CKPA-60` | `[S5]` Ngọc Duy | Benchmark `OPS 01` lô 500 dòng (`0.3738s` ≪ `30 phút`), bảo toàn LKG 100%, idempotent retry | **Merged / PASS** |

### Kết quả kiểm chứng CI Local trên `develop` @ `7eeb87b` (2026-11-24)
```text
Open PRs on GitHub (ho4ngTien/CRM-Knowledge-and-Policy-Assistant): 0
cd backend && python -m ruff check .      -> All checks passed!
cd backend && python -m mypy src          -> Success: no issues found in 75 source files
cd backend && APP_ENV=test pytest -q      -> 100 passed, 1 warning in 1.33s
python -m compileall -q worker/src        -> PASS (exit code 0)
CSV template contracts                    -> passages=21 cols, critical_fields=23 cols (PASS)
G1 Full Corpus ceilings                   -> docs=11 (<=30), passages=96 (<=300), critical_fields=40 (<=50) (PASS)
```

---

## 2. Sprint 4 Review — Tiến độ 12 Sub-tasks (G1 Impl W2: 2026-11-16..2026-11-20)

| Mã Jira | Mã G1 Excel | Hạng mục | Phụ trách | Dự toán | Trạng thái (24/11) | Bằng chứng / Ghi chú |
| :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| `CKPA-58` | `CRM-G1-SUB10` | Biên tập Họ 2-3 (≤ 300/50 trần) & `DAT 08` | `[P3]` Chí Kha | 8h | **Done** | PR #27 (`9a45bc6`), `data/g1/full/` |
| `CKPA-59` | `CRM-G1-SUB11` | Code Đối soát, Tombstone, Thu hồi & O1 | `[S2]` Quốc Hưng | 16h | **Done** | PR #28 (`52a0c4c`), migration `20261123_01` |
| `CKPA-60` | `CRM-G1-SUB12` | Benchmark nạp 500 dòng ≤ 30p & LKG (`OPS 01`) | `[S5]` Ngọc Duy | 8h | **Done** | PR #29 (`7eeb87b`), `0.3738s` / LKG 100% |
| `CKPA-62` | `CRM-G1-SUB13` | Duyệt Họ 2-3, 6 chiều chuẩn & Hold (`DAT 04`) | `[P2]` Hữu Tài | 4h | **Done** | Đã duyệt Corpus Họ 2-3 & 6 chiều |
| `CKPA-63` | `CRM-G1-SUB14` | Code Ngày `UTC+7`, 6 Chiều, Trường & Hold | `[S3]` Yến Nhi | 16h | **Done** | PR #23 (`b2d2f19`), `test_sub14_selection.py` |
| `CKPA-66` | `CRM-G1-SUB16` | Hoàn tất 200 Câu hỏi thực & Check source | `[P4]` Trà My | 16h | **Done** | PR #15 (Purchaser repo), P3 & P1 đã duyệt |
| `CKPA-67` | `CRM-G1-SUB17` | Chia 60/40/100 (Gom biến thể) + 80 Challenges | `[S4]` Quý Hải | 4h | **In Progress** | Quá hạn `2026-11-18`; chưa có cập nhật nạp kho `sealed-eval-repo` |
| `CKPA-70` | `CRM-G1-SUB19` | Kiểm toán Lộ lọt Link, Citation & Cache (`SEC 01`) | `[P5]` Anh Khoa | 8h | **In Progress** | **Reopened 24/11 01:58** (xem Mục 4) |
| `CKPA-71` | `CRM-G1-SUB20` | Review PR (S1), Sổ giờ W2 & S4 Retro | `[S1]` Hoàng Tiến | 8h | **In Progress** | Đã lập biên bản v1.0 này; chờ chốt cùng `CKPA-70` & `CKPA-64` |
| `CKPA-64` | `CRM-G1-SUB15` | Kiểm thử biên Ngày & Trường (`<, =, >`) S4 | `[S4]` Quý Hải | 8h | **To Do** | Quá hạn `2026-11-20`; đang block `CKPA-61` & `CKPA-72` |
| `CKPA-68` | `CRM-G1-SUB18` | Đồng gán nhãn Chuẩn 100 Sealed + 80 Chal | `[P2]` Hữu Tài | 8h | **To Do** | Chờ `CKPA-67` hoàn tất phân vùng trong `sealed-eval-repo` |
| `CKPA-72` | `CRM-G1-SUB21` | Sửa lỗi Selection/Hold cuối Sprint 4 | `[S3]` Yến Nhi | 8h | **To Do** | Chờ danh sách lỗi từ `CKPA-64` & `CKPA-70` |

- **Tỷ lệ hoàn tất Sprint 4 tại thời điểm 2026-11-24:** **6/12 Sub-tasks `Done` (68h / 112h = 60.7%)**; Story `CKPA-57` (WP02) đã `Done` 100% (3/3 sub-tasks); 3 Story còn lại (`CKPA-61`, `CKPA-65`, `CKPA-69`) giữ `In Progress`.

---

## 3. Bảng Giờ Công Tuần 2 (Sprint 4 DUO: 2026-11-16..2026-11-20) — Chuẩn RFP Mục 11

Đối chiếu định mức chuẩn trong `PhanCongCongViec_G1.xlsx` (`2_Ma_Tran_10Vai_Workload_G1`, tổng G1 = **276h** gồm W1 `100h` + W2 `112h` + W3 `64h`):

| Mã Role | Thành viên | Phía RFP | Sub-tasks Sprint 4 (W2) | Kế hoạch W2 (h) | Đã ghi nhận Done (h) | Đang mở / Carry-over (h) | Ghi chú đối chiếu |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `P1` | Mỹ Vân | Purchaser | *(PO nghiệm thu `CKPA-65`, `CKPA-66`, `CKPA-70`)* | 0h | 0h | 0h | Không gán sub-task W2 theo kế hoạch G1 |
| `P2` | Hữu Tài | Purchaser | `CKPA-62` (4h), `CKPA-68` (8h) | 12h | 4h | 8h | `CKPA-68` chờ `CKPA-67` |
| `P3` | Chí Kha | Purchaser | `CKPA-58` (8h) | 8h | 8h | 0h | Hoàn tất 100% W2 |
| `P4` | Trà My | Purchaser | `CKPA-66` (16h) | 16h | 16h | 0h | Hoàn tất 100% W2 |
| `P5` | Anh Khoa | Purchaser | `CKPA-70` (8h) | 8h | 0h | 8h | Reopened — đang sửa script kiểm toán thật |
| `S1` | Hoàng Tiến | Supplier | `CKPA-71` (8h) | 8h | 0h* | 8h* | Đã hoàn thiện PR Audit & Biên bản v1.0 (~6h/8h), còn 2h chốt sau `CKPA-64`/`70` |
| `S2` | Quốc Hưng | Supplier | `CKPA-59` (16h) | 16h | 16h | 0h | Hoàn tất 100% W2 |
| `S3` | Yến Nhi | Supplier | `CKPA-63` (16h), `CKPA-72` (8h) | 24h | 16h | 8h | `CKPA-72` chờ đầu vào lỗi từ `CKPA-64` & `CKPA-70` |
| `S4` | Quý Hải | Supplier | `CKPA-67` (4h), `CKPA-64` (8h) | 12h | 0h | 12h | Nút cổ chai lớn nhất của Sprint 4 |
| `S5` | Ngọc Duy | Supplier | `CKPA-60` (8h) | 8h | 8h | 0h | Hoàn tất 100% W2 |
| **TỔNG** | **10 Vai trò** | **5 P + 5 S** | **12 Sub-tasks Sprint 4** | **112h** | **68h** | **44h** | **Không vai trò nào vượt trần 40h/tuần** |

> **Lưu ý quản trị (cần chốt trong `CKPA-80` DEL 03):** Hiện mô tả Jira của `CKPA-77`/`CKPA-80` vẫn ghi tổng giờ W1–W3 là `372h` (số cũ trước khi rút gọn), trong khi `PhanCongCongViec_G1.xlsx` và `CKPA-44` ghi **276h** (`100h + 112h + 64h`). Cần thống nhất dùng **276h** làm chuẩn đối chiếu với `DEL 05`.

---

## 4. Danh sách Lỗi & Hạng mục Ưu tiên Xử lý cho `CKPA-72` và Mở khóa Sprint 5

| Mức độ | Mã Jira | Phụ trách | Mô tả lỗi / Thiếu sót cần khắc phục | Tác động |
| :---: | :---: | :--- | :--- | :--- |
| **P0 (Blocker)** | `CKPA-70` | `[P5]` Anh Khoa | (1) Thay script giả lập `g1_rbac_failclosed_audit_runner.py` bằng kiểm thử tích hợp gọi trực tiếp API/service/cache/DB môi trường Test; (2) Dùng đúng 4 vai trò RFP (`reader`, `policy_owner`, `steward`, `administrator`) trên 3 họ CRM & 7 trạng thái `KNW 03`; (3) Mở PR vào `develop` và sửa lại mã truy vết (`SEC 01/02/05`, `KNW 04`, `OPS 05` thay vì gán nhầm `SEC 08`). | Chặn đóng `CKPA-69`, `CKPA-71` và kiểm định an toàn G1 |
| **P0 (Blocker)** | `CKPA-64` | `[S4]` Quý Hải | Chạy kiểm thử biên độc lập `OPS 03` (`23:59:59` vs `00:00:00` `UTC+7`, lùi ngày, future, thiếu ngày Hold) và `OPS 04` (`<, =, >`, thiếu đơn vị, thiếu footnote, conflict Hold) trên Dev/Val để xuất danh sách ca đạt/lỗi cho `[S3]` xử lý ở `CKPA-72`. | Chặn đóng `CKPA-61` và khởi chạy `CKPA-72` |
| **P0 (Blocker)** | `CKPA-67` → `CKPA-68` | `[S4]` Quý Hải → `[P2]` Hữu Tài | Hoàn tất phân vùng 60/40/100 (gom cụm biến thể `VG-01..16`) + 80 Challenges trong `sealed-eval-repo` để `[P2]` & `[P3]` đồng gán nhãn chuẩn tại `CKPA-68`. | Chặn `CKPA-65` (`G1-AC07`) |
| **P1 (Major)** | `CKPA-72` | `[S3]` Yến Nhi | Sẵn sàng tiếp nhận và vá toàn bộ lỗi Selection/Hold phát sinh từ `CKPA-64` và `CKPA-70` ngay khi có báo cáo (hoặc gộp sang nhánh fix sau tag `v0.2.0-g1-offline` nếu PO đồng ý đóng băng sớm `CKPA-74`). | Ảnh hưởng chất lượng bản `v0.2.0-g1-offline` |
| **P1 (Major)** | `CKPA-82` (`CKPA-66`) | `[P3]` Chí Kha & `[P4]` Trà My | Cập nhật `source_uri_inspection_log.csv` từ `PENDING_CURATION` sang `VERIFIED_ACCESSIBLE` cho Họ 2–3 sau khi `CKPA-58` (11 tài liệu) đã merge vào `develop`. | Đảm bảo 100% `DAT 08` (`G1-AC01`) |

---

## 5. Sprint 4 Retrospective — Bài học & Hành động Cải tiến cho Sprint 5

### Điểm làm tốt (What went well)
1. **Nhóm Build & Ops giữ đúng nhịp chất lượng:** Toàn bộ WP 02 (`CKPA-58`, `CKPA-59`, `CKPA-60`) và WP 03 core (`CKPA-63`) đều merge sạch vào `develop` với **100/100 pytest PASS**, `ruff`/`mypy` sạch lỗi, hiệu năng `OPS 01` đạt `0.3738s` (vượt xa ngưỡng `30 phút`), và giữ đúng ranh giới Base Scope (chặn `O1` mặc định bằng `403`).
2. **Phát hiện sớm lỗi bằng chứng giả lập:** Quy trình rà soát kỹ thuật của `[S1]` đã chặn kịp thời việc đóng `CKPA-70` khi bằng chứng kiểm toán chưa chạy trên hệ thống thật.

### Điểm cần khắc phục (What needs improvement)
1. **Ùn ứ ở khâu Independent QA (`[S4]`) và Security Audit (`[P5]`):** 3/4 nút thắt của Sprint 4 nằm ở `CKPA-64`, `CKPA-67`, `CKPA-70` (đều đã quá hạn gốc `18–20/11`), làm chuỗi `CKPA-68`, `CKPA-72` bị dồn sang Sprint 5.
2. **Đồng bộ thông tin trên Jira:** Còn sai lệch mốc ngày Sprint trong mô tả (`tháng 12` vs `tháng 11`) và tổng giờ W1–W3 (`372h` vs `276h`).

### Hành động cải tiến (Action Items cho Sprint 5)
| # | Hành động | Phụ trách | Thời hạn |
| :---: | :--- | :--- | :--- |
| AI-1 | Gửi nhắc hạn & chốt ETA hoàn thành `CKPA-64`, `CKPA-67` (S4) và bản sửa thật của `CKPA-70` (P5) trong 24h tới | `[S1]` Hoàng Tiến | 2026-11-24 |
| AI-2 | Đóng băng sớm `v0.2.0-g1-offline` (`CKPA-74`) trên nền `develop` @ `7eeb87b` (đã 100/100 test xanh) để mở khóa kiểm định độc lập `CKPA-75`, mọi lỗi phát sinh xử lý qua `CKPA-72`/`CKPA-76` | `[S1]` Hoàng Tiến | 2026-11-24 |
| AI-3 | Bổ sung comment xác nhận review `APPROVE` của `[S1]` trên `CKPA-59`, `CKPA-60` và chuẩn hóa mốc `276h` trong `CKPA-80` (`DEL 03`) | `[S1]` Hoàng Tiến | 2026-11-25 |
