# CKPA-52 Import Log — Họ 1

- Thời điểm chạy: `2026-11-21T11:13:17.318167+07:00`
- Chế độ: `FULL_SNAPSHOT`; dữ liệu hợp lệ lưu trong `import_records` (staging),
  dữ liệu lỗi lưu trong `quarantine_rows`; không tự phát hành vào retrieval.
- Nguồn kiểm checksum: `Source_URI_And_Checksum_Manifest_Family1.csv`.

| CSV | Batch ID | Expected | Received | Imported | Quarantined | Rejected |
|---|---|---:|---:|---:|---:|---:|
| `Policy_Corpus_Family1.csv` | `9a8352fdf52b45eaaec4cc2534d48837` | 40 | 40 | 39 | 1 | 0 |
| `Critical_Fields_Family1.csv` | `ece52479b259414f954c836d2225f7dc` | 16 | 16 | 16 | 0 | 0 |

## Quarantine
- `Policy_Corpus_Family1.csv` row 21 (`PAS-040`): `MISSING_ESSENTIAL_ATTACHMENTS` — DAT 08 Quarantine: missing essential table, diagram, or footnote.

## Reconciliation

- Passages: `40 = 39 imported + 1 quarantined` (PAS-040 /
  `MISSING_ESSENTIAL_ATTACHMENTS`).
- Critical fields: `16 = 16 imported + 0 quarantined`.
- Mỗi lô được bảo vệ bằng idempotency key; chạy lại cùng nội dung không tạo bản sao.
