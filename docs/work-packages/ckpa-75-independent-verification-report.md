# Báo cáo kiểm định CKPA-75 — G1

**Cập nhật:** 2026-11-28
**Base:** `bac9b1d54fca58301bbb46b17eeb18737bf9bf37` (`origin/develop`)
**Kết luận hiện tại:** `PASS` — S4 chấp thuận delta retest trên tag `v0.2.1-g1-offline` ngày 2026-11-28; xem mục “Verdict S4 chính thức”.

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

## Phụ lục xác minh cập nhật — 2026-11-25

Phụ lục này cập nhật trạng thái sau khi PR #34 và #35 được merge vào `develop`. Nó không thay đổi tag đóng băng `v0.2.0-g1-offline`, không thay thế kết quả trên tag và không phải chữ ký nghiệm thu S4.

### Kết quả chạy lại

| Artifact / môi trường | Kết quả |
|---|---|
| Tag `v0.2.0-g1-offline` (`0703568`), `python -m pytest -q` | **99 passed, 0 failed**, exit code 0; 1 deprecation warning. Đây là suite có trên tag; bộ regression CKPA-75 mới không có trên tag nên kết quả này không chứng minh full G1 matrix/fault injection. |
| `develop` (`16da8df`), GitHub Actions [run 45569057179](https://github.com/ho4ngTien/CRM-Knowledge-and-Policy-Assistant/actions/runs/45569057179) | **PASS**: backend CI, worker syntax và CSV contract đều xanh; backend pytest **215 passed**, Ruff và Mypy đạt. CI provision PostgreSQL/Redis. |
| `develop` (`16da8df`), local `python -m pytest -q` không cấu hình PostgreSQL | **214 passed, 1 skipped**, exit code 0; PostgreSQL-only benchmark được skip vì dịch vụ không khả dụng. |
| `develop` (`16da8df`), local pytest với CI PostgreSQL URL | **214 passed, 1 failed**, exit code khác 0: benchmark PostgreSQL nhận `ConnectionRefusedError` tại `localhost:5432`; máy local không có Docker daemon/PostgreSQL. Không tính lượt này là PASS. |

### Trạng thái defect theo artifact

| Defect | Trạng thái trên `develop` mới nhất | Trạng thái trên tag `v0.2.0-g1-offline` |
|---|---|---|
| `DEF-CKPA75-01` — CI thiếu PostgreSQL/Redis | Đã xử lý trong PR #35; workflow khai báo PostgreSQL/Redis và run 45569057179 xanh. | Không thay đổi tag đóng băng. |
| `DEF-CKPA75-02` — SEC 05 commit/ACK, fail-closed, Snapshot Age | PR #35 bổ sung test commit trước cache purge/ACK, lỗi DB và Snapshot Age; CI xanh. Lưu ý các test trong `backend/tests/ops/test_sec05_withdrawal_controls.py` dùng SQLite in-memory adapter, không phải bài test PostgreSQL-backed. Nếu tiêu chí yêu cầu kiểm chứng trên PostgreSQL thật, phần đó vẫn cần xác nhận/bổ sung. | Bộ kiểm chứng mới không có trên tag; chưa chứng minh đầy đủ SEC 05 trên tag. |
| `DEF-CKPA75-03` — OPS 01 PostgreSQL benchmark | PR #35 bổ sung test PostgreSQL trong `backend/tests/test_ops01_benchmark_500.py`; CI xanh xác nhận các assertion 500 dòng, đối soát, SLA và LKG. Cần lưu report số đo cụ thể khi chạy benchmark để evidence dễ kiểm toán. | Không có bộ kiểm chứng mới trên tag. |
| `DEF-CKPA75-04` — checksum fault injection/LKG | PR #35 bổ sung checksum mismatch fault injection và assertion LKG; CI xanh. | Không có bộ kiểm chứng mới trên tag. |
| `DEF-CKPA75-05` — fresh PostgreSQL DB migration | Chưa xác nhận đã xử lý trên `develop`. Migration nền có trong nhánh PR #33 nhưng PR #33 vẫn OPEN/DIRTY, chưa được tích hợp vào `develop`; chưa có kết quả migration fresh-DB cho build mới. | Vẫn là lỗi đã ghi nhận trước đó: migration trên PostgreSQL trống dừng tại `20261123_01` do thiếu bảng `passages`. Không sửa tag. |

### Verdict cập nhật

Các cập nhật PR #34/#35 cải thiện đáng kể và CI của `develop` đạt **215/215**, nhưng không làm thay đổi nội dung tag được yêu cầu. Vì vậy, với đúng điều kiện nghiệm thu trên `v0.2.0-g1-offline`, **chưa có bằng chứng để tuyên bố 100% ca kiểm soát đạt hoặc ký PASS**. Báo cáo này bàn giao rõ sai khác giữa tag đóng băng và `develop`; `DEF-CKPA75-05` cùng các phần kiểm chứng chưa hiện diện trên tag tiếp tục cần SUB24 xử lý/đánh giá. Sau khi có build bất biến được duyệt và bằng chứng đầy đủ, S4 thực hiện retest/sign-off cuối.

## Phụ lục CKPA-76 delta retest — 2026-11-27

Phụ lục này ghi nhận [CKPA-76 Retest Log](</C:/Users/quyha/Downloads/CKPA-76_Retest_Log.md>) được cung cấp ngày 2026-11-27. Log thuộc nhánh `feat/ckpa-76-swarming-clean`, base `0a1bff1` (`origin/develop`), verdict `NEEDS_CI_AND_S4_RETEST`. Đây là kết quả kiểm thử nhánh swarming, **không phải** kết quả trên tag `v0.2.0-g1-offline`, không phải CI xanh và không phải S4 sign-off.

### Bằng chứng được ghi trong CKPA-76 Retest Log

| Kiểm tra | Kết quả được ghi |
|---|---|
| Backend `py -3.12 -m pytest -q` | **232 passed, 1 skipped**, exit code 0; 1 Starlette/httpx deprecation warning. |
| Ruff, Mypy, worker syntax, `git diff --check` | **PASS**; Mypy kiểm tra 76 source files. |
| PostgreSQL 16 OPS 01 benchmark | **Chưa chạy local**; log ghi không có listener PostgreSQL hoặc Docker daemon. Cần CI xác minh. |
| PostgreSQL migration round-trip | Đã cấu hình trong CI (`upgrade head → downgrade base → upgrade head`), nhưng **đang pending** Actions run trên nhánh. |
| S4 delta retest và sign-off | **Chưa thực hiện**; release tagging cũng chưa thực hiện. |

### Cập nhật các finding liên quan

- **CI/PostgreSQL benchmark:** log nêu fix trên develop `ca43c11` cho lỗi benchmark do `drop_all` để lại bảng có foreign key phụ thuộc; nhánh retest dùng `create_all` và `TRUNCATE ... RESTART IDENTITY CASCADE`. Theo log, local PostgreSQL retest chưa chạy và CI trên nhánh vẫn phải xanh trước khi coi là xác minh hoàn tất.
- **SEC 05:** log xác nhận guard từ chối passage `withdrawn`/tombstoned có trên develop và được backend regression suite bao phủ. Riêng log này không đưa ra bằng chứng mới cho toàn bộ yêu cầu CKPA-75 về commit-before-ACK, fail-closed và Snapshot Age trên đúng artifact release; giữ mục này cần được đối chiếu trong S4 delta retest.
- **Document version ID:** nhánh retest thêm xử lý ID vượt giới hạn 64 ký tự bằng SHA-256 suffix xác định và test cho ID composed/already-composed. Đây là finding phát sinh trong vòng swarming, cần xác nhận CI trên nhánh.
- **Normalization benchmark:** ngưỡng đã được nâng từ 50 ms lên 150 ms theo review; chưa phải kết quả kiểm định G1 OPS 01.
- **Migration:** CI round-trip mới được cấu hình nhưng chưa có kết quả; chưa đủ căn cứ đóng finding fresh-schema migration.
- **Tag/release:** log xác nhận chưa dọn PR trùng, chưa tạo tag patch và chưa có S4 delta retest. Không sửa tag `v0.2.0-g1-offline`.

### Verdict cập nhật đến 2026-11-27

Log CKPA-76 cho thấy tiến triển đáng kể ở nhánh swarming (**232 passed, 1 skipped** và các kiểm tra tĩnh đạt), nhưng nhánh đang ở trạng thái `NEEDS_CI_AND_S4_RETEST`. PostgreSQL benchmark, migration round-trip CI, artifact/tag bất biến và S4 delta retest/sign-off vẫn chưa hoàn tất. Kết quả này **không thay thế** kết quả frozen tag (99 passed, nhưng thiếu bộ test CKPA-75 mới và migration DB trống thất bại) và không đủ để tuyên bố CKPA-75 đạt 100%. Giữ verdict báo cáo là **NEEDS_SIGNOFF** cho đến khi CI trên đúng commit xanh, evidence PostgreSQL/migration được lưu, artifact phát hành được xác nhận và S4 ký retest.

## Phụ lục S4 delta retest — tag v0.2.1-g1-offline — 2026-11-28

### Artifact được retest

- **Tag:** `v0.2.1-g1-offline`
- **Commit:** `771b3315cb488421d4a7131a3b6271c376652a06` (đã xác nhận tag trỏ đúng SHA)
- **Worktree:** tách biệt, detached HEAD tại tag; không sửa tag hoặc mã nguồn trong lần retest.
- **CI:** [GitHub Actions run 45908752712](https://github.com/ho4ngTien/CRM-Knowledge-and-Policy-Assistant/actions/runs/45908752712), chạy trên cùng commit.

### Kết quả xác minh

| Kiểm tra | Kết quả |
|---|---|
| Local full backend `python -m pytest -q` | **257 passed, 1 skipped**, exit code 0; skip là bài PostgreSQL-only do môi trường local không có PostgreSQL/Docker. |
| Local G1-targeted suite: CKPA-75 regression, OPS 03/04 boundaries, SEC 05 controls, OPS 01 benchmark | **47 passed, 1 skipped**, exit code 0; PostgreSQL-only benchmark bị skip cùng lý do môi trường. |
| GitHub Actions backend pytest trên tag | **258 passed, 0 failed, 0 skipped**, exit code 0. CI có PostgreSQL 16/pgvector và Redis services. |
| PostgreSQL migration | **PASS trên CI:** `alembic upgrade head → downgrade base → upgrade head`; log xác nhận schema nền và các revision `20261121_01`, `20261123_01`, `20261127_01` được upgrade/downgrade thành công. |
| Ruff / Mypy | **PASS**; local Ruff đạt, local Mypy không lỗi trên 77 source files; CI Ruff/Mypy cũng xanh. |
| Worker syntax / CSV contract / frontend lint-build | **PASS trên CI**; tất cả job của run 45908752712 kết luận success. |
| `git diff --check` | Không phát sinh diff mã nguồn trong worktree retest; báo cáo hiện tại được cập nhật riêng sau lượt chạy. |

### Đối chiếu phạm vi kiểm soát

- **OPS 01:** test 500 dòng kiểm tra `Expected = Accepted + Quarantined`, SLA `<=30 phút`, LKG và idempotency; có checksum mismatch fault injection và assertion quarantine/LKG. Bài PostgreSQL benchmark chạy và pass trong CI. Test harness cũng chạy local nhưng chỉ trên SQLite. GitHub Actions log không in ra thời gian benchmark cụ thể; evidence hiện chứng minh assertion ngưỡng pass, không lưu được số đo thực tế trong log.
- **SEC 01 / KNW 03:** regression kiểm tra 4 vai trò × 9 trạng thái (7 lifecycle chính thức cùng `quarantined` và `feedback_candidate`) và cô lập audience chéo vai trò.
- **SEC 05:** test kiểm tra withdrawal commit trước khi purge/ACK, fail-closed khi DB lỗi, chặn passage withdrawn và các trạng thái Snapshot Age. Các bài kiểm tra thứ tự commit/fail-closed/Snapshot Age trong `backend/tests/ops/test_sec05_withdrawal_controls.py` dùng SQLite in-memory adapter; CI có PostgreSQL/Redis nhưng không nên diễn giải các test adapter này thành kiểm thử các nhánh đó trên PostgreSQL thật.
- **OPS 03:** test ngày biên UTC+7, chuyển UTC sang ngày Việt Nam, thiếu governing date/coverage gap tạo Hold, và matcher dùng đủ sáu chiều scope.
- **OPS 04:** test ngưỡng `<`, `=`, `>`, DAT 08 (unit/attachment), Conflict Hold cùng trường hợp scope không giao nhau.
- **Migration:** lỗi bootstrap DB trống của tag `v0.2.0` được khắc phục trên artifact mới; CI fresh-schema round-trip của chính tag `v0.2.1` đã pass. Tag `v0.2.0` vẫn giữ nguyên, không sửa.

### Kết luận delta retest

Trên đúng artifact `v0.2.1-g1-offline` (SHA `771b3315cb488421d4a7131a3b6271c376652a06`), toàn bộ backend CI và các job release liên quan đều pass; full CI pytest đạt **258/258**, migration PostgreSQL round-trip và các kiểm tra tĩnh đạt. Local full suite đạt **257 passed, 1 skipped** vì thiếu PostgreSQL; CI đã chạy bài bị skip local trên PostgreSQL/pgvector và pass.

Kết quả này đáp ứng bằng chứng tự động hóa delta retest cho các ca được suite bao phủ. Tại thời điểm viết phụ lục, verdict chính thức của S4 còn chờ ghi nhận. Các giới hạn evidence được nêu rõ: log CI không in thời gian OPS 01 cụ thể (assertion `<=30 phút` đã pass), và test thứ tự SEC 05/Snapshot Age dùng SQLite adapter.

## Verdict S4 chính thức — 2026-11-28

**Quyết định:** `PASS` cho delta retest CKPA-75 trên tag bất biến `v0.2.1-g1-offline`, commit `771b3315cb488421d4a7131a3b6271c376652a06`.

S4 xác nhận chấp thuận kết quả kiểm thử được ghi tại phụ lục này: CI backend **258 passed, 0 failed, 0 skipped**, PostgreSQL migration round-trip pass; Ruff, Mypy, worker syntax, CSV contract và frontend lint/build đều pass. Local full suite đạt **257 passed, 1 skipped** do không có PostgreSQL tại máy retest; ca PostgreSQL tương ứng đã chạy trong CI.

Phạm vi verdict là artifact và các ca được thực thi trên tag nêu trên. Các giới hạn đã được ghi nhận khi chấp thuận: CI log không lưu thời gian benchmark OPS 01 dạng số riêng (assertion ngưỡng `<=30 phút` pass); test thứ tự commit SEC 05/fail-closed/Snapshot Age dùng SQLite adapter, không phải toàn bộ các nhánh đó chạy trên PostgreSQL thật. Verdict này không sửa hoặc áp dụng ngược cho tag `v0.2.0-g1-offline`.
