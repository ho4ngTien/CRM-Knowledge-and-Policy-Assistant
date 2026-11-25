# CKPA-60: Báo cáo & Log Benchmark Hiệu năng OPS 01 (500 dòng <= 30p & LKG)

- **Thời điểm chạy (`Asia/Ho_Chi_Minh`):** `2026-11-25T13:46:26.414834+07:00`
- **Người thực hiện:** `[S5]` Nguyễn Ngọc Duy *(phối hợp `[S2]` Quốc Hưng)*
- **Database Engine:** `SQLite in-memory (isolated unit harness)` (`APP_ENV=test`, `SEC 06`)
- **Baseline LKG đầu vào (`CKPA-58`):** `96` dòng (`data/g1/full/Policy_Corpus_G1_Full.csv`)
- **Batch ID (500-row OPS 01):** `29850a84db51423fa4acc24595399285`

## 1. Kết quả Đo Thời gian Thực thi (Ngưỡng `<= 30.0` phút)

| Giai đoạn xử lý | Thời gian (giây) | Thời gian (phút) | Trạng thái |
|---|---:|---:|:---:|
| 1. Nạp, Validate CSV, Staging & Đối soát | `0.5359s` | `0.008931p` | PASS |
| 2. Lập chỉ mục (`index_passages` hash/metadata) | `0.0057s` | `0.000096p` | PASS |
| 3. Kiểm định LKG, Checksum Fault & Idempotency | `0.0388s` | `0.000647p` | PASS |
| **TỔNG THỜI GIAN (`OPS 01`)** | **`0.5804s`** | **`0.009674p`** | **PASS (`<= 30.0p`)** |

## 2. Cơ cấu Lô 500 Dòng Thay Đổi & Đối Soát (Reconciliation)

| Nhóm bản ghi | Số lượng | Hành động / Kết quả |
|---|---:|---|
| Thêm mới (`upsert` new) | 380 | Đã nạp & áp dụng hợp lệ |
| Cập nhật (`upsert` existing) | 60 | Đã cập nhật nội dung mới |
| Xóa mềm (`record_action=tombstone`) | 30 | Đánh dấu `is_tombstoned=True` |
| Dòng lỗi (`has_essential_attachments=false`) | 30 | Đưa vào `quarantine_rows`, không ghi đè LKG |
| **Tổng cộng (`Expected`)** | **500** | `470 accepted + 30 quarantined + 0 rejected` |

## 3. Kiểm chứng Last-Known-Good (LKG), Checksum Fault & Idempotency

- **LKG khi có dòng lỗi trong batch 500 dòng:** `100% NGUYÊN VẸN` (các bản ghi LKG bị đánh lỗi được cách ly vào quarantine, giữ nguyên nội dung cũ).
- **LKG khi có batch lỗi/trễ (`StaleBatchRejected`):** `100% NGUYÊN VẸN` (batch trễ bị từ chối trước khi ghi đè, tổng số bản ghi LKG không thay đổi).
- **LKG khi Fault-Inject `CHECKSUM_MISMATCH` (`DEF-CKPA75-04`):** `100% NGUYÊN VẸN` (bản ghi sai SHA-256 manifest bị cách ly quarantine, nội dung LKG không đổi).
- **Idempotent Retry (`idempotency_key` trùng):** `PASS (0 bản sao)`.
