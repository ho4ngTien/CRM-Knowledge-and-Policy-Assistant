# BÁO CÁO KIỂM TOÁN LỘ LỌT RBAC, SOURCE URI, CACHE & FAIL-CLOSED (GATE G1)

- **Mã công việc Jira:** `CKPA-70` (Parent: `CKPA-44` | Liên quan: `CKPA-69` | Mở khóa: `CKPA-71`)
- **Mã truy vết RFP & Cổng G1:** `SEC 01`, `SEC 05`, `SEC 08`, `ANS 02` | Tiêu chí: `G1-AC03`, `G1-AC04`
- **Phân hệ kiểm thử:** `SUB01` (Test), `SUB07` (Pre-retrieval)
- **Chủ trì thực hiện:** `[P5]` Anh Khoa | **Phối hợp:** `[S5]` Ngọc Duy | **Nghiệm thu:** `[P1]` Mỹ Vân

---

## 1. Phạm vi & Mục tiêu kiểm toán
Đánh giá độc lập khả năng ngăn chặn rò rỉ thông tin phân quyền trước và trong quá trình truy xuất RAG của phân hệ **Purchaser**, tập trung vào 4 rủi ro trọng yếu:
1. Lộ lọt `source_uri`, trích dẫn (`citation`) hoặc tiêu đề tài liệu khi người dùng không đủ thẩm quyền (`SEC 01`, `ANS 02`).
2. Nhiễm chéo bộ nhớ đệm (`Cross-Role Cache Poisoning / Replay`) giữa các vai trò có cấp độ truy cập khác nhau (`SEC 01`).
3. Độ trễ thu hồi quyền truy cập đối với tài liệu đã bị rút/hủy hiệu lực (`Immediate Withdrawal Fail-Closed` — `SEC 05`).
4. Rò rỉ dữ liệu nhạy cảm hoặc tiêu đề tài liệu mật trong nhật ký hệ thống (`Audit Log Redaction` — `SEC 08`).

---

## 2. Ma trận kết quả kiểm thử chéo 4 vai trò

| Mã TC | Hạng mục kiểm thử | Vai trò giả lập | Tài nguyên mục tiêu | Kết quả thực tế | Tỷ lệ rò rỉ | Log SEC 08 | Trạng thái |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **TC-RBAC-01** | Selection & Source URI (`SEC 01`, `ANS 02`) | `Purchaser_Junior_Buyer` (Tier-3) | `PUR-POL-2026-CONFIDENTIAL-01` | Chặn `403 Forbidden`; không trả về `source_uri`, `citation` hay snippet | **0%** | Đầy đủ | **PASS** |
| **TC-RBAC-02** | Cross-Role Cache Isolation (`SEC 01`) | `External_Auditor_ReadOnly` (Tier-4) | `CACHED_QUERY_HASH_8F92A1` | Cache key gắn kèm `role_acl_hash`; từ chối tái sử dụng kết quả của Tier-1 | **0%** | Đầy đủ | **PASS** |
| **TC-REV-03** | Immediate Withdrawal Fail-Closed (`SEC 05`) | `Purchaser_Senior_Manager` (Tier-1) | `SUP-CONTRACT-REVOKED-09` | Ngắt truy xuất tức thì theo cơ chế **Fail-Closed** ngay khi đánh dấu thu hồi | **0%** | Đầy đủ | **PASS** |
| **TC-LOG-04** | Audit Log Redaction Check (`SEC 08`) | `Supplier_Support_Lead` (S1) | `DENIED_ACCESS_EVENT_TRACE` | Chỉ lưu `doc_id_hash` và mã từ chối; che 100% tiêu đề tài liệu và PII | **0%** | Đầy đủ | **PASS** |

---

## 3. Bằng chứng kỹ thuật & Truy vết tệp
- **Script kiểm toán tự động:** `security/scripts/g1_rbac_failclosed_audit_runner.py`
- **Nhật ký thực thi (Audit Log):** `security/g1/g1_rbac_failclosed_audit_CKPA-70.log`
- **Kiểm định tuân thủ CI:** Đã xác minh 0% PII và 0 tệp cấm qua `scripts/ci_purchaser_guard.py`.

---

## 4. Kết luận nghiệm thu (`G1-AC03` & `G1-AC04`)
- **Đạt 100% (4/4 Test Cases):** Toàn bộ truy vấn trái phép, truy vấn lệch vai trò qua cache và tài liệu bị thu hồi đều bị chặn **Fail-Closed** với **0%** rò rỉ `source_uri`/citation.
- **Đủ điều kiện đóng thẻ `CKPA-70`** và mở khóa (`unblock`) cho hạng mục kiểm thử tiếp theo **`CKPA-71`**.