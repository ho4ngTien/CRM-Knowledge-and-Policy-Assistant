> **TRẠNG THÁI:** BẢN DỰ THẢO CHỜ RÀ SOÁT & PHÊ DUYỆT (FOR REVIEW — CHƯA KÝ DUYỆT CHÍNH THỨC). Tài liệu chỉ phục vụ rà soát nghiệm thu Sprint 1 Cổng G0; không cấu thành phê duyệt PO, chữ ký pháp lý, kết luận pháp chế chính thức, báo giá ràng buộc hay giờ công thực tế chưa đối soát. Các mục tiêu định lượng, giả định dự thầu và ví dụ Annex E từ RFP được ghi rõ là đề xuất/tham khảo.

# ĐẶC TẢ PHẠM VI GATE G0 (03 HỌ CHÍNH SÁCH), MA TRẬN THẨM QUYỀN 05 LỚP NGUỒN (`DAT 03`) & QUY TẮC CONFLICT HOLD (`DAT 05`)

- **Đơn vị Bên Mua:** `Công ty Cổ phần Thiết bị Công nghiệp Song Nhật` *(chờ `[P1]` Văn Mỹ Vân / Legal Owner xác nhận chính thức theo Giấy chứng nhận ĐKKD)*
- **Dự án:** SongNhat CRM Knowledge and Policy Assistant (`CKPA`)
- **Mã công việc Jira hợp nhất:** Story `CKPA-8` (*CRM-G0-ST02: [G0][WP01] Chốt 3 họ, Ma trận Thẩm quyền & Ngày*) & Sub-task `CKPA-9` (*CRM-G0-SUB04: [G0][DAT03] Chốt 3 họ, Ma trận 5 lớp & Quy tắc Hold*) — Thuộc Epic `CKPA-3` (*CRM-G0-EP01*)
- **Tiêu chí nghiệm thu & Gói giao nộp:** `G0-AC02` | `DEL01-B` (phần 1/3, liên thông trực tiếp với `CKPA-10` / `SUB05` và `CKPA-11` / `SUB06`)
- **Tham chiếu RFP & SRS:** `RFP Mục 1`, `Mục 2`, `Mục 3 (DAT 03, DAT 04, DAT 05, DAT 08)`, `Mục 4 (ANS 05, ANS 06, ANS 07)`, `Mục 5 (KNW 03, KNW 04, KNW 05)`, `Mục 7 (SEC 01, SEC 02, SEC 05)`, `Mục 9 (OPS 01–08)`, `Mục 11`, `Mục 14`, `VN 04`, `Annex B` | `SRS Mục 2.1–2.3`, `SRS-FR-01.1`, `SRS-FR-04.1..04.4`, `INV-01..06`
- **Chủ trì thực hiện (Assignee):** `[P2]` **Lý Hữu Tài** (*Policy owners — Policy Reviewer #1*)
- **Người giao việc / Rà soát (Reporter):** `[P1]` **Văn Mỹ Vân** (*Purchaser sponsor / Product Owner*)
- **Phối hợp theo RACI:** `[P3]` **Trần Chí Kha** (*Knowledge and data steward — Policy Reviewer #2*), `[P5]` **Nguyễn Anh Khoa** (*Privacy and security owners — Reviewer chính sách bảo mật & quyền riêng tư*), `[S1]` **Hoàng Tiến** (*Named lead / Scrum Master*)
- **Lịch Sprint 1 & Ngày lập bản dự thảo:** `10/11/2026 – 11/11/2026` (Múi giờ chuẩn `Asia/Ho_Chi_Minh`, `UTC+7`)
- **Tệp dữ liệu CSV đi kèm (cùng thư mục `CKPA-09_SUB04`):**
  1. `CKPA-09_SUB04_Policy_Families_Owners_And_Substitutes.csv`
  2. `CKPA-09_SUB04_Base_Scope_O1_OutOfScope_Matrix.csv`
  3. `CKPA-09_SUB04_Authority_Matrix_5_Layers.csv`
  4. `CKPA-09_SUB04_Governing_Date_And_Conflict_Hold_Rules.csv`

---

## 1. Xác nhận 03 Họ Chính sách Cơ sở (`M`), Loại trừ 02 Họ Chưa Sẵn sàng (`O`) & Phân công Chủ sở hữu / Người thay thế (`VN 04`)

Thực hiện yêu cầu `RFP Mục 1`, `Mục 2`, `Mục 11`, `Mục 14` và `VN 04`, `[P2]` Lý Hữu Tài đã tổng hợp khung phạm vi `CKPA-8` và `CKPA-9` để trình `[P1]` Văn Mỹ Vân cùng các Chủ sở hữu Chính sách của `Công ty Cổ phần Thiết bị Công nghiệp Song Nhật` rà soát xác nhận tại Cổng G0:

### 1.1 Danh mục 03 Họ Chính sách Cơ sở (`In-Scope Base — M`) & 02 Họ Loại trừ (`Excluded at G0 — O`)

| Mã Họ (`policy_id`) | Tên Họ Chính sách & Tài liệu Đại diện | Phân loại RFP | Phạm vi Hỗ trợ Được Phép (`M`) | Giới hạn Cứng Không Được Vượt (`ANS 07`) | Chuỗi 6 Chiều `DAT 04` Mẫu Chuẩn | Mẫu G0 & Trần Giả định Dự thầu G1 *(chờ xác nhận G0)* |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: |
| **`POL-001`** | **1. Báo giá và phê duyệt thương mại**<br>(`DOC-001`, `VER-001`) | **`M` — `IN_SCOPE_BASE`** | Giải thích trường CRM bắt buộc, ngưỡng chiết khấu/đơn hàng (`CF-001..004` mẫu) và tuyến xử lý ngoại lệ thương mại đã duyệt | Không tự cấp ngoại lệ/chiết khấu; không suy luận phê duyệt từ khách VIP hay `staff_note` cũ; không tự tạo điều khoản thương mại | `company:SN;branch:all;role:sales;customer_category:b2b_enterprise;product:industrial;transaction_scope:quotation_standard` | **G0:** `10` passages / `4` fields<br>**G1 cap:** `<= 100` passages / `<= 18` fields |
| **`POL-002`** | **2. Xử lý thông tin khách hàng CRM**<br>(`DOC-002`, `VER-001`) | **`M` — `IN_SCOPE_BASE`** | Giải thích quy trình ghi nhận, chỉnh sửa hoặc xác minh thông tin liên hệ/pháp lý khách hàng đã phê duyệt (`CF-005..008` mẫu) | Không tự tiết lộ dữ liệu khách hàng; không tự sửa bản ghi CRM (`0` writeback); không tự xác lập cơ sở pháp lý hoặc miễn trừ chứng từ | `company:SN;branch:all;role:crm;customer_category:b2b_enterprise;product:all;transaction_scope:crm_legal_update` | **G0:** `10` passages / `4` fields<br>**G1 cap:** `<= 100` passages / `<= 16` fields |
| **`POL-003`** | **3. Định tuyến yêu cầu dịch vụ / bảo hành**<br>(`DOC-003`, `VER-001`) | **`M` — `IN_SCOPE_BASE`** | Xác định 03 chứng từ bắt buộc, tuyến chuyển tiếp theo công suất (`<= 37 kW` vs `> 37 kW`, `CF-009..010` mẫu) và đầu mối bảo hành được ủy quyền | Không tự quyết định quyền hưởng bảo hành miễn phí hay tính phí; không hướng dẫn tự tháo lắp hoặc sửa chữa thiết bị công nghiệp | `company:SN;branch:all;role:cskh;customer_category:b2b_factory;product:industrial;transaction_scope:warranty_intake` | **G0:** `10` passages / `2` fields<br>**G1 cap:** `<= 100` passages / `<= 16` fields |
| `EX-POL-004` | *Chính sách Công nợ, Thuế & Kế toán Hợp đồng* | **`O` — `EXCLUDED_AT_G0`** | *Đề xuất loại khỏi Base Scope* | Tư vấn thuế/pháp lý/tín dụng thuộc danh mục từ chối bắt buộc (`ANS 07`) | *Không áp dụng trong Base Scope* | `0` *(Loại bỏ theo `VN 04`)* |
| `EX-POL-005` | *Quy trình Logistics, Kho vận & Giao nhận Quốc tế* | **`O` — `EXCLUDED_AT_G0`** | *Đề xuất loại khỏi Base Scope* | Nằm ngoài 03 họ chính sách CRM khởi đầu của `RFP Mục 1–2` | *Không áp dụng trong Base Scope* | `0` *(Loại bỏ theo `VN 04`)* |

> **Lưu ý tính minh bạch theo RFP (`PROJECT_RFP_REFERENCE.md`):** Toàn bộ số ngưỡng mẫu G0 (`5%`, `15%`, `500 triệu VND`, `1 tỷ VND`, `37 kW`, SLA `2h/4h/48h`) trong `DOC-001..003` là **dữ liệu mẫu đối chiếu quy trình tại Discovery**, KHÔNG tự động khẳng định là quy định thương mại/bảo hành hiện hành của `Công ty Cổ phần Thiết bị Công nghiệp Song Nhật` cho đến khi các Policy Owners chính thức rà soát và ký duyệt kho tri thức G1. Đồng thời, các trần `<= 30` tài liệu / `<= 300` passages / `<= 50` critical fields là giả định dự thầu (`Common Bid Assumptions`) — **tuyệt đối không tự tạo thêm quy tắc chỉ để lấp đầy trần**.

### 1.2 Phân công Chủ sở hữu Chính sách (`Policy Owners`), Người thay thế (`Substitutes — VN 04`) & 02 Policy Reviewers Độc lập (`RFP Mục 11`)

Nhằm bảo đảm quyền sở hữu chính sách và trách nhiệm giải trình luôn thuộc phía Bên Mua (`Purchaser`), không chuyển giao trách nhiệm nội dung sang Nhà cung cấp (`[S1]–[S5]`):

| Phạm vi / Vai trò Quản trị | Vai trò Chuẩn RFP Mục 11 | Nhân sự Dự án Đảm nhiệm | Chức danh Nội bộ Song Nhật & Người thay thế (`VN 04`) | Trạng thái Xác nhận |
| :--- | :--- | :--- | :--- | :---: |
| **Điều phối Chủ sở hữu Chính sách & Policy Reviewer #1** | `Policy owners` | **`[P2]` Lý Hữu Tài** | Chủ trì rà soát nội dung chuyên môn cho `POL-001`, `POL-002`, `POL-003`; chịu trách nhiệm phê duyệt quy tắc thẩm quyền `DAT 03` | `PENDING_G0_SIGNOFF` |
| **Quản lý Tri thức & Policy Reviewer #2** | `Knowledge and data steward` | **`[P3]` Trần Chí Kha** | Rà soát độc lập thứ 2 về cấu trúc 6 chiều `DAT 04`, vòng đời `KNW 03`, tính đầy đủ bảng/chú thích `DAT 08` và đối soát nhập CSV `DAT 02` | `PENDING_G0_SIGNOFF` |
| **Policy Reviewer Chuyên trách Bảo mật & Quyền riêng tư** | `Privacy and security owners` | **`[P5]` Nguyễn Anh Khoa** | Rà soát bắt buộc đối với `POL-002` (thông tin khách hàng CRM), lớp `customer_contract` (`DOC-006`), lớp `staff_note` (`DOC-007`) và tuân thủ `SEC 01–08` | `PENDING_G0_SIGNOFF` |
| **Chủ sở hữu & Người thay thế theo từng họ chính sách (`VN 04`)** | `Policy owners` + `Substitutes` | Phối hợp `[P1]` Văn Mỹ Vân & `[P2]` Lý Hữu Tài | - `POL-001`: Commercial Policy Owner (`Sales Director`) / Substitute 1 (`Deputy Sales Director`)<br>- `POL-002`: CRM Data Governance Owner (`CRM Manager`) / Substitute 2 (`Senior CRM Lead`)<br>- `POL-003`: Warranty Policy Owner (`Service Director`) / Substitute 3 (`Internal Tech Lead`)<br>*(Chờ `[P1]` điền đầy đủ họ tên nhân sự Song Nhật và ký xác nhận tại Cổng G0 trước khi cấp quyền xuất bản)* | `PENDING_NAMED_SLOTS` |
| **Quy tắc Bất biến về Tách vai (SoD — `RFP Mục 8 & Mục 11`)** | 10 vai trò chuẩn (`[P1]–[P5]`, `[S1]–[S5]`) | Toàn đội dự án | - Nhà cung cấp (`[S1]–[S5]`) **không bao giờ** thay mặt Policy Owner ban hành hoặc bịa quy tắc chính sách.<br>- Đội Build (`[S2]` Trần Quốc Hưng, `[S3]` Phạm Lương Yến Nhi) **không có quyền** truy cập tập đánh giá kín `100 Sealed` do `[S4]` Phạm Quý Hải quản lý độc lập.<br>- `Assignee != Reporter` trên mọi tác vụ Jira. | `LOCKED_AT_G0` |

---

## 2. Phân định Ranh giới `In-Scope Base (M)` vs `Option O1 (OFF)` vs `10 Hạng mục Out-of-Scope (O)`

Chi tiết đầy đủ nằm tại tệp `CKPA-09_SUB04_Base_Scope_O1_OutOfScope_Matrix.csv`, tóm tắt các ranh giới ràng buộc như sau:

### 2.1 Phạm vi Cơ sở Bắt buộc (`In-Scope Base — M` / Các giả định dự thầu Mục 2 cần xác nhận tại G0)

| Mã | Nhóm Tham số | Giới hạn / Quy tắc Đề xuất Cần Xác nhận tại G0 (`M`) | Kiểm soát Thực thi |
| :---: | :--- | :--- | :--- |
| **`SCP-M01`** | **Tổ chức & Người dùng** | `1` công ty (`Song Nhật`); `<= 20` named users; `<= 5` phiên đồng thời; 04 vai trò lõi Mục 2 (`reader`, `policy_owner`/`publisher`, `steward`, `administrator`) | Danh tính tổ chức + `least privilege` (`SEC 01`); kiểm tra `audience` 3 tầng (`pre-retrieval`, `pre-generation`, `pre-display`) |
| **`SCP-M02`** | **Kho tri thức & 02 CSV UTF-8** | `<= 30` tài liệu đã duyệt; `<= 300` passages (`<= 6.000` ký tự Unicode/mục); `<= 50` dòng `critical_fields`; **`0` hồ sơ khách hàng** | Chỉ nhận đúng `2` schema CSV UTF-8; dòng lỗi/thiếu chú thích thiết yếu bị cách ly vào `quarantined` (`DAT 02`, `DAT 08`) |
| **`SCP-M03`** | **Làm mới & Thu hồi tức thời** | `1` batch hằng ngày/schema (`<= 500` dòng thay đổi/`<= 30` phút, `OPS 01`); thu hồi (`withdrawn`) cam kết trước ack & dọn cache `<= 300s` (`<= 5` phút, `OPS 05`) | Hiển thị `Snapshot Age` (cảnh báo `> 25h`); `Final Pre-Display Check` tuần tự và `fail-closed` (`SEC 05`) |
| **`SCP-M04`** | **Hạn mức Yêu cầu & AI** | `<= 1.000` `AnswerPackage`/tháng (tính cả `hold` & lỗi); `<= 8` passages/package; `<= 2` LLM calls/package (`<= 6.000` in / `<= 900` out tokens gồm chỉ dẫn); `<= 2.000` calls/tháng | Câu trả lời `100–250` từ tiếng Việt + trích dẫn gốc + trường trọng yếu render bằng code; `p95 <= 25s` tại 5 phiên/100 truy vấn (`OPS 02`); chạm trần -> `HOLD` rõ ràng (`OPS 08`), cấm cắt cụt âm thầm |
| **`SCP-M05`** | **Kiểm soát Ngoài Prompt** | 05 lớp thẩm quyền `DAT 03`; 07 trạng thái vòng đời `KNW 03` (`draft`, `owner_reviewed`, `approved`, `scheduled`, `effective`, `superseded`, `withdrawn`) + 02 trạng thái tiếp nhận (`feedback_candidate`, `quarantined`); ngày chi phối `Asia/Ho_Chi_Minh`; 06 chiều `DAT 04` | Trạng thái phục vụ trực tiếp duy nhất cho câu hỏi hiện hành là `effective`; khóa cứng `ENABLE_ANSWER_STREAMING = False` (`INV-03`); 100% xung đột chuyển `HOLD_DAT05` |
| **`SCP-M06`** | **Lịch trình 05 Cổng (`G0–G4`)** | `<= 2` tuần Discovery (`G0`) + `10` tuần triển khai cơ sở (gồm `>= 20` ngày làm việc quan sát Pilot tại `G3`); đánh giá độc lập `200` tác vụ thực (`60/40/100`) + `80` thách thức (`40` ca VN) | Không gộp `G3` và `G4`; quyết định mở rộng tách riêng nghiệm thu Pilot; mục tiêu giảm `>= 20%` nỗ lực trung bình là mục tiêu đề xuất (tham chiếu Annex E chỉ là ví dụ minh họa) |

### 2.2 Tách biệt Tuyệt đối `Option O1 — Selected CRM Context` (`OFF` trong Base Scope)

- **Trạng thái đề xuất tại Cổng G0:** **`OFF` — TÁCH BIỆT HOÀN TOÀN KHỎI BASE SCOPE (`SCP-O1`).**
- Trong phạm vi cơ sở (`M`), hệ thống sử dụng **`0` hồ sơ khách hàng**, chỉ tiếp nhận đúng `02` tệp CSV UTF-8 (`passages` và `critical_fields`), không triển khai bảng hay đường dẫn nhập dữ liệu khách hàng `O1`, và không gộp khối lượng `O1` vào lộ trình 10 tuần cơ sở.
- Tùy chọn `O1` (lược đồ CSV thứ 3 cho tối đa `2.000` dòng khởi tạo / `5.000` dòng lưu giữ, tối đa `1` bản ghi CRM được chọn mỗi `AnswerPackage`) chỉ được xem xét trong quyết định thương mại và pháp lý tách biệt khi hội đủ đồng thời: (1) Báo giá riêng và Phụ lục hợp đồng; (2) Xác minh nhu cầu lặp lại và giá trị kinh tế; (3) Cơ sở xử lý dữ liệu cá nhân hợp pháp & rà soát quyền chủ thể (`R02/R03`, `SEC 03`); (4) Kiểm soát quyền đọc (`SEC 01`), độ mới (`freshness`) và danh sách trường được phép (`DAT 07`).

### 2.3 Danh mục Đầy đủ 10 Hạng mục Ngoài Phạm vi Mặc định (`Out-of-Scope — O`)

1. **`SCP-O01`:** Kết nối trực tiếp tới CRM hoặc cơ sở dữ liệu sản xuất sống (`Live Connectors`).
2. **`SCP-O02`:** OCR, xử lý giọng nói/âm thanh, tích hợp Zalo hoặc đồng bộ lịch sử hộp thư (`Mailbox`).
3. **`SCP-O03`:** Tự động đọc/trích xuất bảng biểu, sơ đồ hoặc PDF gốc chưa được chuẩn hóa thủ công sang CSV UTF-8 (`VN 03`, `DAT 08`, `R07`).
4. **`SCP-O04`:** Ngôn ngữ khác (như sinh câu trả lời tiếng Anh tự động) hoặc họ chính sách ngoài 03 họ `POL-001..003` (`EX-POL-004`, `EX-POL-005`).
5. **`SCP-O05`:** Soạn thảo phản hồi sẵn sàng gửi trực tiếp cho khách hàng bên ngoài (`KNW 02` — chỉ hướng dẫn nội bộ).
6. **`SCP-O06`:** Ghi ngược vào CRM (`Writeback`), tự tạo tác vụ CRM, bắt buộc workflow engine hoặc tự động phê duyệt giao dịch (`KNW 05`, `ANS 07`).
7. **`SCP-O07`:** Tư vấn pháp lý/thuế, cấp quyền tiết lộ dữ liệu cá nhân, phán quyết điều kiện bảo hành miễn phí/tính phí hoặc hướng dẫn tự tháo lắp/sửa chữa thiết bị (`ANS 07`).
8. **`SCP-O08`:** Tự động huấn luyện (`Auto-training`) hoặc tự động sửa đổi quy tắc từ phản hồi người dùng (`KNW 06`, `SEC 04`).
9. **`SCP-O09`:** Truyền phát (`Streaming`) nội dung câu trả lời trước khi hoàn tất bước kiểm tra nguồn, quyền và trạng thái thu hồi cuối cùng (`INV-03`, `SEC 05`).
10. **`SCP-O10`:** Hỗ trợ vận hành 24/7 ngoài khung giờ làm việc thỏa thuận (`08:00–17:00` giờ Việt Nam các ngày làm việc, độ khả dụng đề xuất `99,5%`, `OPS 06`).

---

## 3. Ma trận Thẩm quyền 05 Lớp Nguồn Tách biệt (`DAT 03` & `DAT 05`)

Chi tiết định chuẩn tại tệp `CKPA-09_SUB04_Authority_Matrix_5_Layers.csv`. Toàn bộ kho nguồn được phân loại nghiêm ngặt thành **đúng 05 lớp nguồn tách biệt** với mã hệ thống viết thường chuẩn hóa:

| Thứ tự | Mã Lớp (`authority_layer_code`) | Tên Lớp Nguồn & Mã Tài liệu Đại diện | Được tạo Quy tắc chung? | Được tự động ghi đè `policy`? | Bản mới nhất tự động thắng? | Quy tắc Sử dụng & Kiểm soát Xung đột (`DAT 03`, `DAT 05`, `ANS 05`) |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | `policy` | **Chính sách công ty đã ban hành**<br>(`DOC-001`, `DOC-002`, `DOC-003`) | **Có** | Không *(chỉ thay thế qua `supersedes` đã duyệt)* | **Không** | Nguồn chuẩn mực cốt lõi khi ở trạng thái `effective` (hoặc `superseded` cho tra cứu lịch sử `DATE-02`). Phải khớp đủ 06 chiều `DAT 04` (`company, branch, role, customer_category, product, transaction_scope`). |
| **2** | `sop` | **Quy trình thao tác chuẩn**<br>(`DOC-004`) | **Có** *(chi tiết thao tác)* | **Không** | **Không** | Hướng dẫn các bước tác nghiệp trên CRM và biểu mẫu kèm theo. Phải tuân thủ khung ngưỡng/thẩm quyền của `policy`; nếu mâu thuẫn với `policy` -> bắt buộc **`HOLD_DAT05`**. |
| **3** | `manufacturer_terms` | **Điều khoản kỹ thuật & bảo hành của Nhà sản xuất**<br>(`DOC-005`) | **Không** | **Không** | **Không** | Xác định tiêu chuẩn kỹ thuật và điều kiện giám định gốc của Hãng sản xuất thiết bị công nghiệp. Không được bỏ qua 03 chứng từ tiếp nhận nội bộ; xung đột tuyến xử lý -> **`HOLD_DAT05`**; yêu cầu phán quyết bảo hành/sửa chữa -> **`HOLD_ANS07`**. |
| **4** | `customer_contract` | **Hợp đồng thương mại / Hợp đồng khung với Khách hàng**<br>(`DOC-006`) | **Không** | **Không tự suy diễn** | **Không** | Trong Base Scope chỉ dùng mẫu/điều khoản hợp đồng đã ẩn danh PII và kiểm soát `audience` (`SEC 01`) để kiểm thử xung đột (`Worked Case B-05`); tách biệt `Option O1` (`OFF`). **Nghiêm cấm suy diễn thứ bậc ưu tiên phổ quát giữa `customer_contract` và `policy` -> 100% mâu thuẫn kích hoạt `HOLD_DAT05` + Local Referral.** |
| **5** | `staff_note` | **Ghi chú nhân viên trên CRM / Tiền lệ ngoại lệ cũ**<br>(`DOC-007`) | **CẤM TUYỆT ĐỐI** | **CẤM TUYỆT ĐỐI** | **Không** | Chỉ là **lịch sử giao dịch có ghi nguồn (`attributed historical context`)** nếu người dùng có quyền xem (`SEC 01`) và đã khử PII (`SEC 02`). **Tuyệt đối không tạo quy tắc chung, không ghi đè `policy`/`sop` và không làm bằng chứng hưởng quyền lợi cho đơn hàng mới hay khách hàng khác (`Worked Case B-06`).** |

### Ba Nguyên tắc Bất biến Về Thẩm quyền & Xung đột (`DAT 03`, `DAT 05`, `ANS 05`)

1. **Bản phát hành mới nhất không mặc nhiên chi phối (*Newest is not automatically controlling*):** Hệ thống không được chọn nguồn chỉ vì có ngày phát hành mới nhất nếu thiếu liên kết thay thế (`supersedes`) hợp lệ, nếu `governing_date` thuộc kỳ hiệu lực lịch sử (`DATE-02`), hoặc nếu phiên bản đang ở trạng thái `scheduled` (`DATE-03`).
2. **Không tự suy diễn thứ bậc ưu tiên phổ quát giữa Hợp đồng và Chính sách (*No inferred universal precedence between `customer_contract` and `policy`*):** Cả ứng dụng lẫn mô hình AI đều không được mặc định hợp đồng khách hàng thắng chính sách công ty hay ngược lại; độ tin cậy của mô hình (`model confidence`) tuyệt đối không thể phân xử xung đột -> **100% ca xung đột bắt buộc kích hoạt `HOLD_DAT05`** và tạo phiếu chuyển tiếp nội bộ (`Local Referral`) cho Policy Owner / Legal Owner.
3. **Ghi chú CRM & ngoại lệ quá khứ không bao giờ tạo ra quy tắc chung:** `staff_note` (`DOC-007`) không bao giờ cấp quyền chiết khấu VIP hay miễn trừ chứng từ cho giao dịch mới (`Worked Case B-06`).

---

## 4. Tóm tắt Quy tắc Ngày Chi phối (`Asia/Ho_Chi_Minh`) & 06 Nhóm Điều kiện Bắt buộc `HOLD`

Chi tiết quy tắc `DATE-01..05` và `HOLD-01..06` được chuẩn hóa tại tệp `CKPA-09_SUB04_Governing_Date_And_Conflict_Hold_Rules.csv` và được đặc tả mở rộng cùng từ điển 06 chiều `DAT 04` & kiểm tra bàn giấy 09 ca Annex B tại **`CKPA-10` (`SUB05`)**:

| Nhóm Mã `HOLD` | Nguyên nhân Kích hoạt | Hành vi Bắt buộc của Hệ thống (Ngoài Prompt) | Tuyến Chuyển tiếp Nội bộ (`Local Referral`) |
| :---: | :--- | :--- | :--- |
| **`HOLD_DAT05`** (`HOLD-01`, `HOLD-02`) | Xung đột giữa `customer_contract` với `policy`/`sop`/`manufacturer_terms`; hoặc `>= 2` phiên bản `effective` chồng lấn `[effective_from, effective_to)` trên cùng 6 chiều `DAT 04` | Tạm dừng kết luận bị ảnh hưởng; hiển thị song song các trích dẫn người dùng được phép xem (`SEC 01`) và nêu rõ lý do xung đột | Policy Owner phụ trách (`POL-001..003`), Knowledge Steward (`[P3]`), Legal Owner (nếu có hợp đồng) |
| **`HOLD_DAT08`** (`HOLD-03`) | Thiếu bảng biểu, sơ đồ hoặc chú thích thiết yếu (`has_essential_attachments = false`, `B-07`); hoặc chứng từ khách hàng bị mờ/rách tem Serial/mất Phiếu BH | Chỉ giải thích phần có ngữ cảnh đầy đủ đã duyệt; cách ly dòng lỗi vào `quarantined` lúc nhập CSV; cấm mô hình tự điền thiếu (`ANS 06`) | Knowledge Steward (`[P3]` Trần Chí Kha) & Policy Owner (`[P2]` Lý Hữu Tài) |
| **`HOLD_ANS06`** (`HOLD-04`) | Thiếu `governing_date`, thiếu 1 trong 06 chiều `DAT 04` (`company`, `branch`, `role`, `customer_category`, `product`, `transaction_scope`) hoặc thiếu thông số ngưỡng (giá trị đơn, lũy kế HĐ, công suất kW) | Giữ kết luận phụ thuộc ngữ cảnh và liệt kê câu hỏi làm rõ (`missing_facts`) ngắn gọn, không đoán mặc định | Người dùng bổ sung dữ kiện hoặc chuyển Policy Owner nếu quy định chưa rõ |
| **`HOLD_ANS07`** (`HOLD-05`) | Yêu cầu tự cấp chiết khấu/ngoại lệ (`B-02`), suy luận ưu đãi từ `staff_note` (`B-06`), tư vấn pháp lý/thuế, tiết lộ dữ liệu khách hàng / ghi sửa CRM (`B-08`), phán quyết bảo hành hoặc hướng dẫn sửa chữa thiết bị | Từ chối minh bạch (`REFUSED_OUT_OF_SCOPE` / `HOLD_ANS07`), trích dẫn điều khoản ranh giới và chỉ dẫn đúng đầu mối có thẩm quyền | Policy Owner / Legal Owner / Privacy Owner (`[P5]`) / Service Tech Lead |
| **`HOLD_SEC05` / `HOLD_OPS08`** (`HOLD-06`) | Nguồn chuyển sang `withdrawn` giữa lúc trả lời (`B-09`), không xác minh được quyền RBAC / trạng thái DB (`fail-closed`), hoặc chạm trần hạn mức tháng/gói (`OPS 08`) | Hủy phát hành câu trả lời tại `Final Pre-Display Check`; chặn tái sử dụng cache (`<= 300s` xóa vật lý); cấm cắt cụt âm thầm | Policy Owner & Operations Specialist (`[S5]` Nguyễn Ngọc Duy) |

---

## 5. Xác nhận Rà soát & Phê duyệt Cổng G0 (Chờ Ký Xác Nhận)

> Các mục đánh dấu bên dưới sẽ chỉ được chuyển trạng thái sau buổi rà soát Cổng G0 cùng `[P1]` Văn Mỹ Vân, 03 Policy Owners của Song Nhật và hoàn tất kiểm tra bàn giấy 09 ca Annex B (`CKPA-10`) cùng thẩm định pháp lý–quyền riêng tư (`CKPA-11`).

| Vai trò RFP Mục 11 | Họ và tên | Trách nhiệm Rà soát / Phê duyệt | Trạng thái Ký duyệt | Ngày xác nhận |
| :--- | :--- | :--- | :---: | :---: |
| **`[P2]` Policy owners (Policy Reviewer #1)** | Lý Hữu Tài | Chủ trì biên soạn Phạm vi 3 họ, Ma trận 5 lớp `DAT 03` & Quy tắc Hold `DAT 05` | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **`[P3]` Knowledge and data steward (Policy Reviewer #2)** | Trần Chí Kha | Rà soát độc lập #2: đối chiếu 6 chiều `DAT 04`, vòng đời `KNW 03` & nguồn `DOC-001..007` | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **`[P5]` Privacy and security owners** | Nguyễn Anh Khoa | Thẩm định ranh giới `customer_contract` (`DOC-006`), `staff_note` (`DOC-007`), `SEC 01/02/05` (`CKPA-11`) | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **`[S1]` Named lead / Scrum Master** | Hoàng Tiến | Xác nhận tính nhất quán liên hồ sơ G0 (`DEL01-B`) và khớp khung giả định dự thầu | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **`[P1]` Purchaser sponsor / Product Owner** | Văn Mỹ Vân | Phê duyệt Phạm vi Base (`M`), Tách `O1` (`OFF`), Danh sách Owner/Substitute Song Nhật & Ma trận Thẩm quyền | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **Legal Owner (Bên Mua — Song Nhật)** | *[Chờ `[P1]` chỉ định]* | Xác nhận tên pháp nhân theo ĐKKD và thẩm định tương tác Hợp đồng – Chính sách – Pháp luật | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
