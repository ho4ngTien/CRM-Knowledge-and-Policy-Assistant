# Sơ đồ Module Backend & Worker — SongNhat CKPA

> Kiến trúc **Modular Monolith** trên `backend/src/` (`FastAPI / Python 3.12+`) kết hợp `worker/src/` (`Celery 5.4+`, múi giờ `Asia/Ho_Chi_Minh`).
> Tham chiếu chuẩn: [SRS](../specs/srs.md) (Mục 4.3 & Mục 7.2).

---

## 1. Sơ đồ phụ thuộc giữa 12 Module, Shared Core & 3 Worker Tasks

```mermaid
flowchart LR
    subgraph sg_entry ["API Entrypoint & Shared Core (backend/src)"]
        MAIN["main.py (/api/v1/* + Exception Handlers + /health)"]
        SHARED["shared/ (auth.py, enums.py, exceptions.py, pii_guard.py) + config.py, db.py"]
        PROMPTS["prompts/ (answer_system_vi.txt - Untrusted Data Isolation)"]
    end

    subgraph sg_sec ["Nhóm Bảo mật & Nhập liệu"]
        MOD_ID["identity - JWT, Org Roles, Least Privilege & Audience"]
        MOD_ING["ingestion - 2 CSV Validators, Quarantine, Manifest (Base Scope Only)"]
        MOD_KNW["knowledge - Docs, Versions, Passages, Tombstone, Snapshot Age"]
    end

    subgraph sg_core ["Nhóm Chính sách & Truy xuất"]
        MOD_POL["policy - Lifecycle (7 states), Authority Matrix, VN Date, Critical Fields"]
        MOD_RET["retrieval - Pre-filtered pgvector + FTS unaccent + CRM Dict"]
    end

    subgraph sg_ai ["Nhóm Điều phối Trả lời & Kiểm chứng"]
        MOD_ANS["answer - Orchestrator (Max 2 LLM Calls, 6000/900 Tokens, 7-Part Pkg)"]
        MOD_VAL["validation - Citation, Critical Fields, Final State Check (No Stream)"]
        MOD_REF["referral - Local Escalation (referred/owner_responded/closed)"]
    end

    subgraph sg_gov ["Nhóm Quản trị, Kiểm toán & Đánh giá"]
        MOD_ADM["admin - Lifecycle Approval, Instant Withdrawal (<=5m), Emergency Disable"]
        MOD_FBK["feedback - 5 Reasons (KNW 07), Unanswered Topics, Candidate Queue"]
        MOD_AUD["audit - Restricted Audit Log, Full Cost Meter, OPS 08 Open Export"]
        MOD_EVL["evaluation - Partition Wall (60/40/100 Sealed + 80 Challenges)"]
    end

    subgraph sg_wrk ["Background Tasks (worker/src/tasks - Asia/Ho_Chi_Minh)"]
        W_IMP["import_task.py - run_batch_import & check_staleness"]
        W_IDX["index_task.py - index_passages, activate_scheduled_policies, withdraw_and_purge_cache"]
        W_EVL["eval_task.py - run_evaluation"]
    end

    MAIN --> SHARED
    MAIN --> MOD_ID
    MAIN --> MOD_ING
    MAIN --> MOD_KNW
    MAIN --> MOD_POL
    MAIN --> MOD_RET
    MAIN --> MOD_ANS
    MAIN --> MOD_VAL
    MAIN --> MOD_REF
    MAIN --> MOD_ADM
    MAIN --> MOD_FBK
    MAIN --> MOD_AUD
    MAIN --> MOD_EVL

    MOD_ING --> MOD_KNW
    MOD_ING --> MOD_POL
    MOD_ING --> W_IMP

    MOD_POL --> W_IDX
    MOD_ADM --> MOD_POL
    MOD_ADM --> MOD_ID
    MOD_ADM --> W_IDX

    MOD_ANS --> MOD_ID
    MOD_ANS --> MOD_POL
    MOD_ANS --> MOD_RET
    MOD_ANS --> MOD_VAL
    MOD_ANS --> MOD_REF
    MOD_ANS --> MOD_AUD
    MOD_ANS --> PROMPTS

    MOD_VAL --> MOD_POL
    MOD_VAL --> MOD_KNW
    MOD_FBK --> MOD_KNW
    MOD_EVL --> W_EVL
    W_EVL --> MOD_ANS
```

---

## 2. Cấu trúc chuẩn mỗi Module & Quy ước ranh giới

Mỗi thư mục dưới `backend/src/modules/<module>/` tuân theo chuẩn 4 file để tách biệt giao thức HTTP với nghiệp vụ cốt lõi:
- `router.py`: Tiếp nhận HTTP request, kiểm tra quyền qua `get_current_user` / `require_roles` từ `shared/auth.py`.
- `schemas.py`: Pydantic v2 input/output contracts khớp [SRS](../specs/srs.md) và [erd-and-csv-contract.md](./erd-and-csv-contract.md).
- `service.py`: Nghiệp vụ thuần (Applicability, Critical Fields, Quarantine, Validation, Orchestration, Cost Metering).
- `models.py`: SQLAlchemy 2.0 async ORM mapping xuống PostgreSQL 16 + `pgvector`.

---

## 3. Ranh giới an toàn giữa các nhóm Module
- **Tách quyền đánh giá (`evaluation` vs `answer/retrieval`):** Endpoint `evaluation` chỉ định danh vai trò `independent_evaluator` / `administrator` được phân quyền đọc tập `sealed_100`.
- **Tách dữ liệu ứng viên (`feedback` vs `policy`):** `feedback` chỉ tạo bản ghi `feedback_candidate`; mọi chuyển đổi thành `draft → effective` phải đi qua `policy` + `admin` có phê duyệt của `policy_owner`.
- **Ranh giới Base Scope (`M`):** Toàn bộ codebase chỉ phục vụ `2` nguồn CSV cơ sở (`passages`, `critical_fields`); không chứa endpoint hay schema nhập hồ sơ khách hàng / `O1`.
