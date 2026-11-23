# CKPA-60: Báo cáo & Log Benchmark Hiệu năng OPS 01 (500 dòng <= 30p & LKG)

- **Thời điểm chạy (`Asia/Ho_Chi_Minh`):** `2026-11-23T21:32:12.413709+07:00`
- **Người thực hiện:** `[S5]` Nguyễn Ngọc Duy *(phối hợp `[S2]` Quốc Hưng)*
- **Môi trường:** Isolated Test Environment (`APP_ENV=test`, `SEC 06`)
- **Baseline LKG đầu vào (`CKPA-58`):** `96` dòng (`data/g1/full/Policy_Corpus_G1_Full.csv`)
- **Batch ID (500-row OPS 01):** `eba109e048d849edb069da399b8980f8`

## 1. Kết quả Đo Thời gian Thực thi (Ngưỡng `<= 30.0` phút)

| Giai đoạn xử lý | Thời gian (giây) | Thời gian (phút) | Trạng thái |
|---|---:|---:|:---:|
| 1. Nạp, Validate CSV, Staging & Đối soát | `0.3416s` | `0.005694p` | PASS |
| 2. Lập chỉ mục (`index_passages` hash/metadata) | `0.0050s` | `0.000084p` | PASS |
| 3. Kiểm định LKG & Idempotency | `0.0271s` | `0.000452p` | PASS |
| **TỔNG THỜI GIAN (`OPS 01`)** | **`0.3738s`** | **`0.006230p`** | **PASS (`<= 30.0p`)** |

## 2. Cơ cấu Lô 500 Dòng Thay Đổi & Đối Soát (Reconciliation)

| Nhóm bản ghi | Số lượng | Hành động / Kết quả |
|---|---:|---|
| Thêm mới (`upsert` new) | 380 | Đã nạp & áp dụng hợp lệ |
| Cập nhật (`upsert` existing) | 60 | Đã cập nhật nội dung mới |
| Xóa mềm (`record_action=tombstone`) | 30 | Đánh dấu `is_tombstoned=True` |
| Dòng lỗi (`has_essential_attachments=false`) | 30 | Đưa vào `quarantine_rows`, không ghi đè LKG |
| **Tổng cộng (`Expected`)** | **500** | `470 accepted + 30 quarantined + 0 rejected` |

## 3. Kiểm chứng Last-Known-Good (LKG) & Idempotency

- **LKG khi có dòng lỗi trong batch 500 dòng:** `100% NGUYÊN VẸN` (các bản ghi LKG bị đánh lỗi được cách ly vào quarantine, giữ nguyên nội dung cũ).
- **LKG khi có batch lỗi/trễ (`StaleBatchRejected`):** `100% NGUYÊN VẸN` (batch trễ bị từ chối trước khi ghi đè, tổng số bản ghi LKG không thay đổi).
- **Idempotent Retry (`idempotency_key` trùng):** `PASS (0 bản sao)`.
