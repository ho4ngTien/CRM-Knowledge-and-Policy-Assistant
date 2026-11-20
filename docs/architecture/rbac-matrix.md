# KHÓA HỢP ĐỒNG API, MA TRẬN RBAC VÀ CẤU HÌNH LLM (GATE G0)
## CRM Knowledge and Policy Assistant — SongNhat CKPA
> **Mã công việc:** CKPA-7 (Gate G0)  
> **Tài liệu quy chuẩn:** SRS Mục 4.3, Mục 7.2, SRS-FR-02, SRS-FR-06.1 | RFP: ANS03, SEC01, DEL01  
> **Chủ trì kỹ thuật:** C1 (Phạm Lương Yến Nhi — LLM Eng)  
> **Phối hợp:** B2 (Hữu Tài — Policy Eng), B3 (Phạm Quý Hải — Retrieval Eng), C2 (Văn Mỹ Vân — FE/Gov UI), C3 (Nguyễn Ngọc Duy — SecOps Eng)  
> **Trạng thái:** KHÓA CỨNG (FROZEN) trước khi bước vào Phase G1

---

## 1. MỤC ĐÍCH VÀ PHẠM VI
Tài liệu này xác lập hợp đồng kỹ thuật bất biến (immutable contract) tại Gate G0 cho hệ thống SongNhat CKPA:
1. **Khóa cứng danh sách endpoint `/api/v1/*`** cho toàn bộ 12 module backend theo kiến trúc Modular Monolith.
2. **Khóa cứng cấu trúc JSON 7 phần** của `AnswerPackage` theo chuẩn kiểm chứng an toàn (ANS 01, ANS 03, SRS-FR-06.1).
3. **Chốt ma trận phân quyền RBAC tối thiểu cho 8 vai trò RFP/SRS** bảo đảm nguyên tắc đặc quyền tối thiểu (Least Privilege) và bức tường ngăn cách (Chinese Wall).
4. **Thống nhất cấu hình môi trường LLM** giữa backend (`backend/src/config.py`), S4 client (`app/config.py`) và biến môi trường mẫu (`.env.example`).
5. **Ký duyệt Gate G0** giữa Squad B và Squad C trước khi triển khai chi tiết Phase G1.

---

## 2. DANH SÁCH 12 MODULE VÀ TOÀN BỘ ENDPOINT CONTRACT `/api/v1/*`

Hệ thống backend triển khai trên FastAPI tại `backend/src/main.py`, mount đầy đủ 12 router tương ứng 12 module nghiệp vụ dưới tiền tố `/api/v1`:

| STT | Module | Prefix Router | Endpoint | Method | Vai trò được phép (RBAC) | Mô tả tóm tắt |
|:---:|:---|:---|:---|:---:|:---|:---|
| **1** | **Identity** | `/api/v1/identity` | `/token` | POST | Public (SSO) | Đổi token OIDC/SSO doanh nghiệp sang session bearer |
| | | | `/me` | GET | Mọi user đăng nhập | Lấy thông tin người dùng, roles và audience scopes |
| | | | `/check-permission` | POST | Mọi user đăng nhập | Kiểm tra quyền truy cập theo thẻ audience của chính sách |
| **2** | **Knowledge** | `/api/v1/knowledge` | `/passages/{passage_id}` | GET | Mọi user hợp lệ | Xem bằng chứng gốc theo URL (kiểm tra audience & trạng thái thu hồi) |
| | | | `/documents/{document_id}/lineage` | GET | Mọi user đăng nhập | Truy vết phả hệ phiên bản tài liệu chính sách |
| | | | `/snapshot-age` | GET | Mọi user đăng nhập | Báo cáo tuổi snapshot dữ liệu phục vụ hiển thị cảnh báo |
| **3** | **Ingestion** | `/api/v1/ingestion` | `/csv/validate` | POST | `steward`, `policy_owner`, `publisher`, `administrator` | Dry-run kiểm thử file CSV 21/23 cột, cách ly vào quarantine nếu lỗi |
| | | | `/quarantine` | GET | `steward`, `policy_owner`, `publisher`, `administrator` | Danh sách dòng dữ liệu bị cách ly chờ xử lý |
| **4** | **Policy** | `/api/v1/policy` | `/authority-matrix` | GET | Mọi user đăng nhập | Xem ma trận thẩm quyền 5 cấp (DAT 03) và chủ sở hữu chính sách |
| | | | `/versions/{policy_version_id}/critical-fields` | GET | Mọi user đăng nhập | Danh sách thông số ràng buộc có cấu trúc (Critical Fields) |
| | | | `/threshold-check` | POST | Mọi user đăng nhập | So khớp ngưỡng số học tất định ngoài LLM |
| **5** | **Retrieval** | `/api/v1/retrieval` | `/search` | POST | Mọi user đăng nhập | Tìm kiếm lai (hybrid) tiếng Việt giới hạn <= 8 đoạn trích dẫn |
| **6** | **Answer** | `/api/v1/answer` | `/` | POST | Mọi user đăng nhập | Hỏi đáp chính sách, trả về AnswerPackage 7 phần đã kiểm chứng |
| | | | `/follow-up` | POST | Mọi user đăng nhập | Đặt câu hỏi làm rõ kế thừa task_id |
| | | | `/regenerate` | POST | Mọi user đăng nhập | Sinh lại câu trả lời sau khi cập nhật nguồn / làm rõ |
| **7** | **Validation** | `/api/v1/validation` | `/verify` | POST | Mọi user đăng nhập | Kiểm tra trạng thái hiệu lực nguồn trích dẫn trước khi render UI |
| **8** | **Referral** | `/api/v1/referral` | `/` | POST | Mọi user đăng nhập | Tạo phiếu chuyển tiếp cán bộ (escalation ticket) |
| | | | `/` | GET | Mọi user đăng nhập | Liệt kê danh sách phiếu chuyển tiếp |
| | | | `/{referral_id}` | PATCH | `policy_owner`, `publisher`, `referral_handler`, `steward`, `administrator` | Cập nhật / đóng phiếu chuyển tiếp |
| **9** | **Feedback** | `/api/v1/feedback` | `/` | POST | Mọi user đăng nhập | Gửi phản hồi nhân viên theo 5 lý do chuẩn (KNW 07) |
| | | | `/candidates` | GET | `steward`, `policy_owner`, `publisher`, `administrator` | Danh sách phản hồi ứng viên chờ đưa vào luồng chính sách |
| **10** | **Audit** | `/api/v1/audit` | `/logs` | GET | `privacy_security_owner`, `legal_owner`, `administrator` | Đọc nhật ký kiểm toán hạn chế (bảo vệ quyền riêng tư & bảo mật) |
| | | | `/cost-meter` | GET | `administrator`, `policy_owner`, `publisher` | Báo cáo chi phí LLM, token, lượt gọi theo tháng (OPS 06) |
| | | | `/export-open` | GET | `administrator`, `policy_owner`, `publisher`, `steward` | Xuất dữ liệu mở không phụ thuộc công nghệ khóa (OPS 08) |
| **11** | **Evaluation**| `/api/v1/evaluation` | `/runs` | POST | `independent_evaluator`, `administrator` | Ghi nhận phiên đánh giá Chinese Wall theo ngưỡng Section 8 |
| | | | `/runs` | GET | Mọi user (theo partition cho phép) | Xem kết quả đánh giá (chặn dev/reader tiếp cận sealed_100) |
| **12** | **Admin** | `/api/v1/admin` | `/policies/{policy_version_id}/transition` | POST | `steward`, `policy_owner`, `publisher`, `administrator` | Chuyển đổi trạng thái vòng đời chính sách (7 trạng thái) |
| | | | `/policies/{policy_version_id}/withdraw` | POST | `policy_owner`, `publisher`, `administrator` | Thu hồi tức thời chính sách, xóa cache trong <= 5 phút |
| | | | `/emergency-disable` | POST | `administrator` | Kích hoạt chế độ khẩn cấp (chuyển sang tra cứu thủ công) |
| | | | `/ops-summary` | GET | `steward`, `policy_owner`, `publisher`, `administrator` | Giám sát giới hạn Base Scope runtime và cờ hệ thống |
| **Global** | **Health** | `/health` | `/health` | GET | Public | Kiểm tra liveness và cờ quản trị hệ thống |

---

## 3. CẤU TRÚC JSON 7 PHẦN CỦA ANSWERPACKAGE

Mọi câu trả lời trả về cho người dùng CRM bắt buộc phải tuân theo schema Pydantic v2 `AnswerPackage` định nghĩa tại `backend/src/modules/answer/schemas.py`. Tuyệt đối không cho phép stream trực tiếp văn bản chưa qua kiểm chứng.

```json
{
  "answer_id": "ans-20261117-uuid",
  "task_id": "task-crm-12345",
  "status": "answered",

  "original_question": "Chính sách bảo hành đổi mới sản phẩm X trong bao nhiêu ngày?",

  "governing_date": "2026-11-17",
  "timezone": "Asia/Ho_Chi_Minh",
  "scope": "company:SN;branch:all;role:all;customer_group:all;product:all",
  "is_historical": false,
  "is_future_preview": false,

  "guidance_text": "Theo quy định hiện hành, sản phẩm X được áp dụng chính sách đổi mới trong vòng 30 ngày kể từ ngày xuất hóa đơn bán lẻ nếu phát sinh lỗi phần cứng do nhà sản xuất.",
  "verbatim_quotes": [
    "Sản phẩm nhóm X được quyền áp dụng 01 lần đổi mới sản phẩm tương đương trong thời hạn 30 ngày dương lịch tính từ ngày xuất hóa đơn nếu phát sinh lỗi kỹ thuật phần cứng."
  ],

  "citations": [
    {
      "document_id": "DOC-WAR-001",
      "document_version_id": "DOC-WAR-001-V2",
      "passage_id": "PSG-WAR-042",
      "title": "Quy chế bảo hành và đổi trả thiết bị 2026",
      "page_number": 12,
      "clause_ref": "Điều 5.1.a",
      "quoted_text": "Sản phẩm nhóm X được quyền áp dụng 01 lần đổi mới sản phẩm tương đương trong thời hạn 30 ngày dương lịch...",
      "evidence_url": "/api/v1/knowledge/passages/PSG-WAR-042"
    }
  ],

  "critical_fields": [
    {
      "field_id": "CF-WAR-001",
      "policy_id": "POL-WAR",
      "policy_version_id": "POL-WAR-V2",
      "document_version_id": "DOC-WAR-001-V2",
      "field_name": "thoi_han_doi_moi_ngay",
      "field_type": "duration",
      "operator": "<=",
      "value": "30",
      "unit": "ngày",
      "currency": null,
      "approval_role": "service_steward",
      "time_limit": "24h",
      "exception_condition": "Không áp dụng đối với sản phẩm có dấu hiệu vào nước hoặc va đập ngoại lực",
      "required_documents": ["hoa_don_vat", "bien_ban_kiem_dinh_kt"],
      "source_clause": "Điều 5.1.a",
      "status": "effective"
    }
  ],

  "missing_facts": [],
  "hold_reason": null,
  "uncertainty_note": null,

  "referral_target": "truong_phong_chinh_sach_dich_vu",
  "internal_use_warning": "Tài liệu lưu hành nội bộ SongNhat. Không cung cấp nguyên văn trích dẫn cho khách hàng.",

  "pii_warning": null,
  "snapshot_age_hours": 1.25,
  "llm_calls_used": 1
}
```

### Chi tiết 7 Phần Bắt Buộc:
1. **Phần 1 — Câu hỏi gốc (`original_question`):** Chuỗi câu hỏi do cán bộ CRM nhập vào, đã được chuẩn hóa và loại bỏ PII/Prompt Injection.
2. **Phần 2 — Ngày hiệu lực & Cờ phạm vi (`governing_date`, `timezone`, `scope`, `is_historical`, `is_future_preview`):** Khóa cứng múi giờ `Asia/Ho_Chi_Minh` và ngày áp dụng tất định.
3. **Phần 3 — Hướng dẫn súc tích & Trích dẫn nguyên văn riêng biệt (`guidance_text`, `verbatim_quotes`):** Văn phong tiếng Việt súc tích (100–250 từ) tách rời hoàn toàn với đoạn trích nguyên văn từ chính sách.
4. **Phần 4 — Bằng chứng trích dẫn có thể nhấp (`citations`):** Danh sách `AnswerCitation` neo trực tiếp vào đoạn văn (`passage_id`), điều khoản (`clause_ref`), số trang và URL xem bằng chứng.
5. **Phần 5 — Thông số chính sách cấu trúc định kiểu (`critical_fields`):** Các tham số `CriticalFieldItem` số học, tiền tệ, thời hạn, điều kiện ngoại lệ được đánh giá ngoài LLM.
6. **Phần 6 — Dữ kiện thiếu, Lý do tạm giữ & Hướng dẫn làm rõ (`missing_facts`, `hold_reason`, `uncertainty_note`):** Nếu thiếu dữ kiện hoặc có mâu thuẫn thẩm quyền, kích hoạt cơ chế Fail-Closed (Hold/Clarification).
7. **Phần 7 — Đầu mối chuyển tiếp & Cảnh báo nội bộ (`referral_target`, `internal_use_warning`):** Đầu mối tiếp nhận khi vượt thẩm quyền và cảnh báo bắt buộc bảo mật thông tin nội bộ.

---

## 4. MA TRẬN RBAC TỐI THIỂU CHO 8 VAI TRÒ RFP/SRS

Hệ thống định nghĩa chính xác 8 vai trò RFP tại `backend/src/shared/enums.py` (`UserRole`):
- `reader`: Nhân viên vận hành CRM, đọc thông tin và gửi câu hỏi / phản hồi.
- `policy_owner`: Chủ sở hữu chính sách, phê duyệt và thu hồi chính sách.
- `publisher`: Người phát hành chính sách (phối hợp / ủy quyền cùng `policy_owner`).
- `steward`: Cán bộ quản trị tri thức, thẩm định dữ liệu nhập liệu CSV và phân loại ứng viên phản hồi.
- `administrator`: Quản trị viên hệ thống, cấu hình và xử lý sự cố vận hành.
- `independent_evaluator`: Đơn vị đánh giá độc lập, thực thi kiểm thử mô hình qua Chinese Wall.
- `privacy_security_owner`: Cán bộ phụ trách an toàn thông tin & quyền riêng tư, rà soát nhật ký kiểm toán.
- `legal_owner`: Cán bộ pháp chế, rà soát tính tuân thủ pháp lý và dữ liệu kiểm toán.
*(Ghi chú: `referral_handler` được duy trì như một vai trò phụ trợ giải quyết phiếu chuyển tiếp nghiệp vụ).*

### Bảng Ma Trận Phân Quyền Endpoint:

| Nhóm Endpoint | `reader` | `policy_owner` | `publisher` | `steward` | `administrator` | `independent_evaluator` | `privacy_security_owner` | `legal_owner` |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `/api/v1/identity/me` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/api/v1/identity/check-permission` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/api/v1/knowledge/*` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/api/v1/policy/authority-matrix` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/api/v1/policy/critical-fields` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/api/v1/policy/threshold-check` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `/api/v1/retrieval/search` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `/api/v1/answer/*` | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/validation/verify` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `/api/v1/referral` (tạo/đọc) | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/referral/{id}` (cập nhật) | — | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/feedback` (gửi phản hồi) | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/feedback/candidates` (duyệt) | — | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/ingestion/*` (CSV / Quarantine) | — | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/admin/policies/transition` | — | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/admin/policies/withdraw` | — | ✓ | ✓ | — | ✓ | — | — | — |
| `/api/v1/admin/emergency-disable` | — | — | — | — | ✓ | — | — | — |
| `/api/v1/admin/ops-summary` | — | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/audit/logs` (nhật ký hạn chế) | — | — | — | — | ✓ | — | ✓ | ✓ |
| `/api/v1/audit/cost-meter` | — | ✓ | ✓ | — | ✓ | — | — | — |
| `/api/v1/audit/export-open` | — | ✓ | ✓ | ✓ | ✓ | — | — | — |
| `/api/v1/evaluation/runs` (POST) | — | — | — | — | ✓ | ✓ | — | — |
| `/api/v1/evaluation/runs` (GET dev/val) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — |
| `/api/v1/evaluation/runs` (GET sealed_100) | — | — | — | — | ✓ | ✓ | — | — |

---

## 5. THỐNG NHẤT CẤU HÌNH MÔI TRƯỜNG LLM

Các tham số giới hạn mô hình LLM được chốt đồng bộ giữa backend (`backend/src/config.py`), S4 application (`app/config.py`) và template môi trường (`.env.example`):

| Tham số cấu hình | Giá trị khóa cứng | Backend (`backend/src/config.py`) | Ứng dụng S4 (`app/config.py`) | Ghi chú quy chuẩn RFP / SRS |
|:---|:---:|:---:|:---:|:---|
| **Max Input Tokens** | `6000` | `LLM_MAX_INPUT_TOKENS = 6000` | `MAX_INPUT_TOKENS = 6000` | Giới hạn budget prompt tiếng Việt bảo thủ |
| **Max Output Tokens** | `900` | `LLM_MAX_OUTPUT_TOKENS = 900` | `MAX_OUTPUT_TOKENS = 900` | Tối đa 250 từ giải thích + trích dẫn |
| **Max Calls per Package** | `2` | `LLM_MAX_CALLS_PER_PACKAGE = 2` | `MAX_LLM_CALLS_PER_PACKAGE = 2` | Tối đa 1 call chính + 1 call regenerate |
| **Max Calls per Month** | `2000` | `LLM_MAX_CALLS_PER_MONTH = 2000` | `LLM_MAX_CALLS_PER_MONTH = 2000` | Hạn mức chi phí hàng tháng (OPS 06) |
| **Streaming Output** | `false` | `ENABLE_ANSWER_STREAMING = False` | `ENABLE_ANSWER_STREAMING = False` | Cấm stream trực tiếp; phải kiểm chứng xong mới hiển thị |
| **Option O1 (Selected CRM Context)** | `false` (Loại trừ) | Đã loại trừ khỏi codebase | Đã loại trừ khỏi codebase | Tùy chọn O1 (DAT 07) cắt hoàn toàn khỏi Base Scope theo SRS §1.4 & §2.3 |
| **Timezone mặc định** | `Asia/Ho_Chi_Minh` | `APP_TIMEZONE = "Asia/Ho_Chi_Minh"` | `Asia/Ho_Chi_Minh` | Múi giờ chuẩn xác định ngày hiệu lực |

---

## 6. KHUNG KÝ CHỐT VÀ NGHIỆM THU GATE G0 (SQUAD B & SQUAD C)

Trước khi chuyển sang cài đặt Phase G1, các thành viên đại diện Squad B và Squad C xác nhận sự đồng thuận về bản hợp đồng API, ma trận RBAC và cấu hình LLM này trên Pull Request của nhánh `docs/CKPA-7-freeze-api-contracts-and-rbac-matrix`:

| Đại diện | Vai trò dự án | Họ và tên | Trạng thái ký duyệt |
|:---|:---|:---|:---:|
| **Squad C (Chủ trì)** | C1 — Lead LLM / Answer & Validation Eng | **Phạm Lương Yến Nhi** | **ĐÃ DUYỆT (Signed)** |
| **Squad B** | B2 — Policy & Governance Eng | **Hữu Tài** | *Chờ xác nhận PR* |
| **Squad B** | B3 — Retrieval & Ingestion Eng | **Phạm Quý Hải** | *Chờ xác nhận PR* |
| **Squad C** | C2 — FE / Gov UI Eng | **Văn Mỹ Vân** | *Chờ xác nhận PR* |
| **Squad C** | C3 — SecOps & Security Eng | **Nguyễn Ngọc Duy** | *Chờ xác nhận PR* |

---
*Tài liệu được sinh và quản lý phiên bản theo quy trình GitFlow chuẩn của dự án SongNhat CKPA.*
