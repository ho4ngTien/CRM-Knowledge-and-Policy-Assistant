> **TRẠNG THÁI:** BẢN DỰ THẢO CHỜ RÀ SOÁT & PHÊ DUYỆT (FOR REVIEW — CHƯA KÝ DUYỆT CHÍNH THỨC). Tài liệu chỉ phục vụ rà soát nghiệm thu Sprint 2 Cổng G0; không cấu thành phê duyệt PO, chữ ký pháp lý, kết luận pháp chế chính thức, báo giá ràng buộc, lệnh giải ngân hay giờ công thực tế chưa đối soát. Các mục tiêu định lượng, giả định dự thầu và ví dụ Annex E từ RFP được ghi rõ là đề xuất/tham khảo.

# `DEL 06` & `DEL01-H`: Điều khoản Vận hành, Cam kết SLA, Bảo hành Công việc, Quyền Thoát Mở (`OPS 08`), Phục hồi Thảm họa Có Replay (`OPS 07`) & Kế hoạch Benchmark `OPS 01–08`

| Thuộc tính | Giá trị |
|---|---|
| **Pháp nhân Bên mua** | Công ty Cổ phần Thiết bị Công nghiệp Song Nhật *(chờ `[P1]` / Legal Owner xác nhận chính thức theo ĐKKD)* |
| **Mã Jira / Sub-task** | `CKPA-33` (`CRM-G0-SUB22`) — thuộc Story `CKPA-32` (`CRM-G0-ST08`: Hoàn tất Điều khoản Vận hành & Pháp lý; hợp nhất phần vận hành của `CKPA-32`) |
| **Cổng & Sprint** | Cổng `G0` — Sprint 2 (`2026-11-16` .. `2026-11-20`) |
| **Mã Tiêu chí Nghiệm thu** | `G0-AC07` |
| **Tham chiếu RFP** | `Mục 1` (`Base Scope M` vs `Option O1`), `Mục 2` (`Limits / Users / Refresh / SLA`), `Mục 9` (`Gates & SLA`), `Mục 12` (`DEL 06` Operating Terms & Data/Exit Rights), `KNW 03`, `KNW 04`, `SEC 04..08`, `Phụ lục C`, `Phụ lục D` (`OPS 01–08`) |
| **Sản phẩm bàn giao** | `DEL 06` (Điều khoản Vận hành đầy đủ 8 nhóm điều khoản) & `DEL01-H` (Kiến trúc Vận hành, DR Replay & Kế hoạch Benchmark `OPS 01–08`) |
| **Chủ trì (Assignee)** | `[S5]` Nguyễn Ngọc Duy — Operations specialist *(Infra / SecOps / SLA — Nhà cung cấp)* |
| **Người giao việc (Reporter)** | `[S1]` Hoàng Tiến — Named lead / Scrum Master |
| **Phối hợp & Thẩm định** | `[P5]` Nguyễn Anh Khoa (Privacy and security owners — `CKPA-34`), `[S4]` Phạm Quý Hải (Quality lead — kiểm tra tính khả kiểm tại `CKPA-35`), `[P1]` Văn Mỹ Vân (Purchaser sponsor / PO) |
| **Tệp CSV đi kèm** | `CKPA-33_SUB22_OPS01-08_Quantitative_Benchmark_Plan.csv` (`8` kịch bản `OPS 01..OPS 08`) |
| **Đồng bộ Sprint 1** | Kế thừa và đồng bộ 100% với `CKPA-17` (RBAC/Chinese Wall), `CKPA-18` (Infra/Subprocessors), `CKPA-19` (Annex C), `CKPA-21` (Hard Caps) |

---

## 1. Phạm vi Kỹ thuật & Các Bất biến Vận hành (`Base Scope M` vs `Option O1`)

Tài liệu này hợp nhất đầy đủ bộ **Điều khoản Vận hành (`DEL 06` — RFP Mục 12)** và **Kế hoạch Kiểm thử Định lượng (`DEL01-H` — `OPS 01–08`)** làm đầu vào kiểm tra tính khả kiểm độc lập cho `[S4]` (`CKPA-35`) và tổng hợp thương mại TCO 3 năm cho `[S1]` (`CKPA-39`).

### Các ràng buộc bất biến khóa cứng:
1. **Phạm vi Cơ sở bắt buộc (`Base Scope: M — Mandatory Core`):** Phục vụ `1` công ty (`Công ty Cổ phần Thiết bị Công nghiệp Song Nhật`), `<= 20` người dùng định danh, `<= 5` phiên đồng thời, `3` họ chính sách (`POL-001..003`), `2` lược đồ UTF-8 CSV (`<= 30` tài liệu, `<= 300` đoạn `<= 6.000` ký tự Unicode, `<= 50` dòng trường trọng yếu), **`0` hồ sơ khách hàng**.
2. **Tùy chọn `O1` — Ngữ cảnh CRM Được Chọn (`Option O1 — Selected CRM Context`):** Khóa cứng **`OPTION_O1_ENABLED = False`** (TẮT hoàn toàn trong Base Scope). Mọi hạ tầng/vận hành cho `O1` là tùy chọn định giá và phê duyệt riêng biệt (`DAT 07`).
3. **Trạng thái phục vụ trực tuyến (`KNW 03`):** Trong `7` trạng thái vòng đời (`draft`, `owner_reviewed`, `approved`, `scheduled`, `effective`, `superseded`, `withdrawn`) + `2` trạng thái tiếp nhận (`feedback_candidate`, `quarantined`), chỉ duy nhất trạng thái **`effective`** được phục vụ trực tiếp cho câu hỏi hiện hành.
4. **Không truyền phát trước kiểm định (`INV-03`):** `ENABLE_ANSWER_STREAMING = False`; múi giờ chuẩn `Asia/Ho_Chi_Minh` (`UTC+7`).
5. **Khóa bảo mật dữ liệu & phân tách trách nhiệm (`SEC 04`, `CKPA-17`):**
   - Bắt buộc cấu hình cứng hóa G1–G2: `LLM_ALLOW_TRAINING = False`, `LLM_ZERO_DATA_RETENTION = True`, `LLM_TELEMETRY_ENABLED = False`.
   - **Chinese Wall `sealed_100` (`CKPA-17` `EP-27`/`EP-29`) & Quyền quản trị vòng đời (`EP-30`):** Vai trò **`administrator` (bao gồm Nhà cung cấp `[S5]`) bị `DENY` tuyệt đối** trên cả `POST`/`GET` của tập `sealed_100` và `POST /api/v1/admin/policies/{id}/transition` (sửa `backend/src/shared/auth.py:65-72` tại G1).
   - **Quyền thu hồi & ngắt khẩn cấp (`CKPA-17` `EP-31`/`EP-32`):** Vai trò **`privacy_security_owner` (`[P5]`)** được cấp quyền trực tiếp kích hoạt `/withdraw` và `/emergency-disable` song song với `policy_owner` và `administrator`.
6. **Nhà cung cấp Hạ tầng / Trung tâm Dữ liệu (`Cloud Host / DC`):** Hiện ở trạng thái **`PENDING_G0_SELECTION`** (giữa Phương án Việt Nam IDC nội địa hoặc Singapore Cloud Region theo `CKPA-18`), bắt buộc chốt `1` phương án duy nhất trước khi đóng Cổng G0 và trước thẩm định pháp lý Cổng G2.

---

## 2. Điều khoản Vận hành `DEL 06` (Đủ `8` Nhóm Điều khoản Bắt buộc theo RFP Mục 12)

### 2.1 Khung Giờ Phục vụ (`Service Hours`) & Mục tiêu Độ sẵn sàng Đề xuất (`>= 99.5%`)
- **Giờ phục vụ chuẩn (`Covered Business Hours`):** `08:00 – 17:00` giờ Việt Nam (`Asia/Ho_Chi_Minh`, `UTC+7`), Thứ Hai đến Thứ Sáu (trừ ngày lễ theo Luật Lao động Việt Nam).
- **Hỗ trợ 24/7 hoặc ngoài giờ làm việc:** **KHÔNG nằm trong Base Scope**; nếu Bên mua có nhu cầu sẽ tách thành **tùy chọn báo giá riêng biệt** tại `DEL 05` (`CKPA-39`).
- **Mục tiêu Độ sẵn sàng đề xuất (`Proposed Availability Target` — cần xác nhận tại G0):** **`>= 99.5%`** trong khung giờ phục vụ chuẩn (`OPS 06`).
  $$\text{Availability (\%)} = \left(1 - \frac{\sum \text{Thời gian gián đoạn ngoài kế hoạch trong giờ phục vụ (phút)}}{\sum \text{Tổng thời gian phục vụ chuẩn trong kỳ (phút)}}\right) \times 100\% \ge 99.5\%$$
  *(Minh họa với tháng 22 ngày làm việc = `11.880` phút phục vụ: tổng gián đoạn ngoài kế hoạch cho phép tối đa `<= 59,4` phút/tháng).*
- **Quy tắc Loại trừ & Báo cáo Nhà cung cấp Thượng nguồn (`Upstream Dependencies`):**
  - **Chỉ được phép loại trừ** khung bảo trì định kỳ đã được hai bên thỏa thuận trước bằng văn bản (thực hiện ngoài giờ phục vụ sau `19:00` hoặc cuối tuần, thông báo trước tối thiểu `>= 48` giờ tới `[P1]` và `[P5]`).
  - **Báo cáo đầu-cuối minh bạch:** Mọi gián đoạn xuất phát từ nhà cung cấp hạ tầng (`SUBP-01`) hoặc nhà cung cấp mô hình LLM/Embedding API (`SUBP-02`/`SUBP-03`) **bắt buộc được ghi nhận và báo cáo đầy đủ trong chỉ số độ sẵn sàng đầu-cuối (end-to-end availability)** gửi `[P1]` và `[P5]`, kèm tách riêng nguyên nhân gốc để đánh giá SLA và kế hoạch chuyển đổi dự phòng (`SUBP-04`).

### 2.2 Cam kết Ứng phó Sự cố (`Incident Response`) & Thông báo Sự cố Nghiêm trọng (`SEC 07`)

| Mức độ sự cố | Tiêu chí định lượng | Xác nhận (`ACK`) | Cô lập (`Containment`) | Kênh thông báo & Thẩm quyền leo thang |
|---|---|---:|---:|---|
| **Critical (`P1`)** | Ngừng phục vụ toàn hệ thống (`HTTP 5xx >= 50%` trong `>= 5` phút) hoặc không thể truy vấn/xác minh chính sách. | **`<= 2` giờ phục vụ** *(covered hours)* | **`<= 4` giờ phục vụ** *(covered hours)* | Jira Ticket + gọi/nhắn trực tiếp `[S1]`, `[P1]`, `[P5]`; kích hoạt hướng dẫn tra cứu CSV thủ công |
| **High (`P2`)** | Lỗi luồng phụ trợ (batch CSV treo, worker chậm `> 30` phút, cảnh báo `Snapshot Age > 25h`) nhưng tra cứu LKG vẫn ổn định. | **`<= 4` giờ phục vụ** | **`<= 8` giờ phục vụ** | Jira Ticket + báo `[S1]`, `[P3]` |
| **Security / Production Data / Critical-Control Incident (`SEC 07`)** | Nghi ngờ rò rỉ `PII`, vượt quyền `RBAC`/Chinese Wall, lộ chính sách `withdrawn`/tương lai hoặc hỏng kiểm soát trọng yếu. | **Kích hoạt tức thời (`T0`)** | **Thông báo chính thức `<= 4` giờ liên tục** *(elapsed hours, đồng hồ 24/7)* | Gửi đồng thời **`[P1]` Văn Mỹ Vân** & **`[P5]` Nguyễn Anh Khoa** kèm đóng băng chứng cứ (`read-only snapshot`) để phục vụ thẩm định pháp lý |

### 2.3 Phụ thuộc Nhà cung cấp, Vị trí Dữ liệu & Subprocessors (`SEC 04`, `SEC 08`)
- Đồng bộ 100% Sổ đăng ký `SUBP-01..SUBP-07` tại `CKPA-18`:
  - `SUBP-01` (Cloud Host / Compute / Storage): **`PENDING_G0_SELECTION`** (chọn `1` trong `2`: Vietnam IDC nội địa hoặc Singapore Cloud Region trước đóng G0).
  - `SUBP-02` & `SUBP-03` (Primary LLM `gpt-4o` & Embedding `text-embedding-3-small` API — Enterprise Tier): OpenAI, LLC / Microsoft Azure OpenAI Service (`PENDING_G0_SELECTION` vùng Đông Á/Singapore), bắt buộc **Enterprise DPA: Zero Data Retention (`ZDR`) + No Model Training**.
  - `SUBP-04` (Contingency Adapter): Google Cloud Vertex AI (`asia-southeast1`), chỉ kích hoạt qua quy trình thay đổi mô hình `SEC 08`.
  - `SUBP-05..SUBP-07` (PostgreSQL 16 + `pgvector`, Redis 7, Encrypted `AES-256` Backup Volume): Self-hosted hoàn toàn trong VPC cô lập của `SUBP-01`, tách biệt 4 lớp Test/Production (`SEC 06`).
- **Kiểm soát thay đổi (`SEC 08`):** Mọi thay đổi nhà cung cấp, mô hình, prompt hệ thống, bộ chọn chính sách hoặc vùng lưu trữ bắt buộc đánh giá rủi ro lại, tái chạy các bài kiểm thử bị ảnh hưởng và được `[P1]` & `[P5]` phê duyệt trước khi đưa lên Production.

### 2.4 Thời hạn Hỗ trợ (`Support Period` — RFP Mục 12 `DEL 06`)
- **Giai đoạn Pilot & Bàn giao (`G3`–`G4`):** Hỗ trợ kỹ thuật đầy đủ trong suốt tối thiểu `20` ngày làm việc quan sát có giám sát (`G3`), giai đoạn quyết định nghiệm thu `G3` và bàn giao `G4` (đã bao gồm trong phạm vi triển khai Base Scope, không phụ thu ẩn).
- **Thời hạn Hỗ trợ Sau Bàn giao (`Post-G4 Support Term`):** Chu kỳ tiêu chuẩn đề xuất **`12` tháng/kỳ**, bắt đầu tính từ ngày `[P1]` ký Biên bản Nghiệm thu `G4` (tổng tầm nhìn đối chiếu TCO là `36` tháng = `3` năm trong `DEL 05` / `CKPA-39`).
- **Phạm vi hỗ trợ chuẩn:** Vá lỗi bảo mật/dependency định kỳ, giám sát độ sẵn sàng (`OPS 06`), hỗ trợ vận hành batch/DR/withdrawal, duy trì bộ đếm chi phí & hạn mức; **không** bao gồm thay đổi tính năng mới hoặc kích hoạt `Option O1` (xử lý qua Change Request tách riêng). Đơn giá hỗ trợ hàng năm: **`PENDING_SUPPLIER_QUOTE`** tại `CKPA-39`.

### 2.5 Bảo hành Công việc (`Work Warranty` — RFP Mục 12 `DEL 06`)
- **Thời hạn bảo hành công việc đề xuất:** Tối thiểu **`90` ngày lịch** *(hoặc thời hạn dài hơn do Nhà cung cấp cam kết trong hồ sơ dự thầu `DEL 05`)* tính từ ngày ký nghiệm thu `G4`.
- **Cam kết khắc phục lỗi miễn phí:** Nhà cung cấp có trách nhiệm sửa chữa **không phát sinh chi phí** mọi khiếm khuyết phần mềm, sai lệch hợp đồng API/CSV và **đặc biệt mọi lỗi kiểm soát trọng yếu (`Critical Control Defects`: vượt quyền RBAC, sai ngày hiệu lực `UTC+7`, hỏng Conflict Hold `DAT 05`, rò rỉ nguồn `withdrawn`, sai số học `critical_fields`, vượt trần im lặng)** do mã nguồn/cấu hình của Nhà cung cấp gây ra trong thời hạn bảo hành.
- **Điều kiện đóng lỗi bảo hành (`Mandatory Independent Retest`):** Mọi bản vá lỗi bảo hành (đặc biệt liên quan tới kiểm soát trọng yếu, bảo mật hoặc thu hồi) **bắt buộc phải qua tái kiểm thử hồi quy độc lập** do `[S4]` (hoặc đơn vị QA được Bên mua ủy quyền) xác nhận `PASS` trước khi xác nhận đóng lỗi; không tự chốt lỗi bởi đội Build.

### 2.6 Điều khoản Gia hạn Minh bạch (`Renewal Terms` — RFP Mục 12 `DEL 06`)
- **Cấm tự động gia hạn khóa chặt (`No Auto-Lock Renewal`):** Hợp đồng hỗ trợ/vận hành **không tự động gia hạn ràng buộc** nếu thiếu xác nhận bằng văn bản của Bên mua (`[P1]`).
- **Thông báo trước & Công khai đơn giá:** Nhà cung cấp gửi thông báo gia hạn kèm bảng giá chi tiết từng dòng (`VND + VAT`) trước tối thiểu **`60` ngày lịch** so với ngày hết hạn kỳ hiện hành. Mọi điều chỉnh đơn giá (nếu có) phải tuân thủ trần chỉ số hóa/giới hạn tăng giá đã thỏa thuận trong hợp đồng gốc `DEL 05`.
- **Tách bạch quyền gia hạn:** Bên mua có toàn quyền gia hạn riêng gói hỗ trợ/hạ tầng Base Scope mà **không bị ép buộc mua kèm `Option O1` hay mua lại phần mã nguồn tùy chỉnh đã thanh toán**, đồng thời có quyền không gia hạn và thực thi quyền thoát mở (`Mục 2.7`) mà không chịu phí phạt chấm dứt bất hợp lý.

### 2.7 Quyền Thoát, Tính Di động Dữ liệu & Độc lập Thanh toán (`Exit Rights & Portability` — `OPS 08` & RFP Mục 12)
- **Quyền sở hữu & Truy cập Dữ liệu theo Vai trò độc lập với Tranh chấp Thanh toán (RFP Mục 12):**
  - Toàn bộ tài liệu chính sách gốc, đoạn văn bản tuyển chọn (`passages`), trường trọng yếu (`critical_fields`), ma trận thẩm quyền, phiếu chuyển tiếp (`local_referrals`), phản hồi (`feedback_candidates`) và nhật ký kiểm toán thuộc quyền sở hữu và kiểm soát tuyệt đối của **Công ty Cổ phần Thiết bị Công nghiệp Song Nhật**.
  - **Cam kết chống giữ dữ liệu làm con tin:** Quyền trích xuất dữ liệu theo phân quyền vai trò của Bên mua **không bị khóa, đình chỉ hay phụ thuộc vào các tranh chấp thanh toán hoặc thương mại**.
- **Cơ chế Xuất Dữ liệu Mở (`Portable Open Exit` — `OPS 08`):**
  - Endpoint: `GET /api/v1/audit/export-open` — vai trò được phép theo `CKPA-17` `EP-25`: `policy_owner`, `publisher`, `steward`, `administrator`, `privacy_security_owner`.
  - Định dạng mở chuẩn hóa: **`UTF-8 CSV` (RFC 4180)**, **`JSON`** và **`Markdown`**, mở và đọc được **`100%`** trên phần mềm trung lập (*Microsoft Excel, LibreOffice Calc, VS Code, trình đọc JSON chuẩn*) mà không cần công cụ giải mã độc quyền.
- **Hỗ trợ chuyển giao khi Thoát (`Exit Transition Assistance`):**
  - Tối thiểu **`30` ngày lịch** hỗ trợ song song kể từ thông báo chấm dứt/không gia hạn để Bên mua tải xuống, kiểm chứng toàn vẹn SHA-256 toàn bộ dữ liệu xuất mở và bàn giao tài liệu vận hành.
  - Sau khi `[P1]` và `[P5]` xác nhận bằng văn bản đã kiểm chứng xong bản xuất, Nhà cung cấp thực hiện hủy vật lý an toàn dữ liệu trên môi trường thuộc phạm vi kiểm soát (tôn trọng `Legal Hold` nếu có) và cấp **Chứng thư Xóa Dữ liệu (`Certificate of Sanitization`)** trong vòng `<= 15` ngày làm việc. Mọi khoản phí hỗ trợ thoát (nếu có) phải kê khai minh bạch trước tại dòng `Exit` trong `DEL 05` (`CKPA-39`).

### 2.8 Thu hồi Tức thời (`SEC 05` / `OPS 05`), Sao lưu/DR Có Replay (`OPS 07`) & Giới hạn Cứng Mục 2 (`OPS 08`)

#### A. Thu hồi Tức thời (`<= 300s`) & Ngắt Khẩn cấp (`<= 60s`)
- **Commit Authoritative DB trước ACK (`INV-06`):** `POST /api/v1/admin/policies/{policy_version_id}/withdraw` (quyền `policy_owner`, `publisher`, `administrator`, `privacy_security_owner` theo `CKPA-17` `EP-31`) bắt buộc commit trạng thái `withdrawn` đồng bộ trên `policy_versions`, `document_versions`, `passages`, `critical_fields` và đánh dấu `is_stale = True` các `answer_packages` liên quan **trước khi** trả `HTTP 200`.
- **Chặn giữa lúc sinh & Thanh lọc Cache:** Tầng 5 Validation (`ENABLE_ANSWER_STREAMING = False`) đọc live DB chặn mọi câu trả lời đang sinh (`409 POLICY_WITHDRAWN` / `STALE` — Worked Case 9); worker `withdraw_and_purge_cache` xóa sạch khóa Redis trong **`<= 300` giây (`<= 5` phút, `CACHE_WITHDRAWAL_MAX_SECONDS = 300`)**.
- **Ngắt Khẩn cấp (`Emergency Disable`):** `POST /api/v1/admin/emergency-disable` (quyền `policy_owner`, `administrator`, `privacy_security_owner` theo `CKPA-17` `EP-32`) đặt `ckpa:emergency_disable = true` làm dừng lưu lượng hỏi đáp AI trong **`<= 60` giây**, chuyển sang thông báo tra cứu CSV nội bộ thủ công.

#### B. Sao lưu `35` Ngày, `RTO <= 4h` / `RPO <= 24h` & Quy trình Khôi phục Bắt buộc Có Replay 4 Bước (`OPS 07`)
- **Lịch sao lưu:** Daily encrypted snapshot (`AES-256`) lúc `02:00` giờ `Asia/Ho_Chi_Minh`, chu kỳ xoay vòng **`35` ngày** (`Annex C`), mục tiêu **`RTO <= 4` giờ phục vụ** (`covered hours`) và **`RPO <= 24` giờ**.
- **4 bước Khôi phục Bắt buộc Có Replay (chống tái sinh dữ liệu đã xóa/thu hồi — `0% Data Resurrection`):**
  1. **Bước 1 — Khóa lưu lượng (`Maintenance Lock`):** Chặn `100%` truy cập người dùng tại Nginx Proxy (`HTTP 503 Maintenance`).
  2. **Bước 2 — Nạp Snapshot vào vùng cô lập:** Khôi phục PostgreSQL 16 + `pgvector` và kho tệp `./data` từ bản sao lưu `AES-256`.
  3. **Bước 3 — Phát lại Bắt buộc Sổ Nhật ký (`Mandatory Replay Ledger`):** Chạy kịch bản đối soát mọi sự kiện phát sinh từ mốc snapshot tới mốc sự cố: **(a)** lệnh xóa `Annex C` (`raw_exports` 90 ngày, `tombstone`, quyền chủ thể dữ liệu), **(b)** lệnh thu hồi chính sách (`withdrawn` / `quarantined`), và **(c)** thay đổi/thu hồi quyền `RBAC` trên danh bạ `20` người dùng.
  4. **Bước 4 — Xả Cache & Kiểm chứng `0%` Resurrection:** Chạy `FLUSHALL` trên Redis, kiểm chứng tự động `0%` bản ghi đã xóa/rút còn trả về ở API/UI, ghi biên bản `OPS 07`, sau đó mới mở lại cổng Nginx.

#### C. Bộ đếm Giới hạn Cứng Mục 2 (`Limit & Cost Meters` — đồng bộ `CKPA-21`)
- **Trần tháng (Giả định dự thầu cần chốt tại G0):** `<= 1.000` `AnswerPackages`/tháng (tính đủ `answered`, `HOLD` và `error`), `<= 2.000` lượt gọi LLM/tháng.
- **Trần mỗi truy vấn:** `<= 2` lượt gọi LLM/gói, `<= 8` đoạn (`<= 6.000` ký tự Unicode/đoạn), `<= 6.000` input tokens / `<= 900` output tokens (gồm instructions), timeout `20s`/call, `p95 <= 25s` tại `5` phiên đồng thời / `20` người dùng định danh.
- **Hành vi chạm trần (`OPS 08`):** Chuyển ngay sang **`HOLD` minh bạch** kèm hướng dẫn tra cứu thủ công — **tuyệt đối `0%` cắt cụt im lặng (`zero silent truncation`)**, ghi nhận đủ vào `usage_cost_meters` (`OPS 06`).

---

## 3. Kế hoạch Benchmark & Đo Kiểm Định lượng `OPS 01–08` (`Phụ lục D RFP`)

*(Chi tiết dạng bảng cấu trúc phục vụ kiểm tra tính khả kiểm tại `CKPA-35` xem tệp đi kèm **`CKPA-33_SUB22_OPS01-08_Quantitative_Benchmark_Plan.csv`**.)*

| Mã | Mục tiêu Kiểm thử | Ngưỡng PASS Định lượng | Cổng | Thực hiện | Kiểm định Độc lập |
|---|---|---|---|---|---|
| **`OPS 01`** | Batch `500` dòng UTF-8 CSV 6 chiều + idempotent retry + `10` tombstone + `Snapshot Age > 25h` | `<= 30` phút; `100%` cân bằng manifest & SHA-256; `0` bản ghi trùng; chặn `100%` batch muộn | `G1`, `G2` | `[S2]`, `[S5]` | `[S4]` Phạm Quý Hải |
| **`OPS 02`** | `100` yêu cầu qua `5` phiên đồng thời (`<= 8` đoạn, `<= 6000/900` tokens, `stream=False`) | `p95 <= 25s`; timeout `<= 20s/call`; `<= 2` calls/pkg; `0` lỗi rò rỉ phiên | `G2` | `[S3]`, `[S5]` | `[S4]` Phạm Quý Hải |
| **`OPS 03`** | Ranh giới ngày giờ `00:00:00+07:00` & `23:59:59+07:00` (`Asia/Ho_Chi_Minh`) cho `scheduled`/`effective`/`superseded` | `100%` chọn đúng phiên bản theo `governing_date` giờ VN; `0` lỗi lệch `UTC` | `G1`, `G2` | `[S3]`, `[S5]` | `[S4]` Phạm Quý Hải |
| **`OPS 04`** | Ranh giới toán tử số học (`<, <=, ==, >=, >`, `between`) & thiếu đơn vị tiền tệ (`VND`/`USD`) trên `critical_fields` | `100%` pass giá trị biên ngoài LLM; `100%` Quarantine dòng `currency` thiếu đơn vị | `G1`, `G2` | `[S3]`, `[S2]` | `[S4]` Phạm Quý Hải |
| **`OPS 05`** | Thu hồi khẩn giữa lúc sinh (Worked Case 9) + Redis cache + `Emergency Disable` | Commit DB trước ACK; purge Redis `<= 300s` (`<= 5` phút); ngắt khẩn `<= 60s`; `0%` hiển thị nguồn rút | `G2` | `[S5]`, `[S3]` | `[S4]` Phạm Quý Hải |
| **`OPS 06`** | Giám sát uptime `20` ngày làm việc (`08:00–17:00` VN) & đối soát `Cost Meter` | Uptime `>= 99.5%` (báo cáo cả upstream); `100%` request (gồm `HOLD`/lỗi) được ghi meter | `G2`, `G3` | `[S5]` | `[S4]` Phạm Quý Hải |
| **`OPS 07`** | Diễn tập DR trên bản sao lưu `35` ngày có phát sinh xóa Annex C, `withdrawn` & thu hồi RBAC sau snapshot | `RTO <= 4` giờ phục vụ; `RPO <= 24` giờ; **`0%` dữ liệu đã xóa/rút/tước quyền sống lại** sau Replay | `G4` | `[S5]`, `[S2]` | `[S4]` Phạm Quý Hải |
| **`OPS 08`** | Chạm trần `1.000` gói / `2.000` calls / `6.000` input tokens + xuất dữ liệu mở `export-open` | `100%` trả `HOLD` minh bạch; **`0%` cắt cụt im lặng**; `100%` tệp `CSV/JSON/MD` đọc được trên trình trung lập | `G4` | `[S5]`, `[S2]` | `[S4]` Phạm Quý Hải |

---

## 4. Khung Rà soát & Ký Xác nhận Cổng G0 (Chờ Phê duyệt)

| Vai trò RFP | Họ và tên | Nội dung rà soát & xác nhận | Trạng thái ký duyệt |
|---|---|---|:---:|
| `[S5]` Operations specialist *(Assignee)* | Nguyễn Ngọc Duy | Chủ trì biên soạn Điều khoản Vận hành `DEL 06` (8 nhóm) & Kế hoạch `OPS 01–08` | `[ ] Chờ ký xác nhận` |
| `[S1]` Named lead / Scrum Master *(Reporter)* | Hoàng Tiến | Đối chiếu đồng bộ điều khoản `Support / Warranty / Renewal / Exit` vào `DEL 05` (`CKPA-39`) | `[ ] Chờ ký xác nhận` |
| `[S4]` Quality lead *(Independent QA)* | Phạm Quý Hải | Kiểm tra tính khả kiểm định lượng `OPS 01–08` tại `CKPA-35` (giữ chặt SoD) | `[ ] Chờ ký xác nhận` |
| `[P5]` Privacy and security owners | Nguyễn Anh Khoa | Rà soát `SEC 04..08`, quyền `privacy_security_owner`, `OPS 07` Replay & đồng bộ `CKPA-34` | `[ ] Chờ ký xác nhận` |
| `[P1]` Purchaser sponsor / Product Owner | Văn Mỹ Vân | Xem xét chấp thuận khung điều khoản vận hành `DEL 06` & `DEL01-H` tại Cổng `G0` | `[ ] Chờ ký xác nhận` |
