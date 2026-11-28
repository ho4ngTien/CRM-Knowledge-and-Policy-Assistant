"use client";

/**
 * CKPA-91 · G2-AC01 · feat/CKPA-91-answer-pkg-o1-flag-fields
 * AnswerPackageRenderer — Hiển thị đầy đủ 7 phần Answer Package & Deterministic Critical Fields
 *
 * Tiêu chí chấp nhận G2-AC01:
 *   ✓ Câu hỏi gốc
 *   ✓ Bản ghi O1 đã chọn (nếu mua/bật O1; khi O1 OFF hiển thị trạng thái khóa Base Scope)
 *   ✓ Trạng thái (Answered / Answered with conditions / Hold and refer / Stale / Refused)
 *   ✓ Ngày hiệu lực chi phối (Asia/Ho_Chi_Minh) & 6 chiều phạm vi khớp
 *   ✓ Thông tin còn thiếu (missing facts), tuyến chuyển xử lý (referral route), uncertainty
 *   ✓ Nút gắn cờ KNW 01 (đủ 5 mã FeedbackReason theo Backend enum)
 *   ✓ Giải thích tiếng Việt (mục tiêu 100–250 từ)
 *   ✓ Hộp nguyên văn trích dẫn (mã, phiên bản, ngày hiệu lực, chủ sở hữu, link gốc)
 *   ✓ Bảng trường trọng yếu từ deterministic code (<= 8 đoạn / <= 6.000 ký tự Unicode, không cắt cụt ngầm)
 *
 * RFP: ANS 01, ANS 03, ANS 04, KNW 01, KNW 02, Mục 2, VN 01, VN 03
 * Assignee: [S3] Phạm Lương Yến Nhi
 */

import Link from "next/link";
import { useState } from "react";

import type {
  AnswerCitation,
  AnswerPackage,
  CriticalFieldItem,
  CustomerContextO1,
  FeedbackReason,
} from "../types/answer";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** 5 exact Backend FeedbackReason values (KNW 01 / KNW 07). */
const KNW01_FLAG_OPTIONS: { value: FeedbackReason; label: string }[] = [
  { value: "missing_source",    label: "Thiếu nguồn (missing source)" },
  { value: "outdated_rule",     label: "Quy định lỗi thời (obsolete rule)" },
  { value: "wrong_scope",       label: "Sai phạm vi (wrong scope)" },
  { value: "missing_exception", label: "Thiếu ngoại lệ (omitted exception)" },
  { value: "rejected",          label: "Từ chối (rejection)" },
];

const SCOPE_DIMENSION_LABELS: { key: string; label: string }[] = [
  { key: "company",           label: "Công ty (company)" },
  { key: "branch",            label: "Chi nhánh (branch)" },
  { key: "role",              label: "Vai trò (role)" },
  { key: "customer_category", label: "Nhóm KH (customer_category)" },
  { key: "product",           label: "Sản phẩm (product)" },
  { key: "transaction_scope", label: "Phạm vi GD (transaction_scope)" },
];

const MAX_CITATIONS = 8;
const MAX_CRITICAL_FIELDS = 8;
const MAX_FIELD_CHARS = 6000;

// ---------------------------------------------------------------------------
// Helpers (deterministic, zero silent truncation)
// ---------------------------------------------------------------------------

function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

function parseScopeDimensions(pkg: AnswerPackage): Record<string, string> {
  if (pkg.scope_matched_dimensions && Object.keys(pkg.scope_matched_dimensions).length > 0) {
    return pkg.scope_matched_dimensions;
  }
  const result: Record<string, string> = {};
  for (const d of SCOPE_DIMENSION_LABELS) {
    result[d.key] = "unspecified";
  }
  for (const part of pkg.scope.split(";")) {
    const trimmed = part.trim();
    if (!trimmed) continue;
    const sepIdx = trimmed.includes(":") ? trimmed.indexOf(":") : trimmed.indexOf("=");
    if (sepIdx <= 0) continue;
    let key = trimmed.slice(0, sepIdx).trim().toLowerCase();
    const val = trimmed.slice(sepIdx + 1).trim();
    if (key === "customer_group") key = "customer_category";
    if (key in result && val) {
      result[key] = val;
    }
  }
  return result;
}

type DisplayStatusKey =
  | "answered"
  | "answered_with_conditions"
  | "hold_and_refer"
  | "hold"
  | "clarification_required"
  | "referred"
  | "stale"
  | "refused_out_of_scope";

function resolveDisplayStatus(pkg: AnswerPackage): DisplayStatusKey {
  if (pkg.status === "stale") return "stale";
  if (pkg.status === "refused_out_of_scope") return "refused_out_of_scope";
  if (pkg.status === "answered_with_conditions") return "answered_with_conditions";
  if (pkg.status === "answered") {
    const hasConditions =
      pkg.is_historical ||
      pkg.is_future_preview ||
      Boolean(pkg.uncertainty_note) ||
      pkg.missing_facts.length > 0 ||
      pkg.critical_fields.some((cf) => Boolean(cf.exception_condition));
    return hasConditions ? "answered_with_conditions" : "answered";
  }
  if (pkg.status === "hold_and_refer") return "hold_and_refer";
  if ((pkg.status === "hold" || pkg.status === "referred") && pkg.referral_target) {
    return "hold_and_refer";
  }
  return pkg.status;
}

function criticalFieldUnicodeLength(cf: CriticalFieldItem): number {
  return [
    cf.field_name,
    cf.value,
    cf.approval_role,
    cf.time_limit ?? "",
    cf.exception_condition ?? "",
    cf.source_clause,
    ...cf.required_documents,
  ]
    .join(" ")
    .length;
}

// ---------------------------------------------------------------------------
// Status Badge
// ---------------------------------------------------------------------------
function StatusBadge({ pkg }: { pkg: AnswerPackage }) {
  const displayKey = resolveDisplayStatus(pkg);
  const MAP: Record<DisplayStatusKey, { label: string; bg: string; color: string }> = {
    answered:                 { label: "Answered (Đã trả lời)",                        bg: "#dcfce7", color: "#166534" },
    answered_with_conditions: { label: "Answered with conditions (Trả lời có điều kiện)", bg: "#fef9c3", color: "#854d0e" },
    hold_and_refer:           { label: "Hold and refer (Tạm giữ & Chuyển xử lý)",      bg: "#fee2e2", color: "#991b1b" },
    hold:                     { label: "Hold (Tạm giữ)",                               bg: "#fef3c7", color: "#92400e" },
    clarification_required:   { label: "Cần làm rõ thêm",                              bg: "#ede9fe", color: "#5b21b6" },
    referred:                 { label: "Đã chuyển xử lý",                              bg: "#e0f2fe", color: "#0369a1" },
    stale:                    { label: "ĐÃ THU HỒI — STALE",                           bg: "#fee2e2", color: "#7f1d1d" },
    refused_out_of_scope:     { label: "Ngoài phạm vi (ANS 07)",                       bg: "#f1f5f9", color: "#475569" },
  };
  const cfg = MAP[displayKey];
  return (
    <span
      data-testid="answer-status-badge"
      style={{
        display: "inline-block",
        padding: "0.25rem 0.75rem",
        borderRadius: "9999px",
        fontSize: "0.85rem",
        fontWeight: 700,
        backgroundColor: cfg.bg,
        color: cfg.color,
      }}
    >
      {cfg.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Part 1: Header (câu hỏi gốc + status + task_id)
// ---------------------------------------------------------------------------
function Part1Header({ pkg }: { pkg: AnswerPackage }) {
  return (
    <section style={SECTION_STYLE}>
      <h3 style={SECTION_TITLE_STYLE}>Phần 1 · Câu hỏi gốc &amp; Trạng thái</h3>
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
        <StatusBadge pkg={pkg} />
        <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
          Task: <code>{pkg.task_id}</code> · Gói: <code>{pkg.answer_id}</code> · LLM calls:{" "}
          <code>{pkg.llm_calls_used}/2</code>
        </span>
      </div>
      <blockquote style={BLOCKQUOTE_STYLE}>{pkg.original_question}</blockquote>

      {pkg.pii_warning && (
        <div role="alert" style={ALERT_STYLE("warning")}>
          <strong>Cảnh báo PII (SEC 02):</strong> {pkg.pii_warning}
        </div>
      )}

      {pkg.status === "stale" && (
        <div role="alert" style={ALERT_STYLE("danger")}>
          <strong>CẢNH BÁO STALE:</strong> Chính sách liên quan vừa bị thu hồi. Tuyệt đối
          không dùng hướng dẫn này; hãy chạy lại truy vấn.
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Option O1 Panel (CustomerContextO1 khi mua/bật; khóa rõ khi Base Scope OFF)
// ---------------------------------------------------------------------------
function O1RecordPanel({
  o1Enabled,
  o1Record,
}: {
  o1Enabled: boolean;
  o1Record?: CustomerContextO1 | null;
}) {
  if (!o1Enabled) {
    return (
      <section
        data-testid="o1-panel-locked"
        style={{
          ...SECTION_STYLE,
          backgroundColor: "#f8fafc",
          border: "1px dashed #cbd5e1",
          padding: "0.65rem 1rem",
        }}
      >
        <div style={{ fontSize: "0.82rem", color: "#475569" }}>
          <strong>Tùy chọn O1 (Selected CRM Context):</strong>{" "}
          <span style={BADGE_STYLE("#e2e8f0", "#334155")}>OFF — Base Scope</span>{" "}
          Không truy cập hồ sơ khách hàng (0 bản ghi O1).
        </div>
      </section>
    );
  }

  return (
    <section
      data-testid="o1-panel-active"
      style={{
        ...SECTION_STYLE,
        backgroundColor: "#f0fdf4",
        border: "1px solid #86efac",
      }}
    >
      <h3 style={{ ...SECTION_TITLE_STYLE, color: "#166534" }}>
        Bản ghi O1 đã chọn (Selected CRM Context · tối đa 1 bản ghi)
      </h3>
      {!o1Record ? (
        <p style={{ margin: 0, fontSize: "0.84rem", color: "#475569" }}>
          O1 đã bật nhưng truy vấn này không đính kèm bản ghi khách hàng chọn lọc.
        </p>
      ) : (
        <dl style={DL_STYLE}>
          <dt>Mã khách hàng (customer_id)</dt>
          <dd>
            <code>{o1Record.customer_id}</code>
          </dd>
          <dt>Phân hạng KH (customer_tier)</dt>
          <dd>{o1Record.customer_tier}</dd>
          <dt>Mã ngành (industry_code)</dt>
          <dd>{o1Record.industry_code ?? "—"}</dd>
          <dt>Chi nhánh phụ trách (assigned_branch)</dt>
          <dd>{o1Record.assigned_branch ?? "—"}</dd>
          <dt>Pháp nhân (assigned_company)</dt>
          <dd>{o1Record.assigned_company ?? "—"}</dd>
        </dl>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Part 2: Ngày hiệu lực chi phối & 6 chiều phạm vi khớp
// ---------------------------------------------------------------------------
function Part2Scope({ pkg }: { pkg: AnswerPackage }) {
  const dims = parseScopeDimensions(pkg);

  return (
    <section style={SECTION_STYLE}>
      <h3 style={SECTION_TITLE_STYLE}>Phần 2 · Ngày hiệu lực chi phối &amp; 6 chiều phạm vi khớp</h3>
      <dl style={DL_STYLE}>
        <dt>Ngày hiệu lực chi phối</dt>
        <dd>
          <strong>{pkg.governing_date}</strong>{" "}
          <span style={{ color: "#64748b" }}>({pkg.timezone})</span>
          {pkg.is_historical && (
            <span style={BADGE_STYLE("#e0f2fe", "#0369a1")}>Hướng dẫn lịch sử</span>
          )}
          {pkg.is_future_preview && (
            <span style={BADGE_STYLE("#fef3c7", "#92400e")}>Xem trước tương lai</span>
          )}
        </dd>

        <dt>Chuỗi phạm vi gốc</dt>
        <dd>
          <code style={{ fontSize: "0.8rem" }}>{pkg.scope}</code>
        </dd>

        {pkg.snapshot_age_hours != null && (
          <>
            <dt>Snapshot Age</dt>
            <dd style={{ color: pkg.snapshot_age_hours > 25 ? "#991b1b" : "#166534" }}>
              {pkg.snapshot_age_hours} giờ
              {pkg.snapshot_age_hours > 25 && " (Cảnh báo > 25 giờ)"}
            </dd>
          </>
        )}
      </dl>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "0.45rem",
          marginTop: "0.35rem",
        }}
      >
        {SCOPE_DIMENSION_LABELS.map((dim) => {
          const val = dims[dim.key] ?? "unspecified";
          const isMatched = val !== "unspecified";
          return (
            <div
              key={dim.key}
              style={{
                padding: "0.4rem 0.6rem",
                borderRadius: 6,
                border: `1px solid ${isMatched ? "#bbf7d0" : "#fecaca"}`,
                backgroundColor: isMatched ? "#f0fdf4" : "#fef2f2",
                fontSize: "0.78rem",
              }}
            >
              <div style={{ color: "#475569", fontWeight: 600 }}>{dim.label}</div>
              <div style={{ color: isMatched ? "#166534" : "#991b1b", fontWeight: 700 }}>
                {val}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Part 3: Giải thích tiếng Việt (100–250 từ) + Nguyên văn
// ---------------------------------------------------------------------------
function Part3Guidance({ pkg }: { pkg: AnswerPackage }) {
  const wordCount =
    pkg.guidance_word_count != null && pkg.guidance_word_count > 0
      ? pkg.guidance_word_count
      : countWords(pkg.guidance_text);
  const isPositiveAnswer =
    pkg.status === "answered" || pkg.status === "answered_with_conditions";
  const inRecommendedRange = wordCount >= 100 && wordCount <= 250;

  return (
    <section style={SECTION_STYLE}>
      <h3 style={SECTION_TITLE_STYLE}>
        Phần 3 · Diễn giải tiếng Việt (mục tiêu 100–250 từ) &amp; Nguyên văn
      </h3>

      <div
        style={{
          backgroundColor: isPositiveAnswer ? "#f0fdf4" : "#fffbeb",
          border: `1px solid ${isPositiveAnswer ? "#86efac" : "#fbbf24"}`,
          borderRadius: 6,
          padding: "1rem",
          lineHeight: 1.75,
          whiteSpace: "pre-wrap",
        }}
      >
        {pkg.guidance_text}
      </div>

      <div
        data-testid="guidance-word-count"
        style={{
          fontSize: "0.78rem",
          color: inRecommendedRange || !isPositiveAnswer ? "#475569" : "#b45309",
        }}
      >
        Độ dài diễn giải: <strong>{wordCount}</strong> từ tiếng Việt (chuẩn thông thường:
        100–250 từ)
        {isPositiveAnswer && wordCount < 100 && " — Ngắn hơn 100 từ"}
        {isPositiveAnswer && wordCount > 250 && " — Vượt 250 từ"}
      </div>

      {pkg.verbatim_quotes.length > 0 && (
        <div>
          <h4 style={{ margin: "0.5rem 0 0.35rem", fontSize: "0.88rem" }}>
            Nguyên văn điều khoản tách biệt
          </h4>
          <ul style={{ paddingLeft: "1.25rem", margin: 0, display: "grid", gap: "0.5rem" }}>
            {pkg.verbatim_quotes.map((q, i) => (
              <li key={i}>
                <blockquote
                  style={{
                    margin: 0,
                    paddingLeft: "0.75rem",
                    borderLeft: "3px solid #94a3b8",
                    color: "#1e293b",
                    fontStyle: "italic",
                  }}
                >
                  {q}
                </blockquote>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Part 4: Hộp nguyên văn trích dẫn (mã, phiên bản, ngày hiệu lực, chủ sở hữu, link gốc)
// ---------------------------------------------------------------------------
function CitationCard({ cit }: { cit: AnswerCitation }) {
  return (
    <article
      style={{
        border: "1px solid #e2e8f0",
        borderRadius: 6,
        padding: "0.75rem",
        backgroundColor: "#f8fafc",
        display: "grid",
        gap: "0.35rem",
        fontSize: "0.85rem",
      }}
    >
      <div>
        <strong>{cit.title}</strong>
      </div>
      <dl style={{ ...DL_STYLE, fontSize: "0.8rem" }}>
        <dt>Mã tài liệu / đoạn</dt>
        <dd>
          <code>{cit.document_id}</code> · <code>{cit.passage_id}</code>
        </dd>
        <dt>Phiên bản</dt>
        <dd>
          <code>{cit.document_version_id}</code>
        </dd>
        <dt>Ngày hiệu lực</dt>
        <dd>{cit.effective_date ?? "Theo ngày chi phối"}</dd>
        <dt>Chủ sở hữu</dt>
        <dd>{cit.owner ?? "Policy Owner"}</dd>
        <dt>Điều khoản / Trang</dt>
        <dd>
          {cit.clause_ref} (trang {cit.page_number})
        </dd>
        <dt>Link gốc</dt>
        <dd style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <Link
            href={`/evidence?passage_id=${encodeURIComponent(cit.passage_id)}`}
            style={{ color: "#2563eb", fontWeight: 600 }}
          >
            Mở Evidence Viewer →
          </Link>
          {cit.evidence_url && (
            <code style={{ fontSize: "0.74rem", color: "#64748b" }}>{cit.evidence_url}</code>
          )}
        </dd>
      </dl>
      {cit.quoted_text && (
        <blockquote
          style={{
            margin: "0.25rem 0 0",
            padding: "0.5rem 0.75rem",
            borderLeft: "3px solid #3b82f6",
            backgroundColor: "#eff6ff",
            fontStyle: "italic",
            fontSize: "0.82rem",
          }}
        >
          {cit.quoted_text}
        </blockquote>
      )}
    </article>
  );
}

function Part4Citations({ citations }: { citations: AnswerCitation[] }) {
  const shown = citations.slice(0, MAX_CITATIONS);
  const overflow = citations.length > MAX_CITATIONS;

  return (
    <section style={SECTION_STYLE}>
      <h3 style={SECTION_TITLE_STYLE}>
        Phần 4 · Hộp nguyên văn trích dẫn ({shown.length}/{MAX_CITATIONS} đoạn tối đa)
      </h3>
      {overflow && (
        <div role="alert" style={ALERT_STYLE("warning")}>
          Số đoạn vượt giới hạn {MAX_CITATIONS} đoạn (chỉ hiển thị {MAX_CITATIONS} đoạn đầu).
        </div>
      )}
      {shown.length === 0 ? (
        <p style={{ color: "#94a3b8", margin: 0 }}>Chưa có trích dẫn được xác minh.</p>
      ) : (
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {shown.map((cit) => (
            <CitationCard key={`${cit.passage_id}-${cit.document_version_id}`} cit={cit} />
          ))}
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Part 5: Critical Fields — Deterministic (0% LLM, <= 8 / <= 6.000 Unicode chars)
// ---------------------------------------------------------------------------
function CriticalFieldRow({ cf }: { cf: CriticalFieldItem }) {
  const charCount = criticalFieldUnicodeLength(cf);
  const exceedsLimit = charCount > MAX_FIELD_CHARS;

  return (
    <tr>
      <td style={TD_STYLE}>
        <strong>{cf.field_name}</strong>
        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
          {cf.field_type} · <code>{cf.field_id}</code>
        </div>
        {exceedsLimit && (
          <div style={{ fontSize: "0.72rem", color: "#991b1b", fontWeight: 700 }}>
            ⚠ Vượt {MAX_FIELD_CHARS} ký tự Unicode ({charCount})
          </div>
        )}
      </td>
      <td style={TD_STYLE}>
        <code>
          {cf.operator} {cf.value} {cf.unit ?? ""} {cf.currency ?? ""}
        </code>
      </td>
      <td style={TD_STYLE}>{cf.approval_role}</td>
      <td style={TD_STYLE}>{cf.time_limit ?? "—"}</td>
      <td style={TD_STYLE}>
        {cf.exception_condition ? (
          <span style={{ color: "#b45309" }}>{cf.exception_condition}</span>
        ) : (
          "—"
        )}
      </td>
      <td style={TD_STYLE}>
        {cf.required_documents.length > 0 ? cf.required_documents.join(", ") : "—"}
      </td>
      <td style={TD_STYLE}>
        <code style={{ fontSize: "0.75rem" }}>{cf.source_clause}</code>
      </td>
    </tr>
  );
}

function Part5CriticalFields({
  fields,
  capWarning,
}: {
  fields: CriticalFieldItem[];
  capWarning?: string | null;
}) {
  const shown = fields.slice(0, MAX_CRITICAL_FIELDS);
  const overflow = fields.length > MAX_CRITICAL_FIELDS;

  return (
    <section style={SECTION_STYLE}>
      <h3 style={SECTION_TITLE_STYLE}>
        Phần 5 · Bảng Trường Trọng yếu — Deterministic Code ({shown.length}/
        {MAX_CRITICAL_FIELDS} mục tối đa)
      </h3>
      <p style={{ fontSize: "0.78rem", color: "#64748b", margin: 0 }}>
        100% trường số học, toán tử &amp; phê duyệt kết xuất trực tiếp từ code xác định (0%
        LLM; giới hạn ≤{MAX_CRITICAL_FIELDS} đoạn / ≤{MAX_FIELD_CHARS.toLocaleString()} ký tự
        Unicode mỗi mục nhập, không cắt ngắn âm thầm).
      </p>
      {(capWarning || overflow) && (
        <div role="alert" style={ALERT_STYLE("warning")}>
          {capWarning ?? `Số trường trọng yếu (${fields.length}) vượt giới hạn ${MAX_CRITICAL_FIELDS}.`}
        </div>
      )}
      {shown.length === 0 ? (
        <p style={{ color: "#94a3b8", margin: 0 }}>
          Không có trường trọng yếu áp dụng cho phạm vi này.
        </p>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem" }}>
            <thead>
              <tr style={{ backgroundColor: "#f1f5f9" }}>
                {[
                  "Trường (Loại)",
                  "Toán tử · Giá trị · Đơn vị",
                  "Thẩm quyền duyệt",
                  "Thời hạn",
                  "Điều kiện ngoại lệ",
                  "Hồ sơ bắt buộc",
                  "Điều khoản nguồn",
                ].map((h) => (
                  <th key={h} style={TH_STYLE}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {shown.map((cf) => (
                <CriticalFieldRow key={cf.field_id} cf={cf} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Part 6: Missing Facts + Referral Route + Hold Reason + Uncertainty
// ---------------------------------------------------------------------------
function Part6MissingAndRouting({ pkg }: { pkg: AnswerPackage }) {
  return (
    <section style={SECTION_STYLE}>
      <h3 style={SECTION_TITLE_STYLE}>
        Phần 6 · Thông tin còn thiếu, Tuyến chuyển xử lý &amp; Độ không chắc chắn
      </h3>

      <div>
        <strong style={{ fontSize: "0.84rem", color: "#b45309" }}>
          Thông tin còn thiếu (Missing Facts):
        </strong>
        {pkg.missing_facts.length === 0 ? (
          <span style={{ fontSize: "0.84rem", color: "#64748b", marginLeft: "0.4rem" }}>
            Không có.
          </span>
        ) : (
          <ul style={{ paddingLeft: "1.25rem", margin: "0.3rem 0 0", display: "grid", gap: "0.25rem" }}>
            {pkg.missing_facts.map((fact, i) => (
              <li key={i} style={{ color: "#7c2d12", fontSize: "0.85rem" }}>
                {fact}
              </li>
            ))}
          </ul>
        )}
      </div>

      <div
        style={{
          padding: "0.55rem 0.85rem",
          backgroundColor: "#eff6ff",
          border: "1px solid #93c5fd",
          borderRadius: 6,
          fontSize: "0.85rem",
        }}
      >
        <strong>Tuyến chuyển xử lý (Referral Route):</strong>{" "}
        <span style={{ color: "#1d4ed8" }}>
          {pkg.referral_target ?? "Không cần chuyển tuyến (đủ căn cứ)"}
        </span>
      </div>

      {pkg.hold_reason && (
        <div style={ALERT_STYLE("warning")} role="note">
          <strong>Lý do HOLD:</strong> {pkg.hold_reason}
        </div>
      )}

      <div
        style={{
          padding: "0.55rem 0.85rem",
          backgroundColor: "#fffbeb",
          border: "1px solid #fde68a",
          borderRadius: 6,
          fontSize: "0.85rem",
        }}
      >
        <strong>Mức độ không chắc chắn (Uncertainty):</strong>{" "}
        {pkg.uncertainty_note ?? "Thấp — đã đối soát nguồn hiệu lực và trường trọng yếu."}
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// KNW 01 Flag Button (ANS 03, KNW 01, KNW 07)
// ---------------------------------------------------------------------------
interface KNW01PanelProps {
  pkg: AnswerPackage;
  onFlag: (reason: FeedbackReason, comment: string) => Promise<void>;
}

function KNW01FlagPanel({ pkg, onFlag }: KNW01PanelProps) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<FeedbackReason>("missing_exception");
  const [comment, setComment] = useState("");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function handleSubmit() {
    const trimmed = comment.trim();
    if (trimmed.length < 3) {
      setErrorMsg("Vui lòng nhập mô tả ít nhất 3 ký tự.");
      return;
    }
    setSending(true);
    setErrorMsg(null);
    try {
      await onFlag(reason, trimmed);
      setSent(true);
      setComment("");
      setTimeout(() => {
        setSent(false);
        setOpen(false);
      }, 2500);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Không thể gửi phản hồi KNW 01.");
    } finally {
      setSending(false);
    }
  }

  return (
    <section style={{ ...SECTION_STYLE, backgroundColor: "#fef2f2" }}>
      <h3 style={{ ...SECTION_TITLE_STYLE, color: "#991b1b" }}>
        Gắn cờ KNW 01 — Báo sai / thiếu ngoại lệ / thiếu căn cứ
      </h3>
      <p style={{ fontSize: "0.82rem", color: "#64748b", margin: 0 }}>
        Phản hồi được lưu ở trạng thái <code>feedback_candidate</code> để Steward &amp; Policy
        Owner kiểm duyệt — <strong>không tự động sửa quy định</strong> (KNW 06).
      </p>

      {!open ? (
        <button
          type="button"
          data-testid="knw01-flag-button"
          onClick={() => setOpen(true)}
          style={BTN_STYLE("#dc2626", "#fff")}
        >
          Gắn cờ báo lỗi KNW 01
        </button>
      ) : sent ? (
        <div
          role="status"
          style={{ padding: "0.6rem", backgroundColor: "#dcfce7", color: "#166534", borderRadius: 6 }}
        >
          Đã ghi nhận phản hồi KNW 01 vào hàng đợi Steward.
        </div>
      ) : (
        <div style={{ display: "grid", gap: "0.6rem" }}>
          <label style={{ fontSize: "0.85rem", fontWeight: 600 }}>
            Lý do gắn cờ (5 mã chuẩn KNW 07):
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value as FeedbackReason)}
              style={{ display: "block", width: "100%", marginTop: "0.3rem", padding: "0.4rem" }}
            >
              {KNW01_FLAG_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>

          <label style={{ fontSize: "0.85rem", fontWeight: 600 }}>
            Mô tả chi tiết (tối thiểu 3 ký tự):
            <textarea
              rows={3}
              placeholder="Ví dụ: Điều khoản 3.2 về ngoại lệ khách hàng VIP chưa được liệt kê..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              maxLength={2000}
              style={{ display: "block", width: "100%", marginTop: "0.3rem", padding: "0.4rem" }}
            />
          </label>

          {errorMsg && (
            <div role="alert" style={{ color: "#991b1b", fontSize: "0.82rem" }}>
              {errorMsg}
            </div>
          )}

          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={sending || comment.trim().length < 3}
              style={BTN_STYLE("#dc2626", "#fff")}
            >
              {sending ? "Đang gửi..." : "Gửi Feedback Candidate"}
            </button>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                setErrorMsg(null);
              }}
              style={BTN_STYLE("#e2e8f0", "#334155")}
            >
              Hủy
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Part 7: Disclaimer KNW 02
// ---------------------------------------------------------------------------
function Part7Disclaimer({ warning }: { warning: string }) {
  return (
    <footer
      role="note"
      aria-label="Cảnh báo nội bộ KNW 02"
      style={{
        padding: "0.75rem 1rem",
        backgroundColor: "#fffbeb",
        border: "1px solid #fbbf24",
        borderRadius: 6,
        fontSize: "0.82rem",
        color: "#78350f",
      }}
    >
      <strong>Lưu ý nội bộ (KNW 02):</strong> {warning}
    </footer>
  );
}

// ---------------------------------------------------------------------------
// Main Component: AnswerPackageRenderer
// ---------------------------------------------------------------------------

export interface AnswerPackageRendererProps {
  pkg: AnswerPackage;
  onKNW01Flag: (reason: FeedbackReason, comment: string) => Promise<void>;
  onReferral?: () => Promise<void>;
  /** Override to force-display O1 state; defaults to pkg.o1_enabled */
  showO1?: boolean;
}

export default function AnswerPackageRenderer({
  pkg,
  onKNW01Flag,
  onReferral,
  showO1,
}: AnswerPackageRendererProps) {
  const o1Enabled = showO1 ?? Boolean(pkg.o1_enabled || pkg.o1_record);

  return (
    <article aria-label="Answer Package" style={{ display: "grid", gap: "1rem" }}>
      <Part1Header pkg={pkg} />
      <O1RecordPanel o1Enabled={o1Enabled} o1Record={pkg.o1_record} />
      <Part2Scope pkg={pkg} />
      <Part3Guidance pkg={pkg} />
      <Part4Citations citations={pkg.citations} />
      <Part5CriticalFields
        fields={pkg.critical_fields}
        capWarning={pkg.critical_field_cap_warning}
      />
      <Part6MissingAndRouting pkg={pkg} />
      <KNW01FlagPanel pkg={pkg} onFlag={onKNW01Flag} />

      {onReferral && (
        <section style={SECTION_STYLE}>
          <h3 style={SECTION_TITLE_STYLE}>Chuyển xử lý nội bộ (Local Referral · KNW 05)</h3>
          <button type="button" onClick={onReferral} style={BTN_STYLE("#2563eb", "#fff")}>
            Chuyển Policy Owner ({pkg.referral_target ?? "policy_owner"})
          </button>
        </section>
      )}

      <Part7Disclaimer warning={pkg.internal_use_warning} />
    </article>
  );
}

// ---------------------------------------------------------------------------
// Style constants
// ---------------------------------------------------------------------------

const SECTION_STYLE: React.CSSProperties = {
  padding: "1rem",
  border: "1px solid #e2e8f0",
  borderRadius: 8,
  backgroundColor: "#fff",
  display: "grid",
  gap: "0.6rem",
};

const SECTION_TITLE_STYLE: React.CSSProperties = {
  margin: 0,
  fontSize: "0.95rem",
  fontWeight: 700,
  color: "#1e293b",
  borderBottom: "1px solid #e2e8f0",
  paddingBottom: "0.4rem",
};

const BLOCKQUOTE_STYLE: React.CSSProperties = {
  margin: "0.25rem 0 0",
  padding: "0.6rem 0.75rem",
  borderLeft: "4px solid #64748b",
  backgroundColor: "#f8fafc",
  color: "#334155",
  fontStyle: "italic",
};

const DL_STYLE: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "auto 1fr",
  gap: "0.25rem 0.75rem",
  margin: 0,
  alignItems: "baseline",
};

const TH_STYLE: React.CSSProperties = {
  padding: "0.4rem 0.5rem",
  textAlign: "left",
  fontWeight: 600,
  borderBottom: "2px solid #cbd5e1",
  whiteSpace: "nowrap",
  fontSize: "0.78rem",
};

const TD_STYLE: React.CSSProperties = {
  padding: "0.4rem 0.5rem",
  borderBottom: "1px solid #e2e8f0",
  verticalAlign: "top",
  fontSize: "0.82rem",
};

function BADGE_STYLE(bg: string, color: string): React.CSSProperties {
  return {
    display: "inline-block",
    padding: "0.1rem 0.5rem",
    borderRadius: "9999px",
    backgroundColor: bg,
    color,
    fontSize: "0.75rem",
    fontWeight: 600,
    marginLeft: "0.35rem",
  };
}

function ALERT_STYLE(type: "warning" | "danger"): React.CSSProperties {
  const map = {
    warning: { bg: "#fffbeb", border: "#fbbf24", color: "#78350f" },
    danger:  { bg: "#fee2e2", border: "#fca5a5", color: "#7f1d1d" },
  };
  const c = map[type];
  return {
    padding: "0.6rem 1rem",
    backgroundColor: c.bg,
    border: `1px solid ${c.border}`,
    borderRadius: 6,
    color: c.color,
    fontSize: "0.85rem",
  };
}

function BTN_STYLE(bg: string, color: string): React.CSSProperties {
  return {
    padding: "0.45rem 1rem",
    backgroundColor: bg,
    color,
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
    fontWeight: 600,
    fontSize: "0.85rem",
  };
}
