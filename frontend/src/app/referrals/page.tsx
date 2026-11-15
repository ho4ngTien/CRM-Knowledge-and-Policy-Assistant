"use client";

import Link from "next/link";
import { useState } from "react";

import { listLocalReferrals } from "../../lib/api";
import type { ReferralItem } from "../../types/answer";

export default function ReferralsTrackerPage() {
  const [referrals, setReferrals] = useState<ReferralItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function handleRefresh() {
    setError(null);
    try {
      const items = await listLocalReferrals();
      setReferrals(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Không thể tải danh sách chuyển xử lý.");
    }
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: "2rem", fontFamily: "sans-serif" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Chuyển xử lý Nội bộ &amp; Knowledge Candidates (/referrals)</h1>
        <Link href="/chat">Quay lại Workspace</Link>
      </header>
      <p>
        Quản lý vòng đời phiếu chuyển tuyến (<code>referred &rarr; owner_responded &rarr; closed</code>
        ) và hàng đợi <code>feedback_candidate</code> do Steward rà soát (không tự động áp dụng vào
        nguồn chính sách hiệu lực — KNW 06).
      </p>

      <button type="button" onClick={handleRefresh}>
        Tải danh sách Local Referrals
      </button>

      {error && <p style={{ color: "#991b1b" }}>{error}</p>}

      <ul style={{ marginTop: "1rem" }}>
        {referrals.map((ref) => (
          <li key={ref.id} style={{ marginBottom: "0.75rem" }}>
            <strong>{ref.id}</strong> [{ref.status}] &mdash; {ref.target_owner} ({ref.policy_family}
            ): {ref.question_summary}
          </li>
        ))}
      </ul>
    </main>
  );
}
