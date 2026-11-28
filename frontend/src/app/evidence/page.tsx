"use client";

/**
 * CKPA-91 · G2-AC01 · feat/CKPA-91-answer-pkg-o1-flag-fields
 * Evidence Viewer — Tải PassageSummary + DocumentLineageResponse + SnapshotAge thật từ API
 *
 * Assignee: [S3] Phạm Lương Yến Nhi
 */

import Link from "next/link";
import { useEffect, useState } from "react";

import { getDocumentLineage, getPassageById, getSnapshotAge } from "../../lib/api";
import type {
  DocumentLineageResponse,
  PassageSummary,
  PolicyLifecycleStatus,
  SnapshotAgeResponse,
} from "../../types/answer";

const STATUS_LABELS: Record<PolicyLifecycleStatus, { label: string; color: string }> = {
  draft:              { label: "Nháp",         color: "#64748b" },
  owner_reviewed:     { label: "Owner đã xem", color: "#7c3aed" },
  approved:           { label: "Đã phê duyệt", color: "#0369a1" },
  scheduled:          { label: "Hẹn giờ",      color: "#b45309" },
  effective:          { label: "Hiệu lực",     color: "#166534" },
  superseded:         { label: "Đã thay thế",  color: "#78350f" },
  withdrawn:          { label: "Đã thu hồi",   color: "#991b1b" },
  feedback_candidate: { label: "Chờ Steward",  color: "#7c3aed" },
  quarantined:        { label: "Cách ly",      color: "#7f1d1d" },
};

const ACTIVE_VIEW_REFRESH_INTERVAL_MS = 60_000;

function StatusTag({ status }: { status: PolicyLifecycleStatus }) {
  const cfg = STATUS_LABELS[status] ?? { label: status, color: "#334155" };
  return (
    <span
      style={{
        display: "inline-block",
        padding: "0.15rem 0.6rem",
        borderRadius: "9999px",
        fontSize: "0.75rem",
        fontWeight: 700,
        backgroundColor: `${cfg.color}22`,
        color: cfg.color,
      }}
    >
      {cfg.label}
    </span>
  );
}

export default function EvidenceViewerPage() {
  const [passageId, setPassageId] = useState<string | null>(null);
  const [allowHistorical, setAllowHistorical] = useState(false);
  const [passage, setPassage] = useState<PassageSummary | null>(null);
  const [lineage, setLineage] = useState<DocumentLineageResponse | null>(null);
  const [snapshotAge, setSnapshotAge] = useState<SnapshotAgeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    setPassageId(params.get("passage_id"));
    setAllowHistorical(params.get("allow_historical") === "true");
  }, []);

  useEffect(() => {
    if (!passageId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([getPassageById(passageId, allowHistorical), getSnapshotAge().catch(() => null)])
      .then(async ([p, snap]) => {
        if (cancelled) return;
        setPassage(p);
        setSnapshotAge(snap);
        try {
          const lin = await getDocumentLineage(p.document_id);
          if (!cancelled) setLineage(lin);
        } catch {
          if (!cancelled) setLineage(null);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setPassage(null);
          setLineage(null);
          setError(err instanceof Error ? err.message : "Không thể tải trích đoạn.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [passageId, allowHistorical]);

  useEffect(() => {
    if (!passageId) return;
    let cancelled = false;
    const refreshPassage = async () => {
      try {
        const latest = await getPassageById(passageId, allowHistorical);
        if (!cancelled) {
          setPassage(latest);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setPassage(null);
          setError(err instanceof Error ? err.message : "Không thể xác minh nguồn hiện tại.");
        }
      }
    };
    const onFocus = () => void refreshPassage();
    const intervalId = window.setInterval(
      () => void refreshPassage(),
      ACTIVE_VIEW_REFRESH_INTERVAL_MS
    );
    window.addEventListener("focus", onFocus);
    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
      window.removeEventListener("focus", onFocus);
    };
  }, [passageId, allowHistorical]);

  return (
    <main
      style={{
        maxWidth: 920,
        margin: "0 auto",
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.25rem",
        }}
      >
        <h1 style={{ fontSize: "1.15rem", margin: 0 }}>Xem Bằng chứng &amp; Lịch sử Phiên bản</h1>
        <Link href="/chat" style={{ fontSize: "0.82rem" }}>
          ← Quay lại Workspace
        </Link>
      </header>

      <p
        style={{
          fontSize: "0.78rem",
          padding: "0.4rem 0.75rem",
          backgroundColor: "#fffbeb",
          border: "1px solid #fde68a",
          borderRadius: 4,
          color: "#78350f",
          margin: "0 0 1rem",
        }}
      >
        <strong>KNW 02:</strong> Kiểm tra quyền <code>audience</code> và trạng thái{" "}
        <code>effective / superseded / withdrawn</code> trực tiếp qua{" "}
        <code>GET /api/v1/knowledge/passages/{"{passage_id}"}</code>. Trang tự kiểm tra lại khi focus
        và mỗi 60 giây; thay đổi có thể trễ tối đa một chu kỳ polling.
      </p>

      {!passageId && (
        <div
          style={{
            padding: "1.5rem",
            border: "1px dashed #cbd5e1",
            borderRadius: 8,
            color: "#94a3b8",
            textAlign: "center",
          }}
        >
          Không có <code>passage_id</code> trong URL. Mở từ nút &ldquo;Mở Evidence Viewer&rdquo;
          trong trang Hỏi đáp.
        </div>
      )}

      {passageId && loading && (
        <p style={{ color: "#64748b" }}>
          Đang tải trích đoạn <code>{passageId}</code>…
        </p>
      )}

      {error && (
        <div
          role="alert"
          style={{
            padding: "0.75rem",
            backgroundColor: "#fee2e2",
            color: "#7f1d1d",
            borderRadius: 6,
            marginBottom: "1rem",
          }}
        >
          <strong>Fail-Closed:</strong> {error}
        </div>
      )}

      {passage && (
        <>
          {(passage.status === "withdrawn" || passage.status === "superseded" || passage.is_tombstoned) && (
            <div
              role="alert"
              style={{
                padding: "0.75rem 1rem",
                backgroundColor: "#fee2e2",
                border: "1px solid #fca5a5",
                borderRadius: 6,
                color: "#7f1d1d",
                fontWeight: 700,
                marginBottom: "1rem",
              }}
            >
              Tài liệu này{" "}
              {passage.status === "withdrawn" || passage.is_tombstoned
                ? "đã bị thu hồi / xóa (withdrawn)"
                : "đã bị thay thế (superseded)"}
              . Tuyệt đối không dùng làm căn cứ cho giao dịch hiện tại.
            </div>
          )}

          <section style={SECTION_STYLE}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                flexWrap: "wrap",
                gap: "0.5rem",
              }}
            >
              <h2 style={{ ...H2_STYLE, margin: 0 }}>{passage.title}</h2>
              <StatusTag status={passage.status} />
            </div>

            <dl style={DL_STYLE}>
              <dt>Passage ID</dt>
              <dd>
                <code>{passage.passage_id}</code>
              </dd>
              <dt>Mã tài liệu / Phiên bản</dt>
              <dd>
                <code>{passage.document_id}</code> · <code>{passage.document_version_id}</code>
              </dd>
              <dt>Điều khoản / Trang</dt>
              <dd>
                {passage.clause_ref} (trang {passage.page_number})
              </dd>
              <dt>Hiệu lực từ / đến</dt>
              <dd>
                {passage.effective_from} → {passage.effective_to ?? "Không giới hạn"}
              </dd>
              <dt>Đối tượng (audience)</dt>
              <dd>{passage.audience.join(", ") || "—"}</dd>
              <dt>Phụ lục thiết yếu (DAT 08)</dt>
              <dd>{passage.has_essential_attachments ? "Đầy đủ" : "Thiếu phụ lục/chú thích"}</dd>
              <dt>Nguồn gốc (source_ref)</dt>
              <dd>
                <code>{passage.source_ref}</code>
              </dd>
              {lineage && (
                <>
                  <dt>Chủ sở hữu / Lớp thẩm quyền</dt>
                  <dd>
                    {lineage.owner} · <code>{lineage.authority_tier}</code> ({lineage.policy_family})
                  </dd>
                </>
              )}
              {snapshotAge?.snapshot_age_hours != null && (
                <>
                  <dt>Snapshot Age</dt>
                  <dd style={{ color: snapshotAge.is_stale ? "#991b1b" : "#166534" }}>
                    {snapshotAge.snapshot_age_hours} giờ
                    {snapshotAge.is_stale && " (Cảnh báo cũ)"}
                  </dd>
                </>
              )}
            </dl>
          </section>

          <section style={SECTION_STYLE}>
            <h2 style={H2_STYLE}>Nội dung trích đoạn</h2>
            <blockquote
              style={{
                margin: 0,
                padding: "0.75rem 1rem",
                borderLeft: "4px solid #3b82f6",
                backgroundColor: "#eff6ff",
                whiteSpace: "pre-wrap",
                lineHeight: 1.75,
                fontSize: "0.9rem",
              }}
            >
              {passage.content}
            </blockquote>
          </section>

          {lineage && lineage.versions.length > 0 && (
            <section style={SECTION_STYLE}>
              <h2 style={H2_STYLE}>Lịch sử Phiên bản (Lineage)</h2>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem" }}>
                <thead>
                  <tr style={{ backgroundColor: "#f1f5f9" }}>
                    {["Mã phiên bản", "Trạng thái", "Hiệu lực từ", "Hiệu lực đến", "Ghi nhận", "Thay thế"].map(
                      (h) => (
                        <th key={h} style={TH_STYLE}>
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody>
                  {lineage.versions.map((entry) => (
                    <tr
                      key={entry.document_version_id}
                      style={{
                        backgroundColor:
                          entry.document_version_id === passage.document_version_id
                            ? "#f0fdf4"
                            : "transparent",
                      }}
                    >
                      <td style={TD_STYLE}>
                        <code style={{ fontSize: "0.76rem" }}>{entry.document_version_id}</code>
                        {entry.document_version_id === passage.document_version_id && (
                          <span style={{ marginLeft: "0.4rem", fontSize: "0.7rem", color: "#166534" }}>
                            (hiện tại)
                          </span>
                        )}
                      </td>
                      <td style={TD_STYLE}>
                        <StatusTag status={entry.status} />
                      </td>
                      <td style={TD_STYLE}>{entry.effective_from}</td>
                      <td style={TD_STYLE}>{entry.effective_to ?? "—"}</td>
                      <td style={TD_STYLE}>{entry.recorded_at}</td>
                      <td style={TD_STYLE}>
                        {entry.supersedes ? (
                          <code style={{ fontSize: "0.74rem" }}>{entry.supersedes}</code>
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}
        </>
      )}
    </main>
  );
}

const SECTION_STYLE: React.CSSProperties = {
  padding: "1rem",
  border: "1px solid #e2e8f0",
  borderRadius: 8,
  marginBottom: "1rem",
  backgroundColor: "#fff",
};

const H2_STYLE: React.CSSProperties = {
  fontSize: "0.95rem",
  fontWeight: 700,
  color: "#1e293b",
  borderBottom: "1px solid #e2e8f0",
  paddingBottom: "0.4rem",
  margin: "0 0 0.5rem",
};

const DL_STYLE: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "auto 1fr",
  gap: "0.25rem 0.75rem",
  margin: 0,
  fontSize: "0.83rem",
};

const TH_STYLE: React.CSSProperties = {
  padding: "0.4rem 0.5rem",
  textAlign: "left",
  fontWeight: 600,
  borderBottom: "2px solid #cbd5e1",
  whiteSpace: "nowrap",
};

const TD_STYLE: React.CSSProperties = {
  padding: "0.4rem 0.5rem",
  borderBottom: "1px solid #e2e8f0",
  verticalAlign: "top",
};
