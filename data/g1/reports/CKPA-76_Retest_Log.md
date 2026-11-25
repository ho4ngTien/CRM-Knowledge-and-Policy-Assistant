# CKPA-76 — Nhật ký Swarming & Retest G1

**Branch:** `feat/CKPA-76-swarming-sua-loi-import-qa-retest-tag`  
**Base:** `16da8df` (`origin/develop`)  
**Trạng thái:** `NEEDS_S4_RETEST` — chưa phải nghiệm thu độc lập hoặc phát hành DEL 03.

## Thay đổi

- Bổ sung migration nền `b01d4334f030` tạo schema ứng dụng để hỗ trợ cài đặt trên PostgreSQL trống.
- Nối chuỗi Alembic thành `base → b01d4334f030 → 20261121_01 → 20261123_01`, bảo đảm các bảng `passages` và `critical_fields` tồn tại trước khi migration reconciliation bổ sung cột.
- Bổ sung bước CI kiểm tra PostgreSQL migration theo vòng `upgrade head → downgrade base → upgrade head`.

## Kết quả retest

| Kiểm tra | Kết quả |
|---|---|
| Backend regression (`py -3.12 -m pytest -q`) | **214 passed, 1 skipped**, exit code 0; 1 cảnh báo deprecation từ Starlette/httpx. |
| OPS 01 PostgreSQL benchmark | **Skipped** — chưa cấu hình `DATABASE_URL` PostgreSQL trên máy local. |
| Alembic offline SQL (`upgrade head --sql`; `downgrade 20261123_01:base --sql`) | **PASS** — sinh SQL xuôi/ngược qua đủ ba revision. |
| Ruff (`py -3.12 -m ruff check .`) | **PASS**. |
| Mypy (`py -3.12 -m mypy src`) | **PASS** — 76 source files. |
| `git diff --check` và `git diff --cached --check` | **PASS**. |
| PostgreSQL thật: upgrade/downgrade/upgrade | **Chưa chạy local** — Docker CLI có nhưng Docker daemon chưa hoạt động. Đã thêm bước thực thi kiểm tra này vào CI; cần CI xanh để xác nhận. |

## Delta theo defect CKPA-75

| Defect | Trạng thái sau lần chạy này |
|---|---|
| DEF-CKPA75-01 — CI thiếu PostgreSQL/Redis | Đã được xử lý trước đó trên develop; workflow hiện khai báo cả hai service. |
| DEF-CKPA75-02 — SEC 05 commit/ACK, fail-closed, Snapshot Age | Regression tests hiện hữu chạy trong suite. Các test adapter đã có dùng SQLite; lần chạy này không thay thế kiểm thử PostgreSQL-backed. |
| DEF-CKPA75-03 — OPS 01 benchmark PostgreSQL | Chưa retest trên PostgreSQL trong môi trường local; bài kiểm thử PostgreSQL bị skip do thiếu `DATABASE_URL`. |
| DEF-CKPA75-04 — checksum fault injection/LKG | Regression test hiện hữu chạy trong suite; suite local đạt. |
| DEF-CKPA75-05 — bootstrap PostgreSQL DB trống | Đã thêm migration nền và nối revision; offline chain đạt. Còn chờ CI chạy migration thực tế trên PostgreSQL. |

## Điều kiện bàn giao còn chờ

1. CI của nhánh phải xanh, bao gồm bước migration PostgreSQL round-trip mới.
2. S4 cần thực hiện delta retest độc lập trên build/commit được review; nhật ký này không thay thế S4 sign-off.
3. Chưa tạo tag phát hành DEL 03 và chưa tuyên bố đạt 100% cho đến khi các mục trên hoàn tất.
