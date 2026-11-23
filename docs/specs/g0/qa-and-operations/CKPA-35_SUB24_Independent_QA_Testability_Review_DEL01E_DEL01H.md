> **TRẠNG THÁI:** BẢN DỰ THẢO CHỜ RÀ SOÁT & PHÊ DUYỆT (FOR REVIEW — CHƯA KÝ DUYỆT CHÍNH THỨC). Tài liệu chỉ phục vụ rà soát nghiệm thu Sprint 2 Cổng G0; không cấu thành phê duyệt PO, chữ ký pháp lý, kết luận pháp chế chính thức, báo giá ràng buộc, lệnh giải ngân hay giờ công thực tế chưa đối soát. Các mục tiêu định lượng, giả định dự thầu và ví dụ Annex E từ RFP được ghi rõ là đề xuất/tham khảo.

# BIÊN BẢN RÀ SOÁT ĐỘC LẬP TÍNH KHẢ KIỂM (`QA TESTABILITY REVIEW`) ĐỐI VỚI `DEL01-E` (09 HỢP ĐỒNG ANNEX B) & `DEL01-H` (`OPS 01–08`)

- **Đơn vị Bên Mua:** `Công ty Cổ phần Thiết bị Công nghiệp Song Nhật` *(chờ `[P1]` / Legal Owner xác nhận chính thức theo Giấy chứng nhận ĐKKD)*
- **Dự án:** SongNhat CRM Knowledge and Policy Assistant (`CKPA`)
- **Mã công việc Jira:** Sub-task `CKPA-35` (*CRM-G0-SUB24: [G0][QA] Kiểm tra Tính khả thi Test DEL01-E & DEL01-H*) — Thuộc Story `CKPA-32` (*CRM-G0-ST08*) & Epic `CKPA-3` (*CRM-G0-EP01*)
- **Tiêu chí nghiệm thu & Gói giao nộp:** `G0-AC04` | Biên bản Kiểm tra Tính khả thi Test `DEL01-E` & `DEL01-H`
- **Tham chiếu RFP:** `Mục 2`, `Mục 8 (Independent acceptance)`, `Mục 11 (SoD)`, `Annex B (RFP-ANXB-01..10)`, `Annex D (OPS 01..08, RFP-ANXD-09)`
- **Chủ trì kiểm định độc lập (Assignee):** `[S4]` **Phạm Quý Hải** (*Quality lead — Independent QA, Strict SoD / Chinese Wall*)
- **Người giao việc / Phê duyệt (Reporter):** `[P1]` **Văn Mỹ Vân** (*Purchaser sponsor / Product Owner*)
- **Phối hợp đối chiếu (RACI):** `[P2]` **Lý Hữu Tài** (*Policy owners*), `[P5]` **Nguyễn Anh Khoa** (*Privacy and security owners*)
- **Lịch Sprint 2 & Ngày lập biên bản:** `18/11/2026` (Múi giờ chuẩn `Asia/Ho_Chi_Minh`, `UTC+7`)
- **Tệp dữ liệu CSV đi kèm:** `CKPA-35_SUB24_Testability_Verification_Matrix_AnnexB_OPS01-08.csv` *(đúng `17` hạng mục: `B-01..B-09` + `OPS 01..08`)*

---

## 1. Tuyên bố Độc lập Kiểm định (`Strict SoD Declaration — RFP Mục 8 & Mục 11`)

- `[S4]` **Phạm Quý Hải** thực hiện cuộc rà soát này ở tư cách **Quality Lead độc lập**. Trong suốt G0 Sprint 1–2, `[S4]` **KHÔNG tham gia thiết kế giao diện `Evidence Workspace`, KHÔNG viết/chỉnh sửa mã nguồn ứng dụng, prompt, bộ chọn chính sách hay kịch bản hạ tầng** của `[S2]`, `[S3]` và `[S5]`.
- Phạm vi thẩm định của biên bản này chỉ tập trung vào một câu hỏi kiểm định duy nhất: **Từng hợp đồng tính năng trong `DEL01-E` (`CKPA-29`: `B-01..B-09`) và từng chỉ tiêu dịch vụ trong `DEL01-H` (`CKPA-33` / `CKPA-18`: `OPS 01..08`) đã có ngưỡng `PASS/FAIL` định lượng, bằng chứng kiểm toán đo được và điều kiện chạy kiểm thử khách quan cho lộ trình `G1–G4` hay chưa?**

---

## 2. Kết quả Rà soát Tính Khả kiểm `DEL01-E` (`09` Hợp đồng Tính năng Annex B — `CKPA-29`)

Toàn bộ `09/09` hợp đồng tính năng (`B-01` đến `B-09`) đã đủ `09` trường hợp đồng chuẩn `RFP-ANXB-10` (*inputs, rights, governing date, 6-dim scope, allowed output, hold reason, owner, audit evidence, test ID*) và đồng bộ `100%` với từ điển 6 chiều `DAT 04` của `CKPA-10`. Kết luận đánh giá từng nhóm:

1. **Nhóm Quy trình, Ngưỡng & Ranh giới (`B-01`, `B-02`, `B-08`) — `TESTABLE_FOR_REVIEW`:**
   - Có tiêu chí `PASS/FAIL` nhị phân rõ ràng: xác minh `OPTION_O1_ENABLED = False`, `0` truy vấn bảng khách hàng, `0` lệnh writeback CRM, render đúng nguyên vẹn cấu trúc `critical_fields` (`CF-002..008`) từ PostgreSQL và bắt buộc có `HOLD_ANS07` khi câu hỏi ép duyệt chiết khấu hoặc tiết lộ/sửa dữ liệu khách hàng.
2. **Nhóm Thời gian `Asia/Ho_Chi_Minh` & Vòng đời `KNW 03` (`B-03`, `B-04`) — `TESTABLE_FOR_REVIEW` *(kèm điều kiện G1 `QA-DEP-02`)*:**
   - Có tiêu chí `PASS/FAIL` đo được tại ranh giới `23:59:59+07:00` vs `00:00:00+07:00`, nhãn `Historical Guidance` và `Future Preview`, cấm `0%` dùng nguồn `scheduled` cho câu hỏi hôm nay.
   - **Điều kiện tiền kiểm thử G1:** Bắt buộc nạp bản lịch sử `VER-000` (`superseded`, trước `2026-11-06T09:00:00+07:00`) và bản tương lai `VER-002` (`scheduled`) cùng cơ chế cố định đồng hồ kiểm thử (`clock fixture` theo `Asia/Ho_Chi_Minh`) trên môi trường Test cô lập.
3. **Nhóm Xung đột, Ghi chú Cũ & Tính Đầy đủ (`B-05`, `B-06`, `B-07`) — `TESTABLE_FOR_REVIEW`:**
   - Đều có tiêu chí `PASS/FAIL` dứt khoát (`100%` `HOLD_DAT05` cho xung đột hợp đồng–chính sách `DOC-006` vs `DOC-001`; kiểm tra tách biệt hai kịch bản `reader` có quyền và không có quyền `audience` trên `DOC-006`; `100%` loại trừ `staff_note` `DOC-007` khỏi quy tắc chung; `100%` `HOLD_DAT08` + cách ly `quarantined` khi `has_essential_attachments = false`).
4. **Nhóm Thu hồi Giữa lúc Trả lời (`B-09`) — `TESTABLE_FOR_REVIEW` *(kèm điều kiện G1 `QA-DEP-04`)*:**
   - Đã tách rạch ròi **03 bài kiểm thử độc lập**: (a) tạm dừng giữa Tầng 4 và Tầng 5 -> rút chính sách & chờ `ack` -> tiếp tục phải bị chặn `409`/`HOLD_SEC05`; (b) từ chối tái sử dụng cache và đo thời gian xóa vật lý Redis `<= 300s`; (c) kiểm thử riêng cơ chế cảnh báo `Stale` cho văn bản đã hiển thị trên phiên trước thời điểm rút.

---

## 3. Kết quả Rà soát Tính Khả kiểm `DEL01-H` (`08` Bài kiểm thử Vận hành `OPS 01–08` — `CKPA-33` / `CKPA-18`)

Toàn bộ `08/08` bài kiểm thử dịch vụ theo Phụ lục D RFP (`OPS 01` đến `OPS 08`) đều đã được đối chiếu với tiêu chí định lượng bắt buộc tại `CKPA-35_SUB24_Testability_Verification_Matrix_AnnexB_OPS01-08.csv`:

| Mã `OPS` | Tiêu chí `PASS` Định lượng Cốt lõi (RFP Phụ lục D) | Tiêu chí `FAIL` Rõ ràng | Cổng Kiểm chứng | Nhận định Khả kiểm |
| :---: | :--- | :--- | :---: | :---: |
| **`OPS 01`** | Nạp `500` dòng thay đổi trong `<= 30` phút; đối soát `100%` (`Expected = Accepted + Quarantined`); vượt qua bộ test trùng lặp, batch muộn, partial feed, full snapshot và tombstone. | Quá `30` phút; sai lệch đối soát dù `1` dòng; batch muộn ghi đè bản mới; xóa ngầm không có tombstone. | `G1`, `G2` | `TESTABLE_FOR_REVIEW` |
| **`OPS 02`** | `5` phiên đồng thời / `100` yêu cầu trong giới hạn ngữ cảnh: `p95 <= 25s`; báo cáo đủ số `hold`, lỗi, `provider throttling`, thời gian từng tầng và chi phí. | `p95 > 25s`; thiếu báo cáo thời gian theo tầng/chi phí; đánh đổi bỏ qua kiểm tra quyền/nguồn để chạy nhanh (`RFP-ANXD-09`). | `G2` | `TESTABLE_FOR_REVIEW` |
| **`OPS 03`** | `100%` chính xác trước và đúng biên ngày `00:00:00`/`23:59:59` `Asia/Ho_Chi_Minh`, bản hết hạn, chồng lấn (`HOLD_DAT05`), sửa hồi tố, tương lai và thiếu quy tắc ngày (`HOLD`). | Lệch múi giờ UTC; chọn sai phiên bản tại biên ngày; không `HOLD` khi chồng lấn hoặc thiếu quy tắc ngày. | `G1`, `G2` | `TESTABLE_FOR_REVIEW` |
| **`OPS 04`** | `100%` chính xác tại biên dưới/bằng/trên (`<, <=, ==, >=, >`), từ chối/HOLD khi thiếu đơn vị hoặc tiền tệ; `0` trường hợp LLM tự sửa giá trị/toán tử/vai trò/điều khoản. | Sai dù `1` trường hợp biên hoặc LLM tự thay đổi số học/đơn vị/vai trò duyệt (`CRIT_FABRICATED_FIELD`). | `G1`, `G2` | `TESTABLE_FOR_REVIEW` |
| **`OPS 05`** | Commit `withdrawn`/thu hồi quyền trước `ack`; `0` câu trả lời bị ảnh hưởng phát mới hoặc tái dùng cache sau `ack`; xóa cache vật lý `<= 300s` (test riêng); ghi nhận rõ giới hạn làm mới giao diện đang mở. | Phát câu trả lời hoặc trả cache chứa nguồn đã rút sau `ack`; xóa cache quá `300s`; không Fail-Closed khi mất trạng thái DB. | `G2` | `TESTABLE_FOR_REVIEW` |
| **`OPS 06`** | Đề xuất `>= 99,5%` trong giờ phục vụ `08:00–17:00` VN (chỉ trừ bảo trì có kế hoạch đã duyệt); báo cáo đầu cuối tính cả gián đoạn từ nhà cung cấp API (`provider impact`) & phân bổ trách nhiệm `DEL 06`. | Loại bỏ sai gián đoạn nhà cung cấp API khỏi báo cáo đầu cuối; thiếu bảng đo uptime và `Cost Meter`. | `G2`, `G3` | `TESTABLE_FOR_REVIEW` |
| **`OPS 07`** | Diễn tập khôi phục trên bản sao lưu thực tế (`35` ngày): `RTO <= 4` giờ làm việc, `RPO <= 24` giờ; **bắt buộc Replay xóa Annex C, thu hồi `withdrawn` và quyền RBAC hiện hành trước khi mở truy cập** (`0%` bản ghi đã xóa/rút xuất hiện lại). | Vượt `RTO 4h` hoặc `RPO 24h`; mở truy cập trước khi chạy Replay; xuất hiện lại dù `1` bản ghi đã xóa/rút hoặc tài khoản đã thu hồi quyền. | `G2`, `G4` | `TESTABLE_FOR_REVIEW` |
| **`OPS 08`** | Làm cạn trần token (`6.000`/`900`), calls (`2`/gói, `2.000`/tháng) & gói (`1.000`/tháng) -> chuyển `HOLD` minh bạch (`0` cắt cụt âm thầm, `0` retry vượt trần); xuất định dạng mở (`CSV UTF-8`/`JSON`/`Markdown`) xác minh đọc độc lập bằng trình đọc trung lập. | Cắt cụt âm thầm đoạn chính sách; tự retry vượt trần; dữ liệu xuất thiếu phiên bản/tham chiếu/audit hoặc không đọc được trên trình đọc trung lập. | `G4` | `TESTABLE_FOR_REVIEW` |

> **Nguyên tắc Ràng buộc Khi Benchmark (`RFP-ANXD-09`):** Mọi kết quả đo `OPS 01–08` phải thực hiện trong môi trường tương đương sản xuất đã thống nhất. **Tốc độ phản hồi (`OPS 02`) tuyệt đối không được đánh đổi bằng việc cắt giảm bước kiểm tra đầy đủ nguồn (`DAT 08`) hay kiểm soát quyền (`SEC 01`)**. Kênh tra cứu thủ công và chuyển tiếp chủ sở hữu phải luôn sẵn sàng trong thời gian hệ thống ngừng hoạt động (`downtime`).

---

## 4. Danh mục 05 Phụ thuộc Tiền Kiểm thử Cần Khép lại Trước Cổng G1–G2 (`Pre-Testability Dependencies`)

Mặc dù `17/17` hạng mục (`B-01..B-09` + `OPS 01..08`) đều đạt trạng thái **`TESTABLE_FOR_REVIEW`** về mặt tiêu chí định lượng, `[S4]` ghi nhận `05` phụ thuộc triển khai bắt buộc hoàn tất trước khi bước vào kiểm thử thực thi tại G1–G2:

| Mã Phụ thuộc | Mô tả Hạng mục Tiền Kiểm thử Bắt buộc | Đầu mối Khắc phục | Mốc Hoàn tất |
| :---: | :--- | :--- | :---: |
| **`QA-DEP-01`** | Chốt duy nhất `01` nhà cung cấp **Cloud Host & Data Center** (`CKPA-18`/`CKPA-33` hiện đang `PENDING_G0_SELECTION`) để xác lập môi trường thực tế đo `OPS 01` và `OPS 02`. | `[P1]`, `[P5]`, `[S1]`, `[S5]` | Trước đóng Cổng G0 |
| **`QA-DEP-02`** | Tuyển chọn phiên bản lịch sử `VER-000` (`superseded`) và phiên bản tương lai `VER-002` (`scheduled`) + trang bị bộ giả lập đồng hồ `Asia/Ho_Chi_Minh` trong môi trường Test cho `B-03`, `B-04`, `OPS 03`. | `[P2]`, `[P3]`, `[S2]`, `[S3]` | Cổng G1 |
| **`QA-DEP-03`** | Hoàn tất chuyển đổi 6 chiều `DAT 04` trong `backend/src/modules/answer/schemas.py` và sửa lỗi phân quyền `ensure_partition_access()` tại `backend/src/shared/auth.py:65-72` (`administrator = DENY` trên `sealed_100`). | `[S2]`, `[S3]` (rà soát `[P5]`, `[S4]`) | Cổng G1 |
| **`QA-DEP-04`** | Bổ sung móc kiểm thử `pause/resume` an toàn (chỉ hoạt động tại `ENV=test`) giữa Tầng 4 và Tầng 5 để tự động hóa kiểm định `B-09` & `OPS 05` không phụ thuộc thời điểm thủ công. | `[S3]`, `[S5]` | Cổng G1 / G2 |
| **`QA-DEP-05`** | Ban hành kịch bản diễn tập `Fallback` tra cứu thủ công khi hệ thống ngừng hoạt động (`downtime`) và danh mục công cụ trung lập (`neutral reader`) kiểm chứng xuất dữ liệu mở `OPS 08`. | `[S5]`, `[P3]`, `[P4]` | Cổng G2 / G4 |

---

## 5. Xác nhận Rà soát Độc lập `CKPA-35` (`SUB24`) (Chờ Ký Xác Nhận)

| Vai trò RFP Mục 11 | Họ và tên | Nội dung Xác nhận | Trạng thái | Ngày xác nhận |
| :--- | :--- | :--- | :---: | :---: |
| **`[S4]` Quality lead (Independent QA)** | Phạm Quý Hải | Chủ trì rà soát độc lập tính khả kiểm `17/17` hạng mục (`B-01..B-09` & `OPS 01..08`); xác nhận tuân thủ SoD | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **`[P2]` Policy owners** | Lý Hữu Tài | Xác nhận các tiêu chí `PASS/FAIL` nghiệp vụ cho `B-01..B-09` và `OPS 03/04` | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **`[P5]` Privacy and security owners** | Nguyễn Anh Khoa | Xác nhận các tiêu chí `PASS/FAIL` bảo mật/quyền riêng tư cho `B-05/06/08/09` và `OPS 05/07/08` | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
| **`[P1]` Purchaser sponsor / Product Owner** | Văn Mỹ Vân | Phê duyệt Biên bản Kiểm tra Tính khả thi Test `DEL01-E` & `DEL01-H` | `[ ] Chờ ký xác nhận` | `... / ... / 2026` |
