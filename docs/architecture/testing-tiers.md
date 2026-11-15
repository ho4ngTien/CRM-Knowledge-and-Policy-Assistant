# Tầng Kiểm thử & Hàng rào Nghiệm thu Độc lập — SongNhat CKPA

> Khung kiểm thử 4 tầng và nguyên tắc độc lập theo Mục 8, Mục 9, Mục 11, Phụ lục D & Phụ lục G của RFP và [SRS](../specs/srs.md) (Mục 8).

---

## 1. Sơ đồ Tầng Kiểm thử & Chinese Wall

```mermaid
flowchart TD
    subgraph sg_t1 ["Tầng 1: Unit & Contract Tests - Squad B & C chạy mỗi PR"]
        T1_1["CSV Validator, Quarantine, Idempotent Retry & Late-Batch"]
        T1_2["RBAC Least Privilege, Audience Check & PII Input Minimization"]
        T1_3["Applicability Giờ VN, Typed Critical Fields & Fail-Closed Guards"]
    end

    CI_GATE{"CI Gate - Pass Ruff Lint & Pytest"}

    subgraph sg_t2 ["Tầng 2: Offline Functional & Challenge Suites - Gate G1"]
        T2_DEV["60 Development Tasks - Công khai cho Dev/AI tune"]
        T2_VAL["40 Validation Tasks - Tinh chỉnh ngưỡng & prompt"]
        T2_CHL["80 Constructed Challenges (Gồm 40 ca VN 02: 10 ngôn ngữ, 10 ngày/phạm vi, 10 ngưỡng/ngoại lệ, 10 quyền/thu hồi)"]
    end

    G1_GATE{"Gate G1 - Controlled Offline"}

    subgraph sg_wall ["Hàng rào Độc lập Chinese Wall - Mục 8 & Mục 11 RFP"]
        CW["CẤM Squad B & C xem 100 Sealed hoặc tự chấm điểm nghiệm thu - D1 & Reviewer Độc lập nắm giữ"]
    end

    subgraph sg_t3 ["Tầng 3: Operations, Security & Resilience Tests - Mở cổng G2 & G4"]
        T3_OPS["OPS 01-06: 500 rows < 30p, 5 concurrent users p95 <= 25s, Cache purge <= 5p, 99.5% Availability"]
        T3_REC["OPS 07: Backup 35 ngày & Restore RTO 4h / RPO 24h (Replay Deletion & Withdrawal)"]
        T3_EXT["OPS 08 (G4): Đốt hết token/call cap không cắt cụt im lặng + Export dữ liệu định dạng mở"]
    end

    subgraph sg_t4 ["Tầng 4: Independent Sealed Acceptance & Pilot Thực tế - Cổng G2 -> G3 -> G4"]
        T4_SEAL["100 Sealed Tasks (D1 chấm): Critical=0, Applicability>=95%, Grounding>=95%, Completeness>=90%, Recall@5>=90%, Usefulness>=80%, Unanswerable<=5%"]
        T4_PILOT["Supervised Pilot >= 20 ngày làm việc (5 non-dev users): Raw vs Staff-Used & Effort giảm >= 20%"]
        T4_SIGN["Quyết định tách biệt tại G3 (Nghiệm thu Pilot vs Đầu tư Mở rộng <=24m Payback) -> Bàn giao G4"]
    end

    T1_1 --> CI_GATE
    T1_2 --> CI_GATE
    T1_3 --> CI_GATE
    CI_GATE --> T2_DEV
    CI_GATE --> T2_VAL
    CI_GATE --> T2_CHL

    T2_DEV --> G1_GATE
    T2_VAL --> G1_GATE
    T2_CHL --> G1_GATE
    G1_GATE -->|"Đạt 100% offline"| CW

    CW --> T3_OPS
    CW --> T3_REC
    CW --> T4_SEAL

    T3_OPS --> T4_PILOT
    T3_REC --> T4_PILOT
    T4_SEAL -->|"Gate G2: 0 Critical Defects"| T4_PILOT
    T4_PILOT --> T4_SIGN
    T3_EXT --> T4_SIGN
```

---

## 2. Ngưỡng Chấp nhận Nghiệm thu Độc lập (`G2` → `G3`)

| Tiêu chí | Ngưỡng bắt buộc (RFP Mục 8) | Ghi chú đo lường & Mẫu số |
|---|---|---|
| **Kiểm soát trọng yếu (`Critical Controls`)** | **`0` lỗi** | Không tiết lộ trái quyền, không bịa/sai `critical_fields`, không duyệt giả, không dùng nguồn tương lai/`withdrawn`. **Bất kỳ lỗi trọng yếu nào chặn phát hành.** |
| **Đúng phiên bản, ngày & phạm vi (`Applicability`)** | **`>= 95%`** | Tính trên tác vụ `100 Sealed` có thể trả lời; kết luận trọng yếu không căn cứ vẫn là lỗi chặn phát hành. |
| **Căn cứ & đầy đủ (`Grounding` & `Completeness`)** | **`>= 95%` căn cứ; `>= 90%` đầy đủ; `0` citation bịa** | Báo tách số nhận định, số tác vụ, lỗi trọng yếu, kết quả thô và kết quả nhân viên đã sử dụng. |
| **Truy xuất (`Recall@5`)** | **`>= 90%`** | Trên tập niêm phong có bằng chứng áp dụng đã duyệt; báo riêng số ca trả lời được, không trả lời được và thiếu nguồn. |
| **Hữu ích / chuyển tuyến (`Usefulness` & `Unanswerable`)** | **`>= 80%` hữu ích; `<= 5%` thiếu căn cứ khi không trả lời được** | `Hold` vẫn nằm trong mẫu số tổng; ca không thể trả lời vẫn áp dụng `0` dung sai lỗi trọng yếu. |
| **Quan sát Pilot có giám sát (`G3`)** | **`>= 20` ngày làm việc; `>= 5` non-dev users; Effort giảm `>= 20%`** | So sánh với cùng corpus đã làm sạch có thể tìm kiếm; tính đủ chuẩn bị, kiểm tra, lần thử thất bại, sửa và fallback; G3 yêu cầu business case riêng (TCO 3 năm + payback `<= 24` tháng). |

---

## 3. Phân bổ 80 Thử thách (Constructed Challenges — Báo cáo riêng)

- **40 ca chung toàn hệ thống:** Chính sách tương lai/lỗi thời, ranh giới ngưỡng (`<, <=, =, >=, >`), thiếu chú thích/bảng, xung đột hợp đồng, sai vai trò, ghi chú CRM cũ ghi đè, prompt injection và thu hồi giữa lúc generation (*Worked Case 9*).
- **40 ca định hướng Việt Nam (`VN 02`):**
  - `10` ca ngôn ngữ (Unicode, thiếu dấu, từ đồng nghĩa, viết tắt CRM, thuật ngữ sản phẩm trộn tiếng Anh, phủ định).
  - `10` ca ngày tháng & phạm vi (múi giờ `Asia/Ho_Chi_Minh`, giao dịch quá khứ, sửa hồi tố, chi nhánh/nhóm khách hàng).
  - `10` ca ngưỡng & ngoại lệ (biên số tiền/chiết khấu, đơn vị/tiền tệ, thiếu chú thích, tuyến ngoại lệ).
  - `10` ca quyền & thu hồi (direct link, citation/snippet, cache 5 phút, lỗi dịch vụ thẩm quyền fail-closed).
