> **TRẠNG THÁI:** BẢN DỰ THẢO CHỜ RÀ SOÁT & PHÊ DUYỆT (FOR REVIEW — CHƯA KÝ DUYỆT CHÍNH THỨC). Tài liệu chỉ phục vụ rà soát nghiệm thu Sprint 2 Cổng G0; không cấu thành phê duyệt PO, chữ ký pháp lý, kết luận pháp chế chính thức, báo giá ràng buộc, lệnh giải ngân hay giờ công thực tế chưa đối soát. Các mục tiêu định lượng, giả định dự thầu và ví dụ Annex E từ RFP được ghi rõ là đề xuất/tham khảo.

# `DEL01-F`: Hồ sơ Tổng hợp Rà soát Pháp lý, Quyền riêng tư, Phân loại AI (`Phụ lục F`), RBAC `20` Người dùng, Cổng Tách biệt `Option O1` & Đề xuất Lưu giữ `Phụ lục C`

| Thuộc tính | Giá trị |
|---|---|
| **Pháp nhân Bên mua** | Công ty Cổ phần Thiết bị Công nghiệp Song Nhật *(chờ `[P1]` / Legal Owner xác nhận chính thức theo ĐKKD)* |
| **Mã Jira / Sub-task** | `CKPA-34` (`CRM-G0-SUB23`) — thuộc Story `CKPA-32` (`CRM-G0-ST08`: Hoàn tất Điều khoản Vận hành & Pháp lý; hợp nhất phần pháp lý/quyền riêng tư của `CKPA-32`) |
| **Cổng & Sprint** | Cổng `G0` — Sprint 2 (`2026-11-16` .. `2026-11-20`) |
| **Mã Tiêu chí Nghiệm thu** | `G0-AC05` |
| **Tham chiếu RFP** | `Mục 1` (`Base Scope M` vs `Option O1`), `Mục 2` (`Users/Caps`), `DAT 07`, `SEC 01..08`, `VN 05`, `Mục 14` (`Deployment`), `Phụ lục C`, `Phụ lục F` (`R02–R05`, `R10`, `R11`) |
| **Sản phẩm bàn giao** | `DEL01-F`: Hồ sơ tổng hợp Pháp lý / AI / Quyền riêng tư, RBAC `20` người dùng (`5` phiên đồng thời), điều kiện pháp lý tách riêng cho `Option O1` & đề xuất lịch lưu giữ `Phụ lục C` trình Legal Owner & Records Owner |
| **Chủ trì (Assignee)** | `[P5]` Nguyễn Anh Khoa — Privacy and security owners *(Phía Bên mua)* |
| **Người giao việc (Reporter)** | `[P1]` Văn Mỹ Vân — Purchaser sponsor / Product Owner |
| **Phối hợp (RACI)** | `[P1]` Văn Mỹ Vân, `[P3]` Trần Chí Kha (Knowledge and data steward), `[S5]` Nguyễn Ngọc Duy (Operations specialist — `CKPA-18`/`CKPA-33`), `[S1]` Hoàng Tiến (Named lead) |
| **Tệp CSV đi kèm** | `CKPA-34_SUB23_AnnexF_Legal_AI_Review_Checklist.csv` (`20` hạng mục kiểm tra pháp lý/AI/bảo mật/lưu giữ) |
| **Đồng bộ Sprint 1** | Hợp nhất và chuẩn hóa toàn bộ từ `CKPA-17` (`SUB10`), `CKPA-18` (`SUB11`) và `CKPA-19` (`SUB12`) |

---

## 1. Nguyên tắc Bất biến về Ranh giới Thẩm quyền Pháp lý (`SEC 03`, `VN 05`, `Phụ lục F`)

> [!CAUTION]
> **HỒ SƠ NÀY LÀ CƠ SỞ KỸ THUẬT – QUẢN TRỊ DO `[P5]` PHỐI HỢP `[S5]` LẬP TẠI CỔNG G0, KHÔNG PHẢI KẾT LUẬN PHÁP LÝ CHÍNH THỨC THAY CHO LEGAL OWNER CỦA SONG NHẬT.**
>
> 1. **Lưu trữ trong lãnh thổ Việt Nam, mã hóa dữ liệu và có nhân viên rà soát (`human-in-the-loop`) KHÔNG tự động xác lập sự tuân thủ hay miễn trừ nghĩa vụ pháp lý.**
> 2. **Quy chế nội bộ của Công ty Cổ phần Thiết bị Công nghiệp Song Nhật không thay thế quy định pháp luật hiện hành.**
> 3. Toàn bộ `6` mã văn bản pháp quy (`R02–R05`, `R10`, `R11`) dưới đây là **dữ kiện nguồn từ Phụ lục F RFP**. **Legal Owner được ủy quyền của Song Nhật bắt buộc phải trực tiếp kiểm tra hiệu lực pháp luật hiện hành trước khi ban hành kết luận pháp lý, xác nhận phân loại AI và ký Phê duyệt Trước Cổng G2 (`Pre-G2 Gate Sign-off`)** — điều kiện chặn tuyệt đối trước khi hệ thống tiếp cận dữ liệu vận hành thật.

---

## 2. Tóm tắt Phạm vi Bảo mật, Luồng Dữ liệu (`SEC 04`) & Ma trận RBAC `20` Người dùng (`SEC 01`)

### 2.1 Ranh giới Dữ liệu Base Scope (`M`) vs `Option O1` (`O`)
- **Phạm vi Cơ sở (`Base Scope M — Mandatory Core`):** Phục vụ `1` công ty, tối đa `20` người dùng định danh (`13` `reader`, `3` `policy_owner`/`publisher`, `2` `steward`, `2` `administrator`/`privacy_security_owner` theo `CKPA-17`), tối đa `5` phiên đồng thời (Redis atomic lock), `3` họ chính sách (`<= 30` tài liệu, `<= 300` đoạn, `<= 50` dòng trường trọng yếu), **`0` hồ sơ khách hàng cá nhân (`SEC 02`)**.
- **Tùy chọn `O1` — Ngữ cảnh CRM Được Chọn (`Option O1 — Selected CRM Context`):** Khóa cứng **`OPTION_O1_ENABLED = False`** (TẮT hoàn toàn trong Base Scope; `0` bảng, `0` endpoint, `0` ngày lưu giữ dữ liệu khách hàng).
- **Khóa Chinese Wall `sealed_100` & Phân tách Quyền (`CKPA-17`):**
  - `POST`/`GET` bản ghi thô `sealed_100`: chỉ `independent_evaluator` (`[S4]` Phạm Quý Hải); `GET` báo cáo phân xử tổng hợp: `ALLOW_CONTROLLED_REVIEW` cho `[P2]` (`policy_owner`) & `[P3]` (`steward`); **`administrator` (gồm `[S5]`) = `DENY`** (cờ sửa bắt buộc `backend/src/shared/auth.py:65-72` ở G1).
  - `POST /api/v1/admin/policies/{id}/transition`: `policy_owner`, `publisher`, `steward` (**`administrator = DENY`** — không để quản trị kỹ thuật tự phê duyệt chính sách).
  - `POST /api/v1/admin/policies/{id}/withdraw` & `/emergency-disable`: cấp quyền đầy đủ cho **`privacy_security_owner` (`[P5]`)** cùng `policy_owner` và `administrator` (`CKPA-17` `EP-31`/`EP-32`).
  - `GET /api/v1/audit/logs`: hạn chế chặt cho `privacy_security_owner`, `legal_owner` và `administrator` (đã tối thiểu hóa PII).

### 2.2 Kiểm kê Luồng Dữ liệu & Subprocessors (`SEC 04`, đồng bộ `CKPA-18` & `CKPA-33`)

| Cấu phần Dữ liệu | Mục đích & Phạm vi Base Scope (`0` hồ sơ KH) | Địa điểm Xử lý & Lưu trữ | Cam kết Bảo vệ & Lưu giữ |
|---|---|---|---|
| **1. Prompts & Inferences** | Câu hỏi nhân viên (đã qua bộ lọc `pii_guard` ở G1–G2) + `<= 8` đoạn chính sách `effective` gửi sinh giải thích tiếng Việt | Xử lý RAM trên máy chủ chính (`PENDING_G0_SELECTION`) -> HTTPS `TLS 1.3` tới Enterprise LLM API (`SUBP-02`: Đông Á / Singapore) | **Enterprise ZDR + No Model Training** (`0` ngày lưu trên đĩa bên thứ ba; giải phóng RAM tức thời) |
| **2. Embeddings API Calls** | Vector hóa `<= 300` đoạn chính sách nội bộ (`text-embedding-3-small`, `1536` dim) & truy vấn tìm kiếm | HTTPS `TLS 1.3` tới Enterprise Embedding API (`SUBP-03`: Đông Á / Singapore) | **Enterprise ZDR + No Model Training** (`0` ngày lưu trên đĩa bên thứ ba) |
| **3. Knowledge & Vector Indexes** | `documents`, `document_versions`, `passages`, `critical_fields`, `passage_embeddings`, Redis cache | Self-hosted `PostgreSQL 16 + pgvector` & `Redis 7` trong VPC riêng của `SUBP-01` (**`PENDING_G0_SELECTION`**: VN IDC hoặc Singapore Cloud) | Cô lập 4 lớp Test/Prod (`SEC 06`); thu hồi tức thời chặn ở `0s` + xóa cache `<= 300s` (`OPS 05`) |
| **4. Audit Logs, Answers & Referrals** | Nhật ký truy cập/chi phí (`audit_logs`, `usage_cost_meters`), `answer_packages`, `local_referrals`, `feedback_candidates` | Self-hosted `PostgreSQL 16` trong `SUBP-01` (`PENDING_G0_SELECTION`) | Tối thiểu hóa PII; append-only; đề xuất **`<= 12` tháng** (`Phụ lục C`), tắt 100% third-party analytics |
| **5. Encrypted Backups** | Snapshot hàng ngày phục vụ DR (`RTO <= 4h` làm việc / `RPO <= 24h`) | Kho sao lưu mã hóa `AES-256` tách biệt (`SUBP-07` theo `SUBP-01`) | Xoay vòng **`35` ngày** kèm bắt buộc **4-step Replay** xóa/thu hồi/RBAC trước khi mở truy cập (`OPS 07`) |

---

## 3. Phân định Vai trò Pháp lý & Rà soát `6` Dẫn chiếu Nguồn Phụ lục F RFP (`R02–R05`, `R10`, `R11`)

### 3.1 Ma trận Phân định Vai trò Pháp lý Dự kiến *(Chờ Legal Owner xác minh theo luật hiện hành)*

| Chủ thể | Luật BVDLCN (`R02` `91/2025/QH15`; `R03` `NĐ 356/2025/NĐ-CP`) | Luật Trí tuệ Nhân tạo (`R04` `134/2025/QH15`; `R10` `NĐ 142/2026/NĐ-CP`) | Luật An ninh mạng (`R05` `116/2025/QH15`) |
|---|---|---|---|
| **Công ty Cổ phần Thiết bị Công nghiệp Song Nhật** *(Bên mua)* | Bên Kiểm soát Dữ liệu Cá nhân (*Data Controller*) | Bên Triển khai Hệ thống AI (*AI Deployer*) | Chủ quản Hệ thống Thông tin doanh nghiệp |
| **Nhà cung cấp Triển khai (`[S1]`–`[S5]`)** | Bên Xử lý Dữ liệu Cá nhân (*Data Processor*) | Bên Phát triển / Cung cấp Giải pháp AI (*AI Solution Provider*) | Đơn vị cung cấp dịch vụ kỹ thuật & vận hành an toàn thông tin |
| **Nhà cung cấp LLM/Embedding API (`SUBP-02`/`03`/`04`)** | Bên Xử lý Phụ (*Subprocessor* — Enterprise DPA / ZDR) | Nhà cung cấp Mô hình AI Nền tảng (*Foundation Model Provider*) | Nhà cung cấp dịch vụ API xử lý tức thời (không lưu trữ) |
| **Nhà cung cấp Hạ tầng (`SUBP-01`: `PENDING_G0_SELECTION`)** | Bên Xử lý Phụ hạ tầng (*Infrastructure Subprocessor*) | Nhà cung cấp hạ tầng triển khai | Đơn vị cung cấp hạ tầng trung tâm dữ liệu (VN IDC hoặc Singapore Cloud) |

### 3.2 Tổng hợp Rà soát `6` Dẫn chiếu Nguồn Phụ lục F *(Chi tiết `20` dòng xem CSV `CKPA-34_SUB23_AnnexF_Legal_AI_Review_Checklist.csv`)*

| Mã RFP | Dẫn chiếu nguồn trong RFP *(Legal Owner xác minh hiệu lực hiện hành)* | Ranh giới kỹ thuật & Thiết kế tại G0 | Câu hỏi/Thẩm định bắt buộc cho Legal Owner tại **Pre-G2 Gate Sign-off** | Trạng thái |
|---|---|---|---|---|
| **`R02`** | **Luật Bảo vệ dữ liệu cá nhân `91/2025/QH15`** | Base Scope có `0` hồ sơ khách hàng (`SEC 02`); chỉ quản lý định danh `20` nhân viên nội bộ và văn bản quy trình đã duyệt; triển khai bộ lọc `pii_guard` chặn nhập PII khách hàng ở G1–G2. | Xác minh văn bản hiện hành; phê duyệt phân định Controller/Processor/Subprocessor trong hợp đồng; xác nhận căn cứ xử lý hợp pháp và nội dung thông báo nội bộ cho `20` người dùng định danh. | `PENDING_LEGAL_OWNER_REVIEW` |
| **`R03`** | **Nghị định `356/2025/NĐ-CP`** *(kèm đối chiếu tính kế thừa/chuyển tiếp từ `NĐ 13/2023/NĐ-CP` khi Legal Owner kiểm tra hiệu lực hiện hành)* | Câu hỏi nhân viên đã qua lọc PII đi qua Enterprise LLM/Embedding API ngoài VN (`SUBP-02`/`03`) và Cloud Host đang `PENDING_G0_SELECTION` (`VN IDC` vs `Singapore`). Cơ chế thông báo sự cố `<= 4` giờ liên tục (`SEC 07`). | Thẩm định luồng API và phương án Cloud Host đã chọn có kích hoạt hồ sơ Đánh giá tác động xử lý DLCN (DPIA) và/hoặc Đánh giá tác động chuyển DLCN ra nước ngoài hay không; duyệt mẫu báo cáo cơ quan chức năng khi có sự cố. | `PENDING_LEGAL_OWNER_REVIEW` |
| **`R04`** | **Luật Trí tuệ nhân tạo `134/2025/QH15`** | Trợ lý chỉ giải thích quy trình nội bộ kèm trích dẫn nguyên văn và cảnh báo rõ vai trò hỗ trợ (`KNW 01`/`02`); cấm tuyệt đối tự động phê duyệt chiết khấu/bảo hành/giao dịch (`ANS 07`); toàn bộ ngưỡng số học chạy xác định ngoài prompt (`INV-01`/`04`). | Xác minh nghĩa vụ pháp lý Deployer vs Provider; phê duyệt câu chữ minh bạch AI trên giao diện `/chat` và điều khoản phân bổ trách nhiệm pháp lý trong hợp đồng với Nhà cung cấp. | `PENDING_LEGAL_OWNER_REVIEW` |
| **`R10`** | **Nghị định `142/2026/NĐ-CP`** *(hướng dẫn Luật AI — nguồn RFP)* | Lưu vết hồ sơ kỹ thuật (`DEL01-A..I`), phiên bản chính sách, quy trình quản lý thay đổi provider/model/prompt/selector (`SEC 08`), tái kiểm thử hồi quy trước triển khai và nhật ký kiểm toán. | Thẩm định tính đầy đủ của hồ sơ kỹ thuật AI, quy trình kiểm soát thay đổi `SEC 08` và nghĩa vụ thông báo sự cố AI bất thường (nếu thuộc diện áp dụng). | `PENDING_LEGAL_OWNER_REVIEW` |
| **`R11`** | **Quyết định `33/2026/QĐ-TTg`** *(Danh mục hệ thống AI rủi ro cao — nguồn RFP)* | **Nhận định kỹ thuật sơ bộ (KHÔNG phải kết luận pháp lý):** Trong Base Scope (`O1` TẮT), hệ thống không chấm điểm tín dụng, không sinh trắc học, không đánh giá/sa thải nhân sự tự động, không tự quyết định quyền lợi hay giao dịch; dự kiến thuộc nhóm thông thường (không rủi ro cao). | Legal Owner trực tiếp đối chiếu toàn văn danh mục rủi ro cao hiện hành và ban hành văn bản phân loại rủi ro AI chính thức trước Cổng G2; quy định tái phân loại bắt buộc nếu mở rộng tính năng hoặc bật `Option O1`. | `PENDING_LEGAL_OWNER_REVIEW` |
| **`R05`** | **Luật An ninh mạng `116/2025/QH15`** | Hệ thống nội bộ `20` người dùng, không chứa bí mật nhà nước; đề xuất kỹ thuật ban đầu Cấp độ `2`; áp dụng `TLS 1.3`, `AES-256`, tách biệt `4` lớp Test/Prod (`SEC 06`), quét lỗ hổng định kỳ và cách ly `Quarantine`. | Thẩm định hồ sơ đề xuất cấp độ an toàn hệ thống thông tin, quy định lưu trữ dữ liệu trong nước (liên kết trực tiếp quyết định `SUBP-01` Cloud Host) và quy trình ứng phó sự cố `SEC 07`. | `PENDING_LEGAL_OWNER_REVIEW` |

---

## 4. Cổng Thẩm định Pháp lý Tách riêng cho `Option O1` (`DAT 07`) & Đề xuất Lưu giữ `Phụ lục C`

### 4.1 Điều kiện Pháp lý Tách riêng cho `Option O1` — Selected CRM Context (`OFF` trong Base Scope)
- **Trạng thái G0:** `Option O1` **KHÔNG nằm trong Base Scope** (`OPTION_O1_ENABLED = False`, `0` bản ghi khách hàng, `0` ngày lưu giữ CRM context).
- **Quy tắc Chặn Cứng (`DAT 07`):** Nếu sau G3 Bên mua xem xét mua riêng `O1` (lược đồ thứ `3` allowlist `<= 2.000` khởi tạo / `<= 5.000` lưu giữ, tối đa `1` bản ghi CRM/gói, cấm PII nhạy cảm/mailbox/dossiers), bắt buộc phải hoàn tất độc lập **đủ `6` cổng thẩm định** (`CKPA-19`): (1) Chứng minh nhu cầu nghiệp vụ thực tế vượt Base Scope; (2) Cơ sở xử lý hợp pháp, thông báo/chấp thuận khách hàng & DPIA riêng theo `R02`/`R03`; (3) Quy trình xóa/đính chính đồng bộ từ CRM gốc trên đủ `6` bề mặt & xóa sớm ngay khi hết nhu cầu (`<= 12` tháng); (4) Phân quyền ngang bằng CRM nguồn (`SEC 01`); (5) Cơ chế cảnh báo độ tươi snapshot (`> 25h`); (6) Báo giá tách biệt `DEL 05` và đánh giá lại phân loại AI (`R11`).

### 4.2 Tóm tắt Đề xuất Lịch Lưu giữ `Phụ lục C`, `Legal Hold` & `Withdrawal != Deletion`
*(Toàn bộ thời hạn là đề xuất vận hành theo Phụ lục C RFP — KHÔNG phải thời hạn luật định; chờ Legal Owner & Records Owner ký duyệt tại **Pre-G2 Gate Sign-off**; chi tiết đầy đủ tại `CKPA-19`)*:

| Nhóm bản ghi | Thời hạn đề xuất (Base `M` vs `O1`) | Quy tắc Bắt buộc (`Phụ lục C`) |
|---|---|---|
| `passages` & `critical_fields` | Duy trì bản `effective` & lịch sử cần thiết (`superseded`/`withdrawn`) | **`Withdrawal != Deletion`:** Thu hồi chặn phục vụ ở `0s` + xóa cache `<= 300s`, giữ bản ghi kiểm toán hạn chế |
| `raw_exports` (vùng staging đối soát) | **Xóa sau `90` ngày** (trừ khi có duyệt giữ đối soát) | Giới hạn quyền nghiêm ngặt chỉ cho chủ đối soát (`[P3]`) |
| `answers`, `referrals`, `feedback`, `audit_logs` | Mức tối thiểu hỗ trợ khiếu nại & Pilot, **tối đa `<= 12` tháng** | Tự động làm sạch định kỳ nếu không gắn cờ `Legal Hold` |
| `o1_crm_context` (`Option O1`) | **`0` ngày trong Base Scope**; nếu mua riêng `O1`: **tối đa `<= 12` tháng và xóa sớm hơn ngay khi hết cần** | Lan truyền xóa đồng bộ trên đủ `6` bề mặt (DB, Vector, Redis, Audit, Subprocessor ZDR, 35d Backup Replay) |
| `backups` (`AES-256`) | **Xoay vòng `35` ngày** (`RTO <= 4h` làm việc / `RPO <= 24h`) | **Bắt buộc 4-step Replay** xóa/thu hồi/RBAC trước khi mở truy cập (`OPS 07`) |
| **`Legal Hold`** | Đình chỉ mọi tác vụ xóa tự động theo lệnh văn bản của Legal Owner / `[P5]` | Vẫn giữ trạng thái chặn phục vụ trực tuyến nếu nguồn đã `withdrawn` |

---

## 5. Điểm Mở Cần Thẩm định & Lộ trình `Pre-G2 Gate Sign-off`

| Mã Mở | Vấn đề Pháp lý / Bảo mật cần Chốt | Người ra quyết định | Mốc chặn |
|---|---|---|---|
| `LEG-OPEN-01` | Chốt duy nhất `1` phương án Cloud Host (`SUBP-01`: Vietnam IDC vs Singapore Cloud) để khóa bản đồ chuyển dữ liệu xuyên biên giới (`R03`, `R05`). | `[P1]`, `[P5]`, Legal Owner | Trước đóng Cổng `G0` / `Pre-G2 Gate Sign-off` |
| `LEG-OPEN-02` | Xác minh hiệu lực pháp luật hiện hành đối với `6` mã dẫn chiếu `R02–R05`, `R10`, `R11` và ban hành văn bản phân loại rủi ro AI & cấp độ ATTT chính thức. | Legal Owner & `[P5]` | `Pre-G2 Gate Sign-off` (Chặn mở dữ liệu thật) |
| `LEG-OPEN-03` | Ký phê duyệt chính thức Lịch lưu giữ `Phụ lục C` (`90d / <=12m / 35d`), quy trình `Legal Hold` và điều khoản `SEC 07` (`<= 4` giờ liên tục) / `SEC 08`. | Legal Owner & Records Owner | `Pre-G2 Gate Sign-off` |
| `LEG-OPEN-04` | Hoàn tất sửa lỗi `backend/src/shared/auth.py:65-72` (`administrator = DENY` trên `sealed_100`), triển khai `pii_guard` & Redis 5-session lock tại G1. | `[S2]`, `[S3]`, `[S5]` (QA `[S4]` xác minh) | Nghiệm thu Cổng `G1` & `G2` |

---

## 6. Khung Rà soát & Ký Xác nhận Cổng G0 (Chờ Phê duyệt)

| Vai trò RFP / Thẩm quyền | Họ và tên | Nội dung xác nhận | Trạng thái ký duyệt |
|---|---|---|:---:|
| `[P5]` Privacy and security owners *(Assignee)* | Nguyễn Anh Khoa | Chủ trì hợp nhất `DEL01-F` (Pháp lý/AI, RBAC 20-User, O1 Gate, Annex C) | `[ ] Chờ ký xác nhận` |
| `[P1]` Purchaser sponsor / Product Owner *(Reporter)* | Văn Mỹ Vân | Xác nhận phạm vi Base Scope (`0` hồ sơ KH, `O1` OFF) & lộ trình `Pre-G2 Gate Sign-off` | `[ ] Chờ ký xác nhận` |
| `[P3]` Knowledge and data steward *(RACI)* | Trần Chí Kha | Xác nhận quy trình đối soát `raw_exports` (`90` ngày) & quyền nguồn `G0-AC03` | `[ ] Chờ ký xác nhận` |
| `[S5]` Operations specialist *(RACI)* | Nguyễn Ngọc Duy | Xác nhận tính nhất quán với `CKPA-18`/`CKPA-33` (`SEC 04..08`, `OPS 05/07`) | `[ ] Chờ ký xác nhận` |
| **Legal Owner Song Nhật** *(Thẩm quyền pháp lý)* | *(Chờ `[P1]`/`[P5]` chỉ định định danh)* | Xác minh pháp luật hiện hành (`R02–R05`, `R10`, `R11`) & ký `Pre-G2 Gate Sign-off` | `[ ] Chờ ký xác nhận` |
| **Records Owner Song Nhật** *(Thẩm quyền lưu trữ)* | *(Chờ `[P1]`/`[P5]` chỉ định định danh)* | Phê duyệt lịch lưu giữ chính thức `Phụ lục C` & quy trình `Legal Hold` | `[ ] Chờ ký xác nhận` |
