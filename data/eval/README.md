# Bộ Dữ liệu Đánh giá Độc lập & Hàng rào Chinese Wall (`data/eval/`)

> Quy định bắt buộc theo RFP Mục 8, Mục 11 và [docs/04-setup-and-operations.md](../../docs/04-setup-and-operations.md).

## 1. Phân chia 4 Tập Kiểm thử
- `dev_60/` (`60` ca thực tế được phép): Phát triển & kiểm thử hàng ngày cho đội Build (**`S2` Quốc Hưng, `S3` Yến Nhi, `S5` Ngọc Duy**).
- `val_40/` (`40` ca thực tế được phép): Tinh chỉnh ngưỡng truy xuất/xếp hạng trước vòng đóng băng G2.
- `sealed_100/` (`100` ca nghiệm thu niêm phong): **Cấm tuyệt đối Đội phát triển (`S2, S3, S5`) xem, đọc hoặc nạp vào nhánh prompt/code**. Chỉ **`S4` (Quý Hải — `Quality lead` / `independent_evaluator`)** nắm giữ và chạy đánh giá nghiệm thu chính thức trước Gate G2.
- `challenges_80/` (`80` ca thử thách dựng sẵn, báo cáo tách riêng khỏi `real_200`): Bao gồm `40` ca cốt lõi (future/superseded, threshold boundaries, missing footnotes, conflicting contracts, role access, old CRM notes, prompt injection, mid-answer withdrawal) và **`40` ca định hướng Việt Nam (`VN 02`)**: `10` ngôn ngữ, `10` ngày/phạm vi, `10` ngưỡng/ngoại lệ, `10` quyền/thu hồi.

## 2. Nguyên tắc Lưu trữ An toàn & Tệp hiện có trong Build Repo
- Build repo này **CHỈ** lưu trữ `60_dev_tasks_nonleaking_clean_pii.csv` và `vn01_crm_dictionary.json`.
- Các tệp `100_real_questions_clean_pii.csv` và `100_real_questions_clean_pii.json` đã bị **xóa khỏi Build repo** để thực thi nghiêm ngặt hàng rào **Chinese Wall (RFP Mục 8)**, chỉ lưu riêng trong `sealed-eval-repo` dưới quyền kiểm soát của `S4` (`independent_evaluator`).
- **KHÔNG** commit tập câu hỏi/đáp án `sealed_100/` lên nhánh phát triển công khai (`develop`/`main`); chỉ lưu schema/báo cáo tổng hợp ẩn danh sau khi được **`S4` (Quý Hải)** & **`P5` (Anh Khoa — Privacy/Security Owner)** cho phép.
- Mỗi biến thể câu hỏi và bản ghi liên quan phải nằm **trọn trong cùng một phân vùng**, tuyệt đối không rò rỉ chéo giữa `dev_60`/`val_40` và `sealed_100`.
