# Gate G1 Curated Data Package — CKPA-50 (Family 1: POL-001)

Gói dữ liệu nguồn Base Scope (0% O1, 0% PII thật) do [P3] Trần Chí Kha biên tập cho **CKPA-50** (CRM-G1-SUB04, Story CKPA-49, Sprint 3 - G1 Impl W1).

## Danh mục tệp bàn giao
- [Policy_Corpus_Family1.csv](family1/Policy_Corpus_Family1.csv) — 40 passages (21 cột UTF-8, đủ 7/7 trạng thái KNW 03, 6/6 chiều DAT 04).
- [Critical_Fields_Family1.csv](family1/Critical_Fields_Family1.csv) — 16 critical fields (23 cột UTF-8, khớp PolicyService & enums.py).
- [Source_URI_And_Checksum_Manifest_Family1.csv](family1/Source_URI_And_Checksum_Manifest_Family1.csv) — Đối soát 56/56 source_uri & SHA-256.
- [CKPA-50_Bao_Cao_Bien_Tap_Ho1_G1_AC01.md](family1/CKPA-50_Bao_Cao_Bien_Tap_Ho1_G1_AC01.md) — Báo cáo biên tập Họ 1 (G1-AC01).
- [Quarantine_Passages_Fixtures_G1.csv](fixtures/Quarantine_Passages_Fixtures_G1.csv) & [Quarantine_CriticalFields_Fixtures_G1.csv](fixtures/Quarantine_CriticalFields_Fixtures_G1.csv) — Bộ fixture kiểm thử Quarantine cho [S2] (CKPA-52).
- [CKPA-52_Import_Log_Ho1.md](reports/CKPA-52_Import_Log_Ho1.md) — Log batch, đối soát, số dòng staging và quarantine của lần nạp Họ 1.
- [BAO_CAO_BLOCKERS_VA_VAN_DE_G1_P3.md](reports/BAO_CAO_BLOCKERS_VA_VAN_DE_G1_P3.md) — Báo cáo phụ thuộc & cảnh báo kỹ thuật schema develop.
- [CKPA-49_Story_Owner_Tracker_Va_PR_Guide.md](reports/CKPA-49_Story_Owner_Tracker_Va_PR_Guide.md) — Bảng theo dõi Story CKPA-49 & hướng dẫn PR.

## Tự kiểm định cục bộ
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File data/g1/scripts/validate_g1_repo.ps1
```

Sau khi áp dụng migration và cấu hình database cô lập:

```powershell
Set-Location backend
python -m scripts.import_family1
```