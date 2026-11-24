# BÁO CÁO NGHIỆM THU KỸ THUẬT & BÀN GIAO BẢN VÁ SELECTION/HOLD CUỐI SPRINT 4
## [G1-AC05 / G1-AC06] Bản vá Selection/Hold Cuối Sprint 4 (Pass 60 Dev / 40 Val)

> **Mã công việc:** `CKPA-72` (`CRM-G1-SUB21`) | **Parent Epic:** `CKPA-44` | **Story:** `CKPA-61` (`CRM-G1-ST05`)  
> **Tiêu chí Cổng G1:** `G1-AC05`, `G1-AC06`  
> **GitHub Branch:** `fix/CKPA-72-selection-hold-sprint4`  
> **Phía phụ trách:** Supplier Team (SongNhat CKPA)  
> **Assignee / Lead kỹ thuật:** `[S3]` Phạm Lương Yến Nhi (Retrieval & Application Engineer)  
> **Reporter / Nghiệm thu (PO/SM):** `[S1]` Hoàng Tiến (Named Lead)  
> **Reviewers / RACI:** `[S1]` Hoàng Tiến, `[S2]` Trần Quốc Hưng (*TUYỆT ĐỐI KHÔNG có `[S4]` trên PR theo đúng nguyên tắc SoD*)  
> **Truy vết RFP:** `WP 03`, `OPS 03`, `OPS 04`, `DAT 04`, `DAT 05`, `DAT 06`, `DAT 08`, `VN 01`, `Mục 9 (G1)`.  
> **Kết quả bàn giao:** Bản vá Selection/Hold Cuối Sprint 4 (Pass 60 Dev / 40 Val) — **0 lỗi mở còn tồn đọng**.

---

## 1. MỤC TIÊU VÀ PHẠM VI BÀN GIAO

Bản vá thực hiện nhiệm vụ xử lý toàn bộ các lỗi logic Ngày hiệu lực, 6 chiều DAT 04, Ngưỡng Critical Field biên (`OPS 04`) và Conflict Hold (`DAT 05`) phát sinh cuối Sprint 4, bảo đảm vượt qua 100% tập dữ liệu thực tế gồm **60 DEV Tasks** và **40 VAL Tasks** (`100_real_questions_clean_pii.json`) không còn lỗi mở.

### Danh mục lỗi từ SUB14, SUB15 và SUB20 đã được xử lý triệt để:

| STT | Mã truy vết | Phân loại lỗi | Hiện trạng trước khi vá | Giải pháp kỹ thuật trong bản vá |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **DAT 04 / TAX-04** | Scope Mismatch không kích hoạt Hold | Khi candidate bị loại sau bước lọc 6 chiều phạm vi (`applicable_ids` rỗng), `evaluate_hold()` chỉ xét `gate_decision` ban đầu nên trả về `must_hold=False` (lọt lưới). | Bổ sung kiểm tra `effective_version_ids`. Khi không có phiên bản nào khớp 6 chiều phạm vi, bắt buộc kích hoạt `DAT04_NO_APPLICABLE_VERSION` (`must_hold=True`). |
| **2** | **DAT 05 / TAX-02** | False Conflict Hold giữa các phạm vi tách biệt | Hai chính sách áp dụng cho hai chi nhánh khác nhau (ví dụ HN và HCM) bị `PolicyService` đánh đồng là xung đột do xét trước khi lọc phạm vi (Over-Hold). | Tính toán xung đột dựa trên `matched_candidates` (chỉ các phiên bản thực sự cùng khớp phạm vi 6 chiều). Nếu chỉ có 1 phiên bản khớp phạm vi thì không kích hoạt xung đột giả. |
| **3** | **OPS 04 / SUB15** | Lỗi parse ngưỡng số học chứa ký tự định dạng | `Decimal(target.strip())` ném lỗi `InvalidOperation` khi gặp số có định dạng hàng nghìn (`500,000,000`, `500.000.000`), đơn vị (`50 kW`, `15 ngày làm việc`) hoặc `%`. | Xây dựng bộ trích xuất số học regex `_parse_decimal()` tự động làm sạch dấu phân cách hàng nghìn, đơn vị đo lường và hỗ trợ toán tử chuỗi (`<=`, `>=`, `<`, `>`, `==`, `between`). |
| **4** | **TAX-11 / DAT 08** | Lọt phiên bản SCHEDULED khi truy vấn tương lai | `run_selection()` tự động gán `allow_future_preview = date_result.is_future_preview` mà không kiểm tra cờ của người gọi, có nguy cơ dùng phiên bản SCHEDULED trái phép. | Bổ sung tham số `allow_future_preview=False` và `allow_historical=True` tường minh tại `SelectionService` và `router.py`, bảo đảm tuân thủ nguyên tắc 0 dung sai của `TAX-11`. |

---

## 2. MA TRẬN KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (120/120 PASS)

Toàn bộ **120 test cases** của backend bao gồm **52 test SUB14**, **20 test kiểm định 60 Dev / 40 Val** và toàn bộ suite tích hợp đều **PASS 100%**:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.10, pytest-9.2.0, pluggy-1.7.0 -- D:\Python\python.exe
rootdir: C:\Users\ACER\Desktop\crm-knowledge-and-policy-assistant\backend
configfile: pyproject.toml
plugins: anyio-4.16.0, asyncio-1.5.0
120 passed, 1 warning in 2.21s
All checks passed! (Ruff linter 0 errors)
===============================================================================
```

### 2.1 Chi tiết 20 Test Cases Kiểm định 60 Dev / 40 Val (`test_selection_60dev_40val.py`)

| Nhóm kiểm thử | Số ca | Nội dung kiểm chứng | Kết quả |
| :--- | :---: | :--- | :---: |
| **Phân vùng dữ liệu** | 3 | Kiểm chứng đủ 60 DEV (`DEV-001..060`), 40 VAL (`VAL-001..040`), phủ trọn 16 Variant Groups (`VG-01..16`) và ngày hiệu lực `2026-11-15`. | **PASS** |
| **Ngày chi phối (OPS 03)** | 3 | Tra cứu ngày theo timezone `Asia/Ho_Chi_Minh`, biên `00:00:00` vs `23:59:59` UTC+7 không lệch ngày, 0% gọi LLM. | **PASS** |
| **Phạm vi 6 chiều (DAT 04)** | 3 | Khớp wildcard 6 chiều, bắt buộc HOLD `DAT04_NO_APPLICABLE_VERSION` khi sai lệch chi nhánh/phạm vi, không phát sinh xung đột giả. | **PASS** |
| **Ngưỡng số học (OPS 04)** | 5 | Kiểm thử hạn mức chiết khấu `<= 5%` (VG-01), `between 5;15` (VG-02), đơn hàng lớn `>= 1 tỷ` (VG-03), ngưỡng công suất `< 50 kW` vs `>= 50 kW` (VG-08/09), hợp đồng lũy kế `< 500M` vs `>= 500M` (VG-13/14). Xử lý sạch dấu phân cách hàng nghìn và đơn vị đo. | **PASS** |
| **Cổng Hold bắt buộc** | 3 | Xung đột Hợp đồng khung vs Chính sách giá `DAT05_SOURCE_CONFLICT` (VG-06, VG-16); Thiếu phụ lục / rách tem Serial `DAT08_MISSING_TABLE_OR_ANNOTATION` (VG-11). | **PASS** |
| **Quét toàn diện 60 Dev / 40 Val** | 2 | Vòng lặp duyệt trọn vẹn 60 câu DEV và 40 câu VAL, xác nhận tỷ lệ phân bổ Hold đạt chuẩn (11 HOLD trong DEV, 7 HOLD trong VAL; 100% ca direct answer đi qua an toàn). | **PASS** |

---

## 3. BẢNG ĐỐI CHIẾU TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA)

| Tiêu chí nghiệm thu | Yêu cầu | Thực tế đạt được | Đánh giá |
| :--- | :--- | :--- | :---: |
| **Điều kiện** | Danh sách lỗi từ SUB14, SUB15, SUB20 | Rà soát toàn diện và xử lý 4 lỗi logic về Scope Mismatch, False Conflict, Định dạng số học và Khóa cờ Future Preview. | **ĐẠT** |
| **Khi** | S3 vá lỗi và pass unit test 60 Dev / 40 Val | Hoàn tất bộ test chuyên biệt `test_selection_60dev_40val.py` đạt 20/20 PASS + 52/52 test SUB14 PASS (tổng 120 test backend pass). | **ĐẠT** |
| **Thì** | 0 lỗi mở còn tồn đọng khi đóng Sprint 4 | 0 lỗi mở (Zero open defects), Ruff lint 0 errors, 0% gọi LLM trong toàn bộ pipeline Selection/Hold. | **ĐẠT** |

---

## 4. HƯỚNG DẪN REVIEW VÀ MERGE

1. **Nhánh làm việc:** `fix/CKPA-72-selection-hold-sprint4`
2. **Reviewers chỉ định:** `[S1]` Hoàng Tiến, `[S2]` Trần Quốc Hưng.
3. **Quy định tuân thủ RACI:** Tuyệt đối **không tag `[S4]` Quý Hải** vào PR của nhánh tính năng để bảo toàn tính độc lập kiểm thử của bộ phận QA (SoD).
4. **Lệnh kiểm tra trước khi merge:**
   ```bash
   cd backend
   pytest tests/test_selection_60dev_40val.py -v
   pytest tests/test_sub14_selection.py -v
   ruff check src tests
   ```

---
*Báo cáo được lập bởi `[S3]` Phạm Lương Yến Nhi — Trình duyệt: `[S1]` Hoàng Tiến & `[S2]` Trần Quốc Hưng.*
