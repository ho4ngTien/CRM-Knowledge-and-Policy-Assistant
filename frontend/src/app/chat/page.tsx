"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";

import { askPolicyQuestion, createLocalReferral, submitFeedback } from "../../lib/api";
import type { AnswerPackage, FeedbackReason } from "../../types/answer";

const FEEDBACK_OPTIONS: { value: FeedbackReason; label: string }[] = [
  { value: "missing_source", label: "Thiếu nguồn tài liệu (missing_source)" },
  { value: "outdated_rule", label: "Quy định đã lỗi thời (outdated_rule)" },
  { value: "wrong_scope", label: "Sai phạm vi áp dụng (wrong_scope)" },
  { value: "missing_exception", label: "Thiếu ngoại lệ (missing_exception)" },
  { value: "rejected", label: "Từ chối dùng hướng dẫn (rejected)" },
];

export default function ChatSplitScreenPage() {
  const [question, setQuestion] = useState("");
  const [governingDate, setGoverningDate] = useState("");
  const [scope, setScope] = useState(
    "company:SN;branch:all;role:sales;customer_group:all;product:all"
  );
  const [answer, setAnswer] = useState<AnswerPackage | null>(null);
  const [feedbackReason, setFeedbackReason] = useState<FeedbackReason>("missing_source");
  const [feedbackComment, setFeedbackComment] = useState("");
  const [statusNote, setStatusNote] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleAsk(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setStatusNote(null);
    try {
      const pkg = await askPolicyQuestion({
        question,
        governing_date: governingDate || undefined,
        scope,
      });
      setAnswer(pkg);
    } catch (err) {
      setStatusNote(err instanceof Error ? err.message : "Không thể kết nối máy chủ kiểm chứng.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReferral() {
    if (!answer) return;
    try {
      const ticket = await createLocalReferral({
        task_id: answer.task_id,
        answer_package_id: answer.answer_id,
        target_owner: answer.referral_target ?? "policy_owner",
        policy_family: "commercial_quoting_approval",
        question_summary: answer.original_question,
      });
      setStatusNote(`Đã tạo phiếu chuyển xử lý nội bộ ${ticket.id}.`);
    } catch (err) {
      setStatusNote(err instanceof Error ? err.message : "Lỗi tạo phiếu chuyển xử lý.");
    }
  }

  async function handleFeedback() {
    if (!answer || !feedbackComment.trim()) return;
    try {
      await submitFeedback({
        task_id: answer.task_id,
        answer_package_id: answer.answer_id,
        reason: feedbackReason,
        comment: feedbackComment,
      });
      setStatusNote("Đã gửi phản hồi vào hàng đợi Steward (không tự sửa quy định).");
      setFeedbackComment("");
    } catch (err) {
      setStatusNote(err instanceof Error ? err.message : "Lỗi gửi phản hồi.");
    }
  }

  return (
    <main
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        gap: "1.5rem",
        padding: "1.5rem",
        fontFamily: "sans-serif",
      }}
    >
      {/* Left Pane: Query, Governing Date, Guidance & Triage */}
      <section style={{ borderRight: "1px solid #e2e8f0", paddingRight: "1.25rem" }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1>Hỏi đáp Chính sách CRM</h1>
          <Link href="/">Trang chủ</Link>
        </header>

        <p style={{ fontSize: "0.85rem", color: "#b45309" }}>
          SEC 02: Không nhập SĐT, email, CCCD/MST hoặc dữ liệu cá nhân khách hàng vào câu hỏi.
        </p>

        <form onSubmit={handleAsk} style={{ display: "grid", gap: "0.75rem" }}>
          <textarea
            rows={4}
            placeholder="Nhập câu hỏi chính sách (ví dụ: Báo giá chiết khấu 12% cần ai duyệt?)"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            style={{ width: "100%", padding: "0.5rem" }}
          />
          <label>
            Ngày chi phối (giờ Asia/Ho_Chi_Minh, để trống = hôm nay):{" "}
            <input
              type="date"
              value={governingDate}
              onChange={(e) => setGoverningDate(e.target.value)}
            />
          </label>
          <label>
            Phạm vi áp dụng:{" "}
            <input
              type="text"
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              style={{ width: "100%", padding: "0.4rem" }}
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Đang truy xuất & kiểm chứng..." : "Tra cứu chính sách (Không Stream)"}
          </button>
        </form>

        {statusNote && (
          <p role="status" style={{ marginTop: "0.75rem", color: "#0f766e" }}>
            {statusNote}
          </p>
        )}

        {answer && (
          <article style={{ marginTop: "1.25rem", display: "grid", gap: "0.75rem" }}>
            <div>
              <strong>Trạng thái gói trả lời:</strong> <code>{answer.status}</code> | Task:{" "}
              <code>{answer.task_id}</code>
            </div>

            {answer.pii_warning && (
              <div style={{ padding: "0.5rem", backgroundColor: "#fef2f2", color: "#991b1b" }}>
                {answer.pii_warning}
              </div>
            )}

            <div>
              <h2>Diễn giải hướng dẫn (Verified)</h2>
              <p>{answer.guidance_text}</p>
            </div>

            {answer.hold_reason && (
              <div style={{ padding: "0.75rem", backgroundColor: "#fff7ed", border: "1px solid #fdba74" }}>
                <strong>Lý do HOLD / Làm rõ:</strong> {answer.hold_reason}
                {answer.missing_facts.length > 0 && (
                  <ul>
                    {answer.missing_facts.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button type="button" onClick={handleReferral}>
                Chuyển Policy Owner ({answer.referral_target ?? "policy_owner"})
              </button>
            </div>

            <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.75rem" }}>
              <h3>Phản hồi quy trình (5 lý do KNW 07)</h3>
              <select
                value={feedbackReason}
                onChange={(e) => setFeedbackReason(e.target.value as FeedbackReason)}
              >
                {FEEDBACK_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Ghi chú chi tiết thiếu sót..."
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
                style={{ width: "100%", margin: "0.5rem 0", padding: "0.4rem" }}
              />
              <button type="button" onClick={handleFeedback}>
                Gửi Feedback Candidate
              </button>
            </div>
          </article>
        )}
      </section>

      {/* Right Pane: Verbatim Evidence, Deterministic Critical Fields & Stale Guards */}
      <section>
        <h2>Bằng chứng &amp; Trường Trọng yếu</h2>
        {!answer ? (
          <p style={{ color: "#64748b" }}>
            Nguyên văn điều khoản trích dẫn, bảng Critical Fields xác định từ DB và ngày hiệu lực
            sẽ hiển thị tại đây sau khi kiểm chứng hoàn tất.
          </p>
        ) : (
          <div style={{ display: "grid", gap: "1rem" }}>
            {answer.status === "stale" && (
              <div
                role="alert"
                style={{ padding: "0.75rem", backgroundColor: "#fee2e2", color: "#991b1b" }}
              >
                CẢNH BÁO STALE: Chính sách liên quan vừa bị thu hồi. Tuyệt đối không dùng hướng
                dẫn này; hãy chạy lại truy vấn.
              </div>
            )}

            <div style={{ fontSize: "0.9rem", backgroundColor: "#f8fafc", padding: "0.75rem" }}>
              <strong>Ngày chi phối:</strong> {answer.governing_date} ({answer.timezone}){" "}
              {answer.is_historical && <span>[Hướng dẫn lịch sử]</span>}
              {answer.is_future_preview && <span>[Chính sách tương lai chưa hiệu lực]</span>}
              <br />
              <strong>Snapshot Age:</strong>{" "}
              {answer.snapshot_age_hours != null ? `${answer.snapshot_age_hours} giờ` : "Chưa có dữ liệu"}
            </div>

            <div>
              <h3>Nguyên văn trích dẫn (Verbatim Quotes)</h3>
              {answer.verbatim_quotes.length === 0 ? (
                <p>Không có nguyên văn hợp lệ.</p>
              ) : (
                <ul>
                  {answer.verbatim_quotes.map((quote) => (
                    <li key={quote}>
                      <blockquote>{quote}</blockquote>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div>
              <h3>Nguồn trích dẫn (Citations)</h3>
              {answer.citations.length === 0 ? (
                <p>Chưa có trích dẫn được xác minh.</p>
              ) : (
                <ul>
                  {answer.citations.map((cit) => (
                    <li key={`${cit.passage_id}-${cit.document_version_id}`}>
                      <strong>{cit.title}</strong> ({cit.document_version_id}, trang{" "}
                      {cit.page_number}, {cit.clause_ref}) &mdash;{" "}
                      <Link href={`/evidence?passage_id=${encodeURIComponent(cit.passage_id)}`}>
                        Mở nguồn
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div>
              <h3>Trường trọng yếu từ DB (Critical Fields)</h3>
              {answer.critical_fields.length === 0 ? (
                <p>Không có trường trọng yếu áp dụng.</p>
              ) : (
                <table border={1} cellPadding={6} style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr>
                      <th>Trường</th>
                      <th>Toán tử / Giá trị</th>
                      <th>Thẩm quyền duyệt</th>
                      <th>Điều khoản nguồn</th>
                    </tr>
                  </thead>
                  <tbody>
                    {answer.critical_fields.map((cf) => (
                      <tr key={cf.field_id}>
                        <td>{cf.field_name}</td>
                        <td>
                          {cf.operator} {cf.value} {cf.unit ?? ""} {cf.currency ?? ""}
                        </td>
                        <td>{cf.approval_role}</td>
                        <td>{cf.source_clause}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <footer
              style={{
                padding: "0.75rem",
                backgroundColor: "#fffbeb",
                border: "1px solid #fbbf24",
                fontSize: "0.85rem",
              }}
            >
              {answer.internal_use_warning}
            </footer>
          </div>
        )}
      </section>
    </main>
  );
}
