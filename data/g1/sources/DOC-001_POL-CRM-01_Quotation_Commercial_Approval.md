# DOC-001 — Quy trình Báo giá và Phê duyệt Thương mại sản phẩm công nghiệp SongNhat (VER-000/001/002)

- **Policy Family:** `POL-001`
- **Authority Layer (DAT 03):** `policy`
- **Source URI (Repo-relative):** `data/g1/sources/DOC-001_POL-CRM-01_Quotation_Commercial_Approval.md`
- **Curated Passages Count:** 29
- **Ghi chú đồ án:** Hồ sơ tham chiếu nguồn tổng hợp phục vụ kiểm chứng source_uri (DAT 08 / G1-AC01) trong phạm vi Base Scope (0% PII thật).

## Mục lục Điều khoản đã Trích xuất
### PAS-001 | VER-001 | Điều 1.1 (Trang 1) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Mục đích & Phạm vi
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:all_commercial`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Mục đích: Chuẩn hóa quy trình lập báo giá, áp dụng mức chiết khấu và phân cấp thẩm quyền phê duyệt thương mại đối với các dòng sản phẩm công nghiệp của SongNhat (Động cơ công nghiệp 3 pha, Động cơ phòng nổ, Biến tần trung thế, Bộ truyền động bánh răng, Thiết bị truyền lực công nghiệp) trên hệ thống CRM. Áp dụng bắt buộc cho toàn bộ giao dịch B2B nội địa. [Dữ liệu giả lập phục vụ đồ án]

### PAS-002 | VER-001 | Điều 1.2–1.3 (QBG-01-02..03) (Trang 1) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Hiệu lực báo giá & Trường CRM bắt buộc
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-02..03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:standard_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Nguyên tắc báo giá chuẩn và thông tin khởi tạo bắt buộc (Worked Case 1): Chuyên viên kinh doanh lập báo giá căn cứ trên Bảng giá niêm yết hiện hành bằng tiền tệ VND. Trước khi xuất báo giá cho khách hàng doanh nghiệp hoặc đại lý mới trên CRM, hồ sơ bắt buộc phải có đủ: Mã số thuế (MST), Giấy chứng nhận Đăng ký kinh doanh (ĐKKD), Phân nhóm khách hàng (Nhà máy hoặc Đại lý) và Thông tin Người liên hệ nhận báo giá. Thời hạn hiệu lực của báo giá tối đa là 15 ngày làm việc kể từ ngày phát hành (Critical Field CF-004). [Dữ liệu giả lập phục vụ đồ án]

### PAS-003 | VER-001 | Điều 1.3 (QBG-01-03) (Trang 1) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Quy định kiểm tra hồ sơ trước báo giá
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-03)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:standard_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Kiểm soát điều kiện tiên quyết khi tạo báo giá trên CRM: Hệ thống và nhân viên kinh doanh không được phát hành báo giá chính thức nếu thiếu bất kỳ trường bắt buộc nào tại Điều 1.2–1.3 hoặc khi chưa xác định rõ dòng sản phẩm, đơn vị tính và điều kiện giao hàng tiêu chuẩn (Incoterms/nội địa). Trường hợp khách hàng chưa cung cấp đủ MST hoặc ĐKKD, chỉ được cung cấp thông tin giới thiệu sản phẩm chung, không tạo cam kết giá. [Dữ liệu giả lập phục vụ đồ án]

### PAS-004 | VER-001 | Điều 2.1 (QBG-01-04) (Trang 1) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Ngưỡng chiết khấu cơ bản (<= 5%)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:standard_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Mức chiết khấu thương mại tiêu chuẩn (discount_rate <= 5% - Critical Field CF-001): Áp dụng cho đơn hàng B2B có tỷ lệ chiết khấu tối đa 5% trên Bảng giá niêm yết hiện hành và tổng giá trị đơn hàng dưới 500.000.000 VND. Thẩm quyền phê duyệt: Chuyên viên Kinh doanh (reader / Sales Staff) được quyền tự lập và xác nhận báo giá trên CRM. Thời hạn xử lý (SLA): Tối đa 02 giờ làm việc kể từ khi nhận đủ thông tin yêu cầu hợp lệ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-005 | VER-001 | Điều 2.2 (QBG-01-05) (Trang 1) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Ngưỡng chiết khấu tầm trung (5% < CK <= 15%)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-05)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:mid_tier_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Mức chiết khấu thương mại tầm trung (5% < discount_rate <= 15% - Critical Field CF-002): Áp dụng cho đơn hàng đề xuất mức chiết khấu từ trên 5% đến tối đa 15% (với tổng giá trị đơn hàng dưới 1.000.000.000 VND). Chứng từ bắt buộc trên CRM: Phiếu đề xuất chiết khấu kèm Bảng tính biên lợi nhuận dự kiến (Gross Margin Sheet). Thẩm quyền phê duyệt: Trưởng phòng Kinh doanh (Sales Manager). Thời hạn xử lý (SLA): Tối đa 04 giờ làm việc. [Dữ liệu giả lập phục vụ đồ án]

### PAS-006 | VER-001 | Điều 2.3 (QBG-01-06) (Trang 2) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Đơn hàng lớn (>= 1 tỷ VND) hoặc Chiết khấu > 15%
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-06)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:large_order_or_high_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Ngưỡng đơn hàng giá trị lớn hoặc chiết khấu đặc biệt (order_value >= 1.000.000.000 VND OR discount_rate > 15% - Worked Case 2 & Critical Field CF-003): Mọi đơn hàng có tổng giá trị từ 1,0 tỷ VND trở lên hoặc đề xuất mức chiết khấu vượt quá 15% bắt buộc phải đính kèm Hợp đồng nguyên tắc/Hợp đồng dự thảo và Tờ trình phê duyệt ngoại lệ thương mại. Thẩm quyền phê duyệt: Giám đốc Kinh doanh / Giám đốc Thương mại (Sales Director). Thời hạn xử lý (SLA): Tối đa 48 giờ làm việc. Nghiêm cấm nhân viên hoặc Trợ lý AI tự cấp chiết khấu vượt ngưỡng. [Dữ liệu giả lập phục vụ đồ án]

### PAS-007 | VER-001 | Điều 2.4 (QBG-01-07) (Trang 2) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Cấm suy luận ưu đãi VIP từ ghi chú CRM cũ
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-07)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:exception_request`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Nguyên tắc cấm suy luận phê duyệt từ tiền lệ hoặc ghi chú cũ (No Inferred Approval - Worked Case 6): Ghi chú CRM của nhân viên (staff_note) hoặc các ngoại lệ thương mại đã duyệt trong quá khứ cho khách hàng VIP chỉ được coi là lịch sử giao dịch có ghi nguồn của đơn hàng cũ, tuyệt đối không tạo thành quy tắc chung và không tự động ghi đè chính sách hiện hành. Mọi đơn hàng mới có mức chiết khấu > 15% hoặc giá trị >= 1 tỷ VND đều phải trình duyệt lại theo đúng Điều 2.3. [Dữ liệu giả lập phục vụ đồ án]

### PAS-008 | VER-001 | Điều 2.5 (QBG-01-08) (Trang 2) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Xử lý xung đột Hợp đồng khung (Conflict Hold)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-08)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:contract_conflict`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy tắc tạm giữ khi xung đột giữa Hợp đồng khách hàng và Chính sách công ty (Conflict Hold DAT 05 - Worked Case 5): Hệ thống và nhân viên không được tự suy diễn thứ bậc ưu tiên phổ quát giữa Hợp đồng khung ký riêng với khách hàng (customer_contract) và Chính sách báo giá chung (policy), đồng thời không mặc định văn bản mới nhất thắng. Khi phát hiện điều khoản chiết khấu/giá mâu thuẫn, bắt buộc giữ kết luận ở trạng thái chờ (HOLD), hiển thị đồng thời các bằng chứng được phép và chuyển Chủ sở hữu chính sách thương mại (Commercial Policy Owner) quyết định. [Dữ liệu giả lập phục vụ đồ án]

### PAS-009 | VER-001 | Điều 3.1 (QBG-01-09) (Trang 2) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Ngày chi phối (Governing Date) & Chính sách tương lai
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-09)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:dated_or_future_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy tắc xác định ngày hiệu lực theo múi giờ Việt Nam Asia/Ho_Chi_Minh (DAT 04, OPS 03 - Worked Case 3 & 4): Câu hỏi quy trình chung áp dụng phiên bản effective tại ngày hiện tại (giờ VN). Câu hỏi gắn với báo giá/giao dịch có ngày cụ thể áp dụng phiên bản có hiệu lực tại đúng ngày phát hành báo giá đó và phải gắn nhãn 'Hướng dẫn lịch sử'. Các chính sách ở trạng thái lên lịch tương lai (scheduled) tuyệt đối không được dùng làm quy tắc hiện hành trước thời điểm effective_from. [Dữ liệu giả lập phục vụ đồ án]

### PAS-010 | VER-001 | Điều 3.2 (QBG-01-10) (Trang 2) — [effective]
- **Title:** Chính sách Báo giá và Phê duyệt Thương mại - Kiểm soát chú thích & bảng biểu thiết yếu (DAT 08)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-10)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:attachment_completeness`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Quy định toàn vẹn bảng phân cấp thẩm quyền và chú thích ngoại lệ (DAT 08 - Worked Case 7): Mọi điều khoản ngưỡng chiết khấu phải đi kèm đầy đủ chú thích điều kiện thanh toán và bảng phân loại nhóm sản phẩm công nghiệp. Nếu đoạn văn bản nhập vào thiếu bảng hoặc chú thích thiết yếu (has_essential_attachments=false), hệ thống phải cách ly vào Quarantine và tạm giữ (HOLD) hướng dẫn đối với ngưỡng bị ảnh hưởng cho đến khi Policy Steward bổ sung đầy đủ. [Dữ liệu giả lập phục vụ đồ án]

### PAS-031 | VER-001 | Phụ lục A1 (QBG-01-A1) (Trang 3) — [effective]
- **Title:** Chính sách Báo giá - Phụ lục chiết khấu Động cơ 3 pha tiêu chuẩn
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-A1)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:motor_3phase;transaction_scope:volume_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phụ lục A1 - Động cơ công nghiệp 3 pha (IE2/IE3): Áp dụng trần chiết khấu cơ bản <= 5% (CF-001) cho đơn hàng tiêu chuẩn < 500 triệu VND. Đối với đơn mua số lượng từ 20 bộ trở lên trong cùng báo giá, nhân viên được phép đề xuất khung chiết khấu sản lượng 5%–10% trình Sales Manager phê duyệt kèm bảng tính Gross Margin (CF-011). [Dữ liệu giả lập phục vụ đồ án]

### PAS-032 | VER-001 | Phụ lục A2 (QBG-01-A2) (Trang 3) — [effective]
- **Title:** Chính sách Báo giá - Phụ lục chiết khấu Động cơ phòng nổ (Ex-d)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-A2)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:explosion_proof_motor;transaction_scope:specialized_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phụ lục A2 - Động cơ phòng nổ chuẩn Ex-d / ATEX: Do yêu cầu chứng chỉ chống cháy nổ và đặt hàng nhập khẩu đặc thù, mức chiết khấu tối đa cấp Sales Staff là <= 3% (CF-012). Mọi đề xuất chiết khấu > 3% cho dòng Động cơ phòng nổ bắt buộc chuyển Sales Manager hoặc Sales Director phê duyệt tùy theo giá trị đơn hàng; không áp dụng mức 5% của động cơ thường. [Dữ liệu giả lập phục vụ đồ án]

### PAS-033 | VER-001 | Phụ lục A3 (QBG-01-A3) (Trang 3) — [effective]
- **Title:** Chính sách Báo giá - Phụ lục Biến tần trung thế (MV Inverter)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-A3)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:mv_inverter;transaction_scope:technical_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phụ lục A3 - Biến tần trung thế (Medium Voltage Inverter): Báo giá bắt buộc đính kèm Bản thông số kỹ thuật (Datasheet) đã được Kỹ sư Ứng dụng xác nhận tải công suất. Chiết khấu tiêu chuẩn <= 5% do Sales Staff lập; mức > 5% đến 12% thuộc thẩm quyền Sales Manager (CF-013); mức > 12% hoặc đơn hàng biến tần trung thế >= 1 tỷ VND trình Sales Director trong SLA 48 giờ làm việc. [Dữ liệu giả lập phục vụ đồ án]

### PAS-034 | VER-001 | Phụ lục A4 (QBG-01-A4) (Trang 4) — [effective]
- **Title:** Chính sách Báo giá - Phụ lục Hộp giảm tốc & Bộ truyền động bánh răng
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-A4)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:gearbox;transaction_scope:bundled_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phụ lục A4 - Bộ truyền động bánh răng và Hộp giảm tốc công nghiệp (Gearbox): Báo giá phải nêu rõ tỷ số truyền, kiểu lắp đặt (chân đế/mặt bích) và điều kiện giao hàng tại kho SongNhat (EXW/nội địa). Chiết khấu theo chính sách chung CF-001..CF-003; trường hợp báo giá đồng bộ cả động cơ và hộp giảm tốc phải liệt kê mã hàng tách dòng trên CRM. [Dữ liệu giả lập phục vụ đồ án]

### PAS-035 | VER-001 | Điều 4.1 (QBG-01-11) (Trang 4) — [effective]
- **Title:** Chính sách Báo giá - Yêu cầu tạm ứng đơn hàng đặt nhập khẩu
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-11)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:non_stock_order`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.1 - Điều kiện đặt cọc / tạm ứng cho đơn hàng không có sẵn kho (Non-stock / Make-to-order): Báo giá cho thiết bị phải nhập khẩu theo cấu hình riêng bắt buộc ghi rõ tỷ lệ tạm ứng tối thiểu >= 30% tổng giá trị đơn hàng ngay khi ký xác nhận đơn hàng (CF-014). Đề xuất giảm tỷ lệ tạm ứng xuống dưới 30% được xếp vào ngoại lệ thương mại và phải trình Sales Director duyệt bằng văn bản (không tự ý cam kết với khách hàng). [Dữ liệu giả lập phục vụ đồ án]

### PAS-036 | VER-001 | Điều 4.2 (QBG-01-12) (Trang 4) — [effective]
- **Title:** Chính sách Báo giá - Quy trình gia hạn báo giá hết hiệu lực
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-12)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:quote_renewal`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.2 - Gia hạn báo giá sau 15 ngày làm việc (CF-004): Báo giá đã quá thời hạn hiệu lực 15 ngày làm việc không được tự động dùng để chốt đơn. Chuyên viên kinh doanh phải tạo phiên bản báo giá tái phát hành trên CRM, kiểm tra lại Bảng giá niêm yết hiện hành (VND) và trình duyệt lại nếu mức chiết khấu vượt ngưỡng 5% hoặc tỷ giá nhập khẩu biến động > 3%. [Dữ liệu giả lập phục vụ đồ án]

### PAS-037 | VER-001 | Điều 4.3 (QBG-01-13) (Trang 5) — [effective]
- **Title:** Chính sách Báo giá - Báo giá Dự án Nhà máy & Gói thầu B2B
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-13)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:factory_project;product:industrial;transaction_scope:project_bidding`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.3 - Báo giá gói thầu hoặc dự án nhà máy mới (Project Bidding): Hồ sơ trên CRM bắt buộc đính kèm Danh mục vật tư BOQ, Bản xác nhận tồn kho/tiến độ nhập khẩu từ bộ phận Mua hàng và Phiếu đánh giá biên lợi nhuận. Mọi báo giá dự án từ 1 tỷ VND trở lên phải qua Sales Director duyệt tối thiểu 48 giờ làm việc trước hạn đóng thầu (CF-003). [Dữ liệu giả lập phục vụ đồ án]

### PAS-038 | VER-001 | Điều 4.4 (QBG-01-14) (Trang 5) — [effective]
- **Title:** Chính sách Báo giá - Phạm vi Chi nhánh HN/ĐN/HCM & Ngoại lệ khu vực
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-14)`
- **Scope (6-dim DAT 04):** `company:SN;branch:HN,DN,HCM;role:sales;customer_group:b2b;product:industrial;transaction_scope:regional_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 4.4 - Áp dụng theo Chi nhánh khu vực (Miền Bắc HN, Miền Trung ĐN, Miền Nam HCM): Các chi nhánh áp dụng thống nhất bảng giá và phân cấp chiết khấu SongNhat (company:SN). Riêng chi phí vận chuyển ngoại tỉnh hoặc giao hàng vào khu công nghiệp xa cảng phải ghi tách dòng riêng trên báo giá, không gộp ẩn vào tỷ lệ chiết khấu sản phẩm. [Dữ liệu giả lập phục vụ đồ án]

### PAS-039 | VER-001 | Điều 5.1 (QBG-01-15) (Trang 6) — [effective]
- **Title:** [Hạn chế quyền] Chính sách Báo giá - Sàn biên lợi nhuận gộp nội bộ (Gross Margin Floor)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-15-CONFIDENTIAL)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales_manager;customer_group:b2b;product:industrial;transaction_scope:margin_floor_check`
- **Audience (SEC 01):** `policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Điều 5.1 (Tài liệu nội bộ cấp Quản trị chính sách — KHÔNG hiển thị cho Reader): Sàn biên lợi nhuận gộp tối thiểu để Sales Manager phê duyệt chiết khấu tầm trung (5%–15%) là Gross Margin >= 18% đối với động cơ tiêu chuẩn và >= 22% đối với biến tần trung thế (CF-015). Mọi đơn hàng có Gross Margin dưới sàn bắt buộc chuyển thẳng Sales Director và Legal/Finance xem xét. [Dữ liệu giả lập phục vụ đồ án]

### PAS-040 | VER-001 | Phụ lục B1 (QBG-01-B1) (Trang 7) — [effective]
- **Title:** Chính sách Báo giá - Bảng chiết khấu bậc thang Đại lý Cấp 1 (Thiếu Chú thích Bảng DAT 08)
- **Source Ref:** `POL-001 / POL-CRM-01_v1.0.docx (QBG-01-B1)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:distributor_tier1;product:industrial;transaction_scope:quarterly_rebate`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `false`

Phụ lục B1 - Bảng chiết khấu bậc thang Đại lý Cấp 1 theo doanh số quý: Mức chiết khấu bổ sung cuối quý áp dụng theo Phụ lục Bảng quy đổi doanh số đính kèm (Lưu ý: bảng điều kiện loại trừ hàng dự án và chú thích cuối trang 7 chưa được đính kèm đầy đủ trong bản trích xuất này -> gắn cờ has_essential_attachments=false để hệ thống tạm giữ HOLD theo DAT 08 cho đến khi bổ sung đủ). [Dữ liệu giả lập phục vụ đồ án]

### PAS-041 | DOC001-VER-000 | Điều 2.1–2.3 v0.9 (Trang 1) — [superseded]
- **Title:** [Lịch sử v0.9] Chính sách Báo giá - Ngưỡng chiết khấu cũ (<= 3% / 3%-10%)
- **Source Ref:** `POL-001 / POL-CRM-01_v0.9_superseded.docx (QBG-00-04)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:standard_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lịch sử v0.9 (hiệu lực từ 01/01/2025 đến 08:59:59 ngày 06/11/2026 giờ VN — đã bị thay thế bởi VER-001): Trong giai đoạn trước 06/11/2026, mức chiết khấu tiêu chuẩn Sales Staff tự duyệt tối đa là <= 3% (CF-016), mức tầm trung Sales Manager duyệt là trên 3% đến <= 10% (CF-017), và mức > 10% hoặc đơn hàng >= 500 triệu VND phải trình Sales Director. Chỉ sử dụng cho truy vấn lịch sử có ngày phát hành báo giá trước 06/11/2026 09:00 +07:00. [Dữ liệu giả lập phục vụ đồ án]

### PAS-042 | DOC001-VER-000 | Điều 1.2 v0.9 (Trang 1) — [superseded]
- **Title:** [Lịch sử v0.9] Chính sách Báo giá - Hiệu lực báo giá cũ (10 ngày làm việc)
- **Source Ref:** `POL-001 / POL-CRM-01_v0.9_superseded.docx (QBG-00-02)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:standard_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lịch sử v0.9 (đã hết hiệu lực từ 06/11/2026 09:00 +07:00): Thời hạn hiệu lực tối đa của báo giá phát hành trong giai đoạn 01/01/2025 – 06/11/2026 08:59:59 là 10 ngày làm việc (CF-018), thay vì 15 ngày làm việc như quy định hiện hành VER-001. Khi tra cứu giao dịch có ngày phát hành thuộc giai đoạn này bắt buộc gắn nhãn 'Hướng dẫn lịch sử'. [Dữ liệu giả lập phục vụ đồ án]

### PAS-043 | DOC001-VER-000 | Điều 2.3 v0.9 (Trang 2) — [superseded]
- **Title:** [Lịch sử v0.9] Chính sách Báo giá - SLA duyệt ngoại lệ cũ (72 giờ làm việc)
- **Source Ref:** `POL-001 / POL-CRM-01_v0.9_superseded.docx (QBG-00-06)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:large_order_or_high_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lịch sử v0.9 (đã hết hiệu lực): Thời hạn xử lý (SLA) của Sales Director đối với tờ trình chiết khấu đặc biệt trên 10% hoặc đơn hàng >= 500 triệu VND trong kỳ hiệu lực 2025–11/2026 là tối đa 72 giờ làm việc. Đã được rút ngắn xuống 48 giờ làm việc tại VER-001. [Dữ liệu giả lập phục vụ đồ án]

### PAS-044 | DOC001-VER-002 | Điều 2.3 v2.0 (Trang 2) — [scheduled]
- **Title:** [Tương lai v2.0 - Scheduled] Chính sách Báo giá 2027 - Ngưỡng đơn hàng lớn >= 1,5 tỷ VND
- **Source Ref:** `POL-001 / POL-CRM-01_v2.0_scheduled.docx (QBG-02-06)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:large_order_or_high_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lên lịch tương lai v2.0 (trạng thái scheduled — bắt đầu hiệu lực từ 00:00:00 ngày 01/01/2027 giờ VN, thay thế VER-001): Từ ngày 01/01/2027, ngưỡng đơn hàng giá trị lớn cần Sales Director phê duyệt điều chỉnh lên >= 1.500.000.000 VND (CF-019) với SLA 36 giờ làm việc. TUYỆT ĐỐI KHÔNG áp dụng cho câu hỏi hoặc giao dịch hiện hành trước 01/01/2027 00:00:00 +07:00. [Dữ liệu giả lập phục vụ đồ án]

### PAS-045 | DOC001-VER-002 | Điều 1.2 v2.0 (Trang 1) — [scheduled]
- **Title:** [Tương lai v2.0 - Scheduled] Chính sách Báo giá 2027 - Hiệu lực báo giá 20 ngày làm việc
- **Source Ref:** `POL-001 / POL-CRM-01_v2.0_scheduled.docx (QBG-02-02)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:standard_quotation`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Phiên bản lên lịch tương lai v2.0 (trạng thái scheduled — có hiệu lực từ 01/01/2027 00:00:00 +07:00): Thời hạn hiệu lực báo giá tiêu chuẩn cho khách hàng nhà máy B2B dự kiến tăng từ 15 lên 20 ngày làm việc (CF-020). Chỉ hiển thị khi nhân viên hỏi rõ về chính sách 2027 kèm nhãn 'Hướng dẫn tương lai — Chưa có hiệu lực'. [Dữ liệu giả lập phục vụ đồ án]

### PAS-046 | DOC001-VER-003-DRAFT | Dự thảo Mục 1 (Trang 1) — [draft]
- **Title:** [Dự thảo - Draft] Đề xuất điều chỉnh chiết khấu thanh toán sớm 100%
- **Source Ref:** `POL-001 / POL-CRM-01_v2.1_draft.docx (QBG-DR-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:early_payment_discount`
- **Audience (SEC 01):** `policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Bản dự thảo (trạng thái draft — CHƯA được phê duyệt và CẤM dùng làm hướng dẫn hiện hành theo KNW 03/ANS 02): Đề xuất thử nghiệm cộng thêm 1,5% chiết khấu thanh toán trả trước 100% trong 3 ngày làm việc. Bộ lọc Pre-retrieval phải chặn 100% bản ghi trạng thái draft. [Dữ liệu giả lập phục vụ đồ án]

### PAS-047 | DOC001-VER-001-REV | Dự thảo Phụ lục C (Trang 1) — [owner_reviewed]
- **Title:** [Owner Reviewed] Bản rà soát bổ sung quy tắc báo giá phụ tùng thay thế
- **Source Ref:** `POL-001 / POL-CRM-01_v1.1_owner_reviewed.docx (QBG-RV-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:spare_parts;transaction_scope:spare_parts_quotation`
- **Audience (SEC 01):** `policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Trạng thái owner_reviewed (Chủ sở hữu chính sách đã rà soát sơ bộ nhưng CHƯA ký duyệt chính thức và CHƯA phát hành theo KNW 03): Quy tắc báo giá phụ tùng thay thế lẻ dưới 20 triệu VND áp dụng bảng giá phụ tùng tiêu chuẩn. Phải bị bộ lọc 7 trạng thái chặn hoàn toàn khỏi hướng dẫn hiện hành. [Dữ liệu giả lập phục vụ đồ án]

### PAS-048 | DOC001-VER-001-APP | Phụ lục D (Chờ phát hành) (Trang 1) — [approved]
- **Title:** [Approved] Bản đã duyệt chờ lên lịch phát hành chiết khấu gói bảo trì
- **Source Ref:** `POL-001 / POL-CRM-01_v1.2_approved.docx (QBG-AP-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:mv_inverter;transaction_scope:maintenance_bundle`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Trạng thái approved (đã có chữ ký duyệt nhưng CHƯA lên lịch hiệu lực và CHƯA ở trạng thái effective theo KNW 03): Gói dịch vụ bảo trì định kỳ đi kèm báo giá biến tần áp dụng biểu phí dịch vụ năm 2027. Bộ lọc Pre-retrieval không được dùng trạng thái approved làm căn cứ hiện hành. [Dữ liệu giả lập phục vụ đồ án]

### PAS-049 | DOC001-VER-001-WD | Thông báo khuyến mãi (Đã thu hồi) (Trang 1) — [withdrawn]
- **Title:** [Đã thu hồi - Withdrawn] Chương trình khuyến mãi chiết khấu nhanh Q3/2026
- **Source Ref:** `POL-001 / POL-CRM-01_promo_withdrawn.docx (QBG-WD-01)`
- **Scope (6-dim DAT 04):** `company:SN;branch:all;role:sales;customer_group:b2b;product:industrial;transaction_scope:promo_discount`
- **Audience (SEC 01):** `reader,policy_owner,steward,administrator`
- **Essential Attachments (DAT 08):** `true`

Trạng thái withdrawn (ĐÃ THU HỒI KHẨN CẤP theo SEC 05 / KNW 04 — CẤM phục vụ hoặc tái sử dụng từ cache): Chương trình cho phép Sales Staff tự duyệt chiết khấu 8% trong tuần cao điểm đã bị đình chỉ ngay lập tức do sai lệch biên lợi nhuận. Mọi truy vấn liên quan phải chặn fail-closed và đánh dấu stale các câu trả lời trước đó. [Dữ liệu giả lập phục vụ đồ án]

