# Lịch làm việc 10 tuần — Hoàng Tiến (A1 · PM / BA Lead)

> **Trạng thái:** Đã duyệt ngày 15/11/2026.
> **Nguồn:** [05-jira-5gates-import.csv](../work-packages/05-jira-5gates-import.csv) (task có `Role-A1` hoặc ghi A1 trong mục "Phụ trách", cột `Blocked By`), [weekly-report.md](./weekly-report.md) (standup 2 ngày/lần, bắt đầu T3 17/11). Bản theo dõi trong Excel: sheet `Lich_PM_Tien` của [ke-hoach-quan-ly-5-gate-noi-bo.xlsx](../work-packages/ke-hoach-quan-ly-5-gate-noi-bo.xlsx).
> **Phạm vi 10 tuần:** Tuần dự án **T3 → T12** (20/11/2026 – 29/01/2027), tức "10 tuần triển khai cơ sở" sau G0 theo RFP. Tuần chạy từ **Thứ 6 → Thứ 5**, khớp Sprint Jira và sheet Gantt. Có thêm **Tuần 0** (16–19/11) để chốt G0.

---

## 1. Nhịp cố định hằng tuần

| Thời điểm | Việc | Thời lượng | Đầu ra |
|---|---|---|---|
| **Thứ 6** (đầu tuần dự án) | Rà board Jira CKPA, phát task cuốn chiếu: chỉ mở task đã xong hết `Blocked By`; kiểm WIP ≤ 1–2 task/người | 45' | Sprint board cập nhật |
| **Thứ 3 · Thứ 5 · Thứ 7** | Standup theo format 4 câu hỏi; ghi nhận vi phạm theo [rules.md](./rules.md) | 15' | Danh sách blocker |
| **Thứ 5** (cuối tuần dự án) | Review tiến độ và rủi ro với các Squad (A–D). Nếu là tuần cuối Gate thì họp chốt Gate với Sponsor | 45–60' | Biên bản review / Gate |
| **Chủ nhật** | Viết Weekly Report, cập nhật trạng thái trong file Excel nội bộ | 45' | `weekly-report` tuần |

**Các buổi họp chốt Gate:** G0 **T5 19/11** · G1 **T5 10/12** · G2 **T5 24/12** · G3 **T2 25/01** · G4 **T6 29/01**.

---

## 2. Tuần 0 — Chốt G0 (16/11 – 19/11)

- **T3 17/11:** Standup đầu tiên.
- **#8** *(phối hợp D2, 12h, hạn 19/11)*: Biên bản so sánh 3 phương án có giá và quyết định phạm vi G0.
- **#12** *(phối hợp D2, C3, hạn 18/11)*: Xác nhận baseline nhà cung cấp / pháp lý.
- Import CSV vào Jira CKPA (map `Link "Relates"`, `Link "Blocks"`), gán Assignee cho 10 thành viên.
- **T5 19/11 — Họp chốt G0 (DEL 01):** 3 nhóm chính sách + Policy Owner, 30 đoạn + 10 trường (#6), SRS/ERD/CSV/API đã khóa (#9, #10), Docker/CI (#11), kế hoạch eval (#13).

---

## 3. Lịch 10 tuần

### T3 · 20/11 – 26/11 · G1 Lõi tri thức ngoại tuyến
- **T6 20/11:** Kick-off G1, mở Sprint `Gate-G1-Controlled-Offline`, phát **#17** (B1, B2, C3).
- Theo dõi **#18** RBAC, **#19** CSV validator, **#21** policy lifecycle (bắt đầu 24/11, chờ #17 xong).
- **#22** *(phối hợp A2, từ 25/11)*: Làm việc với Policy Owner để duyệt phần mở rộng kho tri thức.
- Xác nhận đủ Policy Owner + người thay thế cho cả 3 nhóm (`VN 04`).

### T4 · 27/11 – 03/12 · G1
- Bám đường găng: **#19 → #20** (30/11) **→ #23** (01/12) **→ #24, #26**.
- **#22:** Thúc Policy Owner duyệt từng đợt đoạn/trường (≤ 300 đoạn / ≤ 50 trường).
- Review rủi ro giữa G1, kiểm WIP.

### T5 · 04/12 – 10/12 · G1 (tuần chốt)
- Theo dõi **#25, #27, #28, #29** và **#30** (D1/D2: 40 Val + 80 Challenges).
- Kiểm tra Chinese Wall: Squad B/C không truy cập bộ Sealed.
- **T5 10/12 — Họp chốt G1:** 2 CSV + Quarantine, RBAC, Lifecycle, Fail-Closed, kho đã duyệt.

### T6 · 11/12 – 17/12 · G2 Dùng thử có giám sát
- **T6 11/12:** Kick-off G2.
- **#41 — chủ trì** *(12–19/12, 12h)*: Hồ sơ pháp lý SEC 03, lưu giữ/xóa dữ liệu, làm việc với Privacy/Legal owner.
- **#40 — chủ trì** *(16–19/12, 10h)*: Incident Runbook và Change Control (cần #38, #39 xong).
- Chuẩn bị nội dung đào tạo cho **#42**; chốt danh sách **≥ 5 người dùng Pilot không phải dev** (A1, A2, D1, D2 + đại diện nghiệp vụ).

### T7 · 18/12 – 24/12 · G2 (tuần chốt)
- Hoàn tất **#40, #41** (19/12).
- **#42 — chủ trì** *(17–21/12, 8h)*: Đào tạo Policy Owner và 5 Staff Users.
- Giám sát **#43** OPS 01–07, **#44** Sealed (D1 chấm độc lập), **#45** sửa lỗi và retest.
- **T5 24/12 — Họp chốt G2:** Không còn lỗi nghiêm trọng, pháp lý xong, đã đào tạo, có phương án dự phòng. **Nếu G2 đạt sớm thì khởi động Pilot ngay 24/12** (21 ngày làm việc, dự phòng 1 ngày).

### T8 · 25/12 – 31/12 · G3 Pilot
- **T6 25/12:** Bắt đầu **#49 — chủ trì** *(cùng D1, 40h)* theo mốc cơ sở, nếu chưa khởi động từ 24/12.
- Lập log hằng ngày: tác vụ, lượt thử, hold, lỗi, công sức chuẩn bị/kiểm tra/dự phòng.
- Phối hợp **#50** (A2, C3, D2): chi phí, Snapshot Age, thay đổi.

### T9 · 01/01 – 07/01 · G3 *(01/01 nghỉ Tết Dương lịch)*
- Pilot tiếp tục; review số liệu tuần 1 với D1.

### T10 · 08/01 – 14/01 · G3
- Review giữa Pilot; dựng khung báo cáo DEL 03 (với D1) và dữ liệu đầu vào DEL 05 (với D2).

### T11 · 15/01 – 21/01 · G3
- Pilot vẫn chạy, đếm ngày làm việc hằng ngày.
- **#51** *(phối hợp D1, từ 18/01)*: Dựng bản nháp DEL 03 song song bằng số liệu tạm.
- **#52** *(phối hợp D2, từ 19/01)*: Dựng TCO 3 năm và thời gian hoàn vốn (DEL 05).
- Nhắc C3/D2 chuẩn bị sẵn kịch bản restore/xóa cho **#58** vì G4 bị nén còn 5 ngày.

### T12 · 22/01 – 29/01 · G3 chốt → G4 Bàn giao
- **T6 22/01:** Kết thúc quan sát Pilot (**đủ 20 ngày làm việc**).
- **T7 23/01:** Chốt số liệu cuối cho **#51** (DEL 03) và **#52** (DEL 05).
- **T2 25/01 — #53 chủ trì** *(6h)*: **Họp chốt G3** với Sponsor, biên bản tách riêng quyết định mở rộng. Mở G4 ngay sau họp.
- **G4 nén 25/01 – 29/01:** giám sát **#57** OPS 08 (25–26/01), **#58** khôi phục/xóa đa lớp (25–27/01), **#60** đóng gói DEL 04 (26–28/01).
- **#59** *(phối hợp C3, D2, 25–28/01, 10h)*: Điều khoản vận hành DEL 06.
- **#61 — chủ trì** *(28–29/01, 8h)*: Demo 9 tình huống mẫu.
- **T6 29/01 — Ký nghiệm thu G4** + retrospective toàn đội.

---

## 4. Khối lượng của Tiến trong 10 tuần

| Loại | Task Jira | Giờ ước lượng |
|---|---|---|
| Chủ trì | #40, #41, #42, #49, #53, #61 | **84h** |
| Phối hợp | #22, #51, #52, #59 | 66h *(giờ của cả task, chia với người chủ trì)* |
| Nhịp quản lý | Standup ×3, review, phát task, weekly report | ~4h/tuần ≈ **40h** |

Tuần nặng nhất: **T7** (#40, #41, #42 + chốt G2) và **T12** (kết thúc Pilot, chốt DEL 03/05, họp G3, toàn bộ G4).

---

## 5. Quyết định về rủi ro Pilot (đã duyệt: Hướng 1 + 2)

Cửa sổ cũ của #49 (25/12 – 20/01) chỉ có **18 ngày làm việc** (trừ nghỉ 01/01), chưa đủ **20 ngày** theo RFP/SRS. Đã áp dụng:

- **Hướng 2:** Khởi động Pilot từ **T5 24/12** nếu G2 được chốt sớm → 21 ngày làm việc (dự phòng 1 ngày).
- **Hướng 1:** Mốc cơ sở **25/12/2026 – 22/01/2027** = đúng 20 ngày làm việc. #51/#52 dựng song song, chốt G3 dời sang **T2 25/01**, G4 nén còn **25–29/01**.

Ngày đã cập nhật trong CSV Jira:

| ID | Hạng mục | Cũ | Mới |
|---|---|---|---|
| #46 | Epic G3 | 25/12 – 22/01 | 25/12 – **25/01** |
| #47 | Story G3-S1 | 25/12 – 19/01 | 25/12 – **22/01** |
| #48 | Story G3-S2 | 18/01 – 22/01 | 18/01 – **25/01** |
| #49 | Pilot 20 ngày | 25/12 – 20/01 | 25/12 – **22/01** (+ ghi chú khởi động sớm 24/12) |
| #50 | Theo dõi Pilot | 25/12 – 20/01 | 25/12 – **22/01** |
| #51 | DEL 03 | 18/01 – 21/01 | 18/01 – **23/01** (+ ghi chú dựng song song) |
| #52 | DEL 05 | 19/01 – 22/01 | 19/01 – **23/01** |
| #53 | Biên bản G3 | 21/01 – 22/01 | **25/01** |
| #54 | Epic G4 | 23/01 – 29/01 | **25/01** – 29/01 |
| #55 | Story G4-S1 | 23/01 – 27/01 | **25/01** – 27/01 |
| #57 | OPS 08 | 23/01 – 26/01 | **25/01** – 26/01 |
| #58 | Restore / xóa | 23/01 – 27/01 | **25/01** – 27/01 |
