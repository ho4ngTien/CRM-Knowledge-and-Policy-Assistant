"use client";

import Link from "next/link";
import { useState } from "react";

import { getAdminOpsSummary, withdrawPolicyImmediately } from "../../lib/api";
import type { AdminOpsSummary } from "../../types/answer";

export default function AdminConsolePage() {
  const [summary, setSummary] = useState<AdminOpsSummary | null>(null);
  const [withdrawVersionId, setWithdrawVersionId] = useState("");
  const [withdrawReason, setWithdrawReason] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function loadSummary() {
    try {
      const data = await getAdminOpsSummary();
      setSummary(data);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Yêu cầu quyền Steward/Owner/Admin.");
    }
  }

  async function handleInstantWithdraw() {
    if (!withdrawVersionId.trim() || !withdrawReason.trim()) return;
    try {
      const result = await withdrawPolicyImmediately(withdrawVersionId, withdrawReason);
      setMessage(
        `Đã thu hồi ngay ${withdrawVersionId} (trạng thái: ${result.status}, ` +
          `đánh dấu stale: ${result.stale_answers_marked}).`
      );
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Không thể thu hồi chính sách.");
    }
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem", fontFamily: "sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Quản trị Tri thức, Vòng đời &amp; Vận hành (/admin)</h1>
        <Link href="/">Trang chủ</Link>
      </header>

      {message && (
        <p role="status" style={{ padding: "0.75rem", backgroundColor: "#f1f5f9" }}>
          {message}
        </p>
      )}

      <section style={{ marginTop: "1rem", padding: "1rem", border: "1px solid #cbd5e1" }}>
        <h2>Thông số giới hạn Base Scope</h2>
        <button type="button" onClick={loadSummary}>
          Tải cấu hình vận hành hiện tại
        </button>
        {summary && (
          <ul>
            <li>Timezone hiệu lực: {summary.timezone}</li>
            <li>Streaming pre-verification: {summary.answer_streaming_enabled ? "ON" : "OFF (KNW 04)"}</li>
            <li>
              Corpus tối đa: {summary.corpus_max_documents} tài liệu / {summary.corpus_max_passages}{" "}
              đoạn / {summary.corpus_max_critical_fields} critical fields
            </li>
            <li>
              Pilot giới hạn: {summary.pilot_max_named_users} người dùng,{" "}
              {summary.pilot_max_concurrent_sessions} phiên đồng thời
            </li>
            <li>Ngưỡng cảnh báo Snapshot Age: &gt; {summary.snapshot_staleness_threshold_hours}h</li>
          </ul>
        )}
      </section>

      <section style={{ marginTop: "1.25rem", padding: "1rem", border: "1px solid #ef4444" }}>
        <h2>Thu hồi chính sách khẩn cấp (Instant Withdrawal &le; 5 phút)</h2>
        <div style={{ display: "grid", gap: "0.5rem" }}>
          <input
            type="text"
            placeholder="Policy Version ID (VD: PVER-001)"
            value={withdrawVersionId}
            onChange={(e) => setWithdrawVersionId(e.target.value)}
          />
          <input
            type="text"
            placeholder="Lý do thu hồi bắt buộc..."
            value={withdrawReason}
            onChange={(e) => setWithdrawReason(e.target.value)}
          />
          <button type="button" onClick={handleInstantWithdraw}>
            Thu hồi ngay &amp; Xóa cache Redis (&le; 300s)
          </button>
        </div>
      </section>
    </main>
  );
}
