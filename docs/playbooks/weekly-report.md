# Weekly Report — CRM Knowledge & Policy Assistant
**Người báo cáo:** Hoàng Tiến (PM / Project Leader)  
**Thời gian:** 2026-W46 (Tuần bắt đầu tiếp nhận vai trò Leader)  

---

## 1. Công việc đã thực hiện
- **Tiếp nhận chuyển giao vai trò Project Manager / Team Leader:** Khảo sát lại toàn bộ hiện trạng dự án, nhân sự, tài liệu RFP và các cam kết kỹ thuật.
- **Khởi tạo kiến trúc dự án tổng thể (Project Scaffold):** Thiết lập cấu trúc Modular Monolith + RAG + Policy Control Layer (FastAPI, Next.js, Celery, PostgreSQL + pgvector, Redis).
- **Chuẩn hóa bộ quy tắc làm việc và kỷ luật nhóm:**
  - Hoàn thiện `team-playbook.md`, `git-playbook.md`, `jira-playbook.md`.
  - Phê duyệt cơ chế "sẹo" kỷ luật: **1 sẹo = -2%, 5 sẹo = -20%** điểm đánh giá thành viên.
- **Rà soát và hỗ trợ kỹ thuật gói WP02 (Data Import Engine):** Đạt tiêu chí DAT 01 - DAT 08, OPS 01 (nạp 500 dòng < 30 phút).

## 2. Công việc đang thực hiện
- **Tái tổ chức công việc trên Jira:** Chuẩn hóa lại các Epic/Story/Task theo đúng cấu trúc **5 Release Gates (`G0–G4`)** của RFP và [SRS](../specs/srs.md); xuất bảng [05-jira-5gates-import.csv](../work-packages/05-jira-5gates-import.csv) phân công đều 10 thành viên (`Squad A–D`).
- **Xây dựng Roadmap dự án:** Thiết lập lộ trình **5 Release Gates (`G0 → G4`)** không gộp `G3` và `G4` (chi tiết tại [roadmap.md](../specs/roadmap.md)).
- **Chuẩn hóa Đặc tả & Kiến trúc (Scaffold):** Hoàn thiện [srs.md](../specs/srs.md), hợp đồng 2 CSV UTF-8 (`erd-and-csv-contract.md`) và đồng bộ `12` module backend.
- **Định hình thiết kế UI Split-Screen:** 1 bên là Chatbot Workspace tương tác (`/chat`), 1 bên là Policy & Evidence Viewer có tính năng Highlight điều khoản/đoạn trích dẫn căn cứ + hiển thị xác định `Critical Fields`.
- **Thiết lập cơ chế họp định kỳ (Bi-daily standup - 2 ngày/lần):** Thống nhất format 4 câu hỏi kiểm điểm tự giác; chốt buổi họp đầu tiên vào Thứ 3 (17/11/2026).

## 3. Kế hoạch tiếp theo
- Tổ chức buổi họp định kỳ đầu tiên (Thứ 3, 17/11/2026) theo format 4 câu hỏi: *What did you do? What are you doing? What will you do next? Do you need help? Any questions?*
- Khởi động triển khai Sprint 2 trên Jira.
- Chốt phương án AI Stack: Ưu tiên RAG dùng LLM API với ràng buộc nghiêm ngặt *"Huấn luyện/xử lý/index trước, trả lời sau"* (Evidence Retrieval & Verification trước khi sinh lời văn); xem xét Local AI nếu đủ điều kiện GPU.
- Triển khai giao diện Split-Screen và kết nối pgvector cho module retrieval.

## 4. Khó khăn và nhu cầu hỗ trợ
- Việc thay đổi Leader đột xuất cần thời gian tái cơ cấu lại Jira và cân bằng lại tiến độ các thành viên.
- Cần Sponsor / Policy Owner sớm xác nhận 3 họ quy trình CRM mẫu để hoàn tất Cổng G0.
- Khảo sát hạ tầng GPU để đánh giá tính khả thi nếu triển khai Local AI.

## 5. Ý kiến và đề xuất khác
- Áp dụng triệt để kỷ luật nhóm và format họp 2 ngày/lần để tăng tính tự giác của các thành viên.
- Thiết kế UI Split-screen là điểm khác biệt cốt lõi giúp nhân viên đối chiếu văn bản gốc minh bạch.

---

## Chỉ số dự án
| Metric | Giá trị |
|---|---|
| Vai trò Leader | Hoàng Tiến (PM / Tech Lead) |
| Chu kỳ họp | 2 ngày / lần (bắt đầu T3, 17/11) |
| Cơ chế kỷ luật | 1 sẹo (-2%), 5 sẹo (-20%) |
| Gate hiện tại | Chuẩn bị G0 (Ready to Build) |
| Roadmap | 5 Release Gates (G0–G4) theo RFP & SRS |

