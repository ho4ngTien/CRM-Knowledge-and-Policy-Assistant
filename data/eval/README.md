# Bộ Dữ liệu Đánh giá Độc lập & Hàng rào Chinese Wall (`data/eval/`)

> Quy định bắt buộc theo RFP Mục 8, Mục 11, [docs/04-setup-and-operations.md](../../docs/04-setup-and-operations.md), và Quyết định bàn giao Dev/Val số `CKPA-67` (ban hành ngày 24/11/2026).

## 1. Phân chia 4 Tập Kiểm thử & Tổ chức Lưu trữ 3 Kho Git
Toàn bộ dữ liệu kiểm thử và đánh giá độc lập của dự án được quản lý tại Tổ chức GitHub độc lập **[ckpa-dev-val-eval](https://github.com/ckpa-dev-val-eval)** nhằm bảo đảm tính bí mật và ranh giới Chinese Wall tuyệt đối:

- **`dev_60/`** (`60` ca thực tế được phép, sạch PII): Phục vụ phát triển & kiểm thử hàng ngày cho đội Build (**`S2` Quốc Hưng, `S3` Yến Nhi, `S5` Ngọc Duy**).
- **`val_40/`** (`40` ca thực tế được phép, sạch PII): Phục vụ tinh chỉnh ngưỡng truy xuất/xếp hạng và selection hold trước vòng đóng băng G2.
  * *Kênh bàn giao `dev_60` + `val_40`:* Kho Git Private `ckpa-dev-val-eval` do `[S4]` quản trị ACL (cấp quyền `READ-ONLY` cho `[S2]`, `[S3]`), kèm `partition_manifest` mã băm SHA-256 xác nhận 0% trùng lặp với tập Sealed.
- **`sealed_100/`** (`100` ca nghiệm thu niêm phong độc lập): **Cấm tuyệt đối Đội phát triển (`S2, S3, S5`) xem, đọc, fork hoặc clone**. Lưu trữ độc quyền tại kho niêm phong vật lý **[ckpa-dev-val-eval/sealed-eval-repo](https://github.com/ckpa-dev-val-eval/sealed-eval-repo)** dưới quyền sở hữu của **`S4` (Quý Hải — Quality Lead)**.
  * *Gói thay thế độc lập 25/11/2026:* Toàn bộ 100 ca Sealed công khai cũ đã bị hủy hiệu lực niêm phong và được thay thế bằng gói 100 tác vụ mới 100% do `[P4]` Ngô Thị Trà My biên soạn độc lập (24 cột chuẩn, 25 nhóm biến thể `VG-19..VG-43`, quota chuẩn `52 POL-001 / 24 POL-002 / 24 POL-003`, 100% gắn `source_uri` hợp lệ từ 11 tài liệu gốc, 0% PII).
- **`challenges_80/`** (`80` ca thử thách dựng sẵn, lưu trong `sealed-eval-repo`): Báo cáo tách riêng khỏi `real_200`, gồm `40` ca System-Wide và `40` ca định hướng phức tạp tiếng Việt **`VN 02`** (`10` từ đa nghĩa, `10` phủ định kép, `10` phương ngữ, `10` bẫy thông tin).

## 2. Dấu Kiểm toán & Mã Băm Toàn vẹn (Commit Release `33180db`)
Kho niêm phong `sealed-eval-repo` đã được đóng cổng chính thức tại trạng thái **`APPROVED_RELEASED_FROZEN`** (Jira `CKPA-67` & `CKPA-68`):
- **Tác vụ Sealed 100 (`sealed_100.csv`):** `372988c46f537e5f1f5da8fe1fb5602119a5aead076350097b2f95a6abc94b96`
- **Tập Thử thách 80 Challenges (JSON):** `a6c09a7dd0fe2e56b0c94d1f7d922ad9efdeea22e0ef3f7fa439840c35c2a6f8`
- **Tập Thử thách 80 Challenges (CSV):** `aff71709e298c5ee2cbbc5f7d40cffda2c09b9a6b4b7083251f35373205fb606`
- **Biên bản ký xác nhận kép:** `CKPA-68_Bien_Ban_Dong_Gan_Nhan_Va_Ky_Xac_Nhan_Kep_P2_P3.md` (được ký bởi Policy Reviewer #1 `[P2]` Hữu Tài và Policy Reviewer #2 / Data Steward `[P3]` Chí Kha, xác nhận đối soát khớp Full Corpus 3 Họ).

## 3. Nguyên tắc An toàn Dữ liệu trên Build Repo này (`main-app-repo`)
- Build repo này **CHỈ** lưu trữ tệp cấu hình, mã nguồn, tài liệu và `vn01_crm_dictionary.json`.
- Tập `60_dev_tasks_nonleaking_clean_pii.csv` tại đây là bản snapshot phát triển công khai không chứa biến thể Sealed. Sau khi kho bàn giao Private `ckpa-dev-val-eval` vận hành, các cập nhật bộ dữ liệu đánh giá nội bộ sẽ được đồng bộ trực tiếp qua kho Private đó.
- **TUYỆT ĐỐI KHÔNG** commit bất kỳ câu hỏi, đáp án, biến thể hoặc tệp dữ liệu nào thuộc `sealed_100` hoặc `challenges_80` lên repo này. Mọi hành vi làm lộ câu hỏi niêm phong sang đội Build đều dẫn tới việc hủy hiệu lực bộ dữ liệu và bắt buộc làm lại quy trình thay thế độc lập.
