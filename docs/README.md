# Trung tâm Tài liệu Dự án (`docs/`)

Toàn bộ tài liệu kỹ thuật, đặc tả yêu cầu, kiến trúc và quy trình phối hợp của **SongNhat CRM Knowledge & Policy Assistant** được phân nhóm thành `4` thư mục theo phạm vi **Base Scope (`M`)** trong RFP.

## Cấu trúc Thư mục Tài liệu

### 1. [`specs/`](./specs/) — Đặc tả Yêu cầu, Lộ trình & Tuân thủ
| Tài liệu | Mô tả |
|---|---|
| [srs.md](./specs/srs.md) | Đặc tả Yêu cầu Phần mềm (SRS) cho đội `10` người, giới hạn chặt trong Base Scope (`M`). |
| [roadmap.md](./specs/roadmap.md) | Lộ trình triển khai `5` Release Gate (`G0–G4`) và cơ chế cuốn chiếu Jira Sprint. |
| [compliance-matrix.md](./specs/compliance-matrix.md) | Ma trận truy vết `57` mã yêu cầu RFP (`WP`, `MOD`, `DAT`, `EVL`, `OPS`, `SEC`, `VN`, `DEL`). |

### 2. [`architecture/`](./architecture/) — Kiến trúc, Dữ liệu & Kiểm thử
| Tài liệu | Mô tả |
|---|---|
| [overview.md](./architecture/overview.md) | Kiến trúc tổng thể Modular Monolith (`FastAPI` + `Celery` + `Next.js` + `PostgreSQL/pgvector` + `Redis` + `Nginx`). |
| [backend-modules.md](./architecture/backend-modules.md) | Trách nhiệm, hợp đồng dữ liệu và phụ thuộc của `12` module Backend và `3` Worker task. |
| [business-workflows.md](./architecture/business-workflows.md) | Các luồng nghiệp vụ lõi: hỏi đáp có trích dẫn, nhập liệu CSV, chuyển tiếp chủ sở hữu, audit. |
| [policy-lifecycle.md](./architecture/policy-lifecycle.md) | Trạng thái chính sách (`draft` → `reviewed` → `active` → `superseded` / `retired`) và kiểm tra hiệu lực. |
| [erd-and-csv-contract.md](./architecture/erd-and-csv-contract.md) | Mô hình dữ liệu PostgreSQL/pgvector & chuẩn `2` tệp CSV UTF-8 (`21` cột passages / `23` cột critical fields). |
| [testing-tiers.md](./architecture/testing-tiers.md) | Phân tầng kiểm thử (Unit, Integration, Eval `Dev/Val/Sealed`, Ops/Drill). |

### 3. [`playbooks/`](./playbooks/) — Quy trình Phối hợp Đội 10 người
| Tài liệu | Mô tả |
|---|---|
| [team-playbook.md](./playbooks/team-playbook.md) | Tổ chức `4` Squad (`A–D`, `A1–D2`), phân công sở hữu module và RACI. |
| [jira-playbook.md](./playbooks/jira-playbook.md) | Quy trình tạo, cập nhật trạng thái và đóng Ticket Jira theo Gate. |
| [git-playbook.md](./playbooks/git-playbook.md) | Quy ước nhánh (`<type>/<ISSUE-KEY>-<summary-slug>`), commit và bảo vệ `main`/`develop`. |
| [jira-git-workflow.md](./playbooks/jira-git-workflow.md) | Hướng dẫn nhanh (cheat sheet) nhận task Jira → tạo nhánh → lint/test → mở PR. |
| [rules.md](./playbooks/rules.md) | Nội quy nhóm & kỷ luật triển khai. |
| [weekly-report.md](./playbooks/weekly-report.md) | Mẫu báo cáo tiến độ tuần và rà soát rủi ro Gate. |
| [pm-schedule-tien.md](./playbooks/pm-schedule-tien.md) | Lịch làm việc 10 tuần (T3–T12) của PM Hoàng Tiến (A1), mốc họp chốt Gate và quyết định Pilot 20 ngày. |

### 4. [`work-packages/`](./work-packages/) — Backlog Chuẩn Import Jira
| Tài liệu | Mô tả |
|---|---|
| [README.md](./work-packages/README.md) | Hướng dẫn import CSV vào Jira và ánh xạ `10` vai trò (`A1–D2`). |
| [05-jira-5gates-import.csv](./work-packages/05-jira-5gates-import.csv) | Tệp import Jira `5` Gate (`62` dòng: `5` Epics, `10` Stories, `47` Tasks; phủ `57/57` mã RFP). |

---

## Thứ tự đọc nhanh khi Onboarding

1. **Tất cả thành viên (`A1–D2`):** [srs.md](./specs/srs.md) → [roadmap.md](./specs/roadmap.md) → [team-playbook.md](./playbooks/team-playbook.md) → [rules.md](./playbooks/rules.md) → [jira-git-workflow.md](./playbooks/jira-git-workflow.md).
2. **Backend & Dữ liệu (`B1, B2, C1`):** [overview.md](./architecture/overview.md) → [backend-modules.md](./architecture/backend-modules.md) → [erd-and-csv-contract.md](./architecture/erd-and-csv-contract.md) → [policy-lifecycle.md](./architecture/policy-lifecycle.md).
3. **AI/Prompt & Frontend (`C2, C3`):** [business-workflows.md](./architecture/business-workflows.md) → [backend-modules.md](./architecture/backend-modules.md) → [testing-tiers.md](./architecture/testing-tiers.md).
4. **QA, Eval & Ops (`D1, D2`) + PM/BA (`A1, A2`):** [compliance-matrix.md](./specs/compliance-matrix.md) → [testing-tiers.md](./architecture/testing-tiers.md) → [work-packages/README.md](./work-packages/README.md).
