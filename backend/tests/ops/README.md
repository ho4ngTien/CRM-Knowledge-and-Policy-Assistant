# Bộ Kiểm thử Vận hành & An toàn (`backend/tests/ops/`)

> Phục vụ Gate `G2`, `G3` & `G4` theo RFP (`OPS 01–08`, `SEC 01–08`) và [SRS](../../../docs/specs/srs.md) (Mục 6).

## Danh mục Kịch bản Kiểm thử Vận hành Bắt buộc
1. **Stale Snapshot Alert (`OPS 01`):** Mô phỏng batch import cuối cùng cũ hơn `IMPORT_SNAPSHOT_STALENESS_HOURS=25`; xác nhận banner cảnh báo hiển thị rõ ràng trên `/chat`, `/evidence` và `/admin`.
2. **Latency & Budget (`OPS 02`, `OPS 06`):** Xác nhận p95 `<= 8s`, max `2` LLM calls/package, `<= 6000` input tokens / `<= 900` output tokens, chặn vượt hạn mức `1000` packages / `2000` calls/tháng.
3. **Late Batch & Tombstone (`DAT 02`):** Nhập delta có `recorded_at` cũ hơn không ghi đè bản mới hơn; bản ghi vắng mặt không tự xóa nếu thiếu `record_action=tombstone`.
4. **Instant Withdrawal `<= 5 min` (`KNW 04`, Worked Case 9):** Rút chính sách khẩn trong khi request/cache đang tồn tại; kiểm chứng DB cập nhật ngay, Redis cache xóa vật lý trong `<= 300s`, câu trả lời đang mở chuyển nhãn `stale`.
5. **Emergency Disable & Manual Fallback (`OPS 05`):** Bật công tắc tắt khẩn cấp; xác nhận nút tra cứu thủ công bằng gói CSV đã phê duyệt hoạt động bình thường.
6. **Direct URL / Download Permission Guard (`SEC 01`):** Đảm bảo direct link `/api/v1/knowledge/passages/{id}` trả `403/409` đồng nhất với `/chat`.
7. **Backup & Restore Drill (`DEL 05`, Gate G4):** Khôi phục toàn bộ PostgreSQL + Redis + thư mục `./data` từ backup lên môi trường mới và chạy smoke test trong RTO mục tiêu.
8. **Open Exit Export (`OPS 08`, Gate G4):** Xuất toàn bộ tri thức, cấu hình trường trọng yếu, referral và feedback sang UTF-8 CSV/JSON không khóa nhà cung cấp.
