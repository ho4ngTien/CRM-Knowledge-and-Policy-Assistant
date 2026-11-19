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

## Kiến trúc Chuẩn hóa (`Modular Monolith + Deterministic Policy Gate + Constrained RAG`)

Hệ thống được thiết kế theo mô hình **5 tầng** bảo đảm kiểm soát chính sách xác định ngoài LLM prompt (*Policy Control Outside Prompt*) và fail-closed:

1. **Edge Gateway:** `Nginx` reverse proxy (`:80`, cấu hình tại `infra/nginx/nginx.conf`) định tuyến `/` và `/api/*`.
2. **Presentation:** `Next.js 14` / `TypeScript 5` (`:3000` — `/`, `/chat` Split-Screen Workspace, `/evidence`, `/referrals`, `/admin`).
3. **Application & Deterministic Policy Gate:** `FastAPI` Modular Monolith (`:8000 /api/v1/*`, `12` modules) — thực thi RBAC/audience, vòng đời chính sách, ngày hiệu lực múi giờ `Asia/Ho_Chi_Minh`, ma trận thẩm quyền `5` lớp và trường trọng yếu (`critical_fields`) bằng Python/SQL xác định; pipeline **Constrained RAG** giới hạn `<= 8` đoạn / `6.000` input tokens / `900` output tokens / `<= 2` LLM calls/package và chỉ trả `AnswerPackage` sau bước validation cuối.
4. **Async Worker & Scheduler:** `Celery Worker + Beat` (`5.4+`, `Asia/Ho_Chi_Minh`) xử lý batch CSV (`<= 500` dòng/lô), lập chỉ mục vector, kích hoạt chính sách `scheduled` theo phút, kiểm tra `Snapshot Age` theo giờ (`check_staleness`) và xóa cache thu hồi khẩn cấp (`<= 5` phút).
5. **Data & Cache:** `PostgreSQL 16` (`pgvector + unaccent + pg_trgm`) lưu dữ liệu quan hệ, tìm kiếm ngữ nghĩa và từ khóa/trigram tiếng Việt; `Redis 7` làm Celery broker/backend, cache và purge tức thời.

> Chi tiết sơ đồ luồng dữ liệu và hợp đồng module xem tại [docs/02-architecture.md](./docs/02-architecture.md) và [docs/03-database-and-contracts.md](./docs/03-database-and-contracts.md).

---

## Cấu trúc Dự án

```text
.
├── .github/workflows/ci.yml      # CI pipeline (ruff, mypy, pytest, compileall, CSV check, docs-link-check)
├── backend/                      # FastAPI Modular Monolith (12 modules, Alembic, mypy, pytest)
│   ├── migrations/               # Alembic database migrations
│   ├── src/modules/              # admin, answer, audit, evaluation, feedback, identity,
│   │                             # ingestion, knowledge, policy, referral, retrieval, validation
│   └── tests/                    # Unit, contract, eval/ & ops/ test suites
├── worker/                       # Celery Worker + Beat (import_task, index_task, eval_task)
├── frontend/src/app/             # Next.js 14 App Router (/, chat, evidence, referrals, admin)
├── data/                         # Hợp đồng 2 CSV UTF-8 (templates/), dữ liệu mẫu & eval/
├── infra/                        # PostgreSQL init.sql & Nginx reverse proxy config
├── prompts/                      # System prompt tiếng Việt có trích dẫn (answer_system_vi.txt)
├── docs/                         # Trung tâm tài liệu chuẩn hóa 6 tệp (xem docs/README.md)
│   ├── README.md                 # Mục lục điều hướng tài liệu
│   ├── 01-overview.md            # Tổng quan nghiệp vụ, Base Scope (M) & ranh giới O / O1
│   ├── 02-architecture.md        # Kiến trúc 5 tầng, 12 module, Celery Worker + Beat & RAG Gate
│   ├── 03-database-and-contracts.md  # ERD, PostgreSQL/pgvector & hợp đồng 2 CSV UTF-8
│   ├── 04-setup-and-operations.md    # Cài đặt, vận hành, kiểm thử 4 tầng & OPS 01–08
│   └── 05-roadmap-and-team.md    # Lộ trình 5 Gate (G0–G4), 10 vai RFP & quy tắc Dual-Hat
├── .env.example                  # Biến môi trường mẫu (Base Scope M)
├── docker-compose.yml            # db, redis + các service ứng dụng dưới profile app
├── dev.ps1 & Makefile            # Script thao tác nhanh cho local dev, lint, mypy, pytest, migrate
└── README.md
```

---

## Quick Start

### 1. Chuẩn bị môi trường
```bash
cp .env.example .env
```

### 2. Khởi chạy hạ tầng bằng Docker Compose / PowerShell / Make
```powershell
# Chỉ bật PostgreSQL (pgvector + unaccent + pg_trgm) và Redis cho dev local
.\dev.ps1 dev-db        # hoặc: make dev-db

# Chạy toàn bộ stack ứng dụng (backend, worker, beat, frontend, nginx, db, redis) qua --profile app
.\dev.ps1 up            # hoặc: make up / docker compose --profile app up --build -d

# Dừng stack
docker compose --profile app down   # hoặc: .\dev.ps1 down / make down
```
*(Các target chi tiết cho local dev/migrate xem tại [dev.ps1](./dev.ps1), [Makefile](./Makefile) và [docs/04-setup-and-operations.md](./docs/04-setup-and-operations.md)).*

### 3. Kiểm tra Lint, Typecheck (`mypy`), CSV & Test (`pytest`)
```powershell
.\dev.ps1 lint          # ruff check . + mypy src (backend) + compileall (worker/src)
.\dev.ps1 check-csv     # kiểm tra header 2 tệp CSV UTF-8 (21 & 23 cột)
.\dev.ps1 test          # pytest -q (backend)
make lint               # chạy ruff + mypy + compileall + lint frontend
make test               # chạy pytest -q + build frontend
```
Hoặc chạy trực tiếp trong `backend/`:
```bash
cd backend
python -m ruff check .
python -m mypy src
python -m pytest -q
```

---

## Tài liệu Dự án (`docs/`)

Toàn bộ tài liệu được hợp nhất gọn trong `6` tệp tại thư mục `docs/` — xem mục lục đầy đủ tại [docs/README.md](./docs/README.md):

| Tài liệu | Nội dung chính |
|---|---|
| [docs/01-overview.md](./docs/01-overview.md) | Mục tiêu nghiệp vụ, phạm vi Base Scope (`M`), ranh giới ngoài phạm vi (`O`) & tách riêng `O1` |
| [docs/02-architecture.md](./docs/02-architecture.md) | Kiến trúc 5 tầng (`Modular Monolith + Deterministic Policy Gate + Constrained RAG`), `12` module, `Celery Worker + Beat` |
| [docs/03-database-and-contracts.md](./docs/03-database-and-contracts.md) | Thiết kế CSDL (`PostgreSQL 16 + pgvector + unaccent + pg_trgm`), vòng đời chính sách & hợp đồng 2 CSV UTF-8 |
| [docs/04-setup-and-operations.md](./docs/04-setup-and-operations.md) | Hướng dẫn cài đặt, chạy `--profile app`, kiểm thử 4 tầng (`Dev/Val/100 Sealed` + `80 Challenges`), `OPS 01–08` & bàn giao |
| [docs/05-roadmap-and-team.md](./docs/05-roadmap-and-team.md) | Lộ trình `5` Release Gate (`G0–G4`), `10` vai trò chuẩn RFP (`P1–P5`, `S1–S5`), quy tắc **Dual-Hat** & hàng rào Chinese Wall |

---

## Tổ chức Đội 10 người (Chuẩn RFP Mục 11), Quy tắc Dual-Hat & 5 Release Gates

- **Phía Purchaser (`P1–P5`):** `P1` Mỹ Vân (*Purchaser sponsor*) · `P2` Hữu Tài (*Policy owners*) · `P3` Chí Kha (*Knowledge and data steward*) · `P4` Trà My (*Staff users*) · `P5` Anh Khoa (*Privacy and security owners*).
- **Phía Supplier Team (`S1–S5`):** `S1` Hoàng Tiến (*Named lead*) · `S2` Quốc Hưng (*Integration engineer*) · `S3` Yến Nhi (*Retrieval and application engineer*) · `S4` Quý Hải (*Quality lead — đánh giá độc lập*) · `S5` Ngọc Duy (*Operations specialist*).
- **Quy tắc vận hành Dual-Hat (Kiêm nhiệm có kiểm soát — RFP Mục 2 & Mục 11):** Cho phép kiêm nhiệm vai trò khi cần tối ưu nhân lực **nhưng bắt buộc bảo toàn trách nhiệm giải trình và hàng rào độc lập (Chinese Wall)**: `S4` (*Quality lead*) tuyệt đối không tham gia viết code hay tinh chỉnh hệ thống như đội Build (`S2, S3, S5`); nhóm `S2, S3, S5` bị cấm xem/truy cập tập `100 Sealed` và không đóng vai `Staff user` trong Pilot (`G3`); quyền sở hữu và phê duyệt nội dung chính sách luôn thuộc `P2` phía SongNhat.
- **5 Release Gates (`G0–G4`):** `G0 Ready to Build` → `G1 Controlled Offline` → `G2 Supervised Use` → `G3 Pilot Acceptance` → `G4 Production Handover`. Chi tiết lịch trình và điều kiện thoát Gate xem [docs/05-roadmap-and-team.md](./docs/05-roadmap-and-team.md).
