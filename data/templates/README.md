# Hợp đồng 2 Tệp Mẫu CSV UTF-8 (`data/templates/`)

> Chi tiết kiểm tra kiểu dữ liệu & quy tắc Quarantine xem tại [docs/architecture/erd-and-csv-contract.md](../../docs/architecture/erd-and-csv-contract.md).

## 1. Phạm vi Base Scope (Mục 2 RFP & `DAT 01, 02, 08, KNW 03`)
- **Bắt buộc UTF-8** (hỗ trợ UTF-8 with BOM hoặc UTF-8 chuẩn; cấm bảng mã TCVN3/VNI-Windows/Windows-1258).
- **`passages_template.csv` (21 cột):** Tối đa `30` tài liệu hiệu lực, `300` đoạn văn bản tuyển chọn, mỗi đoạn `<= 6.000` ký tự Unicode; batch ngày `<= 500` dòng thay đổi. Nếu `has_essential_attachments=false` -> bắt buộc đưa vào **Quarantine**.
- **`critical_fields_template.csv` (23 cột):** Tối đa `50` trường chính sách trọng yếu có cấu trúc cho `3` nhóm chính sách khởi đầu. Khi `field_type=currency` bắt buộc có `currency` (`VND`/`USD`).
- **Xóa bản ghi có tường minh (`DAT 02`):** Bắt buộc dùng `record_action=tombstone` (hoặc đối soát `full_snapshot` được phê duyệt); không suy diễn xóa từ dòng vắng mặt.

## 2. Tách biệt Tùy chọn `O1`
- Không có tệp template hay code cho `O1 Selected CRM Context` trong Base Scope; chỉ bổ sung thành Change Request tách biệt nếu Gate G0 phê duyệt ký hợp đồng tùy chọn riêng.
