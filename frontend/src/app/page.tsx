import Link from "next/link";

export default function HomePage() {
  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>SongNhat CRM Knowledge &amp; Policy Assistant (CKPA)</h1>
      <p>
        Hệ thống trợ lý tra cứu chính sách CRM nội bộ dựa trên nguồn đã phê duyệt (Base Scope).
        Mọi hướng dẫn đều qua kiểm chứng trích dẫn và trường trọng yếu trước khi hiển thị.
      </p>

      <div
        role="note"
        style={{
          padding: "1rem",
          border: "1px solid #d97706",
          backgroundColor: "#fffbeb",
          borderRadius: 6,
          margin: "1.25rem 0",
        }}
      >
        <strong>Cảnh báo sử dụng nội bộ:</strong> Hướng dẫn làm việc nội bộ — nhân viên phải kiểm
        tra hoàn cảnh, nguồn hiện hành và thẩm quyền trước khi hành động; không thay thế phê duyệt
        hay thực thi. Không nhập SĐT, email hoặc CCCD/MST khách hàng vào ô câu hỏi (`SEC 02`).
      </div>

      <nav style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: "1rem" }}>
        <Link href="/chat" style={{ padding: "1rem", border: "1px solid #cbd5e1", borderRadius: 6 }}>
          <strong>/chat — Split-Screen Workspace</strong>
          <div>Hỏi đáp chính sách (trái) &amp; Bằng chứng, Trường trọng yếu (phải)</div>
        </Link>
        <Link
          href="/evidence"
          style={{ padding: "1rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
        >
          <strong>/evidence — Source &amp; Version Viewer</strong>
          <div>Xem nguyên văn điều khoản gốc, lịch sử phiên bản và quyền audience</div>
        </Link>
        <Link
          href="/referrals"
          style={{ padding: "1rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
        >
          <strong>/referrals — Local Referral &amp; Candidates</strong>
          <div>Theo dõi chuyển xử lý chủ sở hữu chính sách &amp; phản hồi 5 lý do (KNW 07)</div>
        </Link>
        <Link
          href="/admin"
          style={{ padding: "1rem", border: "1px solid #cbd5e1", borderRadius: 6 }}
        >
          <strong>/admin — Governance, Withdrawal &amp; Cost Meter</strong>
          <div>Nhập 2 CSV UTF-8, duyệt 7 trạng thái, rút khẩn cấp &le;5 phút, xuất mở (OPS 08)</div>
        </Link>
      </nav>

      <section style={{ marginTop: "2rem", color: "#475569", fontSize: "0.9rem" }}>
        <p>
          Phương án dự phòng thủ công (`OPS 05`): Khi hệ thống tạm khóa hoặc bảo trì, nhân viên tra
          cứu trực tiếp gói 2 tệp CSV đã phê duyệt tại kho tài liệu nội bộ giờ hành chính VN (08:00
          &ndash; 17:00).
        </p>
      </section>
    </main>
  );
}
