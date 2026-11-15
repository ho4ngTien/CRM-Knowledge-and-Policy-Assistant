# SongNhat CRM Knowledge & Policy Assistant

![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Next.js 14](https://img.shields.io/badge/Next.js-14-000000?logo=next.js&logoColor=white)
![TypeScript 5](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-Vector%20Search-3B6C8E)
![Redis 7](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Celery 5.4+](https://img.shields.io/badge/Celery-5.4%2B-37814A?logo=celery&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

Trợ lý tri thức và chính sách CRM nội bộ cho nhân viên được ủy quyền — hỗ trợ tra cứu quy trình bằng tiếng Việt có trích dẫn điều khoản gốc, kiểm tra phạm vi/ngày hiệu lực/trạng thái phiên bản, xuất các trường dữ liệu quan trọng có cấu trúc (`Critical Fields`), phát hiện thiếu dữ kiện hoặc mâu thuẫn để chuyển tiếp đúng chủ sở hữu chính sách (`Owner Referral`).

> **Phạm vi triển khai:** Chỉ giới hạn trong **Base Scope (`M`)** theo RFP — cung cấp hướng dẫn nội bộ có căn cứ, không thay thế thẩm quyền phê duyệt, không tự thực thi nghiệp vụ trên hệ thống bên ngoài và không kích hoạt các phần mở rộng (`O1`).

---

## Cấu trúc Dự án

```text
.
├── .github/workflows/ci.yml      # CI pipeline (ruff, pytest, compileall, kiểm tra CSV & frontend)
├── backend/                      # FastAPI Modular Monolith (12 modules, Alembic, pytest)
│   ├── migrations/               # Alembic database migrations
│   ├── src/modules/              # admin, answer, audit, evaluation, feedback, identity,
│   │                             # ingestion, knowledge, policy, referral, retrieval, validation
│   └── tests/                    # Unit, contract, eval & ops test suites
├── worker/src/tasks/             # Celery tasks (import_task, index_task, eval_task)
├── frontend/src/app/             # Next.js 14 App Router (chat, evidence, referrals, admin)
├── data/                         # Hợp đồng mẫu 2 CSV UTF-8, dữ liệu mẫu & eval README
├── infra/                        # PostgreSQL init.sql & Nginx reverse proxy config
├── prompts/                      # Prompt trả lời tiếng Việt có trích dẫn (answer_system_vi.txt)
├── docs/                         # Trung tâm tài liệu (xem docs/README.md)
│   ├── specs/                    # SRS, Roadmap 5 Gate, Compliance Matrix (57 mã RFP)
│   ├── architecture/             # Overview, Modules, Workflows, Policy Lifecycle, ERD/CSV, Testing
│   ├── playbooks/                # Team, Jira, Git, Cheat Sheet, Rules, Weekly Report
│   └── work-packages/            # Backlog Jira 5 Gate CSV (62 dòng) & hướng dẫn import
├── .env.example                  # Biến môi trường mẫu (Base Scope M)
├── docker-compose.yml            # PostgreSQL/pgvector, Redis, Backend, Worker, Frontend, Nginx
├── dev.ps1 & Makefile            # Script thao tác nhanh cho local dev, lint, test, migrate
└── README.md
```

---

## Quick Start

### 1. Chuẩn bị môi trường
```bash
cp .env.example .env
```

### 2. Khởi chạy hạ tầng bằng Docker Compose / PowerShell
```powershell
# Chỉ bật DB (PostgreSQL + pgvector) và Redis cho dev local
.\dev.ps1 dev-db

# Hoặc chạy toàn bộ stack qua Docker Compose (--profile app)
.\dev.ps1 up
# Dừng stack
.\dev.ps1 down
```
*(Hoặc chạy trực tiếp `docker compose --profile app up --build -d` / dùng các target tương ứng trong [Makefile](./Makefile)).*

### 3. Kiểm tra Lint & Test
```powershell
.\dev.ps1 lint
.\dev.ps1 test
```
Hoặc chạy trực tiếp trong `backend/`:
```bash
cd backend
python -m ruff check .
python -m pytest -v
```

---

## Tài liệu Dự án (`docs/`)

Toàn bộ tài liệu được sắp xếp gọn theo 4 nhóm — xem mục lục đầy đủ tại [docs/README.md](./docs/README.md):

| Nhóm | Tài liệu trọng tâm |
|---|---|
| **Đặc tả & Lộ trình** | [SRS Đội 10 người](./docs/specs/srs.md) · [Roadmap 5 Gate](./docs/specs/roadmap.md) · [Ma trận 57 mã RFP](./docs/specs/compliance-matrix.md) |
| **Kiến trúc & Dữ liệu** | [Tổng quan Kiến trúc](./docs/architecture/overview.md) · [12 Module Backend/Worker](./docs/architecture/backend-modules.md) · [ERD & 2 CSV UTF-8](./docs/architecture/erd-and-csv-contract.md) · [Kiểm thử Độc lập](./docs/architecture/testing-tiers.md) |
| **Quy trình Nhóm** | [Playbook Nhóm](./docs/playbooks/team-playbook.md) · [Jira–Git Cheat Sheet](./docs/playbooks/jira-git-workflow.md) · [Nội quy Nhóm](./docs/playbooks/rules.md) |
| **Backlog Jira** | [CSV Import Jira 5 Gate (62 dòng)](./docs/work-packages/05-jira-5gates-import.csv) · [Hướng dẫn Import](./docs/work-packages/README.md) |

---

## Tổ chức Đội 10 người & Lộ trình 5 Release Gate

- **4 Squad (`A1–D2`):** Squad A (`A1` Tech Lead/BE, `A2` BA/Steward) · Squad B (`B1` Data/Postgres, `B2` Ingestion/ETL) · Squad C (`C1` Retrieval/Answer, `C2` AI/Prompt, `C3` Frontend Next.js) · Squad D (`D1` QA/Eval, `D2` DevOps/SRE). Chi tiết tại [team-playbook.md](./docs/playbooks/team-playbook.md).
- **5 Gate (`G0–G4`):** `G0 Ready to Build` → `G1 Ingestion & Data Ready` → `G2 Grounded Q&A & Structured Output` → `G3 Pilot Readiness` → `G4 Production Handover`. Chi tiết lịch trình và điều kiện thoát Gate xem [roadmap.md](./docs/specs/roadmap.md).
