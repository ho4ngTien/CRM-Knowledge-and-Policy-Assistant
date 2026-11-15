# Hướng dẫn Import Jira CSV theo 5 Gate — SongNhat CKPA

> Tệp chuẩn import Jira: [05-jira-5gates-import.csv](./05-jira-5gates-import.csv)  
> Căn cứ nội dung: [SRS](../specs/srs.md) và [Roadmap 5 Gate](../specs/roadmap.md).

---

## 1. Cấu trúc tệp CSV chuẩn Jira

Tệp `05-jira-5gates-import.csv` sử dụng mã hóa **UTF-8** và các trường chuẩn của **Atlassian Jira CSV Importer** (áp dụng được cho cả Jira Cloud Team-managed, Company-managed và Jira Server/Data Center):

| Cột CSV | Vai trò khi Import vào Jira | Ghi chú |
|---|---|---|
| `Issue ID` | Định danh tạm thời (`1..62`) để ánh xạ quan hệ cha-con | Map tới **Issue ID** trong bước Field Mapping |
| `Issue Type` | `Epic` (`5` cổng `G0–G4`), `Story` (`10` mốc chính), `Task` (`47` đầu việc cụ thể) | Map tới **Issue Type** (Story & Task đều là cấp 0, cha là Epic) |
| `Parent` | ID của Gate Epic (`1`, `14`, `31`, `46`, `54`) | Map tới **Parent** (Jira Cloud) hoặc **Epic Link** |
| `Summary` | **Ngắn gọn bằng tiếng Anh không dấu (`4–7` từ)** | Dùng tạo trực tiếp nhánh Git: `<type>/<ISSUE-KEY>-<slug>` |
| `Description` | Chi tiết công việc theo `SRS`, `RFP IDs`, `Phụ trách (A1–D2)`, `Phạm vi`, `Phụ thuộc`, `Branch gợi ý`, `Acceptance Criteria` | Map tới **Description** (chứa đủ AC nên không cần custom field riêng) |
| `Priority` | `Highest` / `High` | Map tới **Priority** |
| `Labels` | Nhãn cách nhau bởi khoảng trắng (`G0 WP01 SRS-FR-01 Role-A1`) | Map tới **Labels** (tự động tách nhiều nhãn) |
| `Components` | Nhóm kỹ thuật (`governance-docs`, `data-curation`, `backend-ingestion`, `backend-policy`, `backend-retrieval`, `backend-answer`, `frontend-workspace`, `security-infra`, `qa-eval`, `ops-handover`) | Map tới **Components** |
| `Sprint` | Tên Gate Sprint (`Gate-G0-Discovery` .. `Gate-G4-Handover`) | Map tới **Sprint** |
| `Start date` / `Due date` | Định dạng ISO `YYYY-MM-DD` theo lịch `12` tuần RFP (`2026-11-06` → `2027-01-29`) | Map tới **Start date** / **Due date** (bỏ qua nếu project không bật) |
| `Original Estimate` | Ước lượng giờ công (`6h`..`40h`) | Map tới **Original Estimate** |
| `Assignee` | Để trống tránh lỗi không khớp email/accountId khi import | Gán thành viên theo `Role-A1..D2` ngay sau khi import hoặc điền email trước khi import |
| `Outward issue link (Relates)` | Liên kết `Task ↔ Story` (chỉ chứa `1` Story ID duy nhất để tránh lỗi multi-ID khi import) | Map tới **`Link "Relates"`** trong bước Field Mapping của Jira CSV Importer |
| `Outward issue link (Blocks)` | Quan hệ chặn tuần tự chính (`1` Issue ID đầu tiên bị hạng mục hiện tại chặn) | Map tới **`Link "Blocks"`** trong bước Field Mapping của Jira CSV Importer |
| `Blocked By (Issue IDs)` | Danh sách đầy đủ các `Issue ID` tiền điều kiện phải hoàn thành trước | Cột tham chiếu/kiểm tra `is blocked by` (hoặc map bổ sung nếu dùng script/API sau import) |
| `Blocks (Issue IDs)` | Danh sách đầy đủ các `Issue ID` phía sau bị chặn bởi hạng mục hiện tại | Cột tham chiếu/kiểm tra `blocks` (nghịch đảo chính xác của `Blocked By (Issue IDs)`) |

---

## 2. Quy ước tạo Branch Git từ `Summary` trên Jira

Sau khi import vào Jira và Jira cấp key (ví dụ `CKPA-19`), lập trình viên lấy `Summary` chuyển thành chữ thường nối bằng dấu gạch ngang:

```text
Jira Key : CKPA-19
Summary  : Build 2 CSV validators and quarantine
Branch   : feat/CKPA-19-build-2-csv-validators-and-quarantine
```

Quy tắc tiền tố (`<type>` theo [git-playbook.md](../playbooks/git-playbook.md)):
- `docs/`: tài liệu đặc tả, pháp lý, hướng dẫn, biên bản Gate.
- `feat/`: phát triển tính năng backend, worker, frontend, schema.
- `test/`: kiểm thử đánh giá độc lập, bộ challenges, OPS benchmarks.
- `fix/`: sửa lỗi sau đánh giá G2 hoặc lỗi phát hiện.
- `chore/`: cấu hình Docker/CI, curation dữ liệu, điều phối vận hành pilot.

---

## 3. Bảng quy đổi `Role-*` sang 10 Thành viên trước khi gán `Assignee`

| Mã vai trong Label/Description | Squad | Vị trí phụ trách |
|---|---|---|
| `Role-A1` | Squad A | PM / BA Lead |
| `Role-A2` | Squad A | Policy & Knowledge Steward |
| `Role-B1` | Squad B | Data & Ingestion Engineer |
| `Role-B2` | Squad B | Policy & Lifecycle Engineer |
| `Role-B3` | Squad B | Retrieval & Index Engineer |
| `Role-C1` | Squad C | Answer & Validation LLM Engineer |
| `Role-C2` | Squad C | Frontend Workspace Engineer |
| `Role-C3` | Squad C | Identity, Security & DevOps Engineer |
| `Role-D1` | Squad D | Independent QA & Evaluation Lead *(Giữ `100 Sealed`)* |
| `Role-D2` | Squad D | Commercial, TestOps & Handover Engineer |

> Kế hoạch Jira hợp lệ duy nhất của dự án theo RFP là [05-jira-5gates-import.csv](./05-jira-5gates-import.csv).
