# Ma trận Tuân thủ 57 Mã Yêu cầu RFP (Compliance Matrix)

> Đối chiếu 100% mã yêu cầu trong `SongNhat_CRM_Knowledge_Policy_Assistant_RFP_VI.pdf` (tổng cộng **57 mã**) sang đặc tả [SRS](./srs.md), cấu trúc mã nguồn, 5 cổng phát hành (`G0–G4`) và phụ trách trong đội `10` người.

---

## 1. Work Packages (`WP 01 – WP 06`)

| Mã RFP | Tên gói công việc | SRS Ref | Thành phần hệ thống / Tài liệu | Gate | Squad / Vai |
|---|---|---|---|---|---|
| `WP 01` | Discovery (Khảo sát) | `SRS-FR-01` | `docs/specs/srs.md`, `docs/specs/roadmap.md`, `data/sample/` | `G0` | `A1, A2, D2` |
| `WP 02` | Imports (Nhập dữ liệu) | `SRS-FR-03` | `ingestion`, `knowledge`, `worker/import_task.py`, `data/templates/` | `G1` | `B1` |
| `WP 03` | Selection (Lựa chọn) | `SRS-FR-04`, `SRS-FR-05` | `policy`, `retrieval`, `worker/index_task.py` | `G1` | `B2, B3` |
| `WP 04` | Workspace (Không gian làm việc) | `SRS-FR-06`, `SRS-FR-07.1` | `answer`, `validation`, `referral`, `frontend/chat, evidence` | `G2` | `C1, C2` |
| `WP 05` | Ownership (Quyền sở hữu) | `SRS-FR-04.2`, `SRS-FR-07.2–07.3` | `policy`, `admin`, `feedback`, `frontend/admin, referrals` | `G1–G2` | `B2, C2, A2` |
| `WP 06` | Operation (Vận hành) | `SRS-FR-08`, `SRS-NFR-*` | `audit`, `evaluation`, `infra/`, `docs/` | `G2–G4` | `C3, D1, D2` |

## 2. Data Authority & Applicability (`DAT 01 – DAT 08`)

| Mã RFP | Yêu cầu | SRS Ref | Thành phần hệ thống | Gate | Phụ trách |
|---|---|---|---|---|---|
| `DAT 01` | Provenance (Nguồn gốc dữ liệu) | `SRS-FR-03.2` | `knowledge`, `ingestion`, `passages_template.csv` | `G1` | `B1, A2` |
| `DAT 02` | Integrity (Tính toàn vẹn) | `SRS-FR-03.3` | `ingestion` (idempotent, late-batch guard, tombstone, manifest) | `G1` | `B1` |
| `DAT 03` | Authority (Thẩm quyền 5 lớp) | `SRS-FR-04.1` | `policy` (AuthorityMatrix) | `G0–G1` | `A2, B2` |
| `DAT 04` | Date and scope (Ngày & phạm vi) | `SRS-FR-04.3` | `policy` (`Asia/Ho_Chi_Minh`, governing date, scope) | `G1` | `B2` |
| `DAT 05` | Conflicts (Xung đột -> Hold) | `SRS-FR-04.4` | `policy` (Conflict Hold, no auto-precedence) | `G1` | `B2` |
| `DAT 06` | Critical fields (Trường quan trọng) | `SRS-FR-04.5` | `policy`, `validation`, `critical_fields_template.csv` | `G1` | `B2, C2` |
| `DAT 07` | CRM context (**Ngoài Base Scope / Chỉ áp dụng nếu chọn O1**) | Mục `2.3` (`O1` cắt khỏi codebase nền) | N/A trong Base Scope (chờ quyết định riêng tại `G0`) | `G0` (quyết định) | `A1` |
| `DAT 08` | Completeness (Tính đầy đủ) | `SRS-FR-03.4` | `ingestion`, `knowledge` (`has_essential_attachments`, quarantine) | `G1` | `B1, A2` |

## 3. Question Answering & Explanation (`ANS 01 – ANS 08`)

| Mã RFP | Yêu cầu | SRS Ref | Thành phần hệ thống | Gate | Phụ trách |
|---|---|---|---|---|---|
| `ANS 01` | Intent (Phân biệt câu hỏi chung/KH) | `SRS-FR-06.1` | `answer` | `G1–G2` | `C1` |
| `ANS 02` | Retrieval (Lọc trước + Tiếng Việt) | `SRS-FR-05.1–05.2` | `retrieval`, `policy` | `G1` | `B3, B2` |
| `ANS 03` | Answer package (Gói 7 phần) | `SRS-FR-06.1` | `answer/schemas.py`, `frontend/chat` | `G2` | `C1, C2` |
| `ANS 04` | Critical output (Deterministic) | `INV-04`, `SRS-FR-06.1` | `validation`, `policy`, `frontend/chat` | `G1–G2` | `C1, B2, C2` |
| `ANS 05` | Exceptions (Tuyến ngoại lệ) | `SRS-FR-06.2` | `answer`, `policy` | `G1–G2` | `C1, B2` |
| `ANS 06` | Missing evidence (Làm rõ / Hold) | `SRS-FR-06.2` | `answer`, `referral` | `G1–G2` | `C1` |
| `ANS 07` | Boundaries (Không tư vấn/duyệt) | `SRS-FR-06.2` | `answer`, `prompts/` | `G1–G2` | `C1, C3` |
| `ANS 08` | Robustness (Prompt injection) | `INV-05`, `SRS-FR-06.2` | `answer`, `validation`, `prompts/` | `G1–G2` | `C1, C3` |

## 4. Verification & Knowledge Maintenance (`KNW 01 – KNW 07`)

| Mã RFP | Yêu cầu | SRS Ref | Thành phần hệ thống | Gate | Phụ trách |
|---|---|---|---|---|---|
| `KNW 01` | Evidence (Hiển thị gốc đối chiếu) | `SRS-FR-06.1`, `7.1` | `frontend/chat, evidence` | `G2` | `C2` |
| `KNW 02` | Internal use (Chỉ dùng nội bộ) | `SRS-FR-06.1`, Mục `8.3` | `frontend/chat`, hướng dẫn sử dụng | `G2` | `C2, A1` |
| `KNW 03` | Publication (7 trạng thái vòng đời) | `SRS-FR-04.2` | `policy`, `admin`, `worker/index_task.py` | `G1–G2` | `B2, C2` |
| `KNW 04` | Change impact (Final check & Stale) | `INV-03`, `INV-06` | `validation`, `admin`, `answer` | `G1–G2` | `C1, B2, C3` |
| `KNW 05` | Referral (Chuyển xử lý nội bộ) | `SRS-FR-07.1` | `referral`, `frontend/referrals` | `G2` | `C1, C2` |
| `KNW 06` | Learning (Candidate có kiểm soát) | `SRS-FR-07.2` | `feedback`, `policy` | `G2` | `C2, A2` |
| `KNW 07` | Feedback (5 phân loại & báo cáo) | `SRS-FR-07.2` | `feedback`, `audit` | `G2` | `C2, C1` |

## 5. Security, Privacy & Governance (`SEC 01 – SEC 08`)

| Mã RFP | Yêu cầu | SRS Ref | Thành phần hệ thống | Gate | Phụ trách |
|---|---|---|---|---|---|
| `SEC 01` | Access (Least privilege mọi đường) | `SRS-FR-02` | `identity`, `shared/auth.py` | `G1` | `C3` |
| `SEC 02` | Minimization (Không hồ sơ KH / PII) | `SRS-NFR-08` | `shared/pii_guard.py`, `answer` | `G1` | `C3` |
| `SEC 03` | Deployment (Rà soát pháp lý/mục đích) | `SRS-NFR-10` | Hồ sơ rà soát pháp lý trước dữ liệu thật | `G0` -> `G2` | `A1, D2` |
| `SEC 04` | Providers (Vị trí xử lý, cấm train) | `SRS-NFR-09` | Hợp đồng/kiểm kê nhà cung cấp, `.env.example` | `G0` -> `G2` | `C3, A1` |
| `SEC 05` | Withdrawal (Tuần tự, purge 5m, fail-closed) | `INV-06`, `SRS-NFR-06` | `admin`, `validation`, `worker/index_task.py` | `G2` | `C3, B1` |
| `SEC 06` | Protection (Mã hóa, secrets, tách env) | `SRS-NFR-07` | `infra/`, `.github/workflows/ci.yml`, `config.py` | `G0–G2` | `C3` |
| `SEC 07` | Incidents (Thông báo 4h, bảo toàn log) | `SRS-NFR-04`, `SRS-NFR-09` | `audit`, quy trình sự cố | `G2` | `C3, A1` |
| `SEC 08` | Changes (Đánh giá tác động & rollback) | Mục `8.3` | Quy trình change control, `evaluation` | `G2–G3` | `A1, D1, C3` |

## 6. Operational & Volume Tests (`OPS 01 – OPS 08`)

| Mã RFP | Yêu cầu | SRS Ref | Thành phần hệ thống | Gate | Phụ trách |
|---|---|---|---|---|---|
| `OPS 01` | Import (`500` dòng `<= 30` phút) | `SRS-NFR-01` | `ingestion`, `backend/tests/ops/` | `G1` -> `G2` | `B1, D2` |
| `OPS 02` | Response (`5` users, `p95 <= 25s` / 100 req) | `SRS-NFR-02` | `answer`, `backend/tests/ops/` | `G2` | `C1, D2` |
| `OPS 03` | Dates (Ranh giới hiệu lực giờ VN) | `SRS-FR-04.3`, `SRS-NFR-03` | `policy`, `backend/tests/ops/` | `G1` -> `G2` | `B2, D1` |
| `OPS 04` | Fields (Biên ngưỡng, thiếu đơn vị) | `SRS-FR-04.5` | `policy`, `validation`, `backend/tests/ops/` | `G1` -> `G2` | `B2, D1` |
| `OPS 05` | Withdrawal (Pause/resume, purge 5m) | `SRS-FR-07.3`, `SRS-NFR-06` | `admin`, `validation`, `backend/tests/ops/` | `G2` | `C3, D2` |
| `OPS 06` | Availability (`99.5%` giờ dịch vụ) | `SRS-NFR-04` | `infra/`, `audit` | `G2` -> `G3` | `C3, D2` |
| `OPS 07` | Restore (`RTO 4h`, `RPO 24h`, replay) | `SRS-NFR-05` | `infra/`, `audit`, `backend/tests/ops/` | `G2` -> `G4` | `C3, D2` |
| `OPS 08` | Limits and exit (Cạn cap, export mở) | `SRS-FR-08.1`, `08.3` | `audit`, `backend/tests/ops/` | `G4` | `D2, B1` |

## 7. Vietnam Context (`VN 01 – VN 06`)

| Mã RFP | Yêu cầu | SRS Ref | Thành phần hệ thống | Gate | Phụ trách |
|---|---|---|---|---|---|
| `VN 01` | Language (Unicode, thiếu dấu, phủ định) | `SRS-FR-05.2`, `SRS-NFR-12` | `retrieval`, `answer`, `prompts/` | `G1–G2` | `B3, C1` |
| `VN 02` | Fixtures (`40/80` challenges hướng VN) | Mục `8.1` | `evaluation`, `data/eval/` | `G1` -> `G2` | `D1` |
| `VN 03` | Inputs (2 CSV, không connector/OCR/Zalo) | `SRS-FR-03.1`, Mục `2.2` | `data/templates/`, `ingestion` | `G0–G1` | `A2, B1` |
| `VN 04` | Owners (Chủ sở hữu & người thay thế) | Mục `3.1–3.2` | `docs/playbooks/team-playbook.md`, `policy` | `G0–G1` | `A2, A1` |
| `VN 05` | Governance (PDPL, AI, ANM trước dữ liệu thật) | `SRS-NFR-10` | Hồ sơ pháp lý Annex F | `G0` -> `G2` | `A1, C3` |
| `VN 06` | Value (Đo effort, so sánh 3 phương án) | `SRS-FR-01.3`, Mục `8.3` | Báo cáo pilot & TCO | `G0`, `G3` | `D2, A1` |

## 8. Deliverables (`DEL 01 – DEL 06`)

| Mã RFP | Sản phẩm bàn giao | SRS Ref | Hồ sơ đầu ra | Gate | Phụ trách |
|---|---|---|---|---|---|
| `DEL 01` | Design (Thiết kế) | Mục `8.3` | `docs/specs/srs.md`, `docs/architecture/erd-and-csv-contract.md`, `docs/specs/compliance-matrix.md`, baseline | `G0` | `A1, A2, D1` |
| `DEL 02` | Working core (Phần lõi hoạt động) | Mục `8.3` | `backend/`, `worker/`, `frontend/`, `prompts/` (O1 tách riêng nếu bật) | `G1–G2` | `Squad B, C` |
| `DEL 03` | Evidence (Bằng chứng nghiệm thu & Pilot) | Mục `8.1–8.3` | `evaluation`, báo cáo `100 Sealed` + `80 Challenges` + Pilot `20` ngày làm việc | `G2–G3` | `D1, A1` |
| `DEL 04` | Handover (Bàn giao) | Mục `8.3` | Code đặt hàng, mapping, config, fixtures hợp pháp, guides, exit playbook | `G4` | `D2, C2, B3` |
| `DEL 05` | Commercial response (TCO 3 năm) | Mục `8.3`, Phụ lục E | TCO 3 năm VND/VAT, bảng nhạy cảm hoàn vốn `<= 24` tháng | `G0`, `G3` | `D2, A1` |
| `DEL 06` | Operating terms (Điều khoản vận hành) | Mục `8.3` | SLA `99.5%`, hỗ trợ `08:00–17:00`, ACK 2h/cô lập 4h, subprocessor, exit | `G4` | `C3, A1, D2` |
