# Luồng Nghiệp vụ Chính — SongNhat CKPA

> Đặc tả 2 luồng vận hành cốt lõi theo RFP (Mục 6, Phụ lục A, Phụ lục B) và [SRS](../specs/srs.md) (Mục 5).

---

## 1. Luồng Hỏi – Đáp Có Kiểm soát, Hold & Chuyển Chủ Sở Hữu

```mermaid
sequenceDiagram
    autonumber
    actor Staff as Nhân viên SongNhat
    participant UI as Next.js Split-Screen (/chat)
    participant Auth as identity & PII Guard
    participant Ans as answer Orchestrator
    participant Policy as policy (Applicability & Critical Fields)
    participant Ret as retrieval (pgvector + FTS unaccent)
    participant LLM as LLM Provider (Max 2 calls)
    participant Val as validation & Final Check
    participant Gov as referral / feedback / audit

    Staff->>UI: Nhập câu hỏi CRM, ngày giao dịch (nếu có) & phạm vi
    UI->>Auth: POST /api/v1/answer (JWT Token + Payload)
    Auth->>Auth: Kiểm tra RBAC tối thiểu, Quota & cảnh báo PII đầu vào (SEC 01, SEC 02)
    Auth->>Ans: Chuyển câu hỏi hợp lệ kèm Role, Scope, Ngày áp dụng (Asia/Ho_Chi_Minh)

    Ans->>Policy: Kiểm tra trạng thái thẩm quyền & lọc nguồn áp dụng
    alt Trạng thái thẩm quyền DB không khả dụng (Fail-Closed)
        Policy-->>Ans: AuthorityUnavailable
        Ans-->>UI: Dừng trả lời an toàn & hướng dẫn tra cứu thủ công / chuyển chủ sở hữu
    else Trạng thái khả dụng
        Policy-->>Ans: Danh sách Document/Version hợp lệ + Typed Critical Fields từ DB
        Ans->>Ret: Truy xuất <= 8 đoạn hợp lệ (Việt có/không dấu + viết tắt CRM)
        Ret-->>Ans: Passage + Metadata (doc_id, version_id, passage_id, page, clause_ref)
        Ans->>Policy: Đối chiếu xung đột hợp đồng & tính đầy đủ phụ lục/chú thích (DAT 05, DAT 08)

        alt Thiếu nguồn, xung đột hợp đồng hoặc thiếu phụ lục/chú thích
            Ans->>Gov: HOLD kết luận bị ảnh hưởng & gợi ý Local Referral (KNW 05)
            Gov->>Gov: Ghi Audit & Cost Log (tính cả hold vào mức sử dụng)
            Ans-->>UI: Trả AnswerPackage trạng thái HOLD, lý do cụ thể & chủ sở hữu cần chuyển
        else Đủ căn cứ đã lọc quyền và hiệu lực
            Ans->>LLM: Gửi <= 8 đoạn (<= 6000 in / <= 900 out tokens, tối đa 2 calls)
            LLM-->>Ans: Bản nháp diễn giải 100-250 từ tiếng Việt (KHÔNG stream ra UI)
            Ans->>Val: Kiểm tra Citation, Critical Fields & ranh giới ANS 07/08
            Val->>Policy: Re-check quyền user & authoritative state nguồn lần cuối (KNW 04)

            alt Nguồn vừa bị rút (withdrawn) hoặc thu hồi quyền
                Val-->>Ans: Block & Mark Stale (KNW 04, Worked Case 9)
                Ans->>Gov: Ghi Audit Log sự kiện bị chặn
                Ans-->>UI: Báo nguồn vừa thu hồi - yêu cầu truy vấn mới
            else Validation & Final Check PASS
                Val-->>Ans: Approved 7-Part AnswerPackage
                Ans->>Gov: Ghi Audit Log, Token & Full Cost Meter (OPS 08)
                Ans-->>UI: Hiển thị AnswerPackage 7 phần + Highlight nguồn bên phải Split-Screen
            end
        end
    end

    Staff->>UI: Tạo phiếu Referral nội bộ hoặc gửi Feedback (5 lý do KNW 07)
    UI->>Gov: Lưu Referral (3 trạng thái) hoặc Feedback Candidate (không tự sửa rule)
```

### Quy tắc bất biến trên luồng hỏi – đáp
- **Không phụ thuộc prompt cho logic nghiệp vụ:** Quyền RBAC, trạng thái phát hành, ngày hiệu lực `Asia/Ho_Chi_Minh`, phạm vi (`scope`) và giá trị `critical_fields` xử lý hoàn toàn ở backend (`identity`, `policy`, `validation`).
- **Không stream trước khi kiểm tra cuối:** Chỉ hiển thị `AnswerPackage` sau khi đã đối soát citation và re-check authoritative state nguồn (`KNW 04`, RFP trang 4).
- **Hold rõ ràng thay vì đoán:** Xung đột hợp đồng/chính sách hoặc thiếu phụ lục/chú thích phải giữ kết luận và gợi ý chuyển chủ sở hữu (`referral`), không dùng bộ nhớ LLM hay web công khai (`ANS 06`).

---

## 2. Luồng Nhập liệu 2 CSV Hàng ngày & Rút Chính sách Tức thời

```mermaid
flowchart LR
    subgraph sg_batch ["Luồng Batch Ngày (1 lô/ngày/schema, <= 500 dòng thay đổi)"]
        SRC["Knowledge Steward xuất 2 UTF-8 CSV (passages <= 300, critical_fields <= 50)"]
        ING["Ingestion API & import_task.py"]
        VAL_CSV{"Kiểm tra Schema, UTF-8, <= 6000 ký tự, Footnote/Table, Idempotency"}
        QUAR["Quarantine Queue - Cách ly dòng lỗi kèm lý do"]
        MAN["Manifest Đối soát - Expected / Received / Accepted / Quarantined"]
        DB_UP["Cập nhật DB & Tombstone Deletion (không suy diễn xóa)"]
        IDX["index_task.py - Tạo Vector Embedding vào pgvector"]
        STALE["Beat Job check_staleness (1h/lần) - Cảnh báo Snapshot Age > 25h"]
    end

    subgraph sg_urgent ["Luồng Rút Chính sách Khẩn (Instant Withdrawal - Không chờ batch ngày)"]
        OWN["Policy Owner / Admin kích hoạt Withdraw"]
        AUTH_ST["1. Cập nhật Authoritative State = withdrawn trong DB"]
        W_TASK["2. worker withdraw_and_purge_cache chặn Retrieval & generation đang chạy"]
        CACHE_DEL["3. Xóa Redis Cache vật lý trong <= 5 phút (SEC 05 / OPS 05)"]
        UI_STALE["4. Chặn hiển thị ngay & gắn cờ Stale trên màn hình đang mở"]
    end

    SRC --> ING --> VAL_CSV
    VAL_CSV -->|"Dòng lỗi / Thiếu phụ lục / Lô cũ đến trễ"| QUAR --> MAN
    VAL_CSV -->|"Hợp lệ"| DB_UP --> IDX --> MAN
    DB_UP -.-> STALE

    OWN --> AUTH_ST --> W_TASK --> CACHE_DEL --> UI_STALE
```

### Quy tắc đối soát & độ mới dữ liệu
- **Idempotency & Late-batch:** Chạy lại cùng batch không gây trùng; batch cũ hơn không được ghi đè dữ liệu mới (`DAT 02`).
- **Tombstone:** Thiếu dòng không giải thích không được tự xem là lệnh xóa; xóa chính thức phải qua `record_action=tombstone` hoặc đối soát `full_snapshot` đã duyệt.
- **Snapshot Age:** Celery Beat chạy `check_staleness` mỗi `3600s`; ngưỡng mặc định là `IMPORT_SNAPSHOT_STALENESS_HOURS=25`.
