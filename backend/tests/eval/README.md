# Bộ Kiểm thử Đánh giá Độc lập (`backend/tests/eval/`)

> Phục vụ kiểm thử định kỳ trước Gate `G1` & nghiệm thu bắt buộc trước Gate `G2` (`RFP Mục 8`, `Phụ lục B`, `VN 02`).

## 1. Cấu trúc Đánh giá Tách biệt Bắt buộc
- **`real_200` (`60 dev` / `40 val` / `100 sealed`):**
  - `60 dev` & `40 val`: Bộ kiểm thử tự động chạy CI/tinh chỉnh bởi Squad B & C.
  - `100 sealed`: **Chỉ chạy bởi D1 (`independent_evaluator`)** trong môi trường cách ly Chinese Wall. Không commit dữ liệu `100 sealed` lên nhánh `develop`.
- **`challenges_80` (Báo cáo tách riêng khỏi `real_200`):**
  - `40` thử thách chuẩn RFP (chính sách tương lai, phiên bản cũ, ngưỡng biên, thiếu chú thích/bảng, xung đột hợp đồng, sai quyền, ghi chú CRM cũ, prompt injection, rút chính sách giữa chừng).
  - **`40` thử thách tiếng Việt (`VN 02`):** `10` ngôn ngữ/phủ định/đồng nghĩa, `10` ngày `Asia/Ho_Chi_Minh`/phạm vi, `10` ngưỡng tiền tệ/thời hạn/ngoại lệ, `10` quyền `audience`/thu hồi khẩn.

## 2. Ngưỡng Đậu Cổng Phát hành G2
- Critical controls: **`0` lỗi**.
- Applicability (`100 Sealed` có thể trả lời): **`>= 95%`**.
- Grounding: **`>= 95%`** với **`0` trích dẫn bịa**; Completeness: **`>= 90%`**.
- Retrieval `Recall@5`: **`>= 90%`**.
- Usefulness: **`>= 80%`**; Fabrication trên ca không thể trả lời: **`<= 5%`**.
