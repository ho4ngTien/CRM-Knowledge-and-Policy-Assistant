# Bộ Dữ liệu Đánh giá Độc lập & Hàng rào Chinese Wall (`data/eval/`)

> Quy định bắt buộc theo RFP Mục 8, Mục 11 và [docs/architecture/testing-tiers.md](../../docs/architecture/testing-tiers.md).

## 1. Phân chia 4 Tập Kiểm thử
- `dev_60/` (`60` ca thực tế được phép): Phát triển & kiểm thử hàng ngày cho **Squad B & C**.
- `val_40/` (`40` ca thực tế được phép): Tinh chỉnh ngưỡng truy xuất/xếp hạng trước vòng đóng băng G2.
- `sealed_100/` (`100` ca nghiệm thu niêm phong): **Cấm tuyệt đối Đội phát triển (Squad B & C) xem, đọc hoặc nạp vào nhánh prompt/code**. Chỉ **D1 (`independent_evaluator`)** nắm giữ và chạy đánh giá nghiệm thu chính thức trước Gate G2.
- `challenges_80/` (`80` ca thử thách dựng sẵn, báo cáo tách riêng khỏi `real_200`): Bao gồm `40` ca cốt lõi (future/superseded, threshold boundaries, missing footnotes, conflicting contracts, role access, old CRM notes, prompt injection, mid-answer withdrawal) và **`40` ca định hướng Việt Nam (`VN 02`)**: `10` ngôn ngữ, `10` ngày/phạm vi, `10` ngưỡng/ngoại lệ, `10` quyền/thu hồi.

## 2. Nguyên tắc Lưu trữ An toàn
- **KHÔNG** commit tập câu hỏi/đáp án `sealed_100/` lên nhánh phát triển công khai (`develop`/`main`); chỉ lưu schema/báo cáo tổng hợp ẩn danh sau khi được `D1` & `Privacy/Security Owner` cho phép.
- Mỗi biến thể câu hỏi và bản ghi liên quan phải nằm **trọn trong cùng một phân vùng**, tuyệt đối không rò rỉ chéo giữa `dev_60`/`val_40` và `sealed_100`.
