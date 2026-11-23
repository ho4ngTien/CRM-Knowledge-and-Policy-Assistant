# HỒ SƠ BẰNG CHỨNG CỔNG G1 (DEL 03 PART 1), BÁO CÁO GIỜ CÔNG W1–W3 & KẾ HOẠCH SPRINT 6 (CKPA-80 — BẢN NHÁP v0.9)

- **Mã Jira:** `CKPA-80` (`CRM-G1-SUB27`) | **Parent Epic:** `CKPA-44` | **Story liên quan:** `CKPA-77` (`CRM-G1-ST09`)
- **Tiêu chí Cổng G1:** `G1-AC01`, `G1-AC02`, `G1-AC03`, `G1-AC04`, `G1-AC05`, `G1-AC06`, `G1-AC07`
- **Truy vết RFP:** `Mục 6`, `Mục 9 (G1)`, `Mục 10 (W1–W3 & W4)`, `Mục 11 (Hours by role/week)`, `Mục 12 (DEL 02, DEL 03)`, `DAT 07`, `SEC 06`
- **Assignee / Lead:** `[S1]` Hoàng Tiến (Named Lead) | **Reporter / Nghiệm thu:** `[P1]` Mỹ Vân (Purchaser Sponsor)
- **Phối hợp (RACI):** `[S4]` Quý Hải, `[P5]` Anh Khoa, `[S3]` Yến Nhi
- **Trạng thái hồ sơ:** **Bản nháp v0.9 (2026-11-24)** — Đã điền sẵn toàn bộ bằng chứng Build/Data/Ops đã kiểm chứng; **đang chờ 4 đầu vào bắt buộc (`CKPA-75`, `CKPA-76`, `CKPA-78`, `CKPA-79`)** trước khi hoàn thiện bản v1.0 đệ trình Hội đồng G1 (`CKPA-81`/`CKPA-84`).

---

## 1. Ma trận Bằng chứng Nghiệm thu Cổng G1 (`DEL 03 Part 1` — `G1-AC01..G1-AC07`)

| Mã Tiêu chí | Yêu cầu RFP chính | Bằng chứng đã có (Verified trên `develop` / Jira) | Đầu mục còn chờ để chốt 100% | Trạng thái |
| :---: | :--- | :--- | :--- | :---: |
| **`G1-AC01`** | Full Approved Corpus 3 họ (≤ 30 tài liệu, ≤ 300 đoạn, ≤ 50 trường), 100% `source_uri` & cờ `DAT 08` | `CKPA-50`, `CKPA-51`, `CKPA-58` (PR #27: **11 tài liệu, 96 đoạn, 40 trường**, SHA-256 manifest 7 nguồn), `CKPA-62` (`Done`) | `CKPA-82` (`[P3]` Chí Kha kiểm lại 100% `source_uri` Họ 2–3 và ký `G1-AC01`) | **Đạt Build / Chờ ký `CKPA-82`** |
| **`G1-AC02`** | 2 Base CSV Validators, Quarantine, Full-Snapshot Reconciliation (`Expected = Accepted + Quarantined`), Benchmark `OPS 01` 500 dòng ≤ 30p & LKG 100% | `CKPA-52` (PR #26), `CKPA-59` (PR #28), `CKPA-60` (PR #29: `0.3738s` ≤ 30p, LKG 100%), `CKPA-74` (`v0.2.0-g1-offline`) | `CKPA-75` (`[S4]` chạy độc lập `OPS 01`) & `CKPA-76` (Swarming fix nếu có) | **Đạt Build / Chờ QA `CKPA-75`** |
| **`G1-AC03`** | Immediate Withdrawal commit trạng thái trước `ack`, fail-closed (`SEC 05`, `KNW 04`), khóa `O1` mặc định trong Base Scope (`DAT 07`) | `CKPA-59` (PR #28: authoritative commit trước `ack`, live re-fetch fail-closed, `403 O1_OPTION_DISABLED_IN_BASE_SCOPE`) | `CKPA-70` (`[P5]` chạy kiểm toán thật trên API/cache/DB), `CKPA-75` (`[S4]`), `CKPA-78` (`[S3]` O1 readiness) | **Đang bị chặn bởi `CKPA-70`** |
| **`G1-AC04`** | Pre-retrieval RBAC 4 vai trò (`SEC 01`: `reader`, `policy_owner`, `steward`, `administrator`), 7 trạng thái `KNW 03`, 0% rò rỉ link/citation/cache/log | `CKPA-46` (PR #25), `CKPA-54` (PR #20), `CKPA-56` (`ckpa-56-sprint3-review-retro.md`, 20/20 RBAC/7-state & 100/100 backend tests PASS) | `CKPA-70` (`[P5]` bản sửa thật) & `CKPA-75` (`[S4]`) | **Đang bị chặn bởi `CKPA-70`** |
| **`G1-AC05`** | Governing Date `UTC+7` (`OPS 03`), khớp 6 chiều `DAT 04`, Hold khi thiếu ngày chi phối | `CKPA-62` (`Done`), `CKPA-63` (PR #23: `test_sub14_selection.py` 52/52 PASS) | `CKPA-64` (`[S4]` test biên Sprint 4), `CKPA-75` (`[S4]`), `CKPA-83` (`[P2]` Reviewer #1 xác nhận) | **Chờ QA `CKPA-64`/`75`** |
| **`G1-AC06`** | Deterministic Critical Field Lookup (`DAT 06`, 0% số học qua LLM), Hold khi thiếu bảng/chú thích (`DAT 08`) hoặc xung đột nguồn (`DAT 05`, `OPS 04`) | `CKPA-63` (PR #23: `Decimal` thuần, `llm_used=False`, auto Hold 3 kịch bản) | `CKPA-64` (`[S4]`), `CKPA-72`/`78` (`[S3]`), `CKPA-75` (`[S4]`), `CKPA-83` (`[P2]`) | **Chờ QA `CKPA-64`/`75`** |
| **`G1-AC07`** | Môi trường Test tách Prod (`SEC 06`), 0% PII (`SEC 02`), kho `sealed-eval-repo` chặn `S2/S3`, bộ 200 Real Tasks (60/40/100 gom biến thể) + 80 Challenges (40 `VN 02`) | `CKPA-46`, `CKPA-47`, `CKPA-48`, `CKPA-55`, `CKPA-66` (200 câu sạch PII, P3 & P1 đã duyệt) | `CKPA-67` (`[S4]` phân vùng), `CKPA-68` (`[P2]`/`[P3]` đồng gán nhãn), `CKPA-79` (`[P5]` kiểm toán ACL `sealed-eval-repo` & quét lại 0% PII trên Full Corpus) | **Chờ `CKPA-67/68/79`** |

---

## 2. Báo cáo Tổng hợp Giờ Công G1 Tuần 1–3 theo 10 Vai Trò (RFP Mục 11)

> **Chuẩn hóa số liệu đối chiếu `DEL 05`:** Theo bảng gốc `PhanCongCongViec_G1.xlsx` (`2_Ma_Tran_10Vai_Workload_G1`) và Epic `CKPA-44`, tổng định mức G1 của 30 Sub-tasks là **276h** (`W1 = 100h`, `W2 = 112h`, `W3 = 64h`). Con số `372h` xuất hiện trong mô tả cũ của `CKPA-77`/`CKPA-80` là bản nháp trước khi tối ưu Sprint và được chuẩn hóa về **276h** trong hồ sơ này.

| Mã Role | Thành viên | Phía RFP | W1 — Sprint 3 (Kế hoạch) | W2 — Sprint 4 (Kế hoạch) | W3 — Sprint 5 (Kế hoạch) | Tổng KH G1 (h) | Đã hoàn tất `Done` (h) | Đang mở / Carry-over (h) |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `P1` | Mỹ Vân | Purchaser | 0h | 0h | 4h | **4h** | 0h | 4h (`CKPA-84`) |
| `P2` | Hữu Tài | Purchaser | 8h | 12h | 4h | **24h** | 12h | 12h (`CKPA-68`, `83`) |
| `P3` | Chí Kha | Purchaser | 16h | 8h | 12h | **36h** | 24h | 12h (`CKPA-82`) |
| `P4` | Trà My | Purchaser | 16h | 16h | 0h | **32h** | **32h** | 0h |
| `P5` | Anh Khoa | Purchaser | 8h | 8h | 12h | **28h** | 8h | 20h (`CKPA-70`, `79`) |
| `S1` | Hoàng Tiến | Supplier | 0h | 8h | 8h | **16h** | 4h (`CKPA-74`*) | 12h (`CKPA-71`, `80`) |
| `S2` | Quốc Hưng | Supplier | 8h | 16h | 4h | **28h** | 24h | 4h (`CKPA-76`) |
| `S3` | Yến Nhi | Supplier | 16h | 24h | 4h | **44h** | 32h | 12h (`CKPA-72`, `78`) |
| `S4` | Quý Hải | Supplier | 12h | 12h | 16h | **40h** | 12h | 28h (`CKPA-64`, `67`, `75`) |
| `S5` | Ngọc Duy | Supplier | 16h | 8h | 0h | **24h** | **24h** | 0h |
| **TỔNG** | **10 Vai trò** | **5 P + 5 S** | **100h** | **112h** | **64h** | **276h** | **172h (62.3%)** | **104h (37.7%)** |

*\*Ghi chú: `CKPA-74` (4h) được hoàn tất và gắn tag `v0.2.0-g1-offline` ngày `2026-11-24`. Phần thực tế hoàn tất cuối kỳ sẽ được cập nhật bản v1.0 sau khi đóng các sub-tasks Sprint 5.*

---

## 3. Kế hoạch Triển khai Sprint 6 — Tuần 4 & Cổng G2 (`CKPA-85` / `CRM-G2-EP01`)

Trích xuất đồng bộ từ `PhanCongCongViec_G2_ChuanJira_RFP.xlsx` (tổng dự toán **360h**, 30 Tasks chia 3 giai đoạn trong Sprint 6, áp dụng điều kiện kích hoạt ngay sau khi Hội đồng ký `CKPA-84` chốt G1):

### Giai đoạn 1 (Ngày 1–2 Sprint 6 — Build Workspace, Lifecycle, Ops & Legal Prep)
- **WP 04 — Answer Package & Guardrails (`[S3]` Yến Nhi, 40h):** `CRM-G2-T01` (Answer Package 100–250 từ + Trường cứng `ANS 03-04`), `T02` (Local Referral & 9 ca Phụ lục B `KNW 05`), `T03` (Chống Prompt Injection & khóa Streaming `ANS 08`).
- **WP 04 — Lifecycle & Feedback (`[S2]` Quốc Hưng, 38h):** `CRM-G2-T04` (7 trạng thái & Hiệu lực lịch `KNW 03`), `T05` (Chặn Stale Answer khi Thu hồi `KNW 04`), `T06` (Phân loại Feedback & Ứng viên tri thức `KNW 06-07`).
- **Ops & Fallback (`[S5]` Ngọc Duy, 24h):** `CRM-G2-T07` (Xóa Cache vật lý ≤ 5 phút & Fail-closed `OPS 05`), `T09` (Emergency Disable & Tìm kiếm dự phòng `Mục 9`).
- **Legal/Security & Readiness (`[P5]` Anh Khoa 24h, `[P2]`/`[P3]`/`[P4]` mỗi vai 10h, `[S1]` 12h):** `T22` (Lập luận phân loại rủi ro AI có ngày `Annex F`), `T23` (Thông báo, Sự cố 4h & Change Control `SEC 03-08`), `T14`/`T17`/`T20` (Kiểm tra luồng duyệt/diễn tập thu hồi/đào tạo 5 Rep Users), `T25` (`[S1]` đóng gói Working Core `DEL 02`).

### Giai đoạn 2 (Ngày 3–4 Sprint 6 — Kiểm định Độc lập 180 Ca & Đào tạo)
- **Hiệu năng & Independent QA (`[S5]` 12h, `[S4]` Quý Hải 40h):** `T08` (Benchmark 5 concurrent users, `p95 ≤ 25s` trên 100 requests `OPS 02`), `T10` (80 Challenges & Thu hồi giữa chừng), `T11` (Chấm điểm 100 ca Sealed — Applicability/Recall), `T12` (Báo cáo Điểm số Độc lập & Mẫu số `DEL 03`).
- **Thẩm định độc lập phía Purchaser (`[P2]` 26h, `[P3]` 26h, `[P4]` 24h, `[P5]` 10h):** `T13`/`T16` (Two Policy Reviewers chấm độc lập điều khoản/ngoại lệ/ngày/phạm vi), `T19` (Đánh giá tính hữu ích & mức sửa nhỏ ≥ 80%), `T24` (Xác nhận 0 lỗi tiết lộ trái phép trên 180 ca), `T15`/`T18`/`T21` (Đào tạo Owners/Steward & diễn tập Fallback/Effort).
- **Tổng hợp hồ sơ (`[S1]` 14h):** `T26` (Đệ trình Hồ sơ Điểm số Độc lập & Pháp lý G2).

### Giai đoạn 3 (Ngày 5 Sprint 6 — Hội đồng Nghiệm thu G2 & Kích hoạt Pilot G3)
- `[S1]` Hoàng Tiến (10h): `T27` (Báo cáo giờ công Tuần 4 & Lịch 20 ngày làm việc quan sát G3).
- `[P1]` Mỹ Vân (30h): `T28` (Hội đồng thẩm định 8 tiêu chí Cổng G2 & 4 Critical Gates = 0 lỗi), `T29` (Ký lệnh kích hoạt 20 ngày sử dụng có giám sát), `T30` (Ký Biên bản Nghiệm thu G2 & Giải ngân 25%).

---

## 4. Checklist Hoàn thiện Bản v1.0 (Các đầu mục chờ điền trước khi đóng `CKPA-80`)
- [ ] Đính kèm Báo cáo Kiểm định Độc lập G1 của `[S4]` Quý Hải (`CKPA-75`).
- [ ] Đính kèm Log Swarming Fix & Delta Retest (`CKPA-76`) — xác nhận `0` lỗi Critical Control.
- [ ] Đính kèm Báo cáo tối ưu Selection/Hold & kiểm thử trạng thái O1 (`CKPA-78`).
- [ ] Đính kèm Chứng nhận Kiểm toán ACL kho `sealed-eval-repo` & tái quét 0% PII của `[P5]` Anh Khoa (`CKPA-79`).
- [ ] Cập nhật cột giờ thực tế cuối Sprint 5 và chốt ký trình `[P1]` Mỹ Vân (`CKPA-81`/`CKPA-84`).
