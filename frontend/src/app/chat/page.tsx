"use client";

/**
 * CKPA-91 · G2-AC01 · feat/CKPA-91-answer-pkg-o1-flag-fields
 * Chat (Workspace Nhân viên) — Tích hợp AnswerPackageRenderer + Non-streaming + STALE check
 *
 * Assignee: [S3] Phạm Lương Yến Nhi
 */

import Link from "next/link";
import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";

import AnswerPackageRenderer from "../../components/AnswerPackageRenderer";
import {
  ApiError,
  askFollowUpQuestion,
  askPolicyQuestion,
  createLocalReferral,
  regenerateAnswerPackage,
  submitKNW01Flag,
  verifyAnswerCurrentState,
} from "../../lib/api";
import type { AnswerPackage, FeedbackReason, PolicyFamily } from "../../types/answer";

/** Lightweight authoritative status check (0 LLM tokens / 0 AnswerPackage quota). */
const STALE_POLL_INTERVAL_MS = 60_000;

const DEFAULT_SCOPE =
  "company:SN;branch:all;role:sales;customer_category:all;product:all;transaction_scope:all";

export default function ChatWorkspacePage() {
  const [question, setQuestion] = useState("");
  const [taskId, setTaskId] = useState<string | undefined>(undefined);
  const [governingDate, setGoverningDate] = useState("");
  const [scope, setScope] = useState(DEFAULT_SCOPE);
  const [allowFuture, setAllowFuture] = useState(false);

  const [answer, setAnswer] = useState<AnswerPackage | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusNote, setStatusNote] = useState<string | null>(null);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const answerRef = useRef<AnswerPackage | null>(null);
  answerRef.current = answer;

  const checkCitedPassagesStillValid = useCallback(async () => {
    const current = answerRef.current;
    if (!current || current.status === "stale" || current.citations.length === 0) {
      return;
    }
    try {
      const verification = await verifyAnswerCurrentState(current);
      if (!verification.is_valid || verification.stale) {
        setAnswer((prev) =>
          prev
            ? {
                ...prev,
                status: "stale",
                citations: [],
                verbatim_quotes: [],
                critical_fields: [],
                hold_reason:
                  verification.errors.join(" ") ||
                  "Authoritative source changed while workspace was open (KNW 04).",
              }
            : null
        );
        setStatusNote(
          "Cảnh báo STALE: Nguồn hoặc quyền truy cập đã thay đổi. Tuyệt đối không dùng hướng dẫn cũ."
        );
      }
    } catch (err) {
      const message =
        err instanceof ApiError && err.status === 409
          ? "Nguồn chính sách vừa bị thu hồi (HTTP 409)."
          : "Không thể xác minh trạng thái nguồn hiện tại.";
      setAnswer((prev) =>
        prev
          ? {
              ...prev,
              status: "stale",
              citations: [],
              verbatim_quotes: [],
              critical_fields: [],
              hold_reason: message,
            }
          : null
      );
      setStatusNote(`Cảnh báo STALE: ${message} Tạm ngưng sử dụng hướng dẫn cũ.`);
    }
  }, []);

  useEffect(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (answer && answer.status !== "stale" && answer.citations.length > 0) {
      pollRef.current = setInterval(() => {
        void checkCitedPassagesStillValid();
      }, STALE_POLL_INTERVAL_MS);
    }
    const onFocus = () => {
      void checkCitedPassagesStillValid();
    };
    window.addEventListener("focus", onFocus);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
      window.removeEventListener("focus", onFocus);
    };
  }, [answer, checkCitedPassagesStillValid]);

  async function runQuery(mode: "ask" | "follow_up" | "regenerate") {
    if (!question.trim()) return;
    setLoading(true);
    setStatusNote(null);
    const payload = {
      question,
      task_id: mode === "ask" ? undefined : taskId,
      governing_date: governingDate || undefined,
      scope,
      allow_future_preview: allowFuture,
    };
    try {
      const pkg =
        mode === "follow_up"
          ? await askFollowUpQuestion(payload)
          : mode === "regenerate"
          ? await regenerateAnswerPackage(payload)
          : await askPolicyQuestion(payload);
      setAnswer(pkg);
      setTaskId(pkg.task_id);
    } catch (err) {
      setStatusNote(
        err instanceof Error ? err.message : "Không thể kết nối máy chủ kiểm chứng."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleAsk(event: FormEvent) {
    event.preventDefault();
    void runQuery("ask");
  }

  async function handleReferral() {
    if (!answer) return;
    const policyFamily = detectPolicyFamily(answer);
    try {
      const ticket = await createLocalReferral({
        task_id: answer.task_id,
        answer_package_id: answer.answer_id,
        target_owner: answer.referral_target ?? "policy_owner",
        policy_family: policyFamily,
        question_summary: answer.original_question.slice(0, 200),
      });
      setStatusNote(`Đã tạo phiếu chuyển xử lý nội bộ: ${ticket.id}`);
    } catch (err) {
      setStatusNote(err instanceof Error ? err.message : "Lỗi tạo phiếu chuyển xử lý.");
    }
  }

  async function handleKNW01Flag(reason: FeedbackReason, comment: string) {
    if (!answer) return;
    await submitKNW01Flag({
      task_id: answer.task_id,
      answer_package_id: answer.answer_id,
      reason,
      comment,
    });
    setStatusNote("Đã gửi phản hồi KNW 01 vào hàng đợi Steward.");
  }

  function handleNewQuestion() {
    if (pollRef.current) clearInterval(pollRef.current);
    setAnswer(null);
    setTaskId(undefined);
    setQuestion("");
    setStatusNote(null);
  }

  return (
    <main
      style={{
        display: "grid",
        gridTemplateColumns: "380px 1fr",
        gap: "1.5rem",
        padding: "1.5rem",
        fontFamily: "system-ui, sans-serif",
        maxWidth: 1400,
        margin: "0 auto",
      }}
    >
      <aside>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1rem",
          }}
        >
          <h1 style={{ fontSize: "1.1rem", margin: 0 }}>Hỏi đáp Chính sách CRM</h1>
          <Link href="/" style={{ fontSize: "0.82rem" }}>
            Trang chủ
          </Link>
        </header>

        <p
          style={{
            fontSize: "0.78rem",
            color: "#b45309",
            backgroundColor: "#fffbeb",
            padding: "0.4rem 0.6rem",
            borderRadius: 4,
            border: "1px solid #fde68a",
            margin: "0 0 0.75rem",
          }}
        >
          <strong>SEC 02:</strong> Không nhập SĐT, email, CCCD/MST, STK ngân hàng hoặc dữ liệu
          cá nhân khách hàng vào câu hỏi.
        </p>

        <form onSubmit={handleAsk} style={{ display: "grid", gap: "0.65rem" }}>
          <label style={LABEL_STYLE}>
            Câu hỏi chính sách
            <textarea
              rows={5}
              placeholder="Ví dụ: Báo giá chiết khấu 12% cho khách B2B cần ai duyệt?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              style={{ ...INPUT_STYLE, resize: "vertical" }}
              required
              maxLength={2000}
            />
            <span style={{ fontSize: "0.72rem", color: "#94a3b8" }}>{question.length}/2000</span>
          </label>

          <label style={LABEL_STYLE}>
            Ngày chi phối (Asia/Ho_Chi_Minh — để trống = hôm nay)
            <input
              type="date"
              value={governingDate}
              onChange={(e) => setGoverningDate(e.target.value)}
              style={INPUT_STYLE}
            />
          </label>

          <label style={LABEL_STYLE}>
            Phạm vi áp dụng (6 chiều DAT 04)
            <input
              type="text"
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              style={INPUT_STYLE}
              placeholder={DEFAULT_SCOPE}
            />
            <span style={{ fontSize: "0.72rem", color: "#64748b" }}>
              company · branch · role · customer_category · product · transaction_scope
            </span>
          </label>

          <label style={{ fontSize: "0.82rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <input
              type="checkbox"
              checked={allowFuture}
              onChange={(e) => setAllowFuture(e.target.checked)}
            />
            Cho phép xem trước chính sách tương lai (chưa hiệu lực)
          </label>

          {taskId && (
            <div style={{ fontSize: "0.78rem", color: "#64748b" }}>
              Task hiện tại: <code>{taskId}</code>
            </div>
          )}

          <div style={{ display: "grid", gap: "0.4rem" }}>
            <button type="submit" disabled={loading} style={BTN_STYLE("#1d4ed8", "#fff")}>
              {loading
                ? "Đang kiểm tra quyền, trích dẫn & trường trọng yếu (Không Stream)..."
                : "Tra cứu chính sách"}
            </button>

            {answer && taskId && (
              <>
                <button
                  type="button"
                  onClick={() => void runQuery("follow_up")}
                  disabled={loading}
                  style={BTN_STYLE("#0369a1", "#fff")}
                >
                  Hỏi tiếp theo (Follow-up · giữ Task ID)
                </button>
                <button
                  type="button"
                  onClick={() => void runQuery("regenerate")}
                  disabled={loading}
                  style={BTN_STYLE("#0f766e", "#fff")}
                >
                  Tạo lại gói trả lời (Regenerate)
                </button>
              </>
            )}

            {answer && (
              <button
                type="button"
                onClick={handleNewQuestion}
                style={BTN_STYLE("#e2e8f0", "#334155")}
              >
                Câu hỏi mới
              </button>
            )}
          </div>
        </form>

        {statusNote && (
          <p
            role="status"
            style={{
              marginTop: "0.75rem",
              padding: "0.5rem 0.75rem",
              backgroundColor: statusNote.includes("STALE") || statusNote.includes("Lỗi") ? "#fef2f2" : "#f0fdf4",
              color: statusNote.includes("STALE") || statusNote.includes("Lỗi") ? "#991b1b" : "#166534",
              borderRadius: 6,
              fontSize: "0.85rem",
            }}
          >
            {statusNote}
          </p>
        )}

        <p
          style={{
            marginTop: "1rem",
            fontSize: "0.72rem",
            color: "#94a3b8",
            borderTop: "1px solid #e2e8f0",
            paddingTop: "0.75rem",
          }}
        >
          <strong>KNW 02:</strong> Hướng dẫn nội bộ — nhân viên phải kiểm tra hoàn cảnh, nguồn
          hiện hành và thẩm quyền trước khi hành động. Không thay thế phê duyệt hay thực thi.
        </p>
      </aside>

      <section>
        <h2 style={{ fontSize: "1rem", margin: "0 0 0.75rem", color: "#334155" }}>
          Answer Package 7 phần &amp; Trường Trọng yếu (G2-AC01)
        </h2>

        {!answer ? (
          <div
            style={{
              padding: "2rem",
              border: "1px dashed #cbd5e1",
              borderRadius: 8,
              color: "#94a3b8",
              textAlign: "center",
            }}
          >
            Nhập câu hỏi và nhấn Tra cứu để hiển thị Answer Package đầy đủ 7 phần.
          </div>
        ) : (
          <AnswerPackageRenderer
            pkg={answer}
            onKNW01Flag={handleKNW01Flag}
            onReferral={handleReferral}
          />
        )}
      </section>
    </main>
  );
}

function detectPolicyFamily(pkg: AnswerPackage): PolicyFamily {
  const q = pkg.original_question.toLowerCase();
  if (q.includes("báo giá") || q.includes("chiết khấu") || q.includes("duyệt")) {
    return "commercial_quoting_approval";
  }
  if (q.includes("bảo hành") || q.includes("sửa chữa") || q.includes("warranty")) {
    return "service_warranty_routing";
  }
  return "customer_info_handling";
}

const LABEL_STYLE: React.CSSProperties = {
  display: "grid",
  gap: "0.25rem",
  fontSize: "0.82rem",
  fontWeight: 600,
  color: "#374151",
};

const INPUT_STYLE: React.CSSProperties = {
  width: "100%",
  padding: "0.4rem 0.5rem",
  border: "1px solid #cbd5e1",
  borderRadius: 4,
  fontSize: "0.85rem",
  boxSizing: "border-box",
};

function BTN_STYLE(bg: string, color: string): React.CSSProperties {
  return {
    padding: "0.5rem 1rem",
    backgroundColor: bg,
    color,
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
    fontWeight: 600,
    fontSize: "0.85rem",
    width: "100%",
  };
}
