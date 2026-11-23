# BÁO CÁO SMOKE TEST ĐỘC LẬP & NGHIỆM THU STORY CRM-G1-ST03
## [G1-AC04] Module Lọc RBAC & 7 Trạng thái KNW 03 + 100 Câu hỏi / Từ điển VN 01

> **Mã công việc:** `CRM-G1-ST03` | **Tiêu chí Cổng G1:** `G1-AC04`  
> **GitHub Branch:** `feat/CRM-G1-ST03-rbac-7states-smoke`  
> **Phía phụ trách:** Supplier Team (SongNhat CKPA)  
> **Lead điều phối:** `[S3] Yến Nhi (Retrieval and application engineer)`  
> **Reporter / Nghiệm thu (PO/SM):** `[S1] Hoàng Tiến (Named lead)`  
> **Collaborators / RACI:** `[P4] Trà My`, `[S2] Quốc Hưng`, `[S4] Quý Hải (chạy độc lập SUB09, KHÔNG có trên PR feat/)`  
> **Thời gian:** Sprint 3 (G1 Impl W1)  
> **Truy vết RFP:** `WP 03`, `SEC 01`, `KNW 03`, `ANS 02`, `VN 01`, Mục 8, Mục 9 (G1).

---

## 1. MỤC TIÊU VÀ PHẠM VI NGHIỆM THU

Story `CRM-G1-ST03` hoàn thành trọn vẹn 3 Sub-tasks phối hợp giữa S3, P4 và S4:
1. **Sub-task SUB07 (S3):** Hiện thực bộ lọc Pre-Retrieval RBAC 4 vai trò (`SEC 01`) và kiểm soát chặt chẽ 7 trạng thái vòng đời xuất bản (`KNW 03`), kết hợp module chuẩn hóa câu hỏi và tích hợp Từ điển VN 01 (`ANS 02`, `VN 01`).
2. **Sub-task SUB08 (P4):** Bàn giao 100 câu hỏi thực tế đầu tiên (60 DEV + 40 VAL, 100% sạch PII) và Bộ từ điển CRM Profile VN 01 (42 từ viết tắt, 30 quy tắc bù dấu, 14 từ phủ định bắt buộc bảo toàn).
3. **Sub-task SUB09 (S4):** Thực hiện Smoke Test độc lập trên thư mục kiểm thử ngoại tuyến `backend/tests/` bảo đảm nguyên tắc phân vai độc lập (SoD).

---

## 2. MA TRẬN KẾT QUẢ KIỂM THỬ NGOẠI TUYẾN (TEST RESULTS MATRIX)

Toàn bộ **25/25 test cases** trong hệ thống backend đã vượt qua (PASS 100%):

```text
backend/tests/test_health.py .                                           [  4%]
backend/tests/test_retrieval_rbac_and_7states.py ............            [ 52%]
backend/tests/test_smoke_s4_retrieval.py .....                           [ 72%]
backend/tests/test_srs_scaffold_contracts.py .......                     [100%]
======================== 25 passed, 1 warning in 0.35s ========================
```

### 2.1 Kiểm tra Ma trận Phân quyền RBAC 4 Vai trò (SEC 01)

| Vai trò người dùng | Audience được phép xem | Hành vi kiểm chứng Pre-Retrieval | Kết quả |
|---|---|---|:---:|
| `administrator` | Toàn quyền (`all`, `reader`, `policy_owner`, `steward`, `confidential`) | Cho phép truy xuất mọi đoạn trích hợp lệ | **PASS (0% rò rỉ)** |
| `reader` | Chỉ `reader`, `all`, `public` | Chặn 100% các đoạn chỉ dành cho `policy_owner`, `steward`, `admin` | **PASS (0% rò rỉ)** |
| `policy_owner` | Chỉ `policy_owner`, `all`, `public` | Chặn 100% các đoạn chỉ dành riêng cho `steward` | **PASS (0% rò rỉ)** |
| `steward` | Chỉ `steward`, `all`, `public` | Chặn 100% các đoạn chỉ dành riêng cho `policy_owner` | **PASS (0% rò rỉ)** |

### 2.2 Kiểm tra 7 Trạng thái Vòng đời KNW 03 & Fail-Closed

| Trạng thái tài liệu | Quy định RFP / SRS | Trạng thái mặc định | Chế độ mở rộng | Kết quả kiểm thử |
|---|---|:---:|:---:|:---:|
| `effective` | Phiên bản đang hiệu lực | **Cho phép** | Đúng ngày hiệu lực `governing_date` | **PASS** |
| `scheduled` | Hiệu lực trong tương lai | **Chặn 100%** | Cho phép khi `allow_future_preview=True` | **PASS** |
| `superseded` | Phiên bản lịch sử đã bị thay thế | **Chặn 100%** | Cho phép khi `allow_historical=True` & khớp ngày quá khứ | **PASS** |
| `draft` | Bản nháp đang soạn thảo | **Chặn 100%** | Cấm truy xuất dưới mọi hình thức | **PASS (0% rò rỉ)** |
| `owner_reviewed` | Đang rà soát đối chiếu bản gốc | **Chặn 100%** | Cấm truy xuất dưới mọi hình thức | **PASS (0% rò rỉ)** |
| `approved` | Đã phê duyệt nhưng chưa phát hành | **Chặn 100%** | Cấm truy xuất dưới mọi hình thức | **PASS (0% rò rỉ)** |
| `withdrawn` | Đã thu hồi khẩn cấp | **CẤM TUYỆT ĐỐI** | **Strict Fail-Closed** (cấm kể cả khi bật cờ lịch sử) | **PASS (0% rò rỉ)** |
| `quarantined` | Lỗi schema / thiếu phụ lục (DAT 08) | **Chặn 100%** | Đẩy hàng đợi cách ly | **PASS (0% rò rỉ)** |
| `feedback_candidate`| Ứng viên phản hồi nhân viên (KNW 06) | **Chặn 100%** | Cấm đưa vào retrieval | **PASS (0% rò rỉ)** |

### 2.3 Kiểm tra Ràng buộc Kỹ thuật & Bounded Context
- **Ràng buộc phụ lục bắt buộc (`DAT 08`):** Toàn bộ đoạn trích thiếu phụ lục/chú thích (`has_essential_attachments=False`) bị loại bỏ 100% khỏi kết quả retrieval.
- **Ràng buộc chiều dài văn bản (`SRS-FR-02`):** Đoạn trích vượt quá `6.000` ký tự Unicode bị loại bỏ 100%.
- **Giới hạn số lượng đoạn trích (`Base Scope`):** Số lượng đoạn trích trả về cho một gói câu hỏi luôn bị chặn cứng $\le 8$ đoạn (`top_k <= 8`).

### 2.4 Kiểm tra Chuẩn hóa Tiếng Việt & Bảo toàn Từ phủ định (ANS 02, VN 01)
- **42 từ viết tắt CRM & Chức danh:** Mở rộng thành công từ viết tắt sang thuật ngữ nghiệp vụ chuẩn (`kh`, `ck`, `bg`, `cvkd`, `tpkd`, `b2b`, `po`, `bh`, `scc`, `bo`, `stock`, `pii`...).
- **30 cụm từ không dấu:** Chuẩn hóa tự động các chuỗi không dấu (`chiet khau` $\rightarrow$ `chiết khấu`, `dong co 3 pha` $\rightarrow$ `động cơ công nghiệp 3 pha`...).
- **14 từ phủ định tiếng Việt bắt buộc bảo toàn:** Kiểm thử 100% thành công, không một từ phủ định nào bị lọc bỏ (`không`, `chưa`, `chẳng`, `miễn`, `ngoại trừ`, `ngoài`, `không được`, `cấm`, `loại trừ`, `không áp dụng`, `vắng mặt`, `thiếu`, `từ chối`, `hủy`), loại trừ hoàn toàn nguy cơ đảo ngược nghĩa câu hỏi.

---

## 3. KIỂM TOÁN AN TOÀN TẬP 100 CÂU HỎI THỰC TẾ (SUB08 - P4)

1. **Quy mô tập dữ liệu:** Đầy đủ 100 câu hỏi tại `data/eval/100_real_questions_clean_pii.json` và `data/eval/100_real_questions_clean_pii.csv`.
2. **Phân bổ phân vùng (Partition):**
   - Phân vùng Huấn luyện/Phát triển (`DEV`): 60 câu hỏi.
   - Phân vùng Thẩm định (`VAL`): 40 câu hỏi.
3. **Phân bổ theo 3 họ chính sách Base Scope:**
   - `POL-CRM-01` (Báo giá & Phê duyệt thương mại): 40 câu (24 DEV, 16 VAL).
   - `POL-CRM-02` (Dịch vụ & Bảo hành kỹ thuật): 30 câu (18 DEV, 12 VAL).
   - `POL-CRM-03` (Xử lý thông tin & Dữ liệu khách hàng): 30 câu (18 DEV, 12 VAL).
4. **Kiểm tra 0% PII (`SEC 02`, `SEC 06`):**
   - Số điện thoại cá nhân: **0 phát hiện**.
   - Số CCCD / CMND (9 hoặc 12 chữ số): **0 phát hiện**.
   - Email cá nhân: **0 phát hiện**.
   - 100% câu hỏi đã có trạng thái đồng thuận nhãn vàng `AGREED_BY_P2_AND_P3`.

---

## 4. BẰNG CHỨNG TUÂN THỦ TÁCH VAI (SEPARATION OF DUTIES - SoD)

Nhằm tuân thủ tuyệt đối quy tắc SoD của RFP và Global Definition of Done:
- **Tác giả lập trình (Assignee):** `[S3] Yến Nhi` (nhánh `feat/CRM-G1-ST03-rbac-7states-smoke`).
- **Reviewer trên Pull Request `feat/`:** Chỉ gán **`[S1] Hoàng Tiến`** và **`[S2] Quốc Hưng`**.
- **Kỹ sư Kiểm thử Độc lập (`S4` Quý Hải):** Chỉ chạy kiểm thử và nghiệm thu độc lập trên bộ test `SUB09`, **TUYỆT ĐỐI KHÔNG CÓ TÊN TRÊN PR NHÁNH `feat/`**.
- **Tập 100 Sealed Eval:** Tách biệt độc lập trong `sealed-eval-repo`, chặn quyền Read/Clone đối với S2 và S3 theo cơ chế Chinese Wall.

---

## 5. KẾT LUẬN & ĐỀ NGHỊ NGHIỆM THU

Story **`CRM-G1-ST03`** đã thỏa mãn 100% các Acceptance Criteria:
- [x] Given hạ tầng IAM SUB01 và dữ liệu Họ 1.
- [x] When S3, P4 và S4 hoàn tất 3 Sub-tasks (SUB07..SUB09) trong Sprint 3.
- [x] Then bộ lọc Pre-Retrieval chặn 100% tài liệu ngoài quyền và 6 trạng thái phi-Effective (chỉ lấy Effective).
- [x] And P4 bàn giao 100 câu hỏi thực đầu tiên + từ điển VN 01 và S4 hoàn tất smoke test độc lập + Sprint 3 Review.

**Trạng thái đề xuất:** Sẵn sàng chuyển ticket Jira `CRM-G1-ST03` sang **Ready for Review (In Review)** và tạo PR để [S1] Hoàng Tiến và [S2] Quốc Hưng rà soát mã nguồn.
