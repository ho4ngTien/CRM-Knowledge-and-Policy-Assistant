# TÀI LIỆU BÀN GIAO KỸ THUẬT VÀ PHỐI HỢP TÍCH HỢP (HANDOVER GUIDE)

**Dự án:** AI-06 CRM Knowledge and Policy Assistant (Group 7)  
**Vai trò:** S4 – Application + LLM Engineer (Gói công việc WP04)  
**Thời điểm bàn giao:** Giai đoạn 6B – Sửa sai sót báo cáo Giai đoạn 6  
**Nhánh Git:** `feature/s4-complete`  
**Phiên bản:** `1.2.0` (Prompt `v1.1`, Config `1.2.0`)  
**Trạng thái kiểm thử:** 154/154 Tests Passed (Mock offline)  

---

## 1. Mục đích tài liệu
Tài liệu này cung cấp hướng dẫn bàn giao chi tiết từ vai trò **S4 (Application + LLM Engineer)** tới các thành viên và phân hệ trong dự án:
- **Tích hợp kho tài liệu S3**: Kết nối tìm kiếm ngữ nghĩa và trích xuất bằng chứng.
- **Chuẩn hóa nghiệp vụ và thuật ngữ ngân hàng**: Bổ sung từ điển thuật ngữ tiếng Việt (VN 01).
- **Đánh giá chất lượng và kiểm thử độc lập**: Nghiệm thu chất lượng phản hồi, chống ảo giác và kịch bản Annex B.
- **Hạ tầng, phân quyền và bảo mật**: Triển khai hạ tầng sản xuất, kết nối SSO và bảo mật cơ sở dữ liệu.
- **Ghi chú phân công theo yêu cầu:** OPS 02 (thời gian phản hồi hệ thống) và SEC 02 (chính sách lưu trữ và PII) thuộc phân hệ S5.

---

## 2. Hướng dẫn cài đặt và vận hành trên Windows

Hệ thống được thiết kế chạy chuẩn xác trên môi trường Windows thông qua PowerShell. **Quy tắc bắt buộc:** Luôn sử dụng tiền tố `python -m` cho mọi lệnh để đảm bảo đúng môi trường ảo và module path.

### 2.1 Cài đặt môi trường
```powershell
# 1. Mở PowerShell tại thư mục gốc dự án
cd C:\Users\ACER\Desktop\crm-knowledge-and-policy-assistant

# 2. Tạo và kích hoạt môi trường ảo (nếu chưa có)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Cài đặt các thư viện phụ thuộc
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2.2 Khởi tạo cơ sở dữ liệu nội bộ
```powershell
python -m app.services.database
```

### 2.3 Chạy bộ kiểm thử (Unit & Integration tests)
```powershell
python -m pytest -v
```

### 2.4 Khởi chạy giao diện ứng dụng Workspace (Streamlit)
```powershell
python -m streamlit run app/main.py
```

---

## 3. Cấu trúc thư mục dự án

```text
crm-knowledge-and-policy-assistant/
├── .env.example                     # Mẫu biến môi trường cấu hình
├── .gitignore                       # Quy tắc loại trừ file tạm, cache, test db
├── CHANGELOG.md                     # Lịch sử phát triển và phiên bản
├── README.md                        # Giới thiệu tổng quan và hướng dẫn nhanh
├── pytest.ini                       # Cấu hình kiểm thử pytest
├── requirements.txt                 # Danh sách gói phụ thuộc Python
├── app/                             # Mã nguồn chính của gói S4
│   ├── config.py                    # Cấu hình tập trung, hằng số an toàn, phiên bản
│   ├── main.py                      # Điểm vào giao diện Streamlit (Workspace)
│   ├── models.py                    # Định nghĩa dữ liệu (7 trường, Citation, Enum)
│   ├── components/                  # Thành phần giao diện Streamlit
│   │   ├── feedback_form.py         # Form thu thập phản hồi của nhân viên CRM
│   │   ├── policy_display.py        # Hiển thị câu trả lời (7 trường, citation, hold)
│   │   └── referral_modal.py        # Giao diện chuyển tiếp chuyên viên (Referral)
│   └── services/                    # Tầng nghiệp vụ xử lý lõi (Core Business Layer)
│       ├── citation_verifier.py     # Bộ xác minh trích dẫn nguyên văn (CKPA-39)
│       ├── database.py              # Quản lý SQLite nội bộ (feedback, referral, hold)
│       ├── evidence_provider.py     # Interface trừu tượng kết nối S3
│       ├── evidence_service.py      # Bộ lọc bằng chứng và kiểm tra chunk độc
│       ├── feedback_service.py      # Dịch vụ phản hồi (lọc PII cơ bản)
│       ├── hold_reasons.py          # 14 mã trạng thái HOLD và hướng dẫn
│       ├── input_guard.py           # Bộ lọc đầu vào và chống Injection (ANS 08)
│       ├── llm_client.py            # Interface trừu tượng LLM & MockLLMClient
│       ├── output_guard.py          # Bộ kiểm tra đầu ra, ảo giác số liệu, cấm phê duyệt
│       ├── policy_service.py        # Service facade giao diện gọi pipeline
│       ├── prompt_builder.py        # Bộ nạp prompt tiếng Việt phân lớp
│       ├── qa_pipeline.py           # Pipeline 8 bước xử lý câu hỏi
│       ├── referral_service.py      # Dịch vụ referral nội bộ
│       ├── response_parser.py       # Bộ phân tích JSON 7 trường cố định
│       ├── system_service.py        # Khởi tạo trạng thái phiên làm việc UI
│       └── token_guard.py           # Kiểm soát giới hạn token bảo thủ
├── data/                            # Thư mục chứa CSDL SQLite cục bộ (app.db)
├── docs/                            # Tài liệu kỹ thuật, kiến trúc và quy trình
│   ├── HANDOVER.md                  # Tài liệu bàn giao kỹ thuật này
│   ├── S4_README.md                 # Hướng dẫn chi tiết phân hệ S4
│   ├── OPEN_QUESTIONS.md            # Các câu hỏi tồn đọng liên phân hệ
│   ├── REQUIREMENTS_S4.md           # Đặc tả yêu cầu chính thức phân hệ S4
│   ├── S3_QUESTIONS.md              # Câu hỏi kỹ thuật dành riêng cho phân hệ S3
│   ├── SAFETY.md                    # Tài liệu chính sách an toàn, guardrails
│   ├── STATUS.md                    # Nhật ký tiến độ công việc
│   ├── SYSTEM_BEHAVIOR.md           # Tài liệu mô tả hành vi hệ thống cho người dùng
│   └── TRACEABILITY.md              # Ma trận truy vết Yêu cầu -> Triển khai -> Test
├── prompts/                         # Thư viện Prompt tiếng Việt có quản lý phiên bản
│   ├── system_prompt_vi_v1.0.md
│   ├── system_prompt_vi_v1.1.md     # Prompt hệ thống hiện hành
│   ├── user_template_vi_v1.0.md
│   └── user_template_vi_v1.1.md     # Template người dùng hiện hành
└── tests/                           # Bộ kiểm định chất lượng (154 tests)
    ├── conftest.py                  # Fixtures dùng chung, cô lập database tạm
    ├── fixtures/sample_evidence.py  # Dữ liệu mẫu phục vụ kiểm thử
    ├── test_phase1.py               # Kiểm thử nền tảng, prompt, token
    ├── test_phase2.py               # Kiểm thử 7 trường, xác minh trích dẫn, hold
    ├── test_phase3.py               # Kiểm thử vá trích dẫn, phân tích JSON
    ├── test_phase4.py               # Kiểm thử chống Prompt Injection, output guard
    ├── test_phase4b.py              # Kiểm thử pipeline và retry logic
    ├── test_phase5_ui.py            # Kiểm thử giao diện Streamlit, cô lập tầng dịch vụ
    ├── test_phase6_integration.py   # Kiểm thử tích hợp toàn diện 14 mã HOLD
    └── test_policy_workflow.py      # Kiểm thử luồng nghiệp vụ end-to-end
```

---

## 4. Hướng dẫn cắm ghép module S3 (Evidence Retrieval)

S4 đã bàn giao lớp trừu tượng tại `app/services/evidence_provider.py`. Kỹ sư phụ trách tích hợp chỉ cần kế thừa lớp `EvidenceProvider` và cài đặt hàm `retrieve_evidence`:

```python
from typing import List
from app.services.evidence_provider import EvidenceProvider
from app.models import Citation

class S3ProductionEvidenceProvider(EvidenceProvider):
    def __init__(self, s3_endpoint: str, api_key: str):
        self.endpoint = s3_endpoint
        self.api_key = api_key

    def retrieve_evidence(self, question: str) -> List[Citation]:
        """
        1. Gọi vector search / semantic search từ kho tài liệu chính sách
        2. Chuyển đổi kết quả về danh sách Citation chuẩn của app.models.Citation
        """
        # Triển khai truy xuất thực tế ở đây...
        citations = []
        return citations
```

**Cách lắp ghép vào Pipeline:**
```python
s3_provider = S3ProductionEvidenceProvider(...)
pipeline = QAPipeline(evidence_provider=s3_provider)
```

---

## 5. Hướng dẫn cắm ghép mô hình LLM thật

Hệ thống S4 **tuyệt đối không hardcode bất kỳ nhà cung cấp LLM cụ thể nào** nhằm tuân thủ nguyên tắc độc lập nền tảng và bảo mật dữ liệu ngân hàng.

Để kết nối với LLM thật, kỹ sư triển khai kế thừa lớp `LLMClient` trong `app/services/llm_client.py`:

```python
from app.services.llm_client import LLMClient

class EnterpriseLLMClient(LLMClient):
    def __init__(self, gateway_url: str, credential_token: str):
        self.gateway_url = gateway_url
        self.token = credential_token

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 900
    ) -> str:
        """
        Gửi yêu cầu tới cổng AI nội bộ và trả về chuỗi văn bản (JSON).
        Tuân thủ max_tokens (mặc định tối đa 900 theo CKPA-42).
        """
        # Gọi API sinh văn bản...
        return '{"effective_date": "...", ...}'
```

**Cách lắp ghép vào Gateway và Pipeline:**
```python
from app.services.llm_client import LLMGateway

enterprise_client = EnterpriseLLMClient(...)
gateway = LLMGateway(client=enterprise_client)
pipeline = QAPipeline(llm_gateway=gateway)
```

---

## 6. Danh sách chờ phối hợp liên phân hệ (Waiting List)

| Hạng mục chờ tiếp nhận & phối hợp | Trách nhiệm | Trạng thái hiện tại |
|---|---|---|
| - Chốt định dạng dữ liệu trả về (hợp đồng S3 Retrieval)<br>- Cung cấp trường phân loại quyền truy cập văn bản<br>- Thống nhất ngưỡng điểm tương đồng văn bản | Chưa xác định, cần nhóm xác nhận | Đang chờ phân hệ Retrieval |
| - Chuẩn hóa từ điển thuật ngữ ngân hàng Việt Nam (VN 01)<br>- Rà soát danh mục từ phủ định / ngoại lệ nghiệp vụ | Chưa xác định, cần nhóm xác nhận | Đang chờ phân hệ nghiệp vụ |
| - Bộ test case độc lập đánh giá tỷ lệ ảo giác (Grounding test)<br>- Kiểm định chất lượng câu trả lời ngắn (100–250 từ) | Chưa xác định, cần nhóm xác nhận | Đang chờ phân hệ kiểm thử |
| - Tích hợp hệ thống phân quyền nhân viên SSO/IAM<br>- Thay thế SQLite cục bộ bằng CSDL bảo mật của ngân hàng<br>- Kiểm toán mã nguồn và cấu hình mạng cô lập | Chưa xác định, cần nhóm xác nhận | Đang chờ phân hệ hạ tầng/bảo mật |
| - Phê duyệt danh mục 14 mã trạng thái HOLD và thông điệp tiếng Việt<br>- Chốt chính sách lưu trữ và thời hạn xóa nhật ký truy vấn | Chưa xác định, cần nhóm xác nhận | Đang chờ quản lý dự án / nhóm xác nhận |
| - Đo lường thời gian phản hồi toàn hệ thống (OPS 02, p95 <= 25s)<br>- Chính sách lưu trữ dữ liệu và bảo mật PII (SEC 02) | Thuộc phân hệ S5 theo tài liệu yêu cầu | Đang chờ phân hệ S5 |

---

## 7. Danh mục kiểm tra trước khi đưa vào dữ liệu thật (Pre-Production Checklist)

Trước khi hệ thống được nạp dữ liệu chính sách thực tế hoặc tiếp nhận truy vấn từ người dùng thật, các bước kiểm tra sau phải được hoàn thành:

- [ ] **Chính sách lưu giữ dữ liệu (Data Retention):** Xác định thời gian lưu và cơ chế tự động xóa dữ liệu tại bảng `hold_logs`, `feedback`, `referrals` (thuộc S5).
- [ ] **Xác thực và phân quyền (Authentication & Authorization):** Tích hợp SSO ngân hàng để định danh chính xác nhân viên CRM gửi câu hỏi (chưa xác định, cần nhóm xác nhận).
- [ ] **Bộ đếm Token chính thức (Official Tokenizer):** Thay thế hệ số ước lượng bảo thủ bằng tokenizer chính xác của mô hình được phê duyệt.
- [ ] **Công cụ Guardrail:** Nhóm chưa chọn công cụ guardrail; đây là câu hỏi mở cần thảo luận trước khi vận hành thực tế.
- [ ] **Kiểm thử nghiệm thu bảo mật (Security Audit / Annex B):** Chạy kiểm thử thâm nhập đối với các kịch bản Prompt Injection phức tạp.
- [ ] **Ký biên bản nghiệm thu kỹ thuật WP04:** Đại diện các phân hệ xác nhận tương thích hợp đồng tích hợp.
