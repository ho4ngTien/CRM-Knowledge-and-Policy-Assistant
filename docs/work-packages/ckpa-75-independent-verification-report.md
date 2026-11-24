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
| Tag `v0.2.0-g1-offline` (`0703568`), `pytest -q` | **99 passed, 0 failed**, exit code 0; 1 deprecation warning. Tag không chứa file regression CKPA-75 mới. |
| Tag `v0.2.0-g1-offline`, migration từ DB PostgreSQL trống | **FAIL**, exit code 1: revision `20261123_01` báo `relation "passages" does not exist`; DB tạm đã được xóa sau phép thử. |
| Patch PR #33 (`98a1c24`), `python -m pytest -q` | **151 passed, 0 failed**, exit code 0; 1 Starlette/httpx deprecation warning, khi PostgreSQL/Redis đang chạy. |
| Patch PR #33, migration PostgreSQL trống và round-trip | **PASS**: `upgrade head`; `alembic check`; `downgrade base` → `upgrade head`; `alembic check`; DB tạm đã được xóa. |
| Patch PR #33, `ruff check src tests migrations`, `git diff --check`, `mypy src` | **PASS**, exit code 0; Mypy kiểm tra 76 source files. |
| PostgreSQL/Redis local | Docker daemon hoạt động; test SEC 05 truy cập PostgreSQL và gọi worker purge trên Redis thật. |
| [GitHub Actions PR #33, run 45453913931](https://github.com/ho4ngTien/CRM-Knowledge-and-Policy-Assistant/actions/runs/45453913931) | **FAIL**, exit code 1: 2 failed, 149 passed; PostgreSQL/Redis từ chối kết nối `localhost:5432` / `localhost:6379`. |

Các lượt tag và patch được chạy ở worktree riêng để tránh lẫn mã nguồn. Lượt chạy được thực hiện theo yêu cầu đối chiếu của S4; đây là bằng chứng thực thi để S4 xem xét, không phải chữ ký nghiệm thu thay S4.

OPS 01 dùng harness benchmark hiện có trên SQLite in-memory; kết quả không phải benchmark PostgreSQL hoặc môi trường production.

## Defect register — bàn giao SUB24 / CKPA-76

Các mục dưới đây là defect CI/kiểm định có bằng chứng tái hiện. Chúng **không tự khẳng định đã tái hiện lỗi runtime sản phẩm hoặc Critical Control**. Mức P1/P2 là phân loại bàn giao sơ bộ, cần S4/Swarming xác nhận theo taxonomy và cập nhật trạng thái sau khi sửa.

### DEF-CKPA75-01 — CI không khởi động PostgreSQL/Redis

- **Mức độ đề xuất:** P1 — CI thất bại; xác nhận merge gate theo branch protection.
- **Bằng chứng:** workflow `.github/workflows/ci.yml` chạy `pytest -q` nhưng không khai báo service PostgreSQL hoặc Redis. Run CI của PR #33 thất bại ở `test_sec05_withdrawn_passage_is_denied_by_database_backed_knowledge_service` (kết nối `localhost:5432`) và `test_sec05_redis_withdrawal_task_purges_version_cache_keys` (kết nối `localhost:6379`); kết quả là 2 failed, 149 passed.
- **Tác động:** CI không tái hiện môi trường cần thiết cho các kiểm thử tích hợp SEC 05; PR hiện đỏ dù các test này đạt local khi dịch vụ chạy.
- **Việc cần làm:** khai báo PostgreSQL/Redis services trong CI, health-check và cấu hình URL test; chạy lại toàn bộ suite và đính kèm log xanh.

### DEF-CKPA75-02 — SEC 05 thiếu kiểm chứng thứ tự commit/ACK và Snapshot Age

- **Mức độ đề xuất:** P1 — chưa đủ bằng chứng cho kiểm soát thu hồi tức thì.
- **Bằng chứng:** test hiện có xác nhận KnowledgeService từ chối passage `withdrawn` và worker xóa cache Redis. Không có kiểm thử tích hợp chứng minh trạng thái thu hồi đã commit trước ACK, hành vi fail-closed khi persistence/DB lỗi, hoặc cập nhật/đánh giá Snapshot Age sau thu hồi.
- **Tác động:** chưa chứng minh client không nhận ACK trước khi thu hồi bền vững, và dữ liệu/cache cũ không được dùng khi trạng thái mới chưa khả dụng.
- **Việc cần làm:** thêm test qua API/service boundary; xác nhận DB đã commit trước response ACK, inject lỗi DB để xác nhận fail-closed, và xác nhận Snapshot Age/decision được cập nhật hoặc Hold theo yêu cầu.

### DEF-CKPA75-03 — OPS 01 chưa có bằng chứng benchmark trên PostgreSQL

- **Mức độ đề xuất:** P2 — thiếu bằng chứng môi trường chấp nhận.
- **Bằng chứng:** `backend/scripts/benchmark_ops01_500.py` tạo `sqlite+pysqlite:///:memory:`; kết quả ≤30 phút hiện có là benchmark SQLite.
- **Tác động:** số đo không đại diện cho PostgreSQL/pgvector của G1, nên chưa đủ làm bằng chứng hiệu năng môi trường mục tiêu.
- **Việc cần làm:** chạy lô 500 dòng trên PostgreSQL/pgvector cô lập, ghi thời gian, đối soát và LKG; nếu chỉ chấp nhận SQLite thì cần người có thẩm quyền phê chuẩn sai khác phạm vi.

### DEF-CKPA75-04 — OPS 01 chưa fault-inject checksum mismatch

- **Mức độ đề xuất:** P1 — thiếu kiểm chứng kiểm soát toàn vẹn dữ liệu/LKG.
- **Bằng chứng:** benchmark tạo manifest checksum hợp lệ bằng `_build_manifest`; lỗi được đưa vào là thiếu essential attachment và batch stale. Không tìm thấy ca test làm sai checksum của manifest.
- **Tác động:** chưa chứng minh checksum mismatch bị từ chối/cách ly và không làm thay đổi Last Known Good.
- **Việc cần làm:** sửa checksum của một record trong manifest, chạy import, xác nhận kết quả quarantine/reject đúng hợp đồng và so sánh dữ liệu LKG trước/sau không đổi.

### DEF-CKPA75-05 — Tag v0.2.0 không bootstrap được PostgreSQL DB trống

- **Mức độ đề xuất:** P1 — blocker khởi tạo DB cho artifact đóng băng; không tự phân loại là Critical Control.
- **Bằng chứng:** trên commit tag `0703568`, tạo DB PostgreSQL trống rồi chạy `alembic upgrade head`; migration `20261121_01` chạy, nhưng `20261123_01` dừng tại `ALTER TABLE passages ...` với `UndefinedTableError: relation "passages" does not exist`. Lặp lại trên patch PR #33, chuỗi migration nền mới nâng cấp và round-trip thành công.
- **Tác động:** môi trường mới không thể cài đặt schema bằng migration của tag đóng băng.
- **Việc cần làm:** không sửa tag đã đóng băng; xác định liệu artifact G1 bắt buộc hỗ trợ DB trống hay dựa vào schema được provision riêng. Với artifact mới, đưa migration schema nền vào bản được review và xác minh trên DB trống.

## Acceptance blockers — không phân loại là defect sản phẩm

- Tag `v0.2.0-g1-offline` trỏ tới commit `0703568`; 99 test hiện có đạt nhưng file regression CKPA-75 mới không tồn tại trên tag. Kết quả 99 test không chứng minh đã chạy đủ ma trận G1/fault injection được yêu cầu.
- S4 đã yêu cầu chạy đối chiếu tag và patch; quyết định/ký SoD cuối cùng vẫn chờ S4 xem xét các kết quả và defect register.
- Sau khi PR được review/merge, S4 cần chạy artifact bất biến đúng quy trình. Nếu tiêu chí bắt buộc giữ nguyên tag `v0.2.0-g1-offline`, cần quyết định chính thức về cách xử lý sai khác giữa tag đóng băng và patch mới; không sửa tag đóng băng.

## Điều kiện còn chờ

1. **Chưa có S4 sign-off:** các kết quả so sánh đã được ghi; S4 cần xác nhận verdict, đặc biệt là tag migration FAIL, CI FAIL và các khoảng trống SEC 05/OPS 01.
2. **Chưa có build/tag phát hành mới:** patch đã commit tới `98a1c24` trên PR [#33](https://github.com/ho4ngTien/CRM-Knowledge-and-Policy-Assistant/pull/33), hiện chờ review. Chưa tạo `v0.2.1-g1-offline` và không sửa tag đóng băng.

## Quyết định

Trên patch PR #33, 151 test local, Ruff, Mypy và migration PostgreSQL đều đạt; trên tag đóng băng, 99 test đạt nhưng migration DB trống thất bại. CI PR vẫn đỏ và các defect kiểm định nêu trên chưa đóng. **Chưa thể tuyên bố CKPA-75 đạt 100% hoặc hoàn tất/nghiệm thu** cho đến khi:

- đóng DEF-CKPA75-01..05 hoặc được chấp thuận ngoại lệ có chủ sở hữu;
- review/merge PR #33 và đưa patch/test vào build bất biến mới;
- S4 chạy độc lập full regression/fault injection trên đúng build/tag và ký sign-off theo SoD.
