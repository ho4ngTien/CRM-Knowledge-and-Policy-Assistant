# BÁO CÁO TÌNH HÌNH JIRA, TIẾN ĐỘ, PHỤ THUỘC (BLOCKERS) & CẢNH BÁO KỸ THUẬT G1 — `[P3]` TRẦN CHÍ KHA

- **Vai trò RFP:** `[P3]` Knowledge and Data Steward (Purchaser)
- **Thời điểm đối soát live Jira & GitHub `develop`:** `2026-11-19 21:35 (+07)` (`Asia/Ho_Chi_Minh`)
- **Phạm vi thực hiện:** Các hạng mục độc lập trong **Gate G1** (theo nền tảng G0 đã chốt, **Base Scope thuần túy — cắt O1**, khớp RFP 28 trang & **SCRM Team Onboarding & Workflow Guide v1.0**).

---

## 1. Tình hình Jira Live (Giải thích vì sao có `CKPA-50` & sự tồn tại của 2 dự án)

> **Xác nhận:** Không có bất kỳ thao tác ghi/sửa nào lên Jira từ trợ lý AI. Toàn bộ sự thay đổi trên Jira chiều ngày `2026-11-19` do **`[S1]` Hoàng Tiến** trực tiếp tái cấu trúc sang dự án Scrum chuẩn.

Hiện tại trên `https://crm-knowledge-and-policy-assistant.atlassian.net` đang tồn tại **2 dự án song song**:

| Dự án / Board | Trạng thái thực tế | Giải thích mã task của `[P3]` Chí Kha |
|---|---|---|
| **`CKPAOLD`** (`Board 1: SCRUM board`) | **Dự án CŨ đã đổi tên sang `OLD`** (dữ liệu gốc của file export `CKPA_Jira_Export_2026-11-19` lúc `03:27` và đợt import cũ lúc `13:40`) | • Trong file export sáng `19/11` chỉ có `CKPA-1..62` (khuyết `50..57`) nên **không có `CKPA-50`**.<br>• Đợt import cũ đặt task G1 của Kha là `CKPAOLD-65` (Story), `CKPAOLD-77`, `CKPAOLD-83`, `CKPAOLD-101`. |
| **`CKPA`** (`Board 2: CKPA board`) | **Dự án CHÍNH THỨC MỚI** (`84` issues `CKPA-1..84`, do `[S1]` Hoàng Tiến dựng lúc `16:36–17:37` chiều `19/11`, đúng cấu trúc `Epic -> Story -> Sub-task`). **Cả team đã chuyển sang làm trên dự án này!** | • **`CKPA-47`** (`[P5]` Anh Khoa) đã chuyển **`In Progress`** lúc `20:47` (kèm chứng nhận 0% PII & `g1_security_audit_runner.py`).<br>• **`CKPA-55`** (`[P4]` Trà My) đã chuyển **`In Progress`** lúc `21:29`.<br>• Task của Kha trên **`CKPA` MỚI**:<br>&nbsp;&nbsp;- **G0 (4 issue đang `To Do` do mới dựng lại cấu trúc):** `CKPA-10`, `CKPA-15`, `CKPA-24`, `CKPA-25`.<br>&nbsp;&nbsp;- **G1 (4 issue trọng tâm):** **`CKPA-49`** *(Story Owner)*, **`CKPA-50`** *(Sub-task Họ 1)*, **`CKPA-58`** *(Sub-task Họ 2–3)*, **`CKPA-82`** *(Sub-task re-verify Sprint 5)*. |

---

## 2. Hạng mục G1 `[P3]` đã hoàn thành ngay (Đã kiểm định 100% với RFP + Live `develop` + Script PII `[P5]`)

| Jira Issue (`CKPA` MỚI) | Vai trò Onboarding Guide | Sprint | Trạng thái làm xong | Sản phẩm đầu ra (0 lỗi, 0 broken FK, 0 PII hits) |
|---|---|---|---|---|
| **`CKPA-49`** *(Story)* | **Story Owner** (§6.2) | Sprint 3 | **Đã lập bảng theo dõi Story, quy trình GitHub PR & mẫu comment Jira** | • `CKPA-49_Story_Owner_Tracker_Va_PR_Guide.md` (theo dõi 3 Sub-task `CKPA-50/51/52`, DoD §22, PR template §17, SoD §4/§12) |
| **`CKPA-50`** (`CRM-G1-SUB04`) | **Sub-task Owner** (§6.4) | Sprint 3 | **XONG 100% — Sẵn sàng tạo PR & chuyển `In Review`** | • `Policy_Corpus_Family1.csv` (40 passages, 21 cột UTF-8; `39 Accepted + 1 Quarantined PAS-040`)<br>• `Critical_Fields_Family1.csv` (16 fields, 23 cột UTF-8; `16 Accepted + 0 Quarantined`)<br>• `Source_URI_And_Checksum_Manifest_Family1.csv` (56/56 SHA-256 + `source_uri`)<br>• `CKPA-50_Bao_Cao_Bien_Tap_Ho1_G1_AC01.md` |
| **`CKPA-58`** (`CRM-G1-SUB10`) | **Sub-task Owner** (§6.4) | Sprint 4 | **ĐÃ SOẠN XONG 100% BẢN FULL CORPUS GỐI ĐẦU** *(chờ Story cha `CKPA-57` mở block)* | • `Policy_Corpus_G1_Full.csv` (96 passages / 11 docs, `<= 300/30` trần; `93 Accepted + 3 Quarantined`)<br>• `Critical_Fields_G1_Full.csv` (40 fields, `<= 50` trần; `40 Accepted + 0 Quarantined`)<br>• `Source_URI_And_Checksum_Manifest_G1_Full.csv` (136/136 SHA-256 + `source_uri`)<br>• `CKPA-58_Bao_Cao_Bien_Tap_Full_Corpus_3Ho.md` |
| **Test Fixtures + Self-Audit** | Hỗ trợ `[S2]` `CKPA-52/59` & `[S5]` `CKPA-60` | Sprint 3–4 | **XONG 100%** (tách riêng khỏi corpus chính) | • `Quarantine_Passages_Fixtures_G1.csv` (**6 ca** phủ 100% nhánh `IngestionService._validate_row`)<br>• `Quarantine_CriticalFields_Fixtures_G1.csv` (**4 ca**)<br>• `scripts/validate_corpus_g1.ps1` (kiểm đồng thời RFP + live `develop` + PII script `CKPA-47` của `[P5]`) |
| **`CKPA-82`** (`CRM-G1-SUB28`) | **Sub-task Owner** (§6.4) | Sprint 5 | **BẢN NHÁP PRE-CHECK** *(chờ chốt Corpus cuối Sprint 4 mới ký chính thức)* | • `CKPA-82_Draft_Reverify_G1_AC01/CKPA-82_Bien_Ban_Reverify_Source_URI_G1_AC01_DRAFT.md` |

---

## 3. Bản đồ Phụ thuộc (Ai đang block `[P3]` & `[P3]` đang block ai) — Để báo cáo Team / Leader

### A. Trên Gate G1 (trọng tâm hiện tại — Dự án `CKPA`)
| Issue của `[P3]` | Sprint | Ai đang BLOCK `[P3]` | `[P3]` đang BLOCK ai (Ai đang chờ `[P3]`) | Hành động cần báo cáo ngay |
|---|---|---|---|---|
| **`CKPA-49` (Story)** & **`CKPA-50`** *(Biên tập Họ 1)* | **Sprint 3** | **KHÔNG CÓ** | **`CKPA-51` — Hữu Tài (`[P2]`)** *(Ký duyệt Corpus & Critical Fields Họ 1)* → nối tiếp sang **`CKPA-52` — Quốc Hưng (`[S2]`)** → nối tiếp sang **`CKPA-57` & `CKPA-61`** | **Nộp `CKPA-50` ngay hôm nay**, gắn PR/evidence, chuyển `In Review` và ping **`[P2]` Hữu Tài** duyệt **`CKPA-51`** để mở khóa critical path cho **`[S2]` Quốc Hưng**! |
| **`CKPA-58`** *(Biên tập Họ 2–3 Full)* | **Sprint 4** | **Không bị block trực tiếp.**<br>**Gián tiếp qua Story cha `CKPA-57` (`[S2]` Quốc Hưng):**<br>• `CKPA-48` — **Quý Hải (`[S4]`)** *(Lập `sealed-eval-repo`)*<br>• `CKPA-52` — **Quốc Hưng (`[S2]`)** *(Code 2 Validator CSV Họ 1)* | • **`CKPA-62` — Hữu Tài (`[P2]`)** *(Duyệt Họ 2–3, 6 chiều & Hold)*<br>• **`CKPA-60` — Ngọc Duy (`[S5]`)** *(Benchmark OPS 01 500 dòng `<= 30p` & LKG)* | Báo Leader: `[P3]` đã chuẩn bị sẵn 100% file Họ 2–3 sạch lỗi; chỉ chờ Hưng xong `CKPA-52` & Hải xong `CKPA-48` là nạp test và mở khóa ngay cho Tài (`CKPA-62`) + Duy (`CKPA-60`). |
| **`CKPA-82`** *(Kiểm lại 100% `source_uri` & Ký `G1-AC01`)* | **Sprint 5** | **Không bị block trực tiếp.**<br>**Gián tiếp qua Story cha `CKPA-81` (`[P1]` Mỹ Vân):**<br>• `CKPA-43` — **Hoàng Tiến (`[S1]`)** *(đóng Sprint 2 G0 cuối W2 DUO)*<br>• *Nghiệp vụ thực tế:* chờ chốt Corpus cuối Sprint 4 & `[P4]` Trà My check `source_uri` 200 câu (`CKPA-66`). | **`CKPA-83` — Hữu Tài (`[P2]`)** *(Reviewer #1 xác nhận Ngày, Trường & Hold trước `[P1]` Mỹ Vân ký G1 25% tại `CKPA-84`)* | Đã có sẵn bản nháp & script `validate_corpus_g1.ps1`; giữ `CKPA-82` ký chốt cuối Sprint 5 đúng quy trình. |

### B. Lưu ý phần G0 trên dự án `CKPA` mới (dữ liệu đã chốt từ `CKPAOLD-1..10`)
- 4 issue G0 của Kha (`CKPA-10`, `CKPA-15`, `CKPA-24`, `CKPA-25`) đang ở `To Do` trên dự án mới:
  - `CKPA-10` bị block bởi `CKPA-9` (Hữu Tài) → block `CKPA-11` (Anh Khoa).
  - `CKPA-15` bị block bởi `CKPA-14` (Quốc Hưng) → block `CKPA-24` (Chí Kha).
  - `CKPA-24` / `CKPA-25` bị block bởi `CKPA-7` (Quý Hải), `CKPA-11` (Anh Khoa), `CKPA-15` (Chí Kha) → `CKPA-25` block `CKPA-26` (Quốc Hưng).
- *Đề nghị báo `[S1]` Hoàng Tiến & `[P1]` Mỹ Vân:* Do G0 đã chốt và có đủ 32 file nộp ở `CKPAOLD-1..10`, cần thống nhất cách đóng/đồng bộ trạng thái Sprint 1–2 G0 trên board `CKPA` mới để không làm kẹt `CKPA-43` (đang block toàn bộ 3 Story Sprint 5: `CKPA-73`, `CKPA-77`, `CKPA-81`).

---

## 4. ⚠️ 7 Vấn đề Kỹ thuật, Codebase `develop` & Jira Cần Báo Team Xử Lý Ngay

1. **[Nghiêm trọng — Báo `[S2]` Quốc Hưng `CKPA-52`] Lỗi trùng Khóa chính `DocumentVersion.id = VER-001` đã xác nhận trên LIVE `develop`:**
   - Tại `develop/backend/src/modules/knowledge/models.py` (dòng `31`), bảng `document_versions` khai báo `id: Mapped[str] = mapped_column(String(64), primary_key=True)` ánh xạ trực tiếp từ cột `document_version_id`.
   - Trong khi đó, dữ liệu mẫu G0 (`CKPAOLD-3`) và 60 Dev Tasks (`CKPAOLD-10`) dùng chung `document_version_id = VER-001` cho cả `DOC-001`, `DOC-002`, `DOC-003` -> nạp thẳng vào PostgreSQL sẽ **trùng PK hoặc ghi đè `document_id`**.
   - *Cách `[P3]` đã giảm thiểu:* Toàn bộ bản mới G1 (`DOC001-VER-000`, `DOC001-VER-002`, `DOC004-VER-001`...) đều duy nhất toàn cục; giữ nguyên `VER-001` trên 3 bản G0 để không gãy 60 Dev Tasks. Đề nghị `[S2]` chuẩn hóa key DB thành `f"{document_id}:{document_version_id}"` hoặc composite unique trong `CKPA-52`.

2. **[Nghiêm trọng — Báo `[S2]` Quốc Hưng & `[S3]` Yến Nhi `CKPA-52`, `CKPA-63`] G0 CSV & `develop` mới có 5 chiều `scope`, thiếu chiều thứ 6 `DAT 04` (`transaction_scope`) & lệch tên `customer_group` vs `customer_category`:**
   - RFP Mục 3 (`DAT 04`) yêu cầu **6 chiều**: `company`, `branch`, `role`, `customer category`, `product`, `transaction scope`.
   - Template `develop/data/templates/*.csv` hiện chỉ có 5 chiều (`company`, `branch`, `role`, `customer_group`, `product`).
   - *Cách `[P3]` đã xử lý tương thích ngược:* Giữ nguyên `customer_group` để không vỡ code G0 và **bổ sung đầy đủ `transaction_scope:<giá_trị>`** trên 100% dòng CSV G1. Đề nghị `[S2]` & `[S3]` parse đủ 6 chiều và alias `customer_group` ↔ `customer_category`.

3. **[Quan trọng — Báo `[S2]` Quốc Hưng `CKPA-52`, `CKPA-59`] Bảng `critical_fields` trên LIVE `develop` thiếu `is_tombstoned` & CSV 21/23 cột chưa có `source_uri`/`checksum`:**
   - Xác nhận tại `develop/backend/src/modules/policy/models.py` (dòng `61–88`): ORM `CriticalField` **không có** `is_tombstoned` (và không có `effective_from/to/owner/approver`, chỉ nằm ở `PolicyVersion`), trong khi CSV có `record_action = tombstone` (`DAT 02`).
   - Ngoài ra `G1-AC01` đòi `source_uri` & `checksum` SHA-256 nhưng `PASSAGES_CSV_COLUMNS` (21 cột) chỉ có `source_ref`. `[P3]` đã giữ nguyên đúng 21/23 cột khớp `IngestionService` và xuất kèm **`Source_URI_And_Checksum_Manifest_*.csv`**.

4. **[Đã xác nhận trên LIVE `develop` — Báo `[S2]` Quốc Hưng & `[S3]` Yến Nhi đồng bộ số đối soát] Cơ chế `has_essential_attachments = false` (`DAT 08`):**
   - Tại `develop/backend/src/modules/ingestion/service.py` (dòng `176–182`), `IngestionService._validate_row()` hiện đẩy mọi dòng `has_essential_attachments != "true"` vào **Quarantine (`MISSING_ESSENTIAL_ATTACHMENTS`)**.
   - Do đó số liệu đối soát `Expected = Accepted + Quarantined` (`CKPA-49` AC) khớp chính xác:
     - Họ 1 (`CKPA-50`): `Passages: 40 = 39 Accepted + 1 Quarantined (PAS-040)` | `CriticalFields: 16 = 16 + 0`.
     - Full 3 Họ (`CKPA-58`): `Passages: 96 = 93 Accepted + 3 Quarantined (PAS-040, PAS-066, PAS-082)` | `CriticalFields: 40 = 40 + 0`.

5. **[Nghiêm trọng về SoD & Phạm vi RFP — Báo `[S1]` Hoàng Tiến & `[S4]` Quý Hải] Tồn dư tài liệu/code "ngân hàng" & ghi nhầm vai trò S4 trên nhánh `develop`:**
   - Trên nhánh `develop` hiện có `docs/OPEN_QUESTIONS.md`, `docs/STATUS.md` và thư mục `app/` (Streamlit) vẫn ghi **"ngân hàng"** (`eKYC`, `CASA`, `Term Deposit`, `Overdraft`, `Collateral`) và ghi vai trò **"S4 – Application + LLM Engineer"** — trái ngược trực tiếp với RFP SongNhat CRM và nguyên tắc tách vai **SoD** (`[S4]` Quý Hải là *Quality Lead độc lập*, không code/tinh chỉnh cùng `S2/S3`). Cần `[S1]` dọn sạch hoặc tách khỏi phạm vi bàn giao G1 (`v0.2.0-g1-offline`) để tránh lỗi SoD/scope khi nghiệm thu!

6. **[Nhỏ — Báo `[S3]` Yến Nhi & `[P2]` Hữu Tài] Lệch nhãn `KNW 07` trên `develop/backend/src/shared/enums.py` & `PAS-030`:**
   - `FeedbackReason` (`enums.py:51–58`) và `PAS-030` (bảo toàn từ G0) dùng `outdated_rule` / `missing_exception` / `rejected`, trong khi nguyên văn RFP Trang 7 (`KNW 07`) là `obsolete rule` / `omitted exception` / `rejection`. Cần thống nhất mapping trước G2.

7. **[Lỗi cấu hình Board & Quy ước Branch — Báo `[S1]` Hoàng Tiến (SM)]:**
   - **Trạng thái Sprint trên Board 2 (`CKPA board`):** Hiện mới có `Sprint 1 - G0 Disc W1` là **`active`**, trong khi **`Sprint 3 - G1 Impl W1` vẫn để `future`** — dù thực tế Anh Khoa (`CKPA-47`) và Trà My (`CKPA-55`) đã chuyển task Sprint 3 sang `In Progress`. Nhờ SM kiểm tra việc Start Sprint 3 (vì chạy lịch DUO song song W1) hoặc đóng Sprint 1–2 G0.
   - **Lệch quy ước tên Branch giữa Onboarding Guide §15 vs Jira Description:** Onboarding Guide §15 yêu cầu `data/CKPA-50-...` (`<prefix>/<JIRA-ID>-<slug>`), còn Jira Description import từ Excel ghi `data/CRM-G1-SUB04-...`. Cần SM chốt 1 quy ước duy nhất cho toàn team trước khi mở hàng loạt PR G1.
   - **Còn 2 task mặc định rác trên `CKPA`:** `CKPA-1` (*Connect Github Copilot to Jira*) và `CKPA-2` (*Try: Delegate this work item to a coding agent*) chưa dọn.
