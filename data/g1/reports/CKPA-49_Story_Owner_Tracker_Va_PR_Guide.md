# HƯỚNG DẪN STORY OWNER `CKPA-49`, QUY TRÌNH GITHUB PR & MẪU CẬP NHẬT JIRA (`[P3]` TRẦN CHÍ KHA)

> Tài liệu tuân thủ **SCRM Team Onboarding & Workflow Guide v1.0** (§6.2 Story Owner, §6.4 Sub-task Owner, §9 Cập nhật Jira, §11–19 GitHub Workflow, §22 DoD, §23 SoD) và **RFP SongNhat CKPA**.

---

## 1. Trách nhiệm Story Owner cho `CKPA-49` (Onboarding Guide §6.2)

Trên dự án Jira chính thức **`CKPA` (Board 2)**, `[P3]` Trần Chí Kha được gán làm **Assignee (Story Owner)** của **`CKPA-49`** (`[G1][WP02] Biên tập Họ 1 & 2 Bộ Validator CSV` — `CRM-G1-ST02`, Sprint 3 - G1 Impl W1).

| Sub-task | Mã Excel | Assignee | Trạng thái live (19/11 21:30) | Phụ thuộc | Vai trò theo dõi của Story Owner (`[P3]`) |
|---|---|---|---|---|---|
| **`CKPA-50`** | `CRM-G1-SUB04` | **Chí Kha (`[P3]`)** | `To Do` *(ĐÃ LÀM XONG 100% — sẵn sàng chuyển `In Review`)* | Không có | Tự thực hiện, chạy validator, nộp PR/bằng chứng & chuyển `In Review`, thông báo `[P2]` Hữu Tài |
| **`CKPA-51`** | `CRM-G1-SUB05` | **Hữu Tài (`[P2]`)** | `To Do` | Bị block bởi `CKPA-50` | Đôn đốc `[P2]` ký duyệt nội dung, trạng thái `KNW 03` & ngưỡng Họ 1 (không tự duyệt thay `[P2]`) |
| **`CKPA-52`** | `CRM-G1-SUB06` | **Quốc Hưng (`[S2]`)** | `To Do` | Bị block bởi `CKPA-51` | Bàn giao bộ CSV + Test Fixtures + 4 cảnh báo schema `develop`; kiểm tra khớp đối soát `Expected = Accepted + Quarantined` |

### Checklist DoD của Story `CKPA-49` (Onboarding Guide §22 & Global DoD)
- [ ] `CKPA-50` xong, pass `validate_corpus_g1.ps1` (`0` lỗi, `0` PII hits), có PR & evidence gắn lên Jira.
- [ ] `CKPA-51` được `[P2]` Hữu Tài ký duyệt chính thức (SoD: `Assignee != Reviewer`).
- [ ] `CKPA-52` được `[S2]` Quốc Hưng code 2 Validator CSV + Quarantine và đối soát khớp 100% (`Passages: 40 = 39 Accepted + 1 Quarantined`; `CriticalFields: 16 = 16 Accepted + 0 Quarantined`).
- [ ] Không gán `[S4]` Quý Hải làm reviewer PR nhánh `feat/` hoặc tham gia code cùng `[S2]`/`[S3]`.
- [ ] Tổng hợp bằng chứng đạt `G1-AC01` & `G1-AC02`, báo `[P2]`/`[P1]` nghiệm thu Story `CKPA-49` trước khi chuyển `Done`.

---

## 2. Quy trình GitHub Workflow cho `[P3]` (Onboarding Guide §11–19)

- **Repository:** `https://github.com/ho4ngTien/CRM-Knowledge-and-Policy-Assistant`
- **Branch prefix của `[P3]` (§12):** `data/`
- **⚠️ Lưu ý cần chốt nhanh với `[S1]` Hoàng Tiến trước khi tạo nhánh:**
  - **Onboarding Guide §15** quy định `<prefix>/<JIRA-ID>-<short-description>` → `data/CKPA-50-curate-family1-dat01-08` và `data/CKPA-58-curate-family2-3-ceilings`.
  - **Jira Description** (import từ Excel cũ) ghi `data/CRM-G1-SUB04-curate-family1-dat01-08` và `data/CRM-G1-SUB10-curate-family2-3-ceilings`.
  - Khuyến nghị dùng tên nhánh theo **Onboarding Guide §15 (`data/CKPA-50-...`)** và ghi rõ cả 2 mã `[CKPA-50][CRM-G1-SUB04]` trong tiêu đề PR & commit!

### Bước 1 — Clone & đồng bộ `develop` (nếu máy đã cài Git)
```bash
git clone https://github.com/ho4ngTien/CRM-Knowledge-and-Policy-Assistant.git
cd CRM-Knowledge-and-Policy-Assistant
git fetch origin
git checkout -b develop origin/develop   # hoặc: git checkout develop && git pull origin develop
git status
```

### Bước 2 — Tạo branch & chép dữ liệu cho `CKPA-50` (Họ 1 — Sprint 3)
```bash
git checkout -b data/CKPA-50-curate-family1-dat01-08
```
Đề xuất cấu trúc thư mục chép vào repo (nằm gọn dưới `data/` đã có sẵn trên `develop`):
- `data/g1/family1/Policy_Corpus_Family1.csv`
- `data/g1/family1/Critical_Fields_Family1.csv`
- `data/g1/family1/Source_URI_And_Checksum_Manifest_Family1.csv`
- `data/g1/family1/CKPA-50_Bao_Cao_Bien_Tap_Ho1_G1_AC01.md`
- `data/g1/sources/DOC-001_*.md`, `DOC-004_*.md`, `DOC-006_*.md`, `DOC-007_*.md`
- `data/g1/fixtures/Quarantine_Passages_Fixtures_G1.csv`
- `data/g1/fixtures/Quarantine_CriticalFields_Fixtures_G1.csv`

```bash
git status
git add data/g1/
git commit -m "docs(data): add CKPA-50 Family 1 curated corpus, manifest and quarantine fixtures"
git push -u origin data/CKPA-50-curate-family1-dat01-08
```

### Bước 3 — Tạo branch riêng cho `CKPA-58` (Full 3 Họ — Sprint 4, chỉ tạo PR khi Sprint 4 mở / sau khi `CKPA-52` sẵn sàng)
```bash
git checkout develop
git pull origin develop
git checkout -b data/CKPA-58-curate-family2-3-ceilings
# Chép các file trong CKPA-58_Full_Corpus_G1/ và toàn bộ 11 file sources/ vào data/g1/full/ & data/g1/sources/
git add data/g1/
git commit -m "docs(data): add CKPA-58 full 3-family G1 corpus and SHA-256 manifest"
git push -u origin data/CKPA-58-curate-family2-3-ceilings
```

---

## 3. Mẫu Pull Request chuẩn Onboarding Guide §17 (Copy-Paste trực tiếp lên GitHub)

### PR cho `CKPA-50`
- **Base:** `develop`
- **Compare:** `data/CKPA-50-curate-family1-dat01-08`
- **Title:** `[CKPA-50] Curate Family 1 Policy Corpus, Critical Fields, SHA-256 Manifest & Quarantine Fixtures`
- **Reviewers (đúng SoD — KHÔNG gán `[S4]` Quý Hải):** `[P2]` Hữu Tài (phê duyệt nội dung/chính sách — `CKPA-51`), `[S2]` Quốc Hưng (kiểm tra khớp CSV Validator — `CKPA-52`), `[S1]` Hoàng Tiến (SM).

```markdown
## Summary
Hoàn tất biên tập Corpus & Critical Fields cho Họ 1 (POL-001: Báo giá & Phê duyệt thương mại) theo DEL 01 Field Dictionary, DAT 01–08, KNW 03, SEC 01–02 (Base Scope thuần túy, không bật O1) cùng Manifest SHA-256/source_uri và bộ Test Fixtures Quarantine cho S2.

## Related Jira Issue
- Sub-task: CKPA-50 (CRM-G1-SUB04) — G1-AC01
- Parent Story: CKPA-49 (CRM-G1-ST02) — Sprint 3 - G1 Impl W1
- Unblocks: CKPA-51 ([P2] Hữu Tài), tiếp nối sang CKPA-52 ([S2] Quốc Hưng)

## Changes
- Thêm `Policy_Corpus_Family1.csv` (40 passages, 21 cột UTF-8, giữ nguyên PAS-001..010 từ G0, bổ sung đủ 6 chiều DAT 04 và 7/7 trạng thái KNW 03).
- Thêm `Critical_Fields_Family1.csv` (16 critical fields, 23 cột UTF-8, giữ nguyên CF-001..004 từ G0, tương thích 100% enum & Decimal parsing của `develop`).
- Thêm `Source_URI_And_Checksum_Manifest_Family1.csv` (56/56 bản ghi có SHA-256 & kiểm tra mở `source_uri`) và 4 hồ sơ nguồn tham chiếu (`DOC-001`, `DOC-004`, `DOC-006`, `DOC-007`).
- Thêm bộ Quarantine Test Fixtures tách riêng (`6` passages + `4` critical fields) phủ đủ các nhánh lỗi của `IngestionService._validate_row()`.

## Testing
- Đã chạy `scripts/validate_corpus_g1.ps1`:
  - Schema & Live `develop` IngestionService simulation: `Passages Expected=40 (Accepted 39 + Quarantined 1 PAS-040 DAT 08)`, `CriticalFields Expected=16 (Accepted 16 + Quarantined 0)` — **PASS (0 errors)**.
  - Cross-check FK với 60 Dev Tasks G0: **0 broken FK**.
  - Quét PII theo đúng regex `g1_security_audit_runner.py` (`CKPA-47` của `[P5]` Anh Khoa): **0 Real PII hits**.

## Evidence
- Đính kèm `CKPA-50_Bao_Cao_Bien_Tap_Ho1_G1_AC01.md` và `Source_URI_And_Checksum_Manifest_Family1.csv` trên Jira `CKPA-50`.

## Notes
- Không chuyển `CKPA-50` sang `Done` cho tới khi PR được review/merge và `[P2]` Hữu Tài thẩm định tại `CKPA-51`.
- Đề nghị `[S2]` Quốc Hưng kiểm tra các cảnh báo kỹ thuật schema trong `BAO_CAO_BLOCKERS_VA_VAN_DE_G1_P3.md` (trùng PK `DocumentVersion.id = VER-001` tại `knowledge/models.py:31` và cột `is_tombstoned` của `CriticalField` tại `policy/models.py:61-88`).
```

---

## 4. Mẫu Comment cập nhật Jira (Copy-Paste khi nộp bài lên `CKPA-50` & `CKPA-49`)

### Comment cho `CKPA-50` (chuyển trạng thái `To Do` → `In Review` sau khi đính kèm file/link PR)
> `[Sprint 3 - G1 Impl W1 | CRM-G1-SUB04 | G1-AC01]` Trần Chí Kha (`[P3]` Knowledge and Data Steward) đã hoàn tất biên tập và tự kiểm định Corpus Họ 1 (`POL-001` — Báo giá & Phê duyệt thương mại) trong phạm vi Base Scope (0% O1):
> 1. **Bộ CSV chuẩn UTF-8 khớp 100% live `develop` (`IngestionService` & `PolicyService`):** `Policy_Corpus_Family1.csv` (40 passages, 21 cột, đủ 7/7 trạng thái `KNW 03`, đủ 6/6 chiều `DAT 04`, 3 dòng hạn chế RBAC `SEC 01`, 1 dòng `PAS-040` cố ý `has_essential_attachments=false` để test Quarantine `DAT 08` -> đối soát `40 = 39 Accepted + 1 Quarantined`) và `Critical_Fields_Family1.csv` (16 trường, 23 cột, `16 = 16 Accepted + 0 Quarantined`).
> 2. **Truy vết nguồn & Kiểm định:** `Source_URI_And_Checksum_Manifest_Family1.csv` xác minh 56/56 `source_uri` & `SHA-256`; 0 lỗi gãy FK với 60 Dev Tasks G0; quét PII theo đúng script `g1_security_audit_runner.py` (`CKPA-47` của `[P5]` Anh Khoa) đạt **0 Real PII hits**.
> 3. **Hỗ trợ `[S2]` test Quarantine:** Đính kèm bộ Test Fixtures tách riêng (6 passages + 4 critical fields) phủ đủ mọi nhánh lỗi của `IngestionService._validate_row()`.
> 4. **Bàn giao bước tiếp theo:** Kính mời `[P2]` Hữu Tài thẩm định và ký duyệt tại **`CKPA-51`**, và `[S2]` Quốc Hưng kiểm tra cảnh báo schema (`DocumentVersion.id = VER-001`, 6 chiều `DAT 04`, `CriticalField.is_tombstoned`) trong báo cáo đính kèm trước khi code Validator **`CKPA-52`**.
