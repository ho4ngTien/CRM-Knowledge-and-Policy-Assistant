> **TRẠNG THÁI:** BẢN DỰ THẢO CHỜ RÀ SOÁT & PHÊ DUYỆT (FOR REVIEW — CHƯA KÝ DUYỆT CHÍNH THỨC). Tài liệu chỉ phục vụ rà soát nghiệm thu Sprint 1 Cổng G0; không cấu thành phê duyệt PO, chữ ký pháp lý, kết luận pháp chế chính thức, báo giá ràng buộc hay giờ công thực tế chưa đối soát. Các mục tiêu định lượng, giả định dự thầu và ví dụ Annex E từ RFP được ghi rõ là đề xuất/tham khảo.

# MA TRẬN RBAC 20 NGƯỜI DÙNG ĐỊNH DANH (5 PHIÊN ĐỒNG THỜI), HỢP ĐỒNG API & DỰ THẢO PHÁP LÝ / AI PHỤ LỤC F (GATE G0)
## Dự án: SongNhat CRM Knowledge and Policy Assistant (`CKPA`)

- **Pháp nhân Bên mua:** `Công ty Cổ phần Thiết bị Công nghiệp Song Nhật` *(ghi chú chuẩn: chờ `[P1]` / Legal Owner xác nhận chính thức theo ĐKKD, thay thế biến thể cũ)*.
- **Mã công việc Jira:** `CKPA-17` (`CRM-G0-SUB10` — `[G0][SEC01] Thiết kế RBAC 20-User & Pháp lý Annex F`)
- **Story cha:** `CKPA-16` (`CRM-G0-ST04` — `[G0][SEC] Thiết kế RBAC 20-User, Annex C & Ops`) | **Epic:** `CKPA-3` (`CRM-G0-EP01`)
- **Tiêu chí nghiệm thu Cổng G0:** `G0-AC05` (`DEL01-F`)
- **Tham chiếu RFP:** Mục 1 (`Base vs O1`), Mục 2 (`Users & Limits`), Mục 8 & Mục 11 (`SoD / Chinese Wall`), `DAT 04`, `DAT 07`, `ANS 01`, `ANS 03`, `KNW 03`, `SEC 01`, `SEC 03`, `VN 05`, `Phụ lục F` (`R02–R05`, `R10–R11`)
- **Chủ trì thực hiện (Assignee):** `[P5]` **Nguyễn Anh Khoa** (*Privacy and security owners — Bên mua*)
- **Người báo cáo (Reporter):** `[P1]` **Văn Mỹ Vân** (*Purchaser sponsor / Product Owner — Bên mua*)
- **Phối hợp chuyên môn (RACI & Đối chiếu kỹ thuật):** `[P1]` Văn Mỹ Vân, `[S1]` Hoàng Tiến (*Named lead / Scrum Master*), `[P2]` Lý Hữu Tài (*Policy owners — Policy Reviewer #1*), `[P3]` Trần Chí Kha (*Knowledge and data steward — Policy Reviewer #2*), `[P4]` Ngô Thị Trà My (*Staff users*), `[S3]` Phạm Lương Yến Nhi (*Retrieval and application engineer*), `[S4]` Phạm Quý Hải (*Quality lead — Independent QA*), `[S5]` Nguyễn Ngọc Duy (*Operations specialist*)
- **Tệp dữ liệu kèm theo cùng Sub-task:**
  1. `CKPA-17_SUB10_20_Named_Users_5_Concurrent_Allocation.csv` (Danh bạ phân bổ đúng `20` người dùng định danh & hạn mức `5` phiên đồng thời)
  2. `CKPA-17_SUB10_RBAC_Endpoint_Permission_Matrix.csv` (Ma trận phân quyền chi tiết theo endpoint `/api/v1/*` và khóa Chinese Wall trên `sealed_100`)

---

## 1. MỤC ĐÍCH, PHẠM VI & RANH GIỚI BASE SCOPE (`M`) SO VỚI OPTION O1 (`O`)

Tài liệu này thiết lập khung thiết kế bảo mật truy cập (RBAC), định danh 20 người dùng / 5 phiên đồng thời, hợp đồng cấu trúc dữ liệu `AnswerPackage` 7 phần và dự thảo rà soát pháp lý / phân loại AI bước đầu theo Phụ lục F RFP phục vụ rà soát Sprint 1 Cổng G0.

### 1.1 Khóa ranh giới Phạm vi Cơ sở (`M`) so với Tùy chọn `O1` (`DAT 07`)
- **Phạm vi Cơ sở bắt buộc (`M` — Mandatory Core):**
  - Phục vụ **1 công ty** (`Công ty Cổ phần Thiết bị Công nghiệp Song Nhật`), tối đa **`20` người dùng định danh** (`named users`), tối đa **`5` phiên đồng thời** (`concurrent sessions`).
  - Xử lý văn bản chính sách đã phê duyệt thuộc **3 họ chính sách** qua **2 lược đồ UTF-8 CSV cơ sở** (`passages` tối đa 300 đoạn, `<= 6.000` ký tự Unicode/mục; `critical_fields` tối đa 50 dòng).
  - **Không nạp và không lưu giữ bất kỳ hồ sơ khách hàng nào (`0` customer records)** trong Base Scope (`SEC 02`).
- **Tùy chọn `O1` — Ngữ cảnh CRM Được Chọn (`Option O1 — Selected CRM Context`, `O` — Separately Priced Option, `DAT 07`):**
  - **Trạng thái trong Base Scope: TẮT (`OFF` / không kích hoạt trong Base Scope).**
  - Bản chất đúng theo RFP Mục 1 & `DAT 07`: Tùy chọn `O1` là lược đồ UTF-8 CSV thứ 3 cho phép nhân viên được ủy quyền chọn **tối đa 1 bản ghi ngữ cảnh CRM tối thiểu** cho mỗi `AnswerPackage` (giới hạn `<= 2.000` dòng khởi tạo / `<= 5.000` dòng lưu giữ). *(Tài liệu này đính chính dứt điểm sai sót khái niệm trước đây khi từng gán nhầm Tùy chọn `O1` thành một mô hình suy luận AI bên ngoài.)*
  - Điều kiện kích hoạt riêng biệt: Chỉ được xem xét sau khi có quyết định thương mại độc lập, báo giá riêng (`DEL 05`) và vượt qua đầy đủ 6 bước thẩm định độc lập về nhu cầu, quyền chủ thể dữ liệu, cơ sở xử lý hợp pháp, phân quyền tương đương CRM, độ tươi dữ liệu và giá trị kinh tế (chi tiết tại `CKPA-19`).

### 1.2 Khóa cấu hình giới hạn vận hành & LLM theo Mục 2 RFP (Đề xuất giả định dự thầu cần xác nhận tại G0)
Các thông số dưới đây đối chiếu trực tiếp với khung cấu hình hiện hữu trong `backend/src/config.py` và yêu cầu Mục 2 RFP:

| Tham số hệ thống | Giá trị khóa Base Scope | Tên biến hiện hữu (`backend/src/config.py`) | Ghi chú kiểm soát & Hạng mục đồng bộ G1 |
|---|---:|---|---|
| Giới hạn tài khoản định danh | `<= 20` users | `PILOT_MAX_NAMED_USERS = 20` | Cưỡng chế qua danh bạ OIDC/SSO doanh nghiệp (`SEC 01`) |
| Giới hạn phiên hoạt động đồng thời | `<= 5` sessions | `PILOT_MAX_CONCURRENT_SESSIONS = 5` | Khóa bằng Redis atomic session lock (triển khai tại G1) |
| Trạng thái Tùy chọn `O1` (Selected CRM Context) | `OFF` (`False`) | *(Cần bổ sung `OPTION_O1_ENABLED = False` tại G1)* | Tách biệt hoàn toàn khỏi Base Scope (`DAT 07`) |
| Số đoạn ngữ cảnh tối đa / gói trả lời | `<= 8` passages | `ANSWER_MAX_PASSAGES = 8` | Lọc quyền, trạng thái `effective`, ngày & 6 chiều trước prompt |
| Độ dài tối đa / mục văn bản nhập liệu | `<= 6.000` ký tự Unicode | `PASSAGE_MAX_CHARS = 6000` | Cách ly `quarantined` nếu vượt ngưỡng (`DAT 08`) |
| Ngân sách Input / Output Tokens (gồm instructions) | `<= 6.000` / `<= 900` | `LLM_MAX_INPUT_TOKENS = 6000` / `LLM_MAX_OUTPUT_TOKENS = 900` | Cấm cắt cụt im lặng; trả trạng thái `HOLD` rõ ràng (`OPS 08`) |
| Số lượt gọi sinh/sửa tối đa / AnswerPackage | `<= 2` calls | `LLM_MAX_CALLS_PER_PACKAGE = 2` | Tối đa 1 lượt sinh chính + 1 lượt sửa lỗi hợp lệ |
| Trần gói trả lời & lượt gọi / tháng | `<= 1.000` gói / `<= 2.000` calls | `ANSWER_MAX_PACKAGES_PER_MONTH = 1000` / `LLM_MAX_CALLS_PER_MONTH = 2000` | Bao gồm mọi lượt `HOLD`, `retry` và thất bại (`OPS 08`) |
| Chặn phát trực tiếp văn bản chưa kiểm chứng | `False` (Bắt buộc) | `ENABLE_ANSWER_STREAMING = False` | Bất biến `INV-03`: chỉ hiển thị sau khi xác thực nguồn & quyền |
| Múi giờ chuẩn xác định ngày hiệu lực | `Asia/Ho_Chi_Minh` (`UTC+7`) | `APP_TIMEZONE = "Asia/Ho_Chi_Minh"` | Khóa ranh giới ngày `00:00:00` – `23:59:59` (`OPS 03`) |

---

## 2. PHÂN BỔ ĐÚNG 20 NGƯỜI DÙNG ĐỊNH DANH & CƠ CHẾ 5 PHIÊN ĐỒNG THỜI (`SEC 01`)

### 2.1 Phân bổ 20 Named Users theo đúng 4 nhóm vai trò hệ thống Mục 2 RFP
Tổng số tài khoản vận hành nội bộ được khóa đúng **`20` người dùng định danh** (chi tiết từng suất trong tệp `CKPA-17_SUB10_20_Named_Users_5_Concurrent_Allocation.csv`):

| Nhóm vai trò hệ thống (RFP Mục 2) | Ánh xạ `UserRole` kỹ thuật | Số lượng | Thành phần định danh / Vị trí dự kiến | Quyền trên `sealed_100` |
|---|---|---:|---|:---:|
| **1. Readers** *(Người đọc / tra cứu CRM)* | `reader` | **`13`** | - `USR-01` (`RSU-01`): `[P4]` Ngô Thị Trà My (Đại diện 1/5 Rep Users)<br>- `USR-02..USR-05` (`RSU-02..RSU-05` theo `CKPA-5`/`CKPA-7`): 4 Representative Staff Users phía Song Nhật (chờ `[P1]`/`[P4]` xác nhận danh bạ 100% Bên mua, 0% `S1–S5`)<br>- `USR-06..USR-13`: 8 nhân sự Sales/CRM/CSKH bổ sung (cấp định danh trước G2) | **`DENY`** |
| **2. Policy owners / publishers** | `policy_owner`, `publisher` | **`3`** | - `USR-14`: `[P2]` Lý Hữu Tài (Policy Owner / Policy Reviewer #1)<br>- `USR-15`: `[P1]` Văn Mỹ Vân (Purchaser Sponsor / PO)<br>- `USR-16`: Tài khoản thay thế `publisher` (`VN 04` — ánh xạ `Backup Owner 1 & 3` của `CKPA-9` cho `POL-001`/`POL-003` theo cơ chế kiêm nhiệm tương thích Mục 2 RFP) | `[P2]`: **`ALLOW_CONTROLLED_REVIEW`**<br>Khác: **`DENY`** |
| **3. Stewards** | `steward` | **`2`** | - `USR-17`: `[P3]` Trần Chí Kha (Knowledge & Data Steward / Policy Reviewer #2)<br>- `USR-18`: Tài khoản thay thế `steward` (`VN 04` — ánh xạ `Backup Owner 2` của `CKPA-9` cho `POL-002` kiêm thay thế `[P3]` để giữ đúng trần `20` named users) | `[P3]`: **`ALLOW_CONTROLLED_REVIEW`**<br>Khác: **`DENY`** |
| **4. Administrators** | `administrator`, `privacy_security_owner` | **`2`** | - `USR-19`: `[P5]` Nguyễn Anh Khoa (Quản trị bảo mật, quyền riêng tư & kiểm toán phía Bên mua)<br>- `USR-20`: `[S5]` Nguyễn Ngọc Duy (Quản trị vận hành kỹ thuật / SecOps phía Nhà cung cấp) | **`DENY`** *(Tuyệt đối)* |
| **TỔNG CỘNG (BASE SCOPE CAP)** | **4 nhóm vai trò RFP** | **`20`** | **100% định danh cá nhân; cấm dùng chung tài khoản (`shared accounts`)** | **Khóa Chinese Wall** |

### 2.2 Ranh giới Tách vai SoD ngoài danh bạ 20 người dùng vận hành (Mục 8 & Mục 11)
1. **Nhóm Kiểm thử Độc lập (`[S4]` Phạm Quý Hải — `independent_evaluator`):** Hoạt động trên kho đánh giá tách biệt (`sealed-eval-repo`) và phân vùng API đánh giá độc lập; **không** tham gia nhóm 5 Representative Staff Users, **không** có quyền chỉnh sửa mã nguồn/prompt của đội Build (`[S2]`, `[S3]`).
2. **Đội Phát triển & Quản lý Nhà cung cấp (`[S1]` Hoàng Tiến, `[S2]` Trần Quốc Hưng, `[S3]` Phạm Lương Yến Nhi):** **Không** nằm trong danh bạ 20 người dùng vận hành thật trên dữ liệu khách hàng/chính sách Production và bị **`DENY` 100%** trên phân vùng `sealed_100`.
3. **Nhóm 5 Representative Staff Users (`Mục 11`):** Bắt buộc 100% là nhân sự nghiệp vụ phía Bên mua (`USR-01..USR-05`), tuyệt đối `0%` thành viên Nhà cung cấp (`[S1]`–`[S5]`).

### 2.3 Cơ chế kỹ thuật thực thi giới hạn 5 phiên đồng thời (`Redis Session Lock`)
- **Xác thực định danh tổ chức (`SEC 01`):** Đăng nhập qua OIDC/SSO doanh nghiệp, cấp phát JWT có thời hạn ngắn (`60` phút) gắn nhãn môi trường (`claim: env="production"` hoặc `env="test"` theo `SEC 06`).
- **Khóa 5 phiên đồng thời trên Redis (`PILOT_MAX_CONCURRENT_SESSIONS = 5`):**
  - Sử dụng tập khóa nguyên tử Redis (Lua script) trên khóa `ckpa:sessions:active` lưu `session_id` + `user_id` + `expires_at` (heartbeat trượt mỗi 5 phút; tự động giải phóng ngay khi đăng xuất hoặc hết phiên).
  - Nhiều tab trình duyệt của cùng 1 `user_id` trên cùng 1 phiên xác thực chỉ tính là **1 phiên đồng thời** (session coalescing), ngăn tình trạng 1 nhân viên chiếm nhiều suất.
  - Khi đạt ngưỡng `5/5` phiên đang hoạt động, phiên thứ 6 bị từ chối minh bạch bằng mã HTTP `429 Too Many Requests` (`error_code: CONCURRENT_SESSION_LIMIT_REACHED`, hiển thị hướng dẫn thử lại sau hoặc liên hệ quản trị viên); **tuyệt đối không âm thầm đá phiên đang chạy** và không bỏ qua kiểm soát.
- **Kiểm tra đặc quyền đồng nhất đa tầng (`SEC 01`):** Quyền hạn và thẻ đối tượng (`audience` / `role` / 6 chiều `DAT 04`) được cưỡng chế đồng nhất tại cả 5 điểm: **(1) Pre-retrieval filter**, **(2) Generation context assembly**, **(3) UI Display & Citation Viewer**, **(4) Redis Cache key isolation**, và **(5) Audit Log access control**.

---

## 3. MA TRẬN PHÂN QUYỀN RBAC, KHÓA CHINESE WALL `sealed_100` & CỜ SỬA MÃ NGUỒN G1

### 3.1 Quy tắc Chinese Wall bắt buộc đối với tập đánh giá `sealed_100` (Mục 8 & Mục 11)
Để khắc phục triệt để lỗ hổng phân quyền được phát hiện trong đợt kiểm toán G0, quy tắc truy cập phân vùng `sealed_100` được chốt bất biến như sau:

| Endpoint / Hành động trên `sealed_100` | `independent_evaluator` (`[S4]`) | Policy Reviewers Bên mua (`[P2]` `policy_owner`, `[P3]` `steward`) | `administrator` (gồm `[S5]`) | `reader`, `publisher`, `privacy_security_owner`, `legal_owner`, Build (`[S2]`, `[S3]`), `[S1]` |
|---|:---:|:---:|:---:|:---:|
| `POST /api/v1/evaluation/runs` (`sealed_100`) | **`ALLOW`** | **`DENY`** | **`DENY`** | **`DENY`** |
| `GET /api/v1/evaluation/runs` (`sealed_100` — bản ghi thô / prompt / câu hỏi gốc) | **`ALLOW`** | **`DENY`** *(chỉ nhận phiếu phân xử có kiểm soát khi có tranh chấp điểm số)* | **`DENY`** | **`DENY`** |
| `GET /api/v1/evaluation/runs` (`sealed_100` — báo cáo tổng hợp & phân xử nghiệm thu) | **`ALLOW`** | **`ALLOW_CONTROLLED_REVIEW`** | **`DENY`** | **`DENY`** |

> [!IMPORTANT]
> **Nguyên tắc chống rò rỉ (Anti-Contamination Rule — Mục 8):**
> 1. `administrator` (bao gồm `[S5]` Nguyễn Ngọc Duy phía Nhà cung cấp) bị **`DENY` tuyệt đối** trên cả `GET` và `POST` của `sealed_100`. Quản trị hạ tầng không được phép đọc tập dữ liệu kiểm thử niêm phong; kho `sealed-eval-repo` tách biệt hoàn toàn với tài khoản triển khai ứng dụng.
> 2. Policy Reviewers phía Bên mua (`[P2]` Lý Hữu Tài và `[P3]` Trần Chí Kha) chỉ có quyền **`ALLOW_CONTROLLED_REVIEW`** (xem báo cáo tổng hợp đạt/không đạt và thực hiện phân xử chất lượng độc lập theo biên bản với `[S4]`), **không được chuyển tiếp** nội dung ca kiểm thử `sealed_100` sang đội Build (`[S2]`, `[S3]`) hoặc `administrator`. Nếu phát hiện bất kỳ ca `sealed_100` nào bị lộ sang đội Build, ca đó bị loại vĩnh viễn khỏi tập niêm phong và phải thay thế/kiểm thử độc lập lại.

### 3.2 Ma trận phân quyền tóm tắt theo 12 module API (`/api/v1/*`)
*(Chi tiết từng endpoint, phương thức HTTP và cờ đồng bộ mã nguồn G1 xem đầy đủ tại tệp `CKPA-17_SUB10_RBAC_Endpoint_Permission_Matrix.csv`.)*

| Nhóm Endpoint | `reader` | `policy_owner` | `publisher` | `steward` | `administrator` | `independent_evaluator` | `privacy_security_owner` | `legal_owner` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `/health`, `/api/v1/identity/token` | `PUBLIC` | `PUBLIC` | `PUBLIC` | `PUBLIC` | `PUBLIC` | `PUBLIC` | `PUBLIC` | `PUBLIC` |
| `/api/v1/identity/me`, `/check-permission` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` |
| `/api/v1/knowledge/*` (audience & `effective` checked) | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` |
| `/api/v1/policy/*` (`authority-matrix`, `critical-fields`, `threshold-check`) | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` |
| `/api/v1/retrieval/search`, `/api/v1/validation/verify` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `DENY` | `DENY` |
| `/api/v1/answer/*` (`/`, `/follow-up`, `/regenerate`) | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `DENY` | `DENY` | `DENY` |
| `/api/v1/referral` (`POST`/`GET`) & `/feedback` (`POST`) | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `DENY` | `DENY` | `DENY` |
| `/api/v1/referral/{id}` (`PATCH`), `/feedback/candidates`, `/ingestion/*` | `DENY` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `DENY` | `DENY` | `DENY` |
| `/api/v1/admin/policies/{id}/transition` | `DENY` | `ALLOW` | `ALLOW` | `ALLOW` | `DENY` | `DENY` | `DENY` | `DENY` |
| `/api/v1/admin/policies/{id}/withdraw` (`SEC 05` / `OPS 05`) | `DENY` | `ALLOW` | `ALLOW` | `DENY` | `ALLOW` | `DENY` | `ALLOW` | `DENY` |
| `/api/v1/admin/emergency-disable` | `DENY` | `ALLOW` | `DENY` | `DENY` | `ALLOW` | `DENY` | `ALLOW` | `DENY` |
| `/api/v1/admin/ops-summary`, `/audit/export-open` | `DENY` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `DENY` | `ALLOW` | `DENY` |
| `/api/v1/audit/logs` (nhật ký hạn chế) | `DENY` | `DENY` | `DENY` | `DENY` | `ALLOW` | `DENY` | `ALLOW` | `ALLOW` |
| `/api/v1/audit/cost-meter` (`OPS 06`) | `DENY` | `ALLOW` | `ALLOW` | `DENY` | `ALLOW` | `DENY` | `ALLOW` | `DENY` |
| `/api/v1/evaluation/runs` (`GET` — `dev_60` / `val_40`) | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `ALLOW` | `DENY` | `DENY` |
| `/api/v1/evaluation/runs` (`POST` — `sealed_100`) | `DENY` | `DENY` | `DENY` | `DENY` | **`DENY`** | **`ALLOW`** | `DENY` | `DENY` |
| `/api/v1/evaluation/runs` (`GET` — `sealed_100` controlled review) | `DENY` | **`ALLOW_CONTROLLED_REVIEW`** | `DENY` | **`ALLOW_CONTROLLED_REVIEW`** | **`DENY`** | **`ALLOW`** | `DENY` | `DENY` |

### 3.3 Cờ Sửa Lỗi Mã Nguồn Bắt Buộc tại Gate G1 (`G1 Code Fix Flag — Read-Only Audit`)
Qua kiểm tra đối chiếu mã nguồn hiện có (không chỉnh sửa trong phạm vi G0), các điểm sai lệch bắt buộc phải khắc phục và kiểm thử đơn vị trước khi đóng Gate G1 gồm:
1. **`backend/src/shared/auth.py` (dòng `65–72`, hàm `ensure_partition_access`):**
   - **Lỗi hiện tại trong mã nguồn G0 scaffold:** Dòng `68` đang viết `user.roles & {UserRole.INDEPENDENT_EVALUATOR, UserRole.ADMINISTRATOR}`, vô tình cấp quyền vượt tường lửa Chinese Wall cho `UserRole.ADMINISTRATOR` (bao gồm `[S5]` phía Nhà cung cấp) trên `EvalPartition.SEALED_100`, đồng thời mâu thuẫn với chính thông báo lỗi ở dòng `71` (*"sealed_100 restricted to independent_evaluator"*).
   - **Yêu cầu sửa tại G1:** Loại bỏ `UserRole.ADMINISTRATOR` khỏi điều kiện cho phép `EvalPartition.SEALED_100`; tách riêng quyền chạy/đọc thô `sealed_100` (chỉ `UserRole.INDEPENDENT_EVALUATOR`) với endpoint/scope xem báo cáo phân xử có kiểm soát dành cho Policy Reviewers Bên mua (`UserRole.POLICY_OWNER` `[P2]` & `UserRole.STEWARD` `[P3]`).
2. **`backend/src/shared/auth.py` (dòng `56–62`, hàm `check_policy_audience`):**
   - **Cần rà soát tại G1:** Dòng `58–59` hiện trả `True` vô điều kiện cho `UserRole.ADMINISTRATOR`; cần bảo đảm ngoại lệ này không áp dụng cho ranh giới `sealed_100`, dữ liệu bị Legal Hold hạn chế hoặc phân quyền tài khoản nghiệp vụ.
3. **`backend/src/shared/auth.py` (dòng `28–34`, hàm `get_current_user`):**
   - Hiện là khung fail-closed trả `501 Not Implemented`; tại G1 phải hoàn thiện xác thực OIDC/JWT doanh nghiệp, kiểm tra nhãn `env` (`SEC 06`) và tích hợp Redis Lock giới hạn `<= 5` phiên đồng thời (`PILOT_MAX_CONCURRENT_SESSIONS = 5`).
4. **`backend/src/shared/enums.py` (dòng `6–15`, lớp `UserRole`):**
   - Hiện mới có 7 giá trị (`reader`, `steward`, `policy_owner`, `referral_handler`, `administrator`, `privacy_security_owner`, `independent_evaluator`); cần bổ sung đồng bộ `publisher` và `legal_owner` (hoặc ánh xạ scope chuẩn hóa) khớp 100% với ma trận RBAC này.

---

## 4. HỢP ĐỒNG `AnswerPackage` 7 PHẦN & ĐỦ 6 CHIỀU PHẠM VI `DAT 04`

Mọi phản hồi từ `/api/v1/answer/*` phải tuân thủ cấu trúc 7 phần chuẩn (`ANS 01`, `ANS 03`, `KNW 01`, `DAT 04`) với **đúng 6 chiều phạm vi `DAT 04` theo thứ tự khóa bất biến**: `company`, `branch`, `role`, `customer_category`, `product`, `transaction_scope`.

```json
{
  "answer_id": "ans-20261117-uuid",
  "task_id": "task-crm-12345",
  "status": "answered",
  "original_question": "Sau khi đã thu đủ 03 chứng từ tiếp nhận bảo hành (ảnh tem nhãn Nameplate rõ số seri, hóa đơn/phiếu xuất kho, biên bản mô tả sự cố CRM), phiếu bảo hành động cơ công nghiệp công suất <= 37 kW được định tuyến xử lý theo tuyến nào?",
  "governing_date": "2026-11-17",
  "timezone": "Asia/Ho_Chi_Minh",
  "scope": "company:SN;branch:all;role:cskh;customer_category:b2b_enterprise;product:industrial;transaction_scope:warranty_tier1_internal",
  "is_historical": false,
  "is_future_preview": false,
  "guidance_text": "Theo quy định định tuyến hiện hành thuộc họ chính sách POL-003, khi nhân viên CSKH đã tiếp nhận đủ 03 chứng từ bắt buộc đối với động cơ công nghiệp công suất <= 37 kW, phiếu yêu cầu được định tuyến về Tuyến 1 (Đội Kỹ thuật Nội bộ — Internal Tech Lead) với thời hạn xử lý tiếp nhận trong 4 giờ làm việc. Lưu ý ranh giới bắt buộc (ANS 07): hướng dẫn này chỉ xác định tuyến chuyển tiếp quy trình nội bộ; trợ lý KHÔNG quyết định quyền được bảo hành miễn phí hay tính phí và KHÔNG cung cấp hướng dẫn tháo lắp hay tự sửa chữa thiết bị.",
  "verbatim_quotes": [
    "Yêu cầu dịch vụ và bảo hành đối với động cơ công nghiệp có công suất <= 37 kW sau khi đủ 03 chứng từ tiếp nhận bắt buộc được định tuyến xử lý tại Tuyến 1 (Internal Tech Lead) trong thời hạn 4 giờ làm việc; thẩm quyền đánh giá kỹ thuật và xác định điều kiện miễn phí hoặc tính phí thuộc bộ phận chuyên môn và chủ sở hữu chính sách."
  ],
  "citations": [
    {
      "document_id": "DOC-003",
      "document_version_id": "VER-001",
      "passage_id": "PAS-023",
      "title": "Quy chế định tuyến dịch vụ và bảo hành thiết bị công nghiệp",
      "page_number": 1,
      "clause_ref": "Điều 2.1, trang 1",
      "quoted_text": "Yêu cầu dịch vụ và bảo hành đối với động cơ công nghiệp có công suất <= 37 kW sau khi đủ 03 chứng từ tiếp nhận bắt buộc được định tuyến xử lý tại Tuyến 1 (Internal Tech Lead) trong thời hạn 4 giờ làm việc...",
      "evidence_url": "/api/v1/knowledge/passages/PAS-023"
    }
  ],
  "critical_fields": [
    {
      "field_id": "CF-009",
      "policy_id": "POL-003",
      "policy_version_id": "PV-003",
      "document_version_id": "VER-001",
      "field_name": "nguong_cong_suat_dinh_tuyen_bao_hanh_tuyen_1_kw",
      "field_type": "number",
      "operator": "<=",
      "value": "37",
      "unit": "kW",
      "currency": null,
      "approval_role": "Internal Tech Lead",
      "time_limit": "4 giờ làm việc",
      "exception_condition": "Thiết bị > 37 kW bắt buộc định tuyến Tuyến 2 (Kỹ sư Chuyên sâu / Hãng); không quyết định bảo hành miễn phí hay tính phí và không hướng dẫn tự sửa chữa (ANS 07)",
      "required_documents": [
        "anh_tem_nhan_nameplate_so_seri",
        "hoa_don_hoac_phieu_xuat_kho",
        "bien_ban_mo_ta_su_co_crm"
      ],
      "source_clause": "Điều 2.1, trang 1",
      "status": "effective"
    }
  ],
  "missing_facts": [],
  "hold_reason": null,
  "uncertainty_note": "Chỉ hướng dẫn thủ tục định tuyến nội bộ theo ngưỡng công suất đã duyệt (POL-003); không quyết định điều kiện bảo hành miễn phí/tính phí và không cung cấp hướng dẫn tháo lắp hay sửa chữa thiết bị (ANS 07).",
  "referral_target": "internal_tech_lead_pol_003",
  "internal_use_warning": "Hướng dẫn tra cứu quy trình nội bộ Song Nhật (chỉ phục vụ nhân viên được ủy quyền). Không gửi nguyên văn trích dẫn cho khách hàng, không tự quyết định quyền bảo hành miễn phí/tính phí và không cung cấp chỉ dẫn sửa chữa thiết bị (ANS 07).",
  "pii_warning": null,
  "snapshot_age_hours": 1.25,
  "llm_calls_used": 1
}
```

- **Kiểm soát 7 phần bắt buộc:** (1) `original_question`, (2) `governing_date` + `timezone` + chuỗi 6 chiều `scope` (`DAT 04`), (3) `guidance_text` (100–250 từ tiếng Việt) tách biệt `verbatim_quotes`, (4) `citations` có thể nhấp xem nguồn gốc, (5) `critical_fields` định kiểu tất định ngoài prompt với trạng thái `effective` (`KNW 03`), (6) `missing_facts` / `hold_reason` / `uncertainty_note` fail-closed khi thiếu dữ kiện hoặc xung đột (`DAT 05`), (7) `referral_target` + `internal_use_warning` (`KNW 02`, `KNW 04`).

---

## 5. DỰ THẢO ĐÁNH GIÁ PHÁP LÝ & PHÂN LOẠI AI BƯỚC ĐẦU THEO PHỤ LỤC F (`SEC 03`, `VN 05`)

> [!CAUTION]
> **RANH GIỚI THẨM QUYỀN PHÁP LÝ BẮT BUỘC (RFP Mục 9, `SEC 03`, Phụ lục F):**
> 1. Toàn bộ trích dẫn văn bản pháp luật và ngày hiệu lực dưới đây (`R02–R05`, `R10–R11`) là **dữ kiện nguồn từ Phụ lục F RFP**; **Legal Owner của Công ty Cổ phần Thiết bị Công nghiệp Song Nhật bắt buộc phải tự xác minh hiệu lực pháp luật hiện hành trước khi đưa ra kết luận pháp lý chính thức**.
> 2. Việc lưu trữ tại Việt Nam, mã hóa dữ liệu và có nhân viên rà soát (`human-in-the-loop`) **không tự động chứng minh sự tuân thủ hay miễn trừ nghĩa vụ pháp lý**.
> 3. Không được nạp dữ liệu vận hành thật hay mở Pilot cho người dùng thật tại Cổng G2 nếu chưa có văn bản thẩm định và phê duyệt chính thức của Legal Owner & Privacy/Security Owner (`SEC 03`, `VN 05`).

### 5.1 Bảng kiểm kê bước đầu theo 6 dẫn chiếu nguồn Phụ lục F RFP (`R02–R05`, `R10–R11`)

| Mã RFP | Văn bản dẫn chiếu trong RFP *(dữ kiện nguồn cần Legal Owner xác minh hiện hành)* | Ranh giới kỹ thuật & Vai trò pháp lý dự kiến (G0 Draft) | Nội dung bắt buộc trình Legal Owner thẩm định trước G2 | Trạng thái thẩm định |
|---|---|---|---|---|
| **`R02`** | **Luật Bảo vệ dữ liệu cá nhân `91/2025/QH15`** | - **Bên Kiểm soát Dữ liệu (Controller):** `Công ty Cổ phần Thiết bị Công nghiệp Song Nhật`.<br>- **Bên Xử lý Dữ liệu (Processor):** Nhà cung cấp triển khai hệ thống.<br>- **Bên Xử lý Phụ (Subprocessor):** Nhà cung cấp LLM/Embedding API & Cloud Host (kê khai tại `CKPA-18`).<br>- **Base Scope:** `0` hồ sơ khách hàng (`SEC 02`); chỉ xử lý định danh 20 nhân viên nội bộ và văn bản chính sách. | Xác minh luật hiện hành; phê duyệt phân định vai trò Controller/Processor/Subprocessor trong hợp đồng dịch vụ; xác nhận cơ sở xử lý hợp pháp đối với tài khoản 20 nhân viên nội bộ. | `[ ] Chờ ký xác nhận` *(Legal Owner)* |
| **`R03`** | **Nghị định `356/2025/NĐ-CP`** *(ghi chú đối chiếu tính kế thừa từ `NĐ 13/2023/NĐ-CP` khi kiểm tra văn bản đang có hiệu lực)* | - Giảm thiểu dữ liệu đầu vào (`pii_guard` chặn số CCCD/SĐT/email khách hàng ở G1–G2).<br>- Câu hỏi đã lọc PII + đoạn chính sách nội bộ đi qua LLM/Embedding API khu vực ngoài VN (nếu chọn Enterprise API khu vực Đông Á/Singapore) và Cloud Host đang `PENDING_G0_SELECTION` (`CKPA-18`). | Xác định luồng gọi API & lựa chọn Cloud Host (`VN IDC` hay `Singapore Cloud`) có kích hoạt hồ sơ đánh giá tác động xử lý / chuyển dữ liệu cá nhân ra nước ngoài hay không; duyệt cơ chế thông báo sự cố `<= 4` giờ (`SEC 07`). | `[ ] Chờ ký xác nhận` *(Legal Owner)* |
| **`R04`** | **Luật Trí tuệ nhân tạo `134/2025/QH15`** | - **Bên triển khai AI (Deployer):** Song Nhật.<br>- **Bên cung cấp (Provider):** Nhà cung cấp giải pháp & nhà cung cấp mô hình nền tảng.<br>- **Minh bạch:** Nhãn cảnh báo hướng dẫn nội bộ do AI hỗ trợ; tách biệt trích dẫn nguyên văn và lời giải thích.<br>- **Giám sát con người:** Hệ thống chỉ giải thích quy trình, **cấm** tự duyệt chiết khấu/ngoại lệ/bồi thường/giao dịch (`ANS 07`). | Xác minh nghĩa vụ pháp lý của Deployer vs Provider; duyệt nội dung thông điệp minh bạch trên giao diện và ma trận trách nhiệm khi xảy ra sai lệch mô hình. | `[ ] Chờ ký xác nhận` *(Legal Owner)* |
| **`R10`** | **Nghị định `142/2026/NĐ-CP`** *(hướng dẫn thi hành Luật AI — dữ kiện nguồn RFP)* | - Lưu vết hồ sơ kỹ thuật, phiên bản nguồn, prompt/selector change-control (`SEC 08`), tái kiểm thử trước khi thay đổi mô hình/prompt, nhật ký chi phí & kiểm toán nội bộ. | Thẩm định mức độ đầy đủ của hồ sơ kỹ thuật, quy trình quản lý thay đổi mô hình (`SEC 08`) và nghĩa vụ báo cáo sự cố AI (nếu áp dụng). | `[ ] Chờ ký xác nhận` *(Legal Owner)* |
| **`R11`** | **Quyết định `33/2026/QĐ-TTg`** *(Danh mục hệ thống AI rủi ro cao — dữ kiện nguồn RFP)* | - **Giả thuyết kỹ thuật sơ bộ (không phải kết luận pháp lý):** Hệ thống chỉ tra cứu chính sách nội bộ cho 20 nhân viên, **không** chấm điểm tín dụng, **không** nhận diện sinh trắc học, **không** đánh giá/tuyển dụng nhân sự tự động, **không** tự ra quyết định thương mại hay pháp lý.<br>- **Nhận định kỹ thuật ban đầu:** Dự kiến **không thuộc nhóm AI rủi ro cao** trong Base Scope (`O1` đang TẮT). | Legal Owner trực tiếp đối chiếu danh mục rủi ro cao hiện hành và ban hành quyết định phân loại rủi ro AI chính thức tại G2 (đánh giá lại riêng nếu sau này kích hoạt `O1`). | `[ ] Chờ ký xác nhận` *(Legal Owner)* |
| **`R05`** | **Luật An ninh mạng `116/2025/QH15`** | - Đề xuất kỹ thuật sơ bộ: Hệ thống thông tin nội bộ 20 người dùng, không chứa bí mật nhà nước (đề xuất phân loại ban đầu Cấp độ 2 để Legal/Security Owner xem xét).<br>- Kiểm soát kỹ thuật: `TLS 1.3`, `AES-256`, tách biệt 4 lớp Test/Prod (`SEC 06`), khóa bí mật ngoài mã nguồn, quét lỗ hổng định kỳ, cách ly `Quarantine` file CSV. | Thẩm định cấp độ an toàn hệ thống thông tin, yêu cầu lưu trữ dữ liệu trong nước (gắn trực tiếp với quyết định Cloud Host tại `CKPA-18`) và quy trình báo cáo sự cố. | `[ ] Chờ ký xác nhận` *(Legal Owner)* |

### 5.2 Lộ trình chốt pháp lý G0 -> G2
1. **Tại Cổng G0 (Sprint 1–2):** Chốt ma trận RBAC 20 người dùng (`CKPA-17`), khóa vị trí Cloud Host & Subprocessors (`CKPA-18`), chốt đề xuất lịch lưu giữ Annex C (`CKPA-19`) và gửi gói hồ sơ ban đầu cho Legal Owner Song Nhật.
2. **Tại Cổng G1 (Tuần 3–5):** Chỉ sử dụng dữ liệu kiểm thử đã làm sạch/ẩn danh PII; hoàn tất sửa lỗi mã nguồn `backend/src/shared/auth.py:65-72` (Chinese Wall `sealed_100`), triển khai OIDC/JWT + Redis 5 phiên đồng thời và bộ lọc `pii_guard`.
3. **Trước Cổng G2 (Điều kiện chặn mở Pilot dữ liệu thật):** Legal Owner và `[P5]` Privacy & Security Owner ký ban hành kết luận pháp lý & phân loại AI chính thức; không có chữ ký thì giữ trạng thái `HOLD`.

---

## 6. KHUNG XÁC NHẬN & RÀ SOÁT SPRINT 1 CỔNG G0

| Vai trò RFP | Họ và tên | Nội dung xác nhận | Trạng thái ký duyệt |
|---|---|---|:---:|
| **`[P5]` Privacy and security owners** *(Chủ trì)* | **Nguyễn Anh Khoa** | Chủ trì thiết kế RBAC 20-User, Chinese Wall `sealed_100` & Dự thảo Pháp lý/AI Annex F | `[ ] Chờ ký xác nhận` |
| **`[P1]` Purchaser sponsor / Product Owner** *(Reporter)* | **Văn Mỹ Vân** | Xác nhận tên pháp nhân, danh bạ 5 Rep Users / 20 Named Users & nghiệm thu `G0-AC05` | `[ ] Chờ ký xác nhận` |
| **`[P2]` Policy owners** *(Policy Reviewer #1)* | **Lý Hữu Tài** | Xác nhận quyền `policy_owner` & phạm vi `ALLOW_CONTROLLED_REVIEW` trên `sealed_100` | `[ ] Chờ ký xác nhận` |
| **`[P3]` Knowledge and data steward** *(Policy Reviewer #2)* | **Trần Chí Kha** | Xác nhận quyền `steward`, 6 chiều `DAT 04` & phạm vi `ALLOW_CONTROLLED_REVIEW` | `[ ] Chờ ký xác nhận` |
| **`[S1]` Named lead / Scrum Master** | **Hoàng Tiến** | Xác nhận đối chiếu tiến độ & kế hoạch sửa mã nguồn G1 cho `auth.py` / `enums.py` | `[ ] Chờ ký xác nhận` |
| **`[S3]` Retrieval and application engineer** | **Phạm Lương Yến Nhi** | Xác nhận hợp đồng `AnswerPackage` 7 phần, 6 chiều `DAT 04` & giới hạn Mục 2 | `[ ] Chờ ký xác nhận` |
| **`[S4]` Quality lead** *(Independent QA)* | **Phạm Quý Hải** | Xác nhận khóa Chinese Wall `sealed_100` (`administrator = DENY`) & tiêu chí kiểm thử G1 | `[ ] Chờ ký xác nhận` |
| **`[S5]` Operations specialist** | **Nguyễn Ngọc Duy** | Xác nhận giới hạn `administrator` (`DENY` trên `sealed_100`), Redis 5-session & `SEC 06` | `[ ] Chờ ký xác nhận` |
| **Legal Owner Song Nhật** *(Thẩm quyền pháp lý)* | *(Chờ `[P1]`/`[P5]` chỉ định định danh)* | Thẩm định văn bản pháp luật hiện hành (`R02–R05`, `R10–R11`) & phân loại AI tại G2 | `[ ] Chờ ký xác nhận` |
