# BIÊN BẢN SPRINT 3 REVIEW, RETROSPECTIVE & XÁC NHẬN SMOKE TEST RBAC / 7-STATE (CKPA-56)

- **Mã Jira:** `CKPA-56` (`CRM-G1-SUB09`) | **Parent Epic:** `CKPA-44` | **Story liên quan:** `CKPA-53` (`CRM-G1-ST03`)
- **Mở khóa (Blocks):** `CKPA-61` | **Phụ thuộc đã hoàn tất:** `CKPA-54` (`Done`)
- **Tiêu chí Cổng G1:** `G1-AC04`
- **Truy vết RFP:** `Mục 8`, `Mục 11`, `SEC 01`, `KNW 03`, `ANS 02`, `VN 01`, `Scrum Events`
- **Vai trò tham gia:** `[S1]` Hoàng Tiến (Named Lead / SM — tổng hợp Review & Retro), `[S4]` Quý Hải (Quality Lead — bộ Smoke Test độc lập), `[P1]` Mỹ Vân (PO / Nghiệm thu), `[P5]` Anh Khoa (Security Owner)
- **Ngày lập & xác minh trên `develop`:** `2026-11-24` (commit `c930c32`)

---

## 1. Xác nhận kết quả Smoke Test RBAC 4 Vai trò & 7 Trạng thái KNW 03 (`G1-AC04`)

Dựa trên bộ kiểm thử độc lập tại `backend/tests/test_smoke_s4_retrieval.py`, `backend/tests/test_retrieval_rbac_and_7states.py`, `backend/tests/test_g1_sub01_env_iam.py` và báo cáo nền `docs/work-packages/crm-g1-st03-smoke-test-s4-report.md`, kết quả chạy kiểm chứng thực tế trên nhánh `develop`:

```text
cd backend && python -m pytest tests/test_smoke_s4_retrieval.py tests/test_retrieval_rbac_and_7states.py tests/test_g1_sub01_env_iam.py -v
======================== 20 passed, 1 warning in 0.38s ========================

cd backend && python -m pytest -q
======================== 100 passed, 1 warning in 1.46s =======================
```

### Tóm tắt kiểm chứng cốt lõi
- **RBAC 4 vai trò chuẩn RFP (`SEC 01`):** `reader`, `policy_owner`, `steward`, `administrator` tách biệt 100% ở tầng Pre-Retrieval (0% rò rỉ dữ liệu ngoài quyền).
- **7 trạng thái vòng đời xuất bản (`KNW 03`):** Chỉ trả về `effective` theo mặc định; chặn 100% `draft`, `owner_reviewed`, `approved`, `scheduled`, `superseded`, `quarantined`, `feedback_candidate`; trạng thái `withdrawn` áp dụng **Strict Fail-Closed** kể cả khi bật chế độ lịch sử.
- **Chuẩn hóa tiếng Việt (`VN 01`) & 100 câu hỏi (`CKPA-55`):** 60 DEV + 40 VAL phủ đủ 3 họ chính sách Base Scope, 0% PII, bảo toàn 14 từ phủ định tiếng Việt.
- **Tách vai SoD (`Mục 8`, `Mục 11`):** Bộ test độc lập `test_smoke_s4_retrieval.py` tách khỏi nhánh lập trình của S3; `[S1]` chỉ chạy xác minh regression và lập biên bản Scrum, không sửa logic kiểm định độc lập của `[S4]`.

---

## 2. Sprint 3 Review — Tổng kết Increment (G1 Impl W1)

| Mã Jira | Hạng mục | Người thực hiện | Trạng thái | Bằng chứng chính |
| :--- | :--- | :--- | :---: | :--- |
| `CKPA-46` | Dựng môi trường Test tách Prod & IAM 4 vai (`SEC 06`) | `[S5]` Ngọc Duy | `Done` | PR #25 (`7a7e154`), `test_g1_sub01_env_iam.py` |
| `CKPA-47` | Kiểm toán dữ liệu Test 0% PII (`SEC 02`, `DAT 07`) | `[P5]` Anh Khoa | `Done` | `g1_security_audit_runner.py`, `g1_pii_audit_CKPA-47.log` (48 files @ `a5a6a14`) |
| `CKPA-48` | Lập kho `sealed-eval-repo` chặn Read S2/S3 (`Mục 8`) | `[S4]` Quý Hải | `Done` | Tài liệu thiết lập kho & phân quyền SoD |
| `CKPA-50` | Biên tập Họ 1 đủ trường & `DAT 08` / `source_uri` | `[P3]` Chí Kha | `Done` | PR #18 (`a5a6a14`), Corpus & Critical Fields Họ 1 |
| `CKPA-51` | Ký duyệt Corpus & Critical Fields Họ 1 (`DAT 03`) | `[P2]` Hữu Tài | `Done` | Biên bản phê duyệt Họ 1 + Sign-off `[P1]` |
| `CKPA-52` | Code 2 bộ Validator CSV & Quarantine Họ 1 (`WP 02`) | `[S2]` Quốc Hưng | `Done` | PR #26 (`09e7cf4`), `CKPA-52_Import_Log_Ho1.md` |
| `CKPA-54` | Code lọc RBAC & đủ 7 trạng thái `KNW 03` (`WP 03`) | `[S3]` Yến Nhi | `Done` | PR #20 (`375a5c4`), `test_retrieval_rbac_and_7states.py` |
| `CKPA-55` | 100 câu hỏi thực & Từ điển `VN 01` | `[P4]` Trà My | `Done` | `100_real_questions_clean_pii.csv`, `vn01_crm_dictionary.json` |
| `CKPA-56` | Smoke RBAC/7-State & Họp Sprint 3 Review/Retro | `[S4]` / `[S1]` | **Hoàn tất** | Báo cáo smoke `crm-g1-st03-smoke-test-s4-report.md` & biên bản này |

**Kết quả Sprint 3:** 9/9 Sub-tasks và 3/3 Vertical Stories (`CKPA-45`, `CKPA-49`, `CKPA-53`) đạt mục tiêu Sprint 3 (G1 Impl W1).

---

## 3. Sprint 3 Retrospective — Bài học & Hành động cải tiến cho Sprint 4–5

### Điểm làm tốt (What went well)
1. **Lát cắt dọc hoạt động sớm:** Hạ tầng Test + IAM 4 vai (`CKPA-46`), Corpus Họ 1 (`CKPA-50/51`), CSV Validators (`CKPA-52`), và Pre-Retrieval RBAC/7-State (`CKPA-54`) đều có unit/integration tests tự động chạy xanh (`100/100` tests trên `develop`).
2. **Tuân thủ SoD tốt ở tầng Build:** S2/S3 tách nhánh `feat/` rõ ràng, PR đều qua review ngang hàng trước khi merge.

### Điểm cần khắc phục (What needs improvement)
1. **Phạm vi quét PII của `CKPA-47` mới dừng ở commit `a5a6a14`:** Sau Sprint 3 có thêm Corpus Họ 2–3 (`CKPA-58`) và bộ 200 câu hỏi (`CKPA-66`), bắt buộc phải chạy quét lại 0% PII trước khi chốt G1.
2. **Đồng bộ quản trị Jira & Sprint:** Các Sprint 3–5 vẫn đang ở trạng thái `future`, ngày `Due date` bị lệch so với lịch Sprint, và một số Story không tự đóng khi toàn bộ task con đã `Done`.
3. **Kỷ luật kiểm chứng bằng chứng nghiệm thu:** Mọi script kiểm toán bảo mật/QA trong Sprint 4–5 (như `CKPA-70`, `CKPA-75`) phải chạy trực tiếp trên API/module thật của hệ thống với đúng 4 vai trò RFP (`reader`, `policy_owner`, `steward`, `administrator`), tuyệt đối không dùng script hardcode giả lập.

### Hành động cải tiến (Action Items)
| # | Hành động | Phụ trách | Thời hạn |
| :--- | :--- | :--- | :--- |
| AI-1 | Bắt buộc chạy lại bộ quét 0% PII trên toàn bộ Corpus 3 họ & 200 câu hỏi tại `CKPA-79` trước khi chốt G1 | `[P5]` Anh Khoa | Sprint 5 |
| AI-2 | Yêu cầu mọi bằng chứng kiểm toán/QA đính kèm PR hoặc output thực thi thật trên hệ thống trước khi `[P1]` ký nghiệm thu | `[S1]` Hoàng Tiến & `[P1]` Mỹ Vân | Áp dụng ngay từ Sprint 4 |
| AI-3 | Tách bạch rõ phạm vi Bắt buộc (`M`) và Tùy chọn (`O1` — chỉ kiểm tra trạng thái disabled/blocked nếu chưa có quyết định phê duyệt O1) | `[S1]` Hoàng Tiến | Sprint 4–5 |
| AI-4 | Đồng bộ trạng thái Story/Epic & Sprint trên Jira sau mỗi lần hoàn tất Sub-task | `[S1]` Hoàng Tiến | Hàng tuần |
