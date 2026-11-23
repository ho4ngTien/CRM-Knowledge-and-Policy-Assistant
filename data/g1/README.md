# Gate G1 Curated Data Package — CKPA-50 (Family 1) & CKPA-58 (Full 3 Families)

Gói dữ liệu nguồn Base Scope (0% O1, 0% PII thật) do `[P3]` Trần Chí Kha biên tập cho **CKPA-50** (Sprint 3 — Họ 1) và **CKPA-58** (Sprint 4 — Full 3 Họ `POL-001..003`).

## 1. Gói Họ 1 — CKPA-50 (`family1/`)
- [Policy_Corpus_Family1.csv](family1/Policy_Corpus_Family1.csv) — 40 passages (21 cột UTF-8, `39 Accepted + 1 Quarantined [PAS-040]`).
- [Critical_Fields_Family1.csv](family1/Critical_Fields_Family1.csv) — 16 critical fields (23 cột UTF-8).
- [Source_URI_And_Checksum_Manifest_Family1.csv](family1/Source_URI_And_Checksum_Manifest_Family1.csv) — Đối soát 56/56 `source_uri` & `SHA-256`.
- [CKPA-50_Bao_Cao_Bien_Tap_Ho1_G1_AC01.md](family1/CKPA-50_Bao_Cao_Bien_Tap_Ho1_G1_AC01.md) — Báo cáo biên tập Họ 1 (`G1-AC01`).

## 2. Gói Full 3 Họ — CKPA-58 (`full/`)
- [Policy_Corpus_G1_Full.csv](full/Policy_Corpus_G1_Full.csv) — 96 passages / 11 tài liệu `DOC-001..DOC-011` (`93 Accepted + 3 Quarantined [PAS-040, PAS-066, PAS-082]`, đủ 5/5 lớp `DAT 03`, 6/6 chiều `DAT 04`, 7/7 trạng thái `KNW 03`).
- [Critical_Fields_G1_Full.csv](full/Critical_Fields_G1_Full.csv) — 40 critical fields (23 cột UTF-8, `40 Accepted + 0 Quarantined`).
- [Source_URI_And_Checksum_Manifest_G1_Full.csv](full/Source_URI_And_Checksum_Manifest_G1_Full.csv) — Đối soát 136/136 `source_uri` & `SHA-256`.
- [CKPA-58_Bao_Cao_Bien_Tap_Full_Corpus_3Ho.md](full/CKPA-58_Bao_Cao_Bien_Tap_Full_Corpus_3Ho.md) — Báo cáo biên tập Full Corpus 3 Họ (`G1-AC01`).

## 3. Test Fixtures & Báo cáo theo dõi (`fixtures/`, `reports/`)
- [Quarantine_Passages_Fixtures_G1.csv](fixtures/Quarantine_Passages_Fixtures_G1.csv) & [Quarantine_CriticalFields_Fixtures_G1.csv](fixtures/Quarantine_CriticalFields_Fixtures_G1.csv) — Bộ fixture kiểm thử Quarantine cho `[S2]` (`CKPA-52`/`CKPA-59`).
- [BAO_CAO_BLOCKERS_VA_VAN_DE_G1_P3.md](reports/BAO_CAO_BLOCKERS_VA_VAN_DE_G1_P3.md) — Báo cáo phụ thuộc & cảnh báo kỹ thuật schema `develop`.
- [CKPA-49_Story_Owner_Tracker_Va_PR_Guide.md](reports/CKPA-49_Story_Owner_Tracker_Va_PR_Guide.md) — Bảng theo dõi Story `CKPA-49` & hướng dẫn PR.

## Tự kiểm định cục bộ
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File data/g1/scripts/validate_g1_repo.ps1
```
