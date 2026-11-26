# Trung tâm Tài liệu Dự án — SongNhat CRM Knowledge & Policy Assistant (CKPA)

> Bộ tài liệu kỹ thuật, kiến trúc, hợp đồng dữ liệu, vận hành và phối hợp đội ngũ cho hệ thống **SongNhat CRM Knowledge & Policy Assistant (CKPA)** theo định hướng **Modular Monolith + Deterministic Policy Gate + Constrained RAG**, giới hạn chặt chẽ trong **Base Scope (`M`)** của RFP.

---

## 1. Danh mục 5 Tài liệu Cốt lõi

| Tài liệu | Chủ đề trọng tâm | Đối tượng ưu tiên |
|---|---|---|
| [01-overview.md](./01-overview.md) | Tổng quan dự án, mục tiêu, phạm vi `Base Scope (M)` vs `O1`/`O`, tham số **Common Bid Basis**, `10` điều cấm ngoài phạm vi và tóm tắt đội ngũ `10` người (`P1–P5`, `S1–S5`). | Toàn bộ `10` thành viên |
| [02-architecture.md](./02-architecture.md) | Kiến trúc **Modular Monolith + Deterministic Policy Gate + Constrained RAG**, `6` Bất biến (`INV-01..06`), Pipeline `5` tầng ánh xạ tới `shared/contracts.py`, `12` module Backend + `3` Worker tasks + `5` Frontend routes, `3` Sequence Diagrams (gồm *Worked Case 9*), vòng đời `7+2` trạng thái, `5` ADRs và **phân tách 4 không gian Repo/Môi trường theo RFP**. | `S1`, `S2`, `S3`, `S4`, `S5`, `P2`, `P5` |
| [03-database-and-contracts.md](./03-database-and-contracts.md) | PostgreSQL 16 (`pgvector`, `unaccent`, `pg_trgm`), `erDiagram` `23` bảng ORM & chiến lược index, hợp đồng `2` CSV UTF-8 (`21` & `23` cột), `12` nhóm API `/api/v1/*`, mã lỗi Fail-Closed, JSON `AnswerPackage` `7` phần và hợp đồng `shared/contracts.py`. | `S2`, `S3`, `S5`, `P3`, `S4` |
| [04-setup-and-operations.md](./04-setup-and-operations.md) | Hướng dẫn cài đặt Local (`dev.ps1`, `Makefile`, `docker compose --profile app`), Celery Beat & Cache Purge `<= 300s`, kiểm thử `4` tầng (`60/40/100 Sealed` + `80 Challenges` + `OPS 01–08` với `p95 <= 25s`), Backup/Restore Replay (`35` ngày, `RTO 4h / RPO 24h`), Open Exit (`OPS 08`), Incident Runbook/SLA và Checklist Pháp lý Phụ lục F. | `S5`, `S4`, `P5`, `P3`, `P4`, `S1` |
| [05-roadmap-and-team.md](./05-roadmap-and-team.md) | Lộ trình `5` Release Gates (`G0–G4` trên `12` tuần, không gộp G3 & G4), Ma trận **Dual-Hat** cho `10` người, quy chuẩn Git/Branch/PR, Jira & Rolling Dispatch (`1–2` task/người), nội quy `R01–R10`, cơ chế kỷ luật (`1 sẹo = -2%`, `5 sẹo = -20%`) và họp bi-daily. | Toàn bộ `10` thành viên |

---

## 2. Đặc tả Kỹ thuật G0, Ma trận Tuân thủ & Gói Công việc

| Thư mục / Tài liệu | Nội dung chuẩn hóa trong Build Repo |
|---|---|
| [rfp-compliance-matrix.md](./rfp-compliance-matrix.md) | Ma trận đánh giá tuân thủ RFP & truy vết Jira theo 5 cổng nghiệm thu (`G0–G4`) và từng nhóm yêu cầu (`DAT`, `ANS`, `KNW`, `SEC`, `OPS`, `DEL`). |
| [architecture/rbac-matrix.md](./architecture/rbac-matrix.md) | Hợp đồng API `/api/v1/*`, cấu trúc `AnswerPackage` 7 phần, ma trận RBAC 8 vai trò và cấu hình LLM khóa cứng tại Gate G0. |
| [frontend-arch.md](./frontend-arch.md) | Kiến trúc Frontend Web App mục tiêu (Next.js App Router, phân tầng `core`/`adapters`/`components`, Responsive Web/PWA) tuân thủ `INV-01..06` và Base Scope (`M`). |
| [`specs/g0/`](./specs/g0/) | Bộ **20 tệp đặc tả kỹ thuật G0** đồng bộ từ Jira, chia làm 4 nhóm:<br>- [`specs/g0/policy-and-scope/`](./specs/g0/policy-and-scope/) (`CKPA-09`: 3 họ chính sách, Authority Matrix 5 lớp, ngày hiệu lực, conflict hold, ranh giới O1)<br>- [`specs/g0/rbac-and-legal/`](./specs/g0/rbac-and-legal/) (`CKPA-17`, `CKPA-34`: RBAC 20 users / 5 concurrent, checklist pháp lý/AI Phụ lục F & Phụ lục C)<br>- [`specs/g0/architecture-and-contracts/`](./specs/g0/architecture-and-contracts/) (`CKPA-21`, `CKPA-29`: chính sách ngoài prompt, hard caps Mục 2, Evidence Workspace & 9 hợp đồng Phụ lục B)<br>- [`specs/g0/qa-and-operations/`](./specs/g0/qa-and-operations/) (`CKPA-30`, `CKPA-33`, `CKPA-35`: kế hoạch nghiệm thu 280 ca, phân loại lỗi HOLD, benchmark & SLA `OPS 01–08`, ma trận testability) |
| [`work-packages/`](./work-packages/) | Báo cáo kiểm toán và tổng kết gói công việc trong Build repo (gồm [ckpa-56-sprint3-review-retro.md](./work-packages/ckpa-56-sprint3-review-retro.md), [ckpa-67-68-ban-giao-dev-val-va-niem-phong-sealed-report.md](./work-packages/ckpa-67-68-ban-giao-dev-val-va-niem-phong-sealed-report.md), [ckpa-74-release-v0.2.0-g1-offline.md](./work-packages/ckpa-74-release-v0.2.0-g1-offline.md), [ckpa-80-del03-g1-evidence-and-g2-plan.md](./work-packages/ckpa-80-del03-g1-evidence-and-g2-plan.md)). |

> **Lưu ý phân tách 4 không gian lưu trữ & 3 kho Git theo RFP:** Xem chi tiết phân quyền và ranh giới giữa `main-app-repo` (Public), kho Private bàn giao Dev/Val `ckpa-dev-val-eval` và kho niêm phong `sealed-eval-repo` trực thuộc tổ chức GitHub [ckpa-dev-val-eval](https://github.com/ckpa-dev-val-eval) (Chinese Wall Mục 8/11), môi trường `Test/Prod` (`SEC 06`) và kho Quản trị/Thương mại ngoài Git (`DEL 05`, Mục 13–14) tại [02-architecture.md — Mục 8](./02-architecture.md#8-phân-tách-kho-mã-nguồn-repos-môi-trường--không-gian-lưu-trữ-theo-rfp).

---

## 3. Lộ trình Đọc theo Vai trò (`P1–P5` & `S1–S5`)

| Nhóm vai trò (RFP Mục 11) | Thành viên | Lộ trình đọc khuyến nghị | Điểm cần lưu ý bắt buộc |
|---|---|---|---|
| **Sponsor & Điều phối Nhà cung cấp** | `P1` Mỹ Vân, `S1` Hoàng Tiến | [01-overview.md](./01-overview.md) → [05-roadmap-and-team.md](./05-roadmap-and-team.md) → [04-setup-and-operations.md](./04-setup-and-operations.md) | Không gộp Gate `G3` và `G4`; tách nghiệm thu Pilot với quyết định đầu tư mở rộng (`<= 24` tháng payback); khóa chặt `Base Scope (M)`. |
| **Chủ sở hữu Chính sách, Tri thức & Người dùng đại diện** | `P2` Hữu Tài, `P3` Chí Kha, `P4` Trà My | [01-overview.md](./01-overview.md) → [03-database-and-contracts.md](./03-database-and-contracts.md) (Mục CSV & `AnswerPackage`) → [04-setup-and-operations.md](./04-setup-and-operations.md) → [05-roadmap-and-team.md](./05-roadmap-and-team.md) | Duyệt `3` họ chính sách, Authority Matrix, `2` tệp CSV UTF-8; phân tách `Two policy reviewers` (`P2` + `P3`/`P5`) và `Five representative users` (ngoài đội Build). |
| **Kỹ sư Build (Tích hợp, Truy xuất & Ứng dụng)** | `S2` Quốc Hưng, `S3` Yến Nhi | [01-overview.md](./01-overview.md) → [02-architecture.md](./02-architecture.md) → [03-database-and-contracts.md](./03-database-and-contracts.md) → [04-setup-and-operations.md](./04-setup-and-operations.md) → [05-roadmap-and-team.md](./05-roadmap-and-team.md) | Thực thi `6` bất biến `INV-01..06` ngoài prompt; **tuyệt đối cấm xem `100 Sealed`** hay tham gia làm đại diện Staff User thử nghiệm. |
| **Vận hành Hạ tầng & Bảo mật / Pháp lý** | `S5` Ngọc Duy, `P5` Anh Khoa | [01-overview.md](./01-overview.md) → [02-architecture.md](./02-architecture.md) → [04-setup-and-operations.md](./04-setup-and-operations.md) → [03-database-and-contracts.md](./03-database-and-contracts.md) → [05-roadmap-and-team.md](./05-roadmap-and-team.md) | Bảo đảm Fail-Closed, RBAC `SEC 01`, xóa cache `<= 5` phút, Restore Replay (`OPS 07`), thông báo sự cố `<= 4h` (`SEC 07`) và rà soát Phụ lục F trước G2. |
| **Chất lượng & Kiểm định Độc lập** | `S4` Quý Hải | [01-overview.md](./01-overview.md) → [04-setup-and-operations.md](./04-setup-and-operations.md) → [02-architecture.md](./02-architecture.md) → [03-database-and-contracts.md](./03-database-and-contracts.md) → [05-roadmap-and-team.md](./05-roadmap-and-team.md) | Giữ **độc lập tuyệt đối**: không viết code hoặc tinh chỉnh prompt/retrieval cùng `S2`, `S3`, `S5`; quản lý niêm phong tập `100 Sealed` & `80 Challenges`. |

---

## 4. Thứ tự Ưu tiên Tài liệu & Liên kết Kỹ thuật trong Repository

### Thứ tự ưu tiên khi giải quyết mâu thuẫn (Document Precedence)
1. Hợp đồng đã ký và các phụ lục sửa đổi có hiệu lực.
2. Hồ sơ mời thầu RFP (*SongNhat CRM Knowledge and Policy Assistant RFP*) và các văn bản bổ sung đã phát hành.
3. Đề xuất kỹ thuật – thương mại được chấp thuận.
4. Bộ tài liệu dự án trong `docs/` này.

### Liên kết nhanh tới Mã nguồn & Hạ tầng Hiện hữu
- Tổng quan repo & lệnh nhanh: [README.md](../README.md), [dev.ps1](../dev.ps1), [Makefile](../Makefile), [docker-compose.yml](../docker-compose.yml), [.env.example](../.env.example).
- Backend API & cấu hình chuẩn Base Scope: [backend/src/main.py](../backend/src/main.py), [backend/src/config.py](../backend/src/config.py), [backend/src/shared/contracts.py](../backend/src/shared/contracts.py), [backend/src/shared/enums.py](../backend/src/shared/enums.py), [backend/src/shared/exceptions.py](../backend/src/shared/exceptions.py), [backend/src/shared/auth.py](../backend/src/shared/auth.py), [backend/src/shared/pii_guard.py](../backend/src/shared/pii_guard.py).
- Bộ kiểm thử hợp đồng kiến trúc & Base Scope: [backend/tests/test_srs_scaffold_contracts.py](../backend/tests/test_srs_scaffold_contracts.py), [backend/tests/test_architecture_contracts.py](../backend/tests/test_architecture_contracts.py).
- Hợp đồng JSON gói trả lời: [backend/src/modules/answer/schemas.py](../backend/src/modules/answer/schemas.py) & [frontend/src/types/answer.ts](../frontend/src/types/answer.ts).
- Worker & Scheduled Jobs: [worker/src/celery_app.py](../worker/src/celery_app.py), [worker/src/tasks/import_task.py](../worker/src/tasks/import_task.py), [worker/src/tasks/index_task.py](../worker/src/tasks/index_task.py), [worker/src/tasks/eval_task.py](../worker/src/tasks/eval_task.py).
- Prompt tiếng Việt & Ranh giới dữ liệu không tin cậy: [prompts/answer_system_vi.txt](../prompts/answer_system_vi.txt), [prompts/README.md](../prompts/README.md).
- Mẫu CSV UTF-8 & Đánh giá: [data/templates/passages_template.csv](../data/templates/passages_template.csv), [data/templates/critical_fields_template.csv](../data/templates/critical_fields_template.csv), [data/eval/README.md](../data/eval/README.md).
- Hạ tầng DB, Nginx & CI: [infra/db/init.sql](../infra/db/init.sql), [infra/nginx/nginx.conf](../infra/nginx/nginx.conf), [.github/workflows/ci.yml](../.github/workflows/ci.yml).
