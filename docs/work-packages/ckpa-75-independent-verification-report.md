# Báo cáo kiểm định CKPA-75 — G1

**Cập nhật:** 2026-11-25
**Base:** `bac9b1d54fca58301bbb46b17eeb18737bf9bf37` (`origin/develop`)
**Kết luận:** `NEEDS_SIGNOFF` — chưa phải nghiệm thu release/S4 độc lập.

## Phạm vi xử lý

- `OPS 03`: thiếu ngày chi phối không còn được tự suy diễn từ ngày hệ thống để cho phép xử lý. `PolicyService` trả `can_proceed=False`; `SelectionService` phát Hold `DAT04_NO_GOVERNING_DATE`.
- `DAT 08` / `OPS 03`: trường `NUMBER` và `DURATION` thiếu `unit`, hoặc `CURRENCY` thiếu `currency`, phát Hold.
- Cập nhật các ca happy-path hiện hữu để truyền ngày chi phối tường minh.
- Bổ sung 12 test CKPA-75, bao gồm benchmark 500 dòng/LKG, phân quyền bốn vai trò, chín trạng thái vòng đời, kiểm tra withdrawn trên PostgreSQL, purge cache Redis, Hold ngày/annotation, ngưỡng số và O1 Base Scope.
- Bổ sung migration schema nền và nối chuỗi hiện có: `base -> b01d4334f030 -> 20261121_01 -> 20261123_01`.

## Bằng chứng chạy

| Kiểm tra | Kết quả |
|---|---|
| `python -m pytest -q` trong `backend` | **151 passed, 0 failed**, exit code 0; 1 Starlette/httpx deprecation warning |
| `ruff check src tests migrations` và `git diff --check` | **PASS**, exit code 0 |
| `mypy src` | **PASS**, 76 source files, exit code 0 |
| Migration trên PostgreSQL cô lập | **PASS**: `stamp base` → `upgrade head`; `downgrade base` → `upgrade head`; `alembic check` báo `No new upgrade operations detected` |
| PostgreSQL/Redis cho bộ test | Docker daemon hoạt động; PostgreSQL và Redis cô lập; ca KnowledgeService dùng PostgreSQL; ca purge gọi worker thật và Redis thật |

OPS 01 dùng harness benchmark hiện có, chạy trên SQLite in-memory; kết quả kiểm thử không được diễn giải thành benchmark PostgreSQL hoặc môi trường production.

## Điều kiện còn chờ

1. **Chưa có S4 sign-off độc lập:** các kiểm tra trên chạy trong worktree triển khai, không đáp ứng Separation of Duties.
2. **Chưa có build/tag phát hành:** thay đổi chưa commit/PR; không tạo hoặc sửa tag đóng băng. Bản `v0.2.1-g1-offline` chưa được tạo trong worktree này. Chỉ kiểm định S4 trên artifact bất biến đã review mới có thể đóng CKPA-75.

## Quyết định

Các lỗi logic CKPA-75 và blocker bootstrap DB mới đã được xử lý trên patch local; toàn bộ 151 backend tests, Ruff, Mypy và xác minh migration đều đạt. Tuy nhiên, **chưa thể tuyên bố CKPA-75 hoàn tất/nghiệm thu** cho đến khi:

- review và đưa patch/test vào build bất biến mới;
- S4 chạy độc lập full regression/fault injection trên đúng build/tag và ký sign-off theo SoD.
