# CRM KNOWLEDGE AND POLICY ASSISTANT (NHÓM 7 - AI-06)
## Phân hệ S4: Application + LLM Engineer (Gói công việc WP04)

Hệ thống trợ lý trí tuệ nhân tạo (AI Assistant) hỗ trợ nhân viên quan hệ khách hàng (CRM) ngân hàng tra cứu, đối chiếu và giải thích các quy định, chính sách nội bộ bằng tiếng Việt.

---

## 1. Nguyên tắc hoạt động cốt lõi

Hệ thống được thiết kế theo các nguyên tắc an toàn nghiêm ngặt dành cho ngành ngân hàng:
- **KHÔNG bịa đặt:** Tuyệt đối không sinh nội dung khi không có tài liệu bằng chứng xác thực đi kèm (ANS 06).
- **KHÔNG tự suy diễn phê duyệt:** AI không được thay mặt cấp có thẩm quyền phê duyệt ngoại lệ cho khách hàng, dù khách hàng có mức độ quan trọng cao hay có tiền lệ trước đó (ANS 05).
- **KHÔNG tư vấn pháp lý / hứa hẹn:** Không hướng dẫn kiện tụng, tranh chấp hoặc hứa hẹn bồi thường ngoài thẩm quyền (ANS 07).
- **Trích dẫn nguyên văn:** Mọi câu trả lời phải kèm trích dẫn nguyên văn từ tài liệu nguồn đã xác thực (CKPA-39, KNW 01).
- **Cấu trúc 7 trường cố định:** Phản hồi luôn tuân thủ đúng định dạng 7 trường chuẩn hóa (CKPA-40).
- **Thiếu căn cứ thì TẠM DỪNG (HOLD):** Kích hoạt trạng thái HOLD công khai với mã lỗi minh bạch và câu hỏi gợi ý làm rõ cố định (ANS 01, ANS 06, CKPA-47).
- **Phạm vi nội bộ:** Không cung cấp tính năng xuất/tải dữ liệu chính sách ra ngoài (KNW 02).

---

## 2. Yêu cầu hệ thống và Cài đặt

### Môi trường khuyến nghị
- **Hệ điều hành:** Windows 10 / 11
- **Trình thông dịch:** Python 3.10 trở lên (đã kiểm định tương thích với Python 3.14)
- **Công cụ dòng lệnh:** Windows PowerShell
- **Trình duyệt web:** Google Chrome hoặc Microsoft Edge

### Hướng dẫn cài đặt trên Windows
Mở **PowerShell**, di chuyển vào thư mục dự án và thực hiện các lệnh (bắt buộc dùng cú pháp `python -m`):

```powershell
# 1. Khởi tạo và kích hoạt môi trường ảo
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Cài đặt các thư viện phụ thuộc
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Khởi tạo cơ sở dữ liệu nội bộ SQLite
python -m app.services.database

# 4. Chạy toàn bộ kiểm định (154 tests)
python -m pytest -v

# 5. Khởi chạy ứng dụng Streamlit Workspace
python -m streamlit run app/main.py
```

---

## 3. Cấu trúc thư mục dự án

```text
crm-knowledge-and-policy-assistant/
├── CHANGELOG.md                 # Lịch sử phiên bản (1.0.0, 1.1.0, 1.2.0)
├── README.md                    # Tài liệu tổng quan dự án
├── pytest.ini                   # Cấu hình pytest (testpaths, file patterns)
├── requirements.txt             # Gói phụ thuộc Python
├── app/                         # Mã nguồn ứng dụng S4
│   ├── config.py                # Cấu hình tập trung (CONFIG_VERSION = 1.2.0)
│   ├── main.py                  # Entry point giao diện Streamlit Workspace
│   ├── models.py                # Định nghĩa dữ liệu 7 trường, Enum, Dataclass
│   ├── components/              # Thành phần UI (policy_display, feedback, referral)
│   └── services/                # Tầng nghiệp vụ xử lý lõi (pipeline, guards, parser)
├── data/                        # Thư mục chứa app.db (SQLite nội bộ)
├── docs/                        # Tài liệu chi tiết dự án
│   ├── HANDOVER.md              # Tài liệu bàn giao kỹ thuật liên phân hệ
│   ├── SYSTEM_BEHAVIOR.md       # Mô tả hành vi hệ thống cho người dùng nghiệp vụ
│   ├── TRACEABILITY.md          # Ma trận truy vết Yêu cầu -> Mã nguồn -> Tests
│   ├── REQUIREMENTS_S4.md       # Đặc tả yêu cầu chính thức gói WP04
│   ├── SAFETY.md                # Chính sách an toàn và guardrails
│   ├── STATUS.md                # Tiến độ chi tiết từng giai đoạn
│   ├── OPEN_QUESTIONS.md        # Các câu hỏi tồn đọng liên phân hệ
│   └── S3_QUESTIONS.md          # Yêu cầu kỹ thuật cho module Retrieval S3
├── prompts/                     # Thư viện System Prompt tiếng Việt (v1.0, v1.1)
└── tests/                       # Bộ kiểm thử 154 ca tự động
```

---

## 4. Hướng dẫn tích hợp liên phân hệ

### Tích hợp S3 Retrieval
Kế thừa lớp `app.services.evidence_provider.EvidenceProvider` và triển khai phương thức `retrieve_evidence(question: str) -> List[Citation]`. Xem chi tiết tại [HANDOVER.md](docs/HANDOVER.md).

### Tích hợp LLM thực tế
Kế thừa lớp `app.services.llm_client.LLMClient` và triển khai phương thức `generate(prompt: str, system_prompt: str, max_tokens: int) -> str`. Hệ thống không gắn chặt với bất kỳ nhà cung cấp LLM cụ thể nào.

---

## 5. Tài liệu tham khảo quan trọng
- [Tài liệu hành vi hệ thống](docs/SYSTEM_BEHAVIOR.md)
- [Tài liệu bàn giao kỹ thuật](docs/HANDOVER.md)
- [Ma trận truy vết yêu cầu](docs/TRACEABILITY.md)
- [Đặc tả an toàn và bảo mật](docs/SAFETY.md)
