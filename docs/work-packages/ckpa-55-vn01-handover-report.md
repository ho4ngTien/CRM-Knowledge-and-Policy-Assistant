# BÁO CÁO BÀN GIAO & MINH CHỨNG HOÀN THÀNH SUB-TASK CKPA-55
## [G1][VN01] Chuẩn bị 100 Câu hỏi thực & Từ điển VN

> **Mã công việc (Jira):** `CKPA-55` | **Mã gốc (Excel G1):** `CRM-G1-SUB08`  
> **Tiêu chí nghiệm thu Cổng G1:** `G1-AC07`  
> **Nhánh Git làm việc:** `uat/CRM-G1-SUB08-100-real-tasks-vn01-terms`  
> **Phía phụ trách:** Purchaser (SongNhat)  
> **Assignee / Lead:** `[P4] Ngô Thị Trà My (Staff users)`  
> **Collaborators / RACI:** `[P5] Nguyễn Anh Khoa`, `[S3] Yến Nhi`  
> **Reporter / Nghiệm thu (PO):** `[P1] Mỹ Vân (Purchaser sponsor)`  
> **Người tiếp nhận bàn giao:** `[S4] Quý Hải (Quality Lead)` & `[S3] Yến Nhi (Retrieval Engineer)`  
> **Truy vết RFP:** Mục 8 (Evaluation), Mục 11 (Team Ownership), ANS 02, SEC 02, SEC 06, VN 01.

---

## 1. TỔNG QUAN VÀ MỤC TIÊU CÔNG VIỆC

Theo yêu cầu Cổng G1 (Mục 8 & Mục 11 RFP) và kế hoạch phân công tại tệp `PhanCongCongViec_G1.xlsx`, vai trò **P4 (Người dùng nghiệp vụ đại diện)** cùng 4 nhân sự nghiệp vụ SongNhat thực hiện nhiệm vụ:
1. **Làm sạch và bàn giao 100 câu hỏi thực tế đầu tiên** (gồm 60 ca `DEV` và 40 ca `VAL`), bảo đảm **0% PII** (thông tin định danh cá nhân) theo quy định bảo mật `SEC 02` và `SEC 06`.
2. **Tổng hợp Bảng Từ điển Viết tắt CRM & Thuật ngữ Tiếng Việt (`VN 01 Profile`)**, bao gồm tiếng Việt không dấu, chữ viết tắt CRM và thuật ngữ song ngữ Anh – Việt phục vụ trực tiếp cho module Chuẩn hóa truy vấn (`ANS 02`) của kỹ sư truy xuất `S3`.

---

## 2. KẾT QUẢ BÀN GIAO 1: 100 CÂU HỎI THỰC TẾ ĐỢT 1 (100% SẠCH PII)

### 2.1 Cấu trúc và Phân bổ dữ liệu
Tập 100 câu hỏi thực tế được chọn lọc và kiểm duyệt từ kho câu hỏi nghiệp vụ thực tế, phân rã chính xác theo 3 họ quy trình CRM của SongNhat:

| Họ chính sách | Tên quy trình nghiệp vụ | Số lượng ca `DEV` | Số lượng ca `VAL` | Tổng số câu hỏi |
|---|---|:---:|:---:|:---:|
| **`POL-CRM-01`** | Quy trình Báo giá & Phê duyệt Thương mại | 24 | 16 | **40 câu** (40%) |
| **`POL-CRM-02`** | Quy trình Tiếp nhận Dịch vụ & Bảo hành Kỹ thuật | 18 | 12 | **30 câu** (30%) |
| **`POL-CRM-03`** | Quy trình Xử lý Thông tin & Dữ liệu Khách hàng | 18 | 12 | **30 câu** (30%) |
| **Tổng cộng** | **3 họ chính sách cốt lõi** | **60 ca** | **40 ca** | **100 ca thực tế** |

### 2.2 Kết quả Kiểm tra An toàn Bảo mật PII (SEC 02 & SEC 06)
- **Phương pháp rà soát:** Kết hợp kiểm tra tự động qua biểu thức chính quy (Regex Scan) và rà soát thủ công 100% bởi P4 và P5:
  - Kiểm tra số điện thoại: **0 phát hiện** (Không chứa bất kỳ SĐT cá nhân nào).
  - Kiểm tra Căn cước công dân / CMND: **0 phát hiện** (Không chứa số định danh 9 hoặc 12 chữ số).
  - Kiểm tra Email cá nhân: **0 phát hiện** (Chỉ chứa tên miền giả lập hoặc domain tổ chức mẫu).
  - Kiểm tra định danh khách hàng thật: Toàn bộ tên công ty, khách hàng đều được ẩn danh hóa hoặc dùng mã hóa định danh mẫu (`Khách hàng doanh nghiệp B2B`, `Đại lý A`, `Công ty Cơ điện X`).
- **Trạng thái đồng thuận:** 100% câu hỏi đã có trạng thái đồng thuận nhãn điều khoản vàng (`Gold_Clause_IDs`), phiên bản vàng (`Gold_Version`) và trường trọng yếu (`Gold_Critical_Field_IDs`) bởi Chủ sở hữu chính sách P2 và Quản lý dữ liệu P3 (`AGREED_BY_P2_AND_P3`).

### 2.3 Tệp dữ liệu lưu trữ
- **Định dạng CSV UTF-8 BOM:** [`data/eval/100_real_questions_clean_pii.csv`](../../data/eval/100_real_questions_clean_pii.csv)
- **Định dạng JSON Programmatic:** [`data/eval/100_real_questions_clean_pii.json`](../../data/eval/100_real_questions_clean_pii.json)

---

## 3. KẾT QUẢ BÀN GIAO 2: TỪ ĐIỂN VIẾT TẮT CRM & CHUẨN HÓA TRUY VẤN VN 01

Nhằm phục vụ trực tiếp cho tính năng Chuẩn hóa câu hỏi tiếng Việt trước khi tìm kiếm (`ANS 02` / `VN 01`), P4 đã xây dựng bộ từ điển gồm 4 cấu phần:

### 3.1 Chữ viết tắt CRM & Vai trò phê duyệt (`abbreviations`)
Bao gồm **42 từ viết tắt** xuất hiện liên tục trong giao tiếp hàng ngày của nhân viên tư vấn:
- **Khách hàng & Thị trường:** `kh` (khách hàng, customer), `khtt` (khách hàng thân thiết, VIP), `b2b` (khách hàng doanh nghiệp), `b2c` (khách hàng cá nhân).
- **Thương mại & Báo giá:** `bg` (báo giá, quotation), `qbg` (quy trình báo giá), `ck` (chiết khấu, discount), `hd` / `hđ` (hợp đồng, contract), `po` (đơn đặt hàng), `vat` / `gtgt` (thuế giá trị gia tăng).
- **Chức danh thẩm quyền:** `cvkd` (chuyên viên kinh doanh), `tpkd` (trưởng phòng kinh doanh), `gdkd` / `gđkd` (giám đốc kinh doanh), `gdcn` / `gđcn` (giám đốc chi nhánh), `tgd` / `tgđ` (tổng giám đốc).
- **Dịch vụ & Bảo hành:** `cskh` (chăm sóc khách hàng), `bh` (bảo hành, warranty), `bd` / `bđ` (bảo dưỡng định kỳ), `cvdv` (cố vấn dịch vụ), `ktv` (kỹ thuật viên), `scc` (sửa chữa chung), `ds` / `đs` (đồng sơn).
- **Kho vận & Pháp lý:** `bo` (đơn hàng chờ, back order), `stock` (hàng lưu kho sẵn có), `mst` (mã số thuế), `cccd` / `cmnd` (căn cước công dân), `sla` (cam kết thời gian xử lý), `pii` (thông tin cá nhân).

### 3.2 Chuẩn hóa Tiếng Việt Không dấu (`unaccent_mappings`)
Cung cấp bản đồ ánh xạ 30 cụm từ không dấu sang có dấu chuẩn để hỗ trợ nhân viên khi gõ nhanh trên điện thoại hoặc hệ thống chat:
- `chiet khau` $\rightarrow$ chiết khấu; `bao gia` $\rightarrow$ báo giá; `hop dong` $\rightarrow$ hợp đồng; `khach hang` $\rightarrow$ khách hàng.
- `bien tan trung the` $\rightarrow$ biến tần trung thế; `dong co 3 pha` $\rightarrow$ động cơ công nghiệp 3 pha; `bo truyen dong` $\rightarrow$ bộ truyền động bánh răng; `phu tung` $\rightarrow$ phụ tùng thay thế.
- `giam doc chi nhanh` $\rightarrow$ giám đốc chi nhánh; `truong phong kinh doanh` $\rightarrow$ trưởng phòng kinh doanh; `bien ban giam dinh` $\rightarrow$ biên bản giám định hiện trường.

### 3.3 Thuật ngữ Song ngữ Anh – Việt (`technical_and_product_terms`)
Định nghĩa chuẩn hóa cho các thuật ngữ kỹ thuật pha trộn tiếng Anh trong hợp đồng và catalog SongNhat:
- `motor 3 pha` $\leftrightarrow$ Động cơ công nghiệp 3 pha (`3-phase industrial motor`).
- `inverter` $\leftrightarrow$ Biến tần trung thế (`Medium voltage inverter`).
- `gearbox` $\leftrightarrow$ Bộ truyền động bánh răng (`Gear drive / Gearbox`).
- `back order` $\leftrightarrow$ Đơn đặt hàng phụ tùng không dự trữ sẵn (BO).
- `stock inventory` $\leftrightarrow$ Hàng dự trữ lưu kho sẵn có (Stock).
- `tombstone` $\leftrightarrow$ Đánh dấu thu hồi / xóa bản ghi chính sách.
- `quarantine` $\leftrightarrow$ Hàng đợi cách ly dòng lỗi / thiếu phụ lục.
- `hold` $\leftrightarrow$ Tạm dừng kết luận do xung đột thẩm quyền / thiếu căn cứ.

### 3.4 Bảo toàn Từ phủ định Tiếng Việt (`vietnamese_negations_preserved`)
> [!IMPORTANT]
> Module xử lý ngôn ngữ tuyệt đối **KHÔNG ĐƯỢC XÓA BỎ** các từ phủ định khi tách từ hoặc chuẩn hóa:  
> `không`, `chưa`, `chẳng`, `miễn`, `ngoại trừ`, `ngoài`, `không được`, `cấm`, `loại trừ`, `không áp dụng`, `vắng mặt`, `thiếu`, `từ chối`, `hủy`.  
> Việc loại bỏ từ phủ định sẽ làm đảo ngược hoàn toàn câu hỏi (ví dụ: *"khách hàng không thuộc diện VIP..."* bị hiểu nhầm thành *"khách hàng diện VIP"*).

### 3.5 Tệp lưu trữ và Mã nguồn tích hợp
- **Tệp từ điển chuẩn:** [`data/eval/vn01_crm_dictionary.json`](../../data/eval/vn01_crm_dictionary.json)
- **Tích hợp mã nguồn trực tiếp cho S3:** Đã cập nhật vào [`backend/src/modules/retrieval/models.py`](../../backend/src/modules/retrieval/models.py) (`VIETNAMESE_CRM_SYNONYMS` và `VIETNAMESE_NEGATIONS`).

---

## 4. BIÊN BẢN BÀN GIAO & KÝ NHẬN (HANDOVER SIGN-OFF)

| Vai trò | Thành viên | Trách nhiệm trong Sub-task | Xác nhận bàn giao / Nghiệm thu |
|---|---|---|:---:|
| **Lead bàn giao (P4)** | **Ngô Thị Trà My** | Chủ trì làm sạch 100 câu hỏi & lập Từ điển VN 01 | **ĐÃ HOÀN THÀNH BÀN GIAO** |
| **Xác nhận Bảo mật (P5)** | **Nguyễn Anh Khoa** | Rà soát an toàn 0% PII theo SEC 02 / SEC 06 | **XÁC NHẬN 100% SẠCH PII** |
| **Bên nhận 1 (S4)** | **Quý Hải** | Tiếp nhận 100 câu hỏi sạch phục vụ kiểm thử độc lập | **ĐÃ NHẬN ĐỦ 100 CÂU HỎI** |
| **Bên nhận 2 (S3)** | **Yến Nhi** | Tiếp nhận Từ điển VN 01 tích hợp module truy xuất ANS 02 | **ĐÃ TÍCH HỢP CODE RETRIEVAL** |
| **Chủ đầu tư / PO (P1)** | **Mỹ Vân** | Phê duyệt hoàn thành Sub-task CRM-G1-SUB08 (CKPA-55) | **CHẤP THUẬN NGHIỆM THU** |

---

*Hồ sơ hoàn tất ngày 19/11/2026. Sẵn sàng đóng Ticket CKPA-55 trên Jira và đồng bộ nhánh `uat/CRM-G1-SUB08-100-real-tasks-vn01-terms`.*
