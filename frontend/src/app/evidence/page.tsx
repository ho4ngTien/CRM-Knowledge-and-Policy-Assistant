import Link from "next/link";

export default function EvidenceViewerPage() {
  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: "2rem", fontFamily: "sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Xem Bằng chứng &amp; Lịch sử Phiên bản</h1>
        <Link href="/chat">Quay lại Workspace</Link>
      </header>
      <p>
        Mỗi URL tài liệu/đoạn trích dẫn đều thực thi kiểm tra quyền <code>audience</code> và trạng
        thái <code>effective / superseded / withdrawn</code> trực tiếp qua{" "}
        <code>GET /api/v1/knowledge/passages/&#123;passage_id&#125;</code>.
      </p>
      <section style={{ padding: "1rem", border: "1px solid #cbd5e1", borderRadius: 6 }}>
        <h2>Chuỗi kiểm chứng bắt buộc</h2>
        <ul>
          <li>Tài liệu bị thu hồi (`withdrawn`) bị chặn fail-closed với HTTP 409.</li>
          <li>Bản nháp (`draft`) hoặc cách ly (`quarantined`) không hiển thị cho vai trò `reader`.</li>
          <li>Phiên bản cũ (`superseded`) chỉ mở trong chế độ lịch sử kèm nhãn cảnh báo rõ ràng.</li>
        </ul>
      </section>
    </main>
  );
}
