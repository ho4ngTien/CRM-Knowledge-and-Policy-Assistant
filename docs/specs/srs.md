# Software Requirements Specification (SRS)
# SongNhat CRM Knowledge and Policy Assistant (CKPA)

> **Phiên bản tài liệu:** `1.0`  
> **Ngày lập:** `2026-11-15`  
> **Cơ sở hợp đồng & nghiệp vụ:** *SongNhat – CRM Knowledge and Policy Assistant RFP* (`SongNhat_CRM_Knowledge_Policy_Assistant_RFP_VI.pdf`, ngày tham chiếu `06/11/2026`)  
> **Đối tượng áp dụng:** Đội dự án `10` thành viên (`Squad A–D`) thực hiện trong ranh giới phạm vi RFP.  
> **Trạng thái:** Đặc tả chuẩn hóa làm căn cứ thiết kế, lập kế hoạch 5 Gate (`G0–G4`), chia task Jira và kiểm thử nghiệm thu độc lập.

---

## Mục lục
1. [Giới thiệu, Mục đích & Thứ tự Ưu tiên Tài liệu](#1-giới-thiệu-mục-đích--thứ-tự-ưu-tiên-tài-liệu)
2. [Phạm vi Dự án & Ranh giới Tuyệt đối theo RFP](#2-phạm-vi-dự-án--ranh-giới-tuyệt-đối-theo-rfp)
3. [Tổ chức Đội ngũ 10 Người & Hàng rào Độc lập](#3-tổ-chức-đội-ngũ-10-người--hàng-rào-độc-lập)
4. [Kiến trúc Hệ thống & Các Bất biến Bắt buộc](#4-kiến-trúc-hệ-thống--các-bất-biến-bắt-buộc)
5. [Yêu cầu Chức năng Chi tiết (SRS-FR)](#5-yêu-cầu-chức-năng-chi-tiết-srs-fr)
6. [Yêu cầu Phi chức năng (SRS-NFR)](#6-yêu-cầu-phi-chức-năng-srs-nfr)
7. [Giao diện Hệ thống, API & Hợp đồng Dữ liệu](#7-giao-diện-hệ-thống-api--hợp-đồng-dữ-liệu)
8. [Kiểm thử Độc lập, 5 Cổng Phát hành (G0–G4) & Bàn giao](#8-kiểm-thử-độc-lập-5-cổng-phát-hành-g0g4--bàn-giao)
9. [Ma trận Truy vết 100% Yêu cầu RFP (57 IDs)](#9-ma-trận-truy-vết-100-yêu-cầu-rfp-57-ids)

---

## 1. Giới thiệu, Mục đích & Thứ tự Ưu tiên Tài liệu

### 1.1 Mục đích tài liệu
Tài liệu Đặc tả Yêu cầu Phần mềm (SRS) này định nghĩa đầy đủ các yêu cầu chức năng, phi chức năng, hợp đồng dữ liệu, ranh giới bảo mật, kiến trúc tham chiếu và tiêu chí nghiệm thu cho hệ thống **SongNhat CRM Knowledge and Policy Assistant (CKPA)** — trợ lý tri thức và chính sách CRM nội bộ bằng tiếng Việt có trích dẫn nguồn chính xác dành cho nhân sự được ủy quyền tại SongNhat.

### 1.2 Bối cảnh nghiệp vụ SongNhat
- **Đơn vị mời thầu / Bên mua:** SongNhat — hoạt động trong lĩnh vực phân phối và dịch vụ sản phẩm công nghiệp (động cơ công nghiệp, bộ truyền động và truyền tải `[R01]`).
- **Mục tiêu kinh doanh:** Giảm thời gian tìm kiếm lặp lại, hạn chế các cách giải thích không nhất quán về quy trình đã phê duyệt, hỗ trợ nhân viên xác định thông tin CRM cần có, vai trò phê duyệt và phiên bản nguồn chính xác.
- **Giả thuyết chưa chứng minh:** Việc giảm sự cố tuân thủ, tỷ lệ khách hàng rời bỏ hoặc doanh số bị mất được RFP xác định là giả thuyết chưa chứng minh; không được đưa vào cam kết ROI nếu chưa đo đạc trong Pilot.

### 1.3 Thứ tự ưu tiên tài liệu (Document Precedence)
Theo Quy tắc yêu cầu của RFP (Trang 1), khi có mâu thuẫn giữa các tài liệu, thứ tự áp dụng bắt buộc từ cao xuống thấp là:
1. Hợp đồng đã ký và các phụ lục sửa đổi đã thực thi.
2. RFP (`SongNhat_CRM_Knowledge_Policy_Assistant_RFP_VI.pdf`) và các văn bản bổ sung đã phát hành.
3. Đề xuất được chấp thuận.
4. SRS này và các playbook / tài liệu thiết kế nội bộ (`docs/`).

### 1.4 Quy ước yêu cầu
- **`M` (Mandatory):** Công việc cốt lõi bắt buộc trong phạm vi cơ sở (Base Scope). Các từ *"shall"* / *"must"* thể hiện yêu cầu mang tính hợp đồng khi trao thầu.
- **`O` (Optional):** Hạng mục tùy chọn phải được báo giá, phê duyệt phạm vi, kiểm soát quyền và kiểm thử riêng; không tự động gộp vào Base Scope.
- **`O1` (Selected CRM Context):** Tùy chọn riêng (cần báo giá & ký duyệt tách biệt ở G0 nếu dùng); **cắt hoàn toàn khỏi codebase Base Scope** hiện tại.
- **Tham số chào thầu (Common Bid Basis):** Các con số quy mô và giới hạn trong RFP (Mục 2) là giả định chung để chào thầu và phải được xác nhận lại tại cổng **G0**.

---

## 2. Phạm vi Dự án & Ranh giới Tuyệt đối theo RFP

> **NGUYÊN TẮC TỐI THƯỢNG:** Toàn bộ thiết kế, mã nguồn, dữ liệu và backlog của đội `10` người **chỉ giới hạn trong phạm vi RFP**. Không tự ý thêm tính năng ngoài RFP khi chưa có Change Request được phê duyệt.

### 2.1 Ba nhóm chính sách khởi đầu đề xuất (xác nhận tại G0)
| Nhóm | Phạm vi hỗ trợ được phép (`M`) | Giới hạn cứng (Không được vượt) |
|---|---|---|
| **1. Báo giá và phê duyệt thương mại** | Giải thích thông tin CRM bắt buộc, ngưỡng điều kiện và tuyến xử lý ngoại lệ thương mại đã duyệt | Không tự cấp ngoại lệ/chiết khấu, không suy luận phê duyệt, không tự tạo điều khoản |
| **2. Xử lý thông tin khách hàng** | Giải thích quy trình ghi nhận, chỉnh sửa hoặc xác minh thông tin đã phê duyệt | Không tự tiết lộ dữ liệu khách hàng, không tự xác lập cơ sở pháp lý |
| **3. Định tuyến yêu cầu dịch vụ / bảo hành** | Xác định tài liệu cần thiết, tuyến chuyển tiếp và chủ sở hữu bảo hành được ủy quyền | Không tự quyết định quyền được bảo hành, không hướng dẫn sửa chữa thiết bị |

*(Lưu ý: Nếu một nhóm thiếu chủ sở hữu chính sách hoặc thiếu nguồn được phê duyệt tại G0 thì phải thu hẹp phạm vi hoặc cải thiện nguồn; nhà cung cấp không được tự tạo quy tắc.)*

### 2.2 Tham số Giới hạn Cơ sở (Common Bid Basis — RFP Mục 2)
| Tham số | Giới hạn Base Scope (`M`) | Ghi chú kiểm soát |
|---|---|---|
| **Tổ chức & Người dùng** | `1` công ty (SongNhat); tối đa `20` named users; `5` phiên đồng thời | Vai trò: `reader`, `policy_owner` / `publisher` (+ người thay thế), `steward`, `administrator` (có thể kết hợp nếu được duyệt và giữ độc lập) |
| **Kho tri thức** | Tối đa `30` tài liệu đã duyệt; `300` đoạn tuyển chọn (`passages`); `50` dòng `critical_fields` | Mốc G0 duyệt tối thiểu `30` đoạn + `10` dòng trường quan trọng đầu tiên; không bịa rule chỉ để đạt trần |
| **Đầu vào (Inputs)** | `2` CSV schema UTF-8: `passages` và `critical_fields` | **Không nhập hồ sơ khách hàng, lịch sử hộp thư hoặc hồ sơ CRM đầy đủ** |
| **Làm mới (Refresh)** | `1` batch hằng ngày/schema đang hoạt động; tối đa `500` dòng thay đổi/ngày | Rút chính sách (`withdrawal`) chạy tức thời, không chờ batch; hiển thị **tuổi snapshot** |
| **Yêu cầu (Requests)** | Tối đa `1.000` `answer package`/tháng (tính cả `hold` và `error`) | Mỗi package = `1` tác vụ câu hỏi. `Follow-up` và `regenerate` giữ liên kết tác vụ và vẫn tính vào mức sử dụng |
| **Giới hạn mô hình AI** | Tối đa `2` lần gọi generation/repair mỗi package; mỗi lần tối đa `6.000` input tokens (gồm instructions) và `900` output tokens; trần `2.000` calls/tháng | `Retry` dùng chung hạn mức. Vượt hạn mức phải hiển thị `hold` hoặc cần thay đổi có báo giá được chủ sở hữu duyệt |
| **Ngữ cảnh & Đầu ra** | Tối đa `8` đoạn và `6.000` ký tự Unicode mỗi mục văn bản nhập; đầu ra thường `100–250` từ tiếng Việt | Tuân thủ giới hạn token; **không cắt ngắn âm thầm**; kèm trích dẫn chính xác và trường có cấu trúc |
| **Lịch trình tham chiếu** | Tối đa `2` tuần discovery (`G0`) + `10` tuần triển khai cơ sở (gồm tối thiểu `20` ngày làm việc quan sát) | Không rút ngắn `20` ngày làm việc; không giả định `O1` vừa lịch trình cơ sở |

### 2.3 Ranh giới Tùy chọn `O1` & Các hạng mục Ngoài Phạm vi (`O`)
- **Tùy chọn `O1` — Selected CRM Context (Nằm ngoài Codebase Base Scope):**
  - Không triển khai code/endpoint hay bảng DB trong Base Scope (`M`). Nếu tại G0 (hoặc Change Request sau G0) hai bên phê duyệt báo giá tách biệt, `O1` mới được phát triển riêng cho schema CSV thứ `3` (tối đa `2.000` dòng ban đầu, `5.000` dòng lưu giữ, chọn tối đa `1` bản ghi kiểm soát và đáp ứng kiểm toán `DAT 07`).
- **Ngoài phạm vi mặc định (`O` — CẤM đưa vào Base Pilot):**
  1. Kết nối trực tiếp tới CRM hoặc kho dữ liệu sống (live connector).
  2. OCR, xử lý âm thanh/giọng nói, tích hợp kênh Zalo hoặc lịch sử mailbox.
  3. Tự động đọc/trích xuất bảng, sơ đồ hoặc PDF gốc (thuộc trách nhiệm chuẩn bị thủ công của chủ sở hữu hoặc dịch vụ hỗ trợ báo giá riêng tại G0).
  4. Ngôn ngữ hoặc nhóm chính sách ngoài `3` nhóm đã chốt (sinh câu trả lời tiếng Anh là tùy chọn `O`; không âm thầm dịch điều khoản ràng buộc).
  5. Soạn thảo phản hồi sẵn sàng gửi ra khách hàng bên ngoài (`KNW 02`).
  6. Ghi ngược dữ liệu vào CRM (`writeback`), tạo tác vụ CRM (`KNW 05`), rule engine phức tạp hoặc tự động phê duyệt/thực thi giao dịch (`ANS 07`, RFP trang 4).
  7. Ý kiến pháp lý/thuế, cấp quyền tiết lộ dữ liệu, xét duyệt điều kiện bảo hành hoặc hướng dẫn sửa chữa thiết bị (`ANS 07`).
  8. Tự động huấn luyện hoặc tự động thay đổi quy tắc chính sách từ phản hồi người dùng (`KNW 06`).
  9. Streaming (truyền phát) nội dung hướng dẫn chưa hoàn tất bước kiểm tra nguồn và quyền cuối cùng (RFP trang 4).
  10. Hỗ trợ liên tục 24/7 ngoài giờ làm việc thỏa thuận (`08:00–17:00` giờ Việt Nam ngày làm việc).

---

## 3. Tổ chức Đội ngũ 10 Người & Hàng rào Độc lập

### 3.1 Ánh xạ 10 thành viên (4 Squads) vào Vai trò RFP (Mục 2 & Mục 11)
Để cân bằng khối lượng công việc xuyên suốt 5 Gate nhưng vẫn tuân thủ nghiêm ngặt yêu cầu tách trách nhiệm và đánh giá độc lập của RFP, đội `10` người được tổ chức thành `4` Squad:

| Squad | Mã vai | Vai trò dự án | Vai trò RFP tương ứng | Phạm vi sở hữu chính trên SRS & Repo |
|---|---|---|---|---|
| **Squad A**<br>*(Điều phối & Quản trị Tri thức)* | `A1` | PM / BA Lead | Điều phối Sponsor / Delivery Lead | `WP 01`, `DEL 01`, `SEC 03`, `VN 05`, điều phối Gate `G0–G4`, quản lý `docs/`, Question Inventory & Pilot logistics |
| **Squad A** | `A2` | Policy & Knowledge Steward | Knowledge & Data Steward (+ hỗ trợ Policy Owner curation) | `DAT 01, 03, 08`, `KNW 03, 06`, `VN 04`, soạn & chuẩn hóa `30+300` passages, `10+50` critical rows, Authority/Date Matrix |
| **Squad B**<br>*(Data Pipeline & Policy Core)* | `B1` | Data & Ingestion Engineer | Supplier Integration Eng | `WP 02`, `DAT 01, 02, 08`, `OPS 01`, `OPS 08` (export), `VN 03`: `ingestion`, `knowledge`, `worker/import_task.py`, `data/templates/` |
| **Squad B** | `B2` | Policy & Lifecycle Engineer | Supplier Application Eng | `WP 03`, `WP 05` (BE), `DAT 03–06`, `KNW 03–04`, `OPS 03–04`: `policy` (Lifecycle, VN Applicability, Critical Fields, Conflict Hold) |
| **Squad B** | `B3` | Retrieval & Index Engineer | Supplier Retrieval Eng | `WP 03`, `ANS 02`, `VN 01`: `retrieval` (`pgvector` + FTS `unaccent` + từ điển viết tắt CRM), `worker/index_task.py` |
| **Squad C**<br>*(Workspace UI, LLM & SecOps)* | `C1` | Answer & Validation LLM Engineer | Supplier Application / AI Eng | `WP 04`, `ANS 01, 03–08`, `KNW 04–05`: `answer`, `validation`, `referral` BE, `prompts/`, non-streaming & final check |
| **Squad C** | `C2` | Frontend Workspace Engineer | Supplier Frontend Eng | `WP 04`, `WP 05` (UI), `KNW 01–02, 05, 07`: `frontend/src/app/*` (Split-screen `/chat`, `/evidence`, `/admin`, `/referrals`), User Manuals |
| **Squad C** | `C3` | Identity, Security & DevOps Engineer | Supplier Security / Ops Eng | `WP 06`, `SEC 01–02, 04–08`, `OPS 05–07`: `identity`, `audit`, `admin` BE, `shared/auth.py`, `pii_guard.py`, Docker/CI, 5m Cache Purge, Restore |
| **Squad D**<br>*(QA Độc lập, Thương mại & Bàn giao)* | `D1` | Independent QA & Evaluation Lead | Independent Evaluator / Quality Lead | Mục 8, `VN 02`, `DEL 03`: `evaluation`, `worker/eval_task.py`, quản lý `60/40/100` + `80 Challenges`, chấm độc lập G2 & báo cáo Pilot G3 |
| **Squad D** | `D2` | Commercial, TestOps & Handover Eng | Supplier Ops / Commercial Analyst | `WP 01` (3-route comparison), `WP 06`, `OPS 01–08`, `VN 06`, `DEL 04–06`, Annex E: OPS benchmarks, TCO 3 năm VND/VAT, Exit & Handover Pack |

### 3.2 Quy tắc Hàng rào Độc lập Bắt buộc (Chinese Wall — RFP Mục 8 & Mục 11)
1. **Cách ly tập `100 Sealed`:** Chỉ `D1` (và `A2`/`A1` khi rà soát nhãn chính sách mà **không** chỉnh code/prompt/retrieval) được tiếp cận tập `100` tác vụ nghiệm thu niêm phong. Toàn bộ thành viên `Squad B` (`B1, B2, B3`) và `Squad C` (`C1, C2, C3`) **bị cấm tuyệt đối** xem, truy cập hoặc tinh chỉnh hệ thống dựa trên các ca `100 Sealed`.
2. **Xử lý khi lộ ca Sealed:** Nếu bất kỳ ca nào trong `100 Sealed` bị lộ cho nhóm phát triển, ca đó phải được thay thế và kiểm thử lại độc lập trước khi xét Gate `G2`.
3. **Độc lập chấm điểm & Quan sát Pilot:** Người phát triển/tinh chỉnh hệ thống (`B1–B3, C1–C3`) không được tự chấm điểm nghiệm thu và không được đóng vai `Staff User` trong `20` ngày làm việc quan sát Pilot (`G3`). Tối thiểu `5` người dùng đại diện phi-lập-trình (`A1, A2, D1, D2` + đại diện nghiệp vụ/bên mua) tham gia đo công sức quan sát.
4. **Quyền sở hữu chính sách:** Quyền vận hành hoặc sở hữu nền tảng không chuyển trách nhiệm nội dung chính sách ra khỏi SongNhat (`Policy Owners`).

---

## 4. Kiến trúc Hệ thống & Các Bất biến Bắt buộc

### 4.1 Kiến trúc Tổng thể Tham chiếu
> **Lưu ý RFP Mục 6 & Mục 13:** Kiến trúc dưới đây là thiết kế triển khai đề xuất (Bounded Custom Work / Modular Monolith); không mặc định khóa nhà cung cấp, model AI hay workflow engine (không bắt buộc Camunda). Các giải pháp cấu hình sẵn được đánh giá trên cùng bộ tiêu chí kiểm thử.

- **Phong cách kiến trúc:** **Modular Monolith + Constrained RAG + Deterministic Policy Control Layer**
- **Ngăn xếp công nghệ:**
  - **Backend API:** `Python 3.12+`, `FastAPI`, `SQLAlchemy 2.0` (async), `Alembic`, `Pydantic v2`.
  - **Async Worker & Scheduler:** `Celery 5.4+`, `Redis 7` (broker, cache và instant withdrawal purge).
  - **Database & Retrieval:** `PostgreSQL 16` + `pgvector` (semantic vector) + `unaccent` / Full-Text Search tiếng Việt.
  - **Frontend Workspace:** `Next.js 14`, `React 18`, `TypeScript 5` (Split-Screen Workspace).
  - **Reverse Proxy & Data Volume:** `Nginx Alpine`, volume cục bộ `./data` lưu `2` CSV đầu vào và xuất dữ liệu mở `OPS 08` (không dựng MinIO thừa).

### 4.2 Sáu Bất biến Kiến trúc (Architectural Invariants)
| ID | Bất biến | Mô tả kỹ thuật bắt buộc | Nguồn RFP |
|---|---|---|---|
| **INV-01** | **Policy Control Outside Prompt** | Ủy quyền (`RBAC`, `audience`), trạng thái xuất bản, khoảng hiệu lực (`Asia/Ho_Chi_Minh`), phạm vi (`scope`), xung đột và giá trị `critical_fields` phải xử lý bằng code Python/SQL xác định; tuyệt đối không giao cho LLM prompt tự quyết. | Mục 6, `DAT 06`, `ANS 04` |
| **INV-02** | **Fail-Closed** | Nếu dịch vụ danh tính, quyền truy cập hoặc trạng thái thẩm quyền (`authoritative policy state`) không khả dụng hoặc không xác minh được, hệ thống phải từ chối/dừng an toàn và chuyển sang hướng dẫn tra cứu thủ công / chuyển chủ sở hữu. | `SEC 05`, `ANS 08`, Mục 9 |
| **INV-03** | **No Pre-Verification Streaming** | Chỉ phục vụ `AnswerPackage` hoàn chỉnh sau khi hoàn tất Validation và kiểm tra lần cuối về nguồn & quyền truy cập phía server. Cấm stream từng phần chưa kiểm chứng. | Mục 5 (trang 4), `KNW 04` |
| **INV-04** | **Deterministic Critical Output** | Ngưỡng, toán tử, tiền tệ, đơn vị, vai trò phê duyệt, thời hạn, ngoại lệ và tài liệu bắt buộc được chèn qua thành phần UI/schema có kiểm soát lấy trực tiếp từ DB; phần văn xuôi của LLM không được thay đổi hay tính toán lại chúng. | `DAT 06`, `ANS 04` |
| **INV-05** | **Untrusted Data Isolation** | Câu hỏi đầu vào và văn bản tài liệu nhập được xử lý như dữ liệu không đáng tin cậy, không phải chỉ thị hệ thống; không nhúng secret, không truy xuất web công khai, không cấp công cụ tùy ý cho prompt. | `ANS 08`, `SEC 06` |
| **INV-06** | **Atomic Authoritative Withdrawal** | Thao tác rút chính sách (`withdrawn`) hoặc thu hồi quyền phải ghi nhận vào authoritative state trong DB trước khi xác nhận thành công, chặn cả generation đang chạy, xóa cache vật lý Redis `<= 5 phút` và đánh dấu `stale` trên workspace đang mở. | `KNW 04`, `SEC 05`, `OPS 05` |

### 4.3 Phân bổ 12 Module Backend, Worker & Frontend
| Thành phần | Tên Module / Đường dẫn | Trách nhiệm cốt lõi theo SRS | Squad |
|---|---|---|---|
| **Backend** | `backend/src/modules/identity` | Xác thực danh tính tổ chức, JWT, kiểm tra RBAC tối thiểu & policy audience | `C3` |
| **Backend** | `backend/src/modules/knowledge` | Quản lý Document, DocumentVersion, Passage, SourceReference, Tombstone & Snapshot Age | `B1` |
| **Backend** | `backend/src/modules/ingestion` | 2 UTF-8 CSV Validators cơ sở, Quarantine, Manifest đối soát, Idempotent Retry, Late-batch guard (không có O1) | `B1` |
| **Backend** | `backend/src/modules/policy` | Authority Matrix (5 lớp), Lifecycle State Machine (7 trạng thái), Governing Date (`Asia/Ho_Chi_Minh`), Applicability, Typed Critical Fields, Conflict Hold | `B2` |
| **Backend** | `backend/src/modules/retrieval` | Hybrid search (`pgvector` + FTS `unaccent` tiếng Việt thiếu dấu + từ điển viết tắt CRM) trên tập đã lọc trước | `B3` |
| **Backend** | `backend/src/modules/answer` | Điều phối quy trình hỏi-đáp, giới hạn `8` đoạn/`6000` in/`900` out/`2` calls, prompt tiếng Việt an toàn, đóng gói `AnswerPackage` 7 phần | `C1` |
| **Backend** | `backend/src/modules/validation` | Kiểm tra citation (tồn tại clause/version/quote), khớp `critical_fields`, re-check quyền & authoritative state cuối, chặn/đánh dấu `stale` | `C1` |
| **Backend** | `backend/src/modules/referral` | Phiếu chuyển xử lý nội bộ (`referred`, `owner_responded`, `closed`) với ngữ cảnh tối thiểu (không gửi tin/tạo CRM task) | `C1` |
| **Backend** | `backend/src/modules/feedback` | Ghi nhận 5 loại phản hồi (`KNW 07`), báo cáo chủ đề thường không trả lời được, hàng đợi `feedback_candidate` (`KNW 06`) | `C2/A2` |
| **Backend** | `backend/src/modules/audit` | Nhật ký truy cập, trích dẫn, hold, withdrawal, sự cố; Cost & Quota Meter (`2000` calls/`1000` packages); Open-format Exit Export (`OPS 08`) | `C3/B1` |
| **Backend** | `backend/src/modules/evaluation` | Quản lý phân vùng (`60 Dev`, `40 Val`, `100 Sealed` cách ly, `80 Challenges`), chạy đánh giá & tổng hợp chỉ số nghiệm thu | `D1` |
| **Backend** | `backend/src/modules/admin` | Duyệt chuyển trạng thái vòng đời, kích hoạt Instant Withdrawal, theo dõi Snapshot Age & Emergency Disable | `C3/B2` |
| **Worker** | `worker/src/tasks/import_task.py` | Chạy lô batch CSV (`<= 500` dòng/`30` phút), kiểm tra `check_staleness` mỗi giờ | `B1` |
| **Worker** | `worker/src/tasks/index_task.py` | Tạo embedding vào `pgvector`, kích hoạt chính sách `scheduled` đúng giờ VN, `withdraw_and_purge_cache` (`<= 5` phút) | `B3/C3` |
| **Worker** | `worker/src/tasks/eval_task.py` | Chạy đánh giá ngoại tuyến & tổng hợp số liệu kiểm thử | `D1` |
| **Frontend** | `frontend/src/app/*` | `/`: Auth & Dashboard; `/chat`: Split-screen Workspace + Evidence Highlight; `/evidence`: Source Viewer; `/admin`: Curation & Withdrawal Console; `/referrals`: Referral & Candidate Tracker | `C2` |

---

## 5. Yêu cầu Chức năng Chi tiết (SRS-FR)

### 5.1 Nhóm FR-01: Khảo sát & Mức sẵn sàng G0 (`WP 01`, `DEL 01`, `VN 06`)
- **SRS-FR-01.1:** Hệ thống/tài liệu Discovery phải lưu giữ danh mục câu hỏi đại diện được phép sử dụng, tối thiểu phản ánh `4` tuần lịch sử câu hỏi thực tế hoặc kế hoạch kéo dài quan sát tương đương (`G0`).
- **SRS-FR-01.2:** Ghi nhận đường cơ sở (`baseline`) công sức nhân viên (bao gồm chuẩn bị, tra cứu, kiểm tra, làm lại và dự phòng) cho các tác vụ lặp lại thuộc `3` nhóm chính sách dự kiến.
- **SRS-FR-01.3:** Lập bảng so sánh có chi phí giữa `3` phương án: (1) Thư viện hiện tại có thể tìm kiếm đã làm sạch, (2) Sản phẩm cấu hình sẵn (`[R06–R08]`), và (3) Phát triển tùy chỉnh có giới hạn (`Bounded Custom Work`).
- **SRS-FR-01.4:** Tại G0, chủ sở hữu chính sách phải phê duyệt `30` đoạn nội dung đại diện đầu tiên và `10` dòng `critical_fields` đầu tiên, cùng kế hoạch ngân sách hoàn tất phần dữ liệu còn lại trước `G1`. Quyết định `O1` được lập hồ sơ độc lập.

### 5.2 Nhóm FR-02: Danh tính, Phân quyền & Kiểm soát Truy cập (`SEC 01`, `DAT 07`)
- **SRS-FR-02.1:** Tích hợp xác thực danh tính do tổ chức quản lý; áp dụng nguyên tắc đặc quyền tối thiểu (`least privilege`) cho các vai trò:
  - `reader`: tra cứu câu hỏi, xem bằng chứng được phép theo `audience`, tạo `referral` & `feedback`.
  - `steward`: chuẩn bị, nhập CSV, xử lý `quarantine`, biên tập `draft` và `feedback_candidate` (không tự phê duyệt phát hành thay `policy_owner`).
  - `policy_owner` / `publisher` (và người thay thế): rà soát, phê duyệt, lên lịch hiệu lực, thu hồi tức thời chính sách thuộc phạm vi phụ trách, phản hồi `referral`.
  - `administrator`: quản trị người dùng, cấu hình hệ thống, giám sát vận hành, `emergency disable` (không tự ý sửa nội dung chính sách).
  - `privacy_security_owner` / `legal_owner`: rà soát log audit bị hạn chế, dữ liệu pháp lý `SEC 03`, phê duyệt lưu giữ/xóa.
  - `independent_evaluator`: quyền truy xuất tập `evaluation` (`100 Sealed` & `80 Challenges`); bị tách biệt với vai trò lập trình/tinh chỉnh.
- **SRS-FR-02.2:** Kiểm tra quyền truy cập đối với `policy audience` (và quyền bản ghi `O1` nếu bật) **tại cả 3 lớp**:
  1. Trước khi truy xuất (`pre-retrieval`),
  2. Trước khi đưa vào ngữ cảnh sinh câu trả lời (`pre-generation`),
  3. Ngay trước khi hiển thị (`pre-display`).
- **SRS-FR-02.3:** Thực thi kiểm tra quyền nhất quán trên mọi đường dẫn phụ: direct URL, citation viewer, snippet, cache, log export và file download.

### 5.3 Nhóm FR-03: Nhập liệu CSV, Toàn vẹn Dữ liệu & Cách ly (`WP 02`, `DAT 01`, `DAT 02`, `DAT 08`, `OPS 01`)
- **SRS-FR-03.1:** Hỗ trợ `2` bộ validator bắt buộc cho phạm vi cơ sở dùng định dạng CSV `UTF-8`:
  1. `Passages Validator` (`<= 30` tài liệu, `<= 300` đoạn tuyển chọn, mỗi đoạn `<= 6.000` ký tự Unicode).
  2. `Critical Fields Validator` (`<= 50` dòng trường có kiểu dữ liệu).
  *(Base Scope chỉ có 2 bộ validator trên; không chứa validator hay endpoint hồ sơ khách hàng/`O1`.)*
- **SRS-FR-03.2 (`DAT 01` — Provenance):** Mỗi đoạn nội dung phải lưu ổn định: `passage_id`, `document_id`, `document_version_id`, `title`, `source_ref`, `page_number`/`clause_ref`, `language`, `owner`, `approver`, `recorded_at`, `published_at`, `effective_from`, `effective_to`, `scope`, `audience`, `status`, `supersedes`.
- **SRS-FR-03.3 (`DAT 02` — Integrity):**
  - Khai báo rõ `batch_type` (`full_snapshot` hoặc `delta`).
  - Sinh **Manifest đối soát** ghi nhận: số dòng dự kiến (`expected`), đã nhận (`received`), chấp nhận (`accepted`), từ chối (`rejected`), cách ly (`quarantined`) và danh sách lý do từng dòng.
  - Thao tác thử lại (`retry`) phải **idempotent** (không tạo bản ghi trùng).
  - Batch có `recorded_at` / thứ tự cũ đến muộn (`late batch`) **không được phép** ghi đè phiên bản mới hơn.
  - Xóa bản ghi bắt buộc phải có `record_action=tombstone` hoặc đối soát `full_snapshot` đã duyệt; **tuyệt đối không suy diễn xóa từ việc thiếu dòng**.
- **SRS-FR-03.4 (`DAT 08` — Completeness):** Các dòng vi phạm schema, vượt quá `6.000` ký tự Unicode, không đọc được hoặc có cờ thiếu chú thích/bảng/sơ đồ/tệp đính kèm thiết yếu (`has_essential_attachments=false` khi được yêu cầu) phải bị đẩy vào **Quarantine** kèm lý do cụ thể và tạm giữ quy tắc bị ảnh hưởng.
- **SRS-FR-03.5:** Ghi nhận thời điểm cập nhật thành công gần nhất và hiển thị **tuổi snapshot** (`Snapshot Age`) trên giao diện người dùng và admin; cảnh báo khi vượt ngưỡng cấu hình (`IMPORT_SNAPSHOT_STALENESS_HOURS=25`).

### 5.4 Nhóm FR-04: Thẩm quyền, Vòng đời Chính sách, Ngày Hiệu lực & Trường Trọng yếu (`WP 03`, `WP 05`, `DAT 03–06`, `KNW 03`, `OPS 03–04`)
- **SRS-FR-04.1 (`DAT 03` — Authority Matrix):** Quản lý tách biệt `5` lớp nguồn: `policy` (chính sách công ty), `SOP`, `manufacturer_terms` (điều khoản nhà sản xuất), `customer_contract` (hợp đồng khách hàng) và `staff_note` (ghi chú nhân viên / CRM note cũ). Ghi chú CRM hoặc ngoại lệ trong quá khứ chỉ được xem là lịch sử có ghi nguồn, **không tạo ra quy tắc chung** và **không tự động ghi đè** chính sách đã phát hành.
- **SRS-FR-04.2 (`KNW 03` — Publication Lifecycle):** Quản lý đầy đủ `7` trạng thái chính thức (`draft`, `owner_reviewed`, `approved`, `scheduled`, `effective`, `superseded`, `withdrawn`) cùng trạng thái phụ đầu vào (`feedback_candidate`, `quarantined`). Mọi chuyển trạng thái bắt buộc lưu `actor_id`, `role`, `timestamp` và lý do. Chính sách ở trạng thái `scheduled` không thể trở thành hiện hành trước đúng thời điểm hiệu lực theo múi giờ **`Asia/Ho_Chi_Minh`**.
- **SRS-FR-04.3 (`DAT 04`, `OPS 03` — Governing Date & Scope):**
  - Lọc theo `company`, `branch`, `role`, `customer_group`, `product`, `transaction_type`.
  - Câu hỏi quy trình chung mặc định dùng **ngày hiện tại (giờ VN)** và hiển thị rõ ngày đó.
  - Câu hỏi gắn giao dịch có ngày cụ thể áp dụng logic `governing_date` do `policy_owner` phê duyệt (truy xuất phiên bản `effective` hoặc `superseded` có hiệu lực tại ngày đó và gắn nhãn *"Hướng dẫn lịch sử"*). Nếu thiếu ngày/phạm vi tiên quyết -> yêu cầu làm rõ.
  - Phân biệt thời điểm quy tắc có hiệu lực (`effective_from`/`to`) với thời điểm hệ thống ghi nhận/chỉnh sửa (`recorded_at`). Chỉnh sửa hồi tố tạo phiên bản mới, bảo toàn lịch sử đã ghi nhận tại thời điểm cũ (khi pháp luật cho phép) và gắn cờ câu trả lời bị ảnh hưởng.
- **SRS-FR-04.4 (`DAT 05` — Conflict Hold):** Phiên bản phát hành mới nhất **không mặc nhiên** là phiên bản chi phối. Không suy luận thứ bậc ưu tiên phổ quát giữa hợp đồng khách hàng và chính sách công ty. Khi phát hiện hiệu lực chồng lấn, tương tác hợp đồng không rõ hoặc điều khoản mâu thuẫn -> hệ thống phải **HOLD kết luận bị ảnh hưởng**, hiển thị bằng chứng hợp lệ đang xung đột và chuyển `policy_owner`.
- **SRS-FR-04.5 (`DAT 06`, `OPS 04` — Typed Critical Fields):** Biểu diễn các thông số quan trọng (`threshold/value`, `operator`, `unit`, `currency`, `approval_role`, `time_limit`, `exception_condition`, `required_documents`) thành dữ liệu có kiểu rõ ràng liên kết tới `source_clause` và `policy_version_id`. Mọi tính toán/so sánh biên (`<, <=, =, >=, >`) và hiển thị ra UI được thực hiện bằng code xác định.

### 5.5 Nhóm FR-05: Truy xuất Tiếng Việt Có Kiểm soát (`ANS 02`, `VN 01`)
- **SRS-FR-05.1:** Trước khi tính điểm tương đồng/tìm kiếm, áp dụng **Pre-retrieval Filter** theo: quyền `audience` của user, trạng thái phát hành hợp lệ, khoảng hiệu lực (`governing_date` giờ VN), và các chiều `scope`. Loại bỏ triệt để `draft`, `owner_reviewed`, `approved` (chưa hiệu lực), `scheduled` (tương lai, trừ khi người dùng hỏi rõ hướng dẫn tương lai đã duyệt và được gắn nhãn tương lai), `withdrawn` và `quarantined`.
- **SRS-FR-05.2:** Hỗ trợ **Hybrid Retrieval** kết hợp tìm kiếm ngữ nghĩa (`pgvector`) và tìm kiếm từ khóa tiếng Việt (`PostgreSQL FTS + unaccent`) cùng từ điển đồng nghĩa/viết tắt CRM và thuật ngữ sản phẩm công nghiệp tiếng Anh đã được chủ sở hữu phê duyệt (`[VN 01]`).
- **SRS-FR-05.3:** Bảo toàn nguyên vẹn tên chính sách, mã quy định, số tiền, ngày tháng, đơn vị đo lường, tên vai trò và cấu trúc phủ định (*"không được"*, *"ngoại trừ"*, *"tối đa"*).
- **SRS-FR-05.4:** Giới hạn tối đa `8` đoạn văn bản (`<= 6.000` ký tự Unicode/mục) đưa vào gói ngữ cảnh của một lần truy vấn mà không cắt cụt âm thầm.

### 5.6 Nhóm FR-06: Điều phối Câu trả lời, Gói 7 Phần & 9 Tình huống Mẫu (`WP 04`, `ANS 01`, `ANS 03–08`, `KNW 01–02`, `Phụ lục B`)
- **SRS-FR-06.1 (`ANS 01`, `ANS 03` — AnswerPackage):** Hệ thống trả về đối tượng JSON `AnswerPackage` gồm đầy đủ `7` phần bắt buộc:
  1. `original_question`: Câu hỏi gốc của nhân viên (không nhập hồ sơ KH trong Base Scope).
  2. `governing_date` & `scope`: Ngày chi phối (giờ VN) và phạm vi đã khớp (kèm cờ `is_historical` hoặc `is_future_preview`).
  3. `guidance_text` & `verbatim_quotes`: Phần diễn giải tiếng Việt ngắn gọn (thường `100–250` từ), phân tách trực quan rõ ràng giữa **nguyên văn điều khoản được trích dẫn** với **phần diễn giải**.
  4. `citations`: Danh sách trích dẫn chính xác gồm `document_id`, `document_version_id`, `title`, `page_number`, `clause_ref`, `quoted_text`, link mở bản gốc.
  5. `critical_fields`: Danh sách trường quan trọng có cấu trúc lấy trực tiếp từ DB kèm điều khoản hỗ trợ (`ANS 04`).
  6. `missing_facts`, `hold_reason` & `uncertainty_note`: Thông tin còn thiếu, lý do tạm giữ kết luận (nếu có) hoặc câu hỏi làm rõ chính xác (`ANS 06`).
  7. `referral_target` & `internal_use_warning`: Tuyến chuyển chủ sở hữu kèm thông báo *"Hướng dẫn làm việc nội bộ — nhân viên phải kiểm tra hoàn cảnh, nguồn hiện hành và thẩm quyền trước khi hành động; không thay thế phê duyệt hay thực thi."* (`KNW 02`).
- **SRS-FR-06.2 (`ANS 05–08` — Guardrails & Boundaries):**
  - Giải thích tuyến ngoại lệ và bằng chứng cần nộp; **không suy luận phê duyệt** từ khách hàng VIP, lịch sử bán hàng, thâm niên hay tiền lệ cũ.
  - Khi thiếu bằng chứng/mâu thuẫn -> giải thích lý do và đặt câu hỏi làm rõ hoặc chuyển chủ sở hữu; **tuyệt đối không dùng trí nhớ mô hình, tìm kiếm web hay ghi chú CRM chưa duyệt** để lấp chỗ trống.
  - Từ chối và chuyển tuyến đúng quy trình với các yêu cầu ngoài ranh giới (`ANS 07`): tư vấn pháp lý/thuế, cấp quyền tiết lộ, duyệt bảo hành/chiết khấu, cam kết với khách hàng, hướng dẫn sửa chữa thiết bị.
  - Kiểm soát giới hạn tối đa `2` lần LLM call (generation + tối đa 1 repair) / package, mỗi call `<= 6.000` input tokens & `<= 900` output tokens.
- **SRS-FR-06.3 (9 Worked Cases — Phụ lục B RFP):** Hệ thống phải vượt qua kiểm thử hành vi bắt buộc cho cả `9` tình huống chuẩn:
  1. `General CRM question`: Giải thích trường báo giá bắt buộc không cần hồ sơ KH, trích dẫn quy trình hiện hành, nêu thông tin thiếu.
  2. `Commercial exception`: Hiển thị tuyến xử lý & ngưỡng chính xác theo phạm vi; không tự cấp chiết khấu/tạo điều khoản.
  3. `Dated transaction`: Làm rõ ngày sự kiện chi phối theo logic đã duyệt; gắn nhãn *"Hướng dẫn lịch sử"*.
  4. `Scheduled replacement`: Chính sách tương lai không chi phối hiện tại; chỉ hiện khi hỏi tương lai và gắn nhãn rõ.
  5. `Conflicting contract`: Hold kết luận bị ảnh hưởng, hiển thị bằng chứng được phép và chuyển `policy_owner`.
  6. `Old CRM note`: Coi ngoại lệ cũ là lịch sử có ghi nguồn, không biến thành quy tắc chung.
  7. `Missing footnote`: Hold ngưỡng có chú thích/bảng thiết yếu bị thiếu cho tới khi đủ ngữ cảnh duyệt.
  8. `Data correction`: Giải thích quy trình xác minh/chỉnh sửa đã duyệt; không tự tiết lộ/sửa dữ liệu.
  9. `Withdrawal mid answer`: Tạm dừng generation giữa chừng, ghi nhận withdrawal, tiếp tục kiểm tra cuối -> **giữ lại không phát câu trả lời bị ảnh hưởng** và từ chối tái sử dụng cache.
- **SRS-FR-06.4 (`KNW 04` — Final Source/Permission Check):** Ngay trước khi trả `AnswerPackage` về UI, module `validation` phải đối chiếu lại toàn bộ citation với bảng `passages`/`critical_fields` và kiểm tra lại quyền user + trạng thái nguồn hiện tại trong DB. Nếu bất kỳ nguồn nào vừa bị `withdrawn` hoặc thu hồi quyền -> **Block ngay**, đánh dấu `stale` và yêu cầu truy vấn mới.

### 5.7 Nhóm FR-07: Chuyển Xử lý Nội bộ, Phản hồi & Rút Chính sách Tức thời (`KNW 04–07`, `SEC 05`, `OPS 05`)
- **SRS-FR-07.1 (`KNW 05` — Local Referral):** Cho phép nhân viên tạo bản ghi chuyển xử lý nội bộ gắn với `answer_package_id`, ngữ cảnh tối thiểu (không copy PII dư thừa) và vấn đề chưa giải quyết. Theo dõi tách biệt `3` trạng thái: `referred`, `owner_responded`, `closed`. Nhân viên tự thực hiện gửi qua quy trình nội bộ hiện hữu (hệ thống Base Scope **không gửi email/Zalo, không tạo tác vụ CRM, không tự duyệt ngoại lệ**).
- **SRS-FR-07.2 (`KNW 06`, `KNW 07` — Feedback & Learning Candidates):** Cho phép nhân viên gắn phản hồi theo `5` phân loại RFP: `missing_source` (thiếu nguồn), `outdated_rule` (quy tắc lỗi thời), `wrong_scope` (sai phạm vi), `missing_exception` (bỏ sót ngoại lệ), `rejected` (bị từ chối). Mọi phản hồi và câu trả lời của owner chỉ được lưu làm `feedback_candidate` chờ steward/owner rà soát, phê duyệt, đánh phiên bản và gán ngày hiệu lực — **không tự động huấn luyện hoặc cập nhật rule**. Hỗ trợ báo cáo thống kê các chủ đề thường xuyên không trả lời được mà **không làm lộ ngữ cảnh trái phép**.
- **SRS-FR-07.3 (`SEC 05`, `OPS 05` — Instant Withdrawal & 5m Cache Purge):**
  - Cung cấp thao tác rút chính sách khẩn cho `policy_owner` / `administrator` (độc lập với batch ngày).
  - Tuần tự hóa thao tác rút -> cập nhật authoritative state DB -> worker xóa toàn bộ cache Redis liên quan trong **<= 5 phút (`300s`)** -> gửi tín hiệu làm mới/cảnh báo `stale` cho các phiên workspace đang mở (đồng thời ghi nhận rõ giới hạn kỹ thuật không thể thu hồi bản sao người dùng đã đọc/sao chép ra ngoài).

### 5.8 Nhóm FR-08: Kiểm toán, Đo Chi phí, Đánh giá Độc lập, Khôi phục & Thoát (`WP 06`, `OPS 06–08`, `DEL 03–06`)
- **SRS-FR-08.1 (`Audit & Usage Cost Meter`):** Ghi nhận nhật ký theo `Phụ lục C` (bảo toàn bằng chứng hạn chế truy cập, không ghi secret hoặc PII thừa). Bộ đếm `Cost Meter` phải ghi đủ: mọi gói yêu cầu (kể cả `hold` và `error`), mọi lượt `retry`, `regenerate`, số `input/output tokens`, lượt tạo `embedding`, `indexing` và dung lượng lưu trữ (`storage`). Hiển thị ngưỡng giới hạn (`1.000` packages/tháng, `2.000` LLM calls/tháng) và chặn/`hold` rõ ràng khi chạm trần (`OPS 08`: không cắt ngắn âm thầm hay retry bổ sung).
- **SRS-FR-08.2 (`Independent Evaluation Runner`):** Hỗ trợ quản lý phân vùng dữ liệu kiểm thử (`60 Dev`, `40 Val`, `100 Sealed` cô lập quyền truy cập, `80 Challenges` tách riêng báo cáo) và xuất bảng đối soát kèm mẫu số chính xác (tính cả `hold` trong mẫu số tổng).
- **SRS-FR-08.3 (`Backup, Restore & Open Export`):** Hỗ trợ sao lưu xoay vòng đề xuất `35` ngày; quy trình khôi phục (`RTO 4h`, `RPO 24h`) bắt buộc chạy **replay trạng thái xóa, thu hồi và quyền truy cập hiện hành** trước khi mở lại hệ thống cho người dùng (`OPS 07`). Cung cấp công cụ xuất dữ liệu ở định dạng mở (`JSON/CSV/Markdown`) cho passages, critical fields, versions, references, mappings và audit được phép để đọc bằng công cụ trung lập (`OPS 08`).

---

## 6. Yêu cầu Phi chức năng (SRS-NFR)

| Mã NFR | Nhóm | Chỉ tiêu / Ràng buộc Bắt buộc | Tham chiếu RFP |
|---|---|---|---|
| **SRS-NFR-01** | **Hiệu năng Import** | Xử lý `500` dòng thay đổi trong **<= 30 phút** ở môi trường đã thống nhất; đối soát đầy đủ `100%` từng dòng. | `OPS 01` |
| **SRS-NFR-02** | **Độ trễ Phản hồi** | Với `5` người dùng đồng thời, mục tiêu **p95 <= 25 giây** trên `100` yêu cầu trong giới hạn ngữ cảnh; ghi rõ thời gian từng giai đoạn, `hold`, lỗi và throttling của nhà cung cấp. | `OPS 02` |
| **SRS-NFR-03** | **Múi giờ & Ranh giới Ngày** | Mọi tính toán hiệu lực, lịch phát hành và `governing_date` sử dụng thống nhất múi giờ **`Asia/Ho_Chi_Minh`** (`UTC+7`). | `OPS 03` |
| **SRS-NFR-04** | **Tính sẵn sàng & Hỗ trợ** | Mục tiêu **99,5%** trong giờ dịch vụ thỏa thuận (`08:00–17:00` giờ VN ngày làm việc, trừ bảo trì kế hoạch). Sự cố production trọng yếu: xác nhận (`ACK`) trong `2` giờ hỗ trợ, mục tiêu cô lập `4` giờ hỗ trợ. | `OPS 06`, Mục 9 |
| **SRS-NFR-05** | **Khôi phục Thảm họa** | Mục tiêu thời gian khôi phục (`RTO`) `4` giờ hỗ trợ; điểm khôi phục (`RPO`) `24` giờ; xoay vòng backup `35` ngày; bắt buộc replay deletion/withdrawal/permission trước khi mở truy cập. | `OPS 07`, Phụ lục C |
| **SRS-NFR-06** | **Dọn Cache Thu hồi** | Chặn logic ngay tức thì sau xác nhận DB; dọn cache Redis vật lý tối đa **<= 5 phút (`300s`)**. | `SEC 05`, `OPS 05` |
| **SRS-NFR-07** | **Bảo mật Hạ tầng** | Mã hóa khi truyền (`TLS/HTTPS`) và khi lưu (`at-rest`); hạn chế tuyến outbound; quét tệp nhập; quản lý secrets hoàn toàn ngoài prompt & git; vá dependencies; tách biệt môi trường `test` và `production`. | `SEC 06` |
| **SRS-NFR-08** | **Tối thiểu hóa Dữ liệu (PII)** | Base scope không lưu hồ sơ KH; cảnh báo/lọc PII vô tình xuất hiện trong câu hỏi (`SEC 02`); không đưa PII dư thừa vào log/prompt/referral. | `SEC 02`, `VN 05` |
| **SRS-NFR-09** | **Quản trị Nhà cung cấp & Thông báo Sự cố** | Công khai địa điểm xử lý/lưu giữ/hỗ trợ (prompt, index, log, backup); cấm huấn luyện/tái sử dụng trái phép; tối thiểu telemetry; mục tiêu hợp đồng thông báo sự cố dữ liệu/kiểm soát trọng yếu nghi ngờ trong **4 giờ liên tục** kể từ khi nhận biết. | `SEC 04`, `SEC 07` |
| **SRS-NFR-10** | **Pháp lý Việt Nam (Annex F)** | Trước khi dùng dữ liệu thật (`G2`), `Legal Owner` & `Privacy/Security Owner` phải rà soát & ký duyệt phân loại AI, mục đích, cơ sở hợp pháp theo các văn bản nêu tại Phụ lục F (`Luật 91/2025/QH15`, `NĐ 356/2025/NĐ-CP`, `Luật 134/2025/QH15`, `NĐ 142/2026/NĐ-CP`, `Luật 116/2025/QH15`, `QĐ 33/2026/QĐ-TTg`). Hosting nội địa/mã hóa không tự chứng minh tuân thủ. | `SEC 03`, `VN 05`, Phụ lục F |
| **SRS-NFR-11** | **Lưu giữ Vận hành Đề xuất** | Theo Phụ lục C (đề xuất vận hành, cần Legal/Records Owner phê duyệt): Answer & Referral `<= 12` tháng; Raw exports `<= 90` ngày; Backup `35` ngày; `O1` (nếu bật) `<= 12` tháng; phân biệt chặn truy cập tức thời với hết hạn vật lý. | Phụ lục C |
| **SRS-NFR-12** | **Ngôn ngữ Việt Nam** | Hỗ trợ đầy đủ UTF-8 Unicode tiếng Việt, câu truy vấn thiếu dấu, thuật ngữ sản phẩm công nghiệp tiếng Anh trộn lẫn, viết tắt CRM, số tiền/đơn vị/ngày/phủ định. | `VN 01`, `ANS 02` |

---

## 7. Giao diện Hệ thống, API & Hợp đồng Dữ liệu

### 7.1 Giao diện Người dùng (UI Routes — Split-Screen Workspace)
1. **`/` (Home & Auth Context):** Đăng nhập danh tính tổ chức, hiển thị vai trò hiệu lực, trạng thái tổng quan `Snapshot Age`, hạn mức tháng còn lại và hướng dẫn sử dụng nội bộ / phương án tra cứu thủ công khi có sự cố.
2. **`/chat` (Split-Screen Workspace — Cốt lõi `WP 04`):**
   - **Cửa sổ Trái (Conversation & Triage):** Nhập câu hỏi + chọn `governing_date` (nếu hỏi giao dịch quá khứ/tương lai) + lọc phạm vi (`company/branch/role/customer_group/product`); cảnh báo PII (`SEC 02`); hiển thị phần giải thích ngắn gọn `100–250` từ, câu hỏi làm rõ, lý do `HOLD`, nút tạo **Local Referral** và nút **Feedback** (5 lý do `KNW 07`).
   - **Cửa sổ Phải (Evidence, Critical Fields & Status):** Hiển thị nguyên văn điều khoản trích dẫn có **highlight** mục/trang, liên kết mở nguồn gốc, bảng **Critical Fields** render xác định từ DB (ngưỡng, toán tử, đơn vị, vai trò duyệt, hạn, ngoại lệ), nhãn ngày áp dụng (`Lịch sử`/`Tương lai`/`Hiện hành`), `Snapshot Age`, banner cảnh báo `Stale` tức thì khi chính sách bị thu hồi, và thông báo *"Chỉ dùng nội bộ"*.
3. **`/evidence` (Source & Document Viewer):** Xem chi tiết tài liệu đã phê duyệt, lịch sử phiên bản (`supersedes`), trạng thái vòng đời và điều khoản nguồn theo quyền `audience`.
4. **`/admin` (Curation, Lifecycle, Withdrawal & Ops Console):** Quản lý upload 2 CSV, xem Manifest đối soát & danh sách Quarantine; luồng chuyển trạng thái `draft → owner_reviewed → approved → scheduled → effective`; nút **Instant Withdrawal**; bảng theo dõi Audit Log, Cost Meter (`tokens/calls/packages/holds/errors`) và xuất dữ liệu mở (`OPS 08`).
5. **`/referrals` (Referral & Knowledge Candidate Tracker):** Quản lý trạng thái chuyển tuyến (`referred`, `owner_responded`, `closed`) và hàng đợi `feedback_candidate` chờ `Steward`/`Policy Owner` biên tập có kiểm soát (`KNW 06`).

### 7.2 Hợp đồng API (`/api/v1/*`)
Tất cả endpoint đều gắn middleware xác thực & RBAC tại `backend/src/main.py` (không public endpoint ngoài `/health` và `/api/v1/identity/token`):
- `/api/v1/identity/*`: Đăng nhập, hồ sơ người dùng, kiểm tra vai trò & phạm vi được phép.
- `/api/v1/ingestion/*`: Upload batch CSV (`passages`, `critical_fields`), xem `manifest` đối soát & dòng `quarantine`.
- `/api/v1/knowledge/*`: Truy vấn danh sách tài liệu, phiên bản, passages đã lọc quyền và lịch sử thay thế.
- `/api/v1/policy/*`: Ma trận thẩm quyền, tra cứu `critical_fields`, đánh giá applicability theo ngày VN & phát hiện xung đột.
- `/api/v1/retrieval/*`: API nội bộ/kiểm thử truy xuất hybrid đã lọc quyền/ngày/scope (`pre-filtered`).
- `/api/v1/answer/*`: `POST /api/v1/answer` (trả `AnswerPackage` hoàn chỉnh sau `validation`, không stream), hỗ trợ `follow-up` & `regenerate` giữ `task_id`.
- `/api/v1/validation/*`: Kiểm định citation, kiểm tra authoritative state cuối & đánh dấu `stale`.
- `/api/v1/referral/*`: Tạo và cập nhật trạng thái phiếu chuyển xử lý nội bộ.
- `/api/v1/feedback/*`: Gửi phản hồi 5 phân loại `KNW 07`, báo cáo chủ đề không trả lời được, quản lý `feedback_candidate`.
- `/api/v1/admin/*`: Chuyển trạng thái vòng đời (`KNW 03`), kích hoạt **Instant Withdrawal**, kiểm tra `Snapshot Age`, `Emergency Disable`.
- `/api/v1/audit/*`: Truy vấn log audit có giới hạn quyền, xem `Cost Meter` & xuất dữ liệu mở `OPS 08`.
- `/api/v1/evaluation/*`: Tạo run đánh giá, quản lý phân vùng (chặn dev truy cập `sealed_100`), xem kết quả `real_200` tách riêng `challenges_80`.

### 7.3 Hợp đồng Dữ liệu 2 CSV UTF-8 (`data/templates/`)
Chi tiết đầy đủ kiểu dữ liệu và quy tắc kiểm tra được chốt tại [erd-and-csv-contract.md](../architecture/erd-and-csv-contract.md):
1. **`passages_template.csv` (21 cột chuẩn `DAT 01, DAT 02, DAT 08, KNW 03`):**
   `passage_id, document_id, document_version_id, title, content, source_ref, page_number, clause_ref, language, owner, approver, recorded_at, published_at, effective_from, effective_to, scope, audience, status, supersedes, has_essential_attachments, record_action`
2. **`critical_fields_template.csv` (23 cột chuẩn `DAT 06, DAT 01, DAT 02, Annex C`):**
   `field_id, policy_id, policy_version_id, document_version_id, field_name, field_type, operator, value, unit, currency, approval_role, time_limit, exception_condition, required_documents, effective_from, effective_to, scope, audience, source_clause, owner, approver, status, record_action`
*(Lưu ý: Phạm vi cơ sở không gồm CSV thứ 3 cho `O1 CRM Context`.)*

---

## 8. Kiểm thử Độc lập, 5 Cổng Phát hành (G0–G4) & Bàn giao

### 8.1 Bộ Dữ liệu Kiểm thử Độc lập (RFP Mục 8 & `VN 02`)
- **200 Tác vụ Câu hỏi Thực tế được phép:** chia theo tỷ lệ cố định `60 Development` (dev công khai), `40 Validation` (tinh chỉnh ngưỡng), `100 Sealed Acceptance` (**cô lập tuyệt đối với Dev Squad B/C**). Biến thể và bản ghi liên quan nằm cùng phân vùng. Hai người rà soát chính sách thống nhất nhãn điều khoản, ngày, phạm vi, ngoại lệ và chuyển xử lý.
- **80 Thử thách được tạo dựng (Constructed Challenges — báo cáo tách riêng):** Bao gồm chính sách tương lai/lỗi thời, ranh giới ngưỡng, thiếu chú thích/bảng, xung đột hợp đồng, sai vai trò, ghi chú CRM cũ ghi đè, prompt injection và thu hồi chính sách giữa lúc generation. Trong đó có **40 ca định hướng Việt Nam (`VN 02`)**: `10` ngôn ngữ, `10` ngày/phạm vi, `10` ngưỡng/ngoại lệ, `10` quyền/thu hồi.

### 8.2 Ngưỡng Chấp nhận Định lượng (Bắt buộc Đạt Trước G2)
| Tiêu chí Mục 8 RFP | Ngưỡng Mục tiêu | Nguyên tắc đo & Mẫu số |
|---|---|---|
| **Critical controls** | **`0` lỗi** | Không tiết lộ trái phép, không bịa trường quan trọng, không phê duyệt sai, không dùng nguồn thu hồi/tương lai làm hiện hành. Bất kỳ lỗi trọng yếu nào **chặn phát hành**. |
| **Applicability** | **`>= 95%`** | Đúng phiên bản, phạm vi và ngày chi phối trên tập `100 Sealed` có thể trả lời. |
| **Grounding & Completeness** | **`>= 95%` căn cứ; `>= 90%` đầy đủ; `0` trích dẫn bịa** | Nhận định trọng yếu có điều khoản hỗ trợ; bao gồm đủ điều khoản & ngoại lệ bắt buộc. |
| **Retrieval** | **`Recall@5 >= 90%`** | Trên tập niêm phong có bằng chứng áp dụng đã duyệt; báo riêng số ca trả lời được, không trả lời được và thiếu nguồn. |
| **Usefulness & Referral** | **`>= 80%` hữu ích; `<= 5%` bịa khi không thể trả lời** | `Hold` vẫn tính trong mẫu số tổng; ca không thể trả lời vẫn áp dụng `0` dung sai lỗi trọng yếu. |
| **Observed Effort (`G3`)** | **`>= 20` ngày làm việc; giảm `>= 20%` công sức tổng trung bình** | Chất lượng kiểm toán ngang bằng hoặc tốt hơn so với cùng corpus đã làm sạch có thể tìm kiếm; tính đủ chuẩn bị, kiểm tra, lần thử lỗi, sửa và dự phòng. |

### 8.3 Năm Cổng Phát hành (5 Release Gates — Không gộp G3 và G4)
| Gate | Tên cổng | Điều kiện & Bằng chứng bắt buộc để mở khóa giai đoạn tiếp | Sản phẩm bàn giao |
|---|---|---|---|
| **G0** | **Ready to Build** | Xác nhận 3 nhóm chính sách (hoặc thu hẹp), duyệt `30` đoạn + `10` trường đầu tiên, chứng minh câu hỏi lặp lại (`4` tuần lịch sử hoặc kế hoạch quan sát), ma trận thẩm quyền/ngày, bảng so sánh `3` phương án có giá, quyết định phạm vi cơ sở hoặc dừng (`O1` quyết định riêng). | `DEL 01` (Design) |
| **G1** | **Controlled Offline** | Toàn bộ corpus (`<=300` đoạn) & critical rows (`<=50`) hoàn tất và đối soát `100%`; xác minh phân quyền, ngày hiệu lực giờ VN, xung đột, tham chiếu gốc; test offline `60 Dev + 40 Val` đạt kiểm soát. | `DEL 02` (Offline Core) |
| **G2** | **Supervised Use** | Đạt `100%` ngưỡng kiểm soát độc lập trên `100 Sealed` + `80 Challenges` (`0` critical defects), đạt benchmark `OPS 01–07`, hoàn tất rà soát pháp lý triển khai (`SEC 03`/`Annex F`), đào tạo owners/staff và sẵn sàng phương án tra cứu thủ công dự phòng. | `DEL 02` (Full Workspace), `DEL 03` (Pre-Pilot) |
| **G3** | **Pilot Acceptance** | Hoàn tất tối thiểu `20` ngày làm việc sử dụng có giám sát với `>= 5` non-dev users; báo cáo đầy đủ công sức, sử dụng, chất lượng, chi phí thực tế (`DEL 03`) và hồ sơ thương mại TCO 3 năm VND/VAT + hoàn vốn đơn giản `<= 24` tháng (`DEL 05`). **Quyết định mở rộng tách riêng với nghiệm thu sản phẩm bàn giao.** | `DEL 03`, `DEL 05` |
| **G4** | **Handover** | Đạt kiểm thử khôi phục (`RTO 4h / RPO 24h` kèm replay xóa/rút/quyền), xóa/dọn cache, và xuất dữ liệu mở `OPS 08`; chấp nhận mã đặt hàng, mapping, cấu hình, dữ liệu kiểm thử hợp pháp, tài liệu vận hành (`DEL 06`) và bàn giao (`DEL 04`). | `DEL 04`, `DEL 06` |

---

## 9. Ma trận Truy vết 100% Yêu cầu RFP (57 IDs)

| Nhóm | Mã RFP | Đặc tả SRS tương ứng | Module / Thành phần Repo | Gate chính | Phụ trách |
|---|---|---|---|---|---|
| **Work Packages** | `WP 01` | `SRS-FR-01` | `docs/`, `data/sample/` | `G0` | `A1, A2, D2` |
| | `WP 02` | `SRS-FR-03` | `ingestion`, `knowledge`, `worker/import_task.py` | `G1` | `B1` |
| | `WP 03` | `SRS-FR-04`, `SRS-FR-05` | `policy`, `retrieval`, `worker/index_task.py` | `G1` | `B2, B3` |
| | `WP 04` | `SRS-FR-06`, `SRS-FR-07.1` | `answer`, `validation`, `referral`, `frontend/chat, evidence` | `G2` | `C1, C2` |
| | `WP 05` | `SRS-FR-04.2`, `SRS-FR-07.2–07.3` | `policy`, `admin`, `feedback`, `frontend/admin, referrals` | `G1–G2` | `B2, C2, A2` |
| | `WP 06` | `SRS-FR-08`, `SRS-NFR-*` | `audit`, `evaluation`, `infra/`, `docs/` | `G2–G4` | `C3, D1, D2` |
| **Data & Applicability** | `DAT 01` | `SRS-FR-03.2` | `knowledge`, `ingestion`, `data/templates/` | `G1` | `B1, A2` |
| | `DAT 02` | `SRS-FR-03.3` | `ingestion`, `knowledge` | `G1` | `B1` |
| | `DAT 03` | `SRS-FR-04.1` | `policy`, `docs/architecture/erd-and-csv-contract.md` | `G0–G1` | `A2, B2` |
| | `DAT 04` | `SRS-FR-04.3` | `policy` | `G1` | `B2` |
| | `DAT 05` | `SRS-FR-04.4` | `policy` | `G1` | `B2` |
| | `DAT 06` | `SRS-FR-04.5` | `policy`, `validation`, `frontend/chat` | `G1` | `B2, C2` |
| | `DAT 07` | Mục `2.3` (`O1` cắt khỏi Base Scope) | N/A trong Base Scope (chờ quyết định riêng tại `G0`) | `G0` (quyết định) | `A1` |
| | `DAT 08` | `SRS-FR-03.4` | `ingestion`, `knowledge` | `G1` | `B1, A2` |
| **Answering** | `ANS 01` | `SRS-FR-06.1` | `answer` | `G1–G2` | `C1` |
| | `ANS 02` | `SRS-FR-05.1–05.2` | `retrieval`, `policy` | `G1` | `B3, B2` |
| | `ANS 03` | `SRS-FR-06.1` | `answer`, `frontend/chat` | `G2` | `C1, C2` |
| | `ANS 04` | `INV-04`, `SRS-FR-06.1`, `06.4` | `validation`, `policy`, `frontend/chat` | `G1–G2` | `C1, B2, C2` |
| | `ANS 05` | `SRS-FR-06.2` | `answer`, `policy` | `G1–G2` | `C1, B2` |
| | `ANS 06` | `SRS-FR-06.2` | `answer`, `referral` | `G1–G2` | `C1` |
| | `ANS 07` | `SRS-FR-06.2` | `answer`, `prompts/` | `G1–G2` | `C1, C3` |
| | `ANS 08` | `INV-05`, `SRS-FR-06.2` | `answer`, `validation`, `prompts/` | `G1–G2` | `C1, C3` |
| **Knowledge & Maintenance** | `KNW 01` | `SRS-FR-06.1`, `7.1` | `frontend/chat, evidence` | `G2` | `C2` |
| | `KNW 02` | `SRS-FR-06.1`, Mục `8.3` | `frontend/chat`, `docs/user-training-guide.md` | `G2` | `C2, A1` |
| | `KNW 03` | `SRS-FR-04.2` | `policy`, `admin`, `worker/index_task.py` | `G1–G2` | `B2, C2` |
| | `KNW 04` | `INV-03`, `INV-06`, `SRS-FR-06.4` | `validation`, `admin`, `answer` | `G1–G2` | `C1, B2, C3` |
| | `KNW 05` | `SRS-FR-07.1` | `referral`, `frontend/referrals` | `G2` | `C1, C2` |
| | `KNW 06` | `SRS-FR-07.2` | `feedback`, `policy` | `G2` | `C2, A2` |
| | `KNW 07` | `SRS-FR-07.2` | `feedback`, `audit` | `G2` | `C2, C1` |
| **Security & Governance** | `SEC 01` | `SRS-FR-02` | `identity`, `shared/auth.py` | `G1` | `C3` |
| | `SEC 02` | `SRS-NFR-08` | `shared/pii_guard.py`, `answer` | `G1` | `C3` |
| | `SEC 03` | `SRS-NFR-10` | `docs/legal-privacy-review.md` | `G0` -> `G2` | `A1, D2` |
| | `SEC 04` | `SRS-NFR-09` | `docs/legal-privacy-review.md`, `.env.example` | `G0` -> `G2` | `C3, A1` |
| | `SEC 05` | `INV-06`, `SRS-FR-07.3`, `SRS-NFR-06` | `admin`, `validation`, `worker/index_task.py` | `G2` | `C3, B1` |
| | `SEC 06` | `SRS-NFR-07` | `infra/`, `.github/workflows/ci.yml`, `config.py` | `G0–G2` | `C3` |
| | `SEC 07` | `SRS-NFR-04`, `SRS-NFR-09` | `audit`, `docs/incident-runbook.md` | `G2` | `C3, A1` |
| | `SEC 08` | Mục `8.3` (Change Control) | `docs/incident-runbook.md`, `evaluation` | `G2–G3` | `A1, D1, C3` |
| **Operational Tests** | `OPS 01` | `SRS-NFR-01` | `ingestion`, `backend/tests/ops/` | `G1` -> `G2` | `B1, D2` |
| | `OPS 02` | `SRS-NFR-02` | `answer`, `backend/tests/ops/` | `G2` | `C1, D2` |
| | `OPS 03` | `SRS-FR-04.3`, `SRS-NFR-03` | `policy`, `backend/tests/ops/` | `G1` -> `G2` | `B2, D1` |
| | `OPS 04` | `SRS-FR-04.5` | `policy`, `validation`, `backend/tests/ops/` | `G1` -> `G2` | `B2, D1` |
| | `OPS 05` | `SRS-FR-07.3`, `SRS-NFR-06` | `admin`, `validation`, `backend/tests/ops/` | `G2` | `C3, D2` |
| | `OPS 06` | `SRS-NFR-04` | `infra/`, `audit` | `G2` -> `G3` | `C3, D2` |
| | `OPS 07` | `SRS-NFR-05` | `infra/`, `audit`, `backend/tests/ops/` | `G2` -> `G4` | `C3, D2` |
| | `OPS 08` | `SRS-FR-08.1`, `08.3` | `audit`, `backend/tests/ops/` | `G4` | `D2, B1` |
| **Vietnam Context** | `VN 01` | `SRS-FR-05.2`, `SRS-NFR-12` | `retrieval`, `answer`, `prompts/` | `G1–G2` | `B3, C1` |
| | `VN 02` | Mục `8.1` (`40/80` Challenges) | `evaluation`, `data/eval/` | `G1` -> `G2` | `D1` |
| | `VN 03` | `SRS-FR-03.1`, Mục `2.2` | `data/templates/`, `ingestion` | `G0–G1` | `A2, B1` |
| | `VN 04` | Mục `3.1–3.2` (Owners/Steward) | `docs/playbooks/team-playbook.md`, `policy` | `G0–G1` | `A2, A1` |
| | `VN 05` | `SRS-NFR-10` | `docs/legal-privacy-review.md` | `G0` -> `G2` | `A1, C3` |
| | `VN 06` | `SRS-FR-01.3`, Mục `8.3` | `docs/`, `DEL 05` | `G0`, `G3` | `D2, A1` |
| **Deliverables** | `DEL 01` | Mục `8.3` (`G0`) | `docs/specs/srs.md`, `docs/specs/compliance-matrix.md`, `docs/architecture/erd-and-csv-contract.md` | `G0` | `A1, A2, D1` |
| | `DEL 02` | Mục `8.3` (`G1–G2`) | `backend/`, `worker/`, `frontend/`, `prompts/` | `G1–G2` | `Squad B, C` |
| | `DEL 03` | Mục `8.1–8.3` (`G2–G3`) | `evaluation`, báo cáo đánh giá độc lập & Pilot | `G2–G3` | `D1, A1` |
| | `DEL 04` | Mục `8.3` (`G4`) | Code, config, fixtures hợp pháp, guides, exit pack | `G4` | `D2, C2, B3` |
| | `DEL 05` | Mục `8.3` (`G0`, `G3`) | Báo giá & TCO `3` năm VND/VAT, Annex E | `G3` | `D2, A1` |
| | `DEL 06` | Mục `8.3` (`G4`) | Điều khoản vận hành (`99.5%`, `08–17h`, subprocessor, exit) | `G4` | `C3, A1, D2` |

---
> **Kết luận ranh giới:** Mọi tính năng nằm ngoài bảng `57` mã yêu cầu trên (hoặc thuộc `O1` khi chưa có quyết định phê duyệt riêng tại `G0`) đều **nằm ngoài phạm vi triển khai** của đội dự án.
