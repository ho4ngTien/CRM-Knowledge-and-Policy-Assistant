# DOC-003 — Chính sách Tiếp nhận và Định tuyến Dịch vụ/Bảo hành Thiết bị Công nghiệp SongNhat (VER-000/001/002)

- **Policy Family:** `POL-003`
- **Authority Layer (DAT 03):** `policy`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-003_POL-CRM-02_Warranty_and_Service_Routing.md`
- **Curated Passages Count:** 20
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng `source_uri` (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-021 | VER-001 | Điều 1.2–1.3 (BH-02-02..03) (Trang 1) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - 03 Chứng từ bắt buộc & SLA kiểm tra sơ bộ
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-02..03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:warranty_intake_docs`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Hồ sơ tiếp nhận bảo hành bắt buộc và thời hạn kiểm tra sơ bộ (Critical Field CF-009): Khi khách hàng báo sự cố kỹ thuật đối với Động cơ công nghiệp, Biến tần hoặc Bộ truyền động bánh răng, nhân viên CSKH (reader / CSKH Staff) phải thu thập đủ 03 chứng từ trên ticket CRM: (1) Phiếu bảo hành chính hãng SongNhat; (2) Ảnh chụp rõ nét Tem thông số kỹ thuật (Nameplate) và Số Serial (S/N) nguyên vẹn trên thân máy; (3) Biên bản bàn giao nghiệm thu hoặc Hóa đơn GTGT. SLA kiểm tra sơ bộ tính hợp lệ của hồ sơ: Tối đa 02 giờ làm việc. [Dữ liệu giả lập phục vụ đồ án]

### PAS-022 | VER-001 | Điều 1.1 (BH-02-01) (Trang 1) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Mục đích & Phạm vi sản phẩm công nghiệp
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:all_warranty_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Mục đích quy trình tiếp nhận và định tuyến dịch vụ/bảo hành: Chuẩn hóa việc thu thập bằng chứng kỹ thuật ban đầu và chuyển đúng đầu mối chuyên môn được ủy quyền đối với các thiết bị công nghiệp do SongNhat phân phối. Quy trình này chỉ điều chỉnh bước tiếp nhận và định tuyến trên CRM, không thay thế biên bản giám định kỹ thuật của xưởng hoặc hãng sản xuất. [Dữ liệu giả lập phục vụ đồ án]

### PAS-023 | VER-001 | Điều 2.1 (BH-02-04) (Trang 1) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Định tuyến Tuyến 1 (Công suất <= 37 kW / Phụ kiện)
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:tier1_internal_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Định tuyến xử lý kỹ thuật Tuyến 1 về Xưởng dịch vụ nội bộ SongNhat (power_kw <= 37 kW - Critical Field CF-009): Áp dụng cho các thiết bị động cơ, bộ truyền động bánh răng hoặc thiết bị truyền lực công nghiệp có công suất định mức từ 37 kW trở xuống (<= 37 kW) hoặc gặp sự cố ở phụ kiện ngoại vi, đã nộp đủ 03 chứng từ bảo hành hợp lệ. Đầu mối nhận định tuyến: Trưởng bộ phận Kỹ thuật nội bộ (Internal Tech Lead). Thời hạn định tuyến (SLA): Tối đa 04 giờ làm việc kể từ khi đủ hồ sơ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-024 | VER-001 | Điều 2.2 (BH-02-05) (Trang 2) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Định tuyến Tuyến 2 (Công suất > 37 kW / Bo mạch chính)
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-05)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:tier2_vendor_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Định tuyến xử lý kỹ thuật Tuyến 2 gửi Giám định Hãng sản xuất (power_kw > 37 kW OR main_board_fault - Critical Field CF-010): Áp dụng cho tổ hợp Động cơ phòng nổ, Biến tần trung thế, Thiết bị truyền lực công nghiệp có công suất định mức trên 37 kW (> 37 kW) hoặc tất cả các trường hợp lỗi bo mạch điều khiển trung tâm. Đầu mối nhận định tuyến: Kỹ sư trưởng Phụ trách Hãng (Vendor Chief Engineer). Thời hạn định tuyến (SLA): Tối đa 04 giờ làm việc kể từ khi đủ 03 chứng từ hợp lệ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-025 | VER-001 | Điều 2.3 (BH-02-06) (Trang 2) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Ranh giới cấm phán quyết bảo hành & cấm hướng dẫn sửa chữa
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-06)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:no_adjudication_no_repair`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Giới hạn cứng của Nhân viên CRM/CSKH và Trợ lý AI (Boundary ANS 07): Nhân viên tiếp nhận và hệ thống AI chỉ được phép hướng dẫn danh mục 03 chứng từ cần nộp, thời hạn SLA và định tuyến đúng đầu mối kỹ thuật (Tuyến 1 hoặc Tuyến 2). Tuyệt đối cấm tự phán quyết thiết bị đủ điều kiện bảo hành miễn phí hay tính phí, và cấm cung cấp hướng dẫn kỹ thuật để khách hàng tự tháo nắp máy, đấu nối hoặc sửa chữa thiết bị công nghiệp. [Dữ liệu giả lập phục vụ đồ án]

### PAS-026 | VER-001 | Điều 2.4 (BH-02-07) (Trang 2) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Ngoại lệ mờ/rách tem Serial hoặc mất Phiếu bảo hành
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-07)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:missing_serial_or_card_hold`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Xử lý ngoại lệ thiếu chứng từ cốt lõi hoặc mờ/rách tem Nameplate/Serial (Worked Case 7 & DAT 08): Trường hợp thiết bị Động cơ/Biến tần của khách hàng bị mờ, rách tem thông số Serial (Nameplate) hoặc thất lạc Phiếu bảo hành chính hãng nhưng khách hàng đề nghị hỗ trợ đặc biệt, nhân viên CSKH bắt buộc giữ hồ sơ ở trạng thái chờ (HOLD) và tạo phiếu chuyển xử lý nội bộ (Local Referral) về Chủ sở hữu chính sách bảo hành (Warranty Policy Owner) phối hợp Trưởng bộ phận Kỹ thuật xem xét. [Dữ liệu giả lập phục vụ đồ án]

### PAS-027 | VER-001 | Điều 3.1 (BH-02-08) (Trang 2) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Xác định ngày chi phối bảo hành (Governing Date giờ VN)
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-08)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:dated_warranty_lookup`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy tắc ngày chi phối đối với yêu cầu dịch vụ/bảo hành có ngày giao dịch cụ thể (Worked Case 3, DAT 04): Khi tra cứu quy định định tuyến cho thiết bị đã bàn giao trong quá khứ, hệ thống xác định phiên bản chính sách áp dụng theo ngày tiếp nhận yêu cầu dịch vụ hoặc ngày bàn giao nghiệm thu theo múi giờ Asia/Ho_Chi_Minh do Policy Owner quy định. Nếu thiếu ngày bàn giao/hoàn cảnh tiên quyết, hệ thống phải đặt câu hỏi làm rõ trước khi kết luận. [Dữ liệu giả lập phục vụ đồ án]

### PAS-028 | VER-001 | Điều 3.2 (BH-02-09) (Trang 2) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Xung đột điều khoản Hãng sản xuất và Hợp đồng riêng
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-09)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:oem_contract_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Xử lý mâu thuẫn giữa Điều khoản nhà sản xuất (manufacturer_terms), Hợp đồng khách hàng (customer_contract) và Chính sách bảo hành chung (DAT 03, DAT 05 - Worked Case 5): Khi cam kết SLA hoặc tuyến tiếp nhận trong Hợp đồng riêng của dự án mâu thuẫn với điều khoản chuẩn của Hãng sản xuất hoặc chính sách này, hệ thống phải giữ kết luận ở trạng thái HOLD, trích dẫn rõ các nguồn đang xung đột và chuyển Warranty Policy Owner phân xử. [Dữ liệu giả lập phục vụ đồ án]

### PAS-029 | VER-001 | Điều 3.3 (BH-02-10) (Trang 2) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Thu hồi chính sách khẩn cấp (Instant Withdrawal)
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-10)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:instant_withdrawal`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Cơ chế thu hồi tức thời hướng dẫn định tuyến bảo hành khi phát hiện rủi ro kỹ thuật (Worked Case 9, KNW 04, SEC 05): Khi Warranty Policy Owner kích hoạt lệnh rút chính sách (withdrawn), trạng thái có thẩm quyền trong DB được khóa ngay lập tức, mọi tiến trình sinh câu trả lời đang chạy phải bị chặn ở bước kiểm tra cuối (pre-display check), xóa cache Redis trong vòng 5 phút và gắn cảnh báo 'Stale' trên màn hình nhân viên. [Dữ liệu giả lập phục vụ đồ án]

### PAS-030 | VER-001 | Điều 3.4 (BH-02-11) (Trang 2) — [effective]
- **Title:** Chính sách Tiếp nhận & Định tuyến Bảo hành - Chuyển xử lý nội bộ (Local Referral) & Ứng viên tri thức
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-11)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:local_referral_and_feedback`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy định tạo phiếu chuyển xử lý nội bộ và ghi nhận phản hồi nhân viên (KNW 05, KNW 06, KNW 07): Đối với các sự cố thiết bị ngoài danh mục chuẩn, nhân viên CSKH tạo bản ghi Local Referral (theo dõi 3 trạng thái referred, owner_responded, closed) kèm ngữ cảnh tối thiểu. Mọi phản hồi từ nhân viên (missing_source, outdated_rule, wrong_scope, missing_exception, rejected) chỉ được lưu làm feedback_candidate chờ Steward và Policy Owner duyệt, tuyệt đối không tự động cập nhật rule. [Dữ liệu giả lập phục vụ đồ án]

### PAS-079 | VER-001 | Điều 4.1 (BH-02-12) (Trang 3) — [effective]
- **Title:** Chính sách Bảo hành - Quy định định tuyến riêng cho Động cơ phòng nổ (Ex-d)
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-12)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:explosion_proof_motor;transaction_scope:tier2_vendor_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.1 - Định tuyến bắt buộc cho Động cơ phòng nổ chuẩn Ex-d / ATEX: Do yêu cầu nghiêm ngặt về chứng chỉ an toàn chống cháy nổ, mọi sự cố liên quan đến Động cơ phòng nổ (kể cả công suất <= 37 kW) phải được định tuyến về Tuyến 2 (Vendor Chief Engineer — Giám định Hãng) trong SLA <= 04 giờ làm việc sau khi đủ 03 chứng từ (CF-032). Nghiêm cấm xưởng nội bộ tự mở vỏ chống cháy nổ khi chưa có ủy quyền bằng văn bản từ Hãng. [Dữ liệu giả lập phục vụ đồ án]

### PAS-080 | VER-001 | Điều 4.2 (BH-02-13) (Trang 3) — [effective]
- **Title:** Chính sách Bảo hành - Định tuyến sự cố Biến tần trung thế & Lỗi bo mạch điều khiển
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-13)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:mv_inverter;transaction_scope:tier2_vendor_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.2 - Xử lý tiếp nhận sự cố Biến tần trung thế (MV Inverter) và bo mạch điều khiển trung tâm: Ngoài 03 chứng từ bắt buộc tại Điều 1.2 (Phiếu bảo hành, ảnh Nameplate/Serial, Biên bản bàn giao/Hóa đơn), nhân viên CSKH yêu cầu khách hàng cung cấp ảnh chụp mã lỗi (Fault Code) hiển thị trên màn hình biến tần để đính kèm ticket trước khi định tuyến Tuyến 2 (Vendor Chief Engineer, SLA <= 04 giờ làm việc — CF-033). [Dữ liệu giả lập phục vụ đồ án]

### PAS-081 | VER-001 | Điều 4.3 (BH-02-14) (Trang 3) — [effective]
- **Title:** Chính sách Bảo hành - Thời hạn chuẩn bảo hành & Yêu cầu kiểm tra mốc bàn giao
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-14)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:warranty_period_check`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.3 - Đối chiếu mốc thời hạn bảo hành tham chiếu (12 tháng tiêu chuẩn): Thời hạn bảo hành tiêu chuẩn tham chiếu đối với động cơ và hộp giảm tốc công nghiệp là 12 tháng kể từ ngày ký Biên bản bàn giao nghiệm thu (CF-034). Nhân viên CSKH chỉ ghi nhận mốc ngày bàn giao để chuyển đúng đầu mối kỹ thuật, tuyệt đối không tự kết luận từ chối hay chấp nhận bảo hành miễn phí (ANS 07). [Dữ liệu giả lập phục vụ đồ án]

### PAS-082 | VER-001 | Phụ lục B3 (BH-02-B3) (Trang 5) — [effective]
- **Title:** Chính sách Bảo hành - Phụ lục Danh mục Linh kiện Hao mòn Loại trừ (Thiếu Chú thích DAT 08)
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-B3)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:consumable_parts_exclusion`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `false`

Phụ lục B3 - Danh mục linh kiện tiêu hao (vòng bi, phớt chắn dầu, chổi than) và điều kiện định tuyến dịch vụ tính phí: Việc phân loại phụ kiện tiêu hao áp dụng theo Bảng mã linh kiện đính kèm (Lưu ý: Bảng chi tiết mã linh kiện hao mòn và chú thích loại trừ lỗi lắp đặt ở trang 5 chưa được đính kèm đầy đủ trong bản trích xuất này -> gắn cờ has_essential_attachments=false để hệ thống Quarantine/HOLD theo DAT 08). [Dữ liệu giả lập phục vụ đồ án]

### PAS-083 | VER-001 | Điều 5.1 (BH-02-15) (Trang 4) — [effective]
- **Title:** [Hạn chế quyền] Chính sách Bảo hành - Định mức chi phí giám định hiện trường nội bộ
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-15-CONFIDENTIAL)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:service_manager;customer_group:b2b;product:industrial;transaction_scope:field_inspection_budget`
- **Audience (SEC 01):** `policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 5.1 (Tài liệu nội bộ cấp Quản trị dịch vụ — KHÔNG hiển thị cho role reader theo SEC 01): Định mức ngân sách phê duyệt cử kỹ sư kiểm tra hiện trường khẩn cấp đối với sự cố dây chuyền nhà máy là <= 15.000.000 VND/lượt thuộc thẩm quyền Service Director (CF-035); vượt mức 15 triệu VND trình Ban Giám đốc phê duyệt trước khi điều động. [Dữ liệu giả lập phục vụ đồ án]

### PAS-084 | VER-001 | Điều 4.4 (BH-02-16) (Trang 4) — [effective]
- **Title:** Chính sách Bảo hành - Định tuyến khu vực Chi nhánh HN/ĐN/HCM
- **Source Ref:** `POL-003 / POL-CRM-02_v1.0.docx (BH-02-16)`
- **Scope (6-dim DAT 04):** `company:SN;branch:HN,DN,HCM;role:cskh;customer_group:b2b;product:industrial;transaction_scope:regional_warranty_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.4 - Phân tuyến tiếp nhận theo Chi nhánh khu vực (Miền Bắc HN, Miền Trung ĐN, Miền Nam HCM): Yêu cầu Tuyến 1 (<= 37 kW) được định tuyến về Xưởng dịch vụ nội bộ tại chi nhánh gần nhất (HN/ĐN/HCM); mọi yêu cầu Tuyến 2 (> 37 kW, lỗi bo mạch chính hoặc Động cơ phòng nổ) tập trung về đầu mối Vendor Chief Engineer tại Trụ sở chính. [Dữ liệu giả lập phục vụ đồ án]

### PAS-085 | DOC003-VER-000 | Điều 2.1 v0.9 (Trang 1) — [superseded]
- **Title:** [Lịch sử v0.9] Chính sách Bảo hành - Ngưỡng công suất Tuyến 1 cũ (<= 22 kW)
- **Source Ref:** `POL-003 / POL-CRM-02_v0.9_superseded.docx (BH-00-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:tier1_internal_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lịch sử v0.9 (hiệu lực 01/01/2025 – 06/11/2026 08:59:59 +07:00, đã bị thay thế bởi VER-001): Trong giai đoạn trước 06/11/2026, ngưỡng công suất định tuyến Xưởng dịch vụ nội bộ Tuyến 1 là <= 22 kW (CF-036); thiết bị > 22 kW phải gửi Giám định Hãng Tuyến 2 với SLA định tuyến 08 giờ làm việc. Chỉ áp dụng cho yêu cầu lịch sử trước 06/11/2026 09:00 +07:00 kèm nhãn 'Hướng dẫn lịch sử'. [Dữ liệu giả lập phục vụ đồ án]

### PAS-086 | DOC003-VER-002 | Điều 2.1 v2.0 (Trang 1) — [scheduled]
- **Title:** [Tương lai v2.0 - Scheduled] Chính sách Bảo hành 2027 - Nâng ngưỡng Tuyến 1 lên <= 45 kW
- **Source Ref:** `POL-003 / POL-CRM-02_v2.0_scheduled.docx (BH-02-04-v2)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:tier1_internal_routing`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lên lịch tương lai v2.0 (trạng thái scheduled — hiệu lực từ 01/01/2027 00:00:00 +07:00, thay thế VER-001): Sau khi Xưởng dịch vụ nội bộ SongNhat nâng cấp bàn thử tải, ngưỡng công suất định tuyến Tuyến 1 dự kiến nâng từ <= 37 kW lên <= 45 kW (CF-037). TUYỆT ĐỐI KHÔNG áp dụng cho yêu cầu bảo hành năm 2026. [Dữ liệu giả lập phục vụ đồ án]

### PAS-087 | DOC003-VER-001-WD | Thông báo (Đã thu hồi) (Trang 1) — [withdrawn]
- **Title:** [Đã thu hồi - Withdrawn] Hướng dẫn cho phép CSKH tự tiếp nhận bảo hành thiếu ảnh Serial
- **Source Ref:** `POL-003 / POL-CRM-02_memo_withdrawn.docx (BH-WD-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:industrial;transaction_scope:warranty_intake_docs`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Trạng thái withdrawn (ĐÃ THU HỒI KHẨN CẤP theo SEC 05 / KNW 04 — CẤM phục vụ hoặc tái sử dụng): Thông báo cũ cho phép chuyển ticket sang Xưởng kỹ thuật khi chưa có ảnh chụp Tem Nameplate/Serial đã bị đình chỉ ngay lập tức do gây sai lệch nguồn gốc thiết bị. Mọi câu trả lời liên quan phải bị chặn fail-closed. [Dữ liệu giả lập phục vụ đồ án]

### PAS-088 | DOC003-VER-001-REV | Dự thảo Phụ lục D (Trang 1) — [owner_reviewed]
- **Title:** [Owner Reviewed] Bản rà soát quy định cho mượn thiết bị dự phòng tạm thời
- **Source Ref:** `POL-003 / POL-CRM-02_v1.1_owner_reviewed.docx (BH-RV-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:cskh;customer_group:b2b;product:mv_inverter;transaction_scope:loaner_equipment`
- **Audience (SEC 01):** `policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Trạng thái owner_reviewed (Chủ sở hữu bảo hành đã rà soát nhưng CHƯA phê duyệt/phát hành theo KNW 03): Đề xuất điều kiện cho mượn biến tần dự phòng trong thời gian chờ Hãng giám định Tuyến 2. Bộ lọc 7 trạng thái phải chặn hoàn toàn khỏi hướng dẫn hiện hành. [Dữ liệu giả lập phục vụ đồ án]

