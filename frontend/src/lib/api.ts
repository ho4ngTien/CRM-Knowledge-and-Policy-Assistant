/**
 * CKPA-91 · G2-AC01 — API client synced with FastAPI /api/v1 endpoints.
 * Assignee: [S3] Phạm Lương Yến Nhi
 */
import type {
  AdminOpsSummary,
  AnswerPackage,
  CustomerContextO1,
  DocumentLineageResponse,
  KNW01FlagRequest,
  PassageSummary,
  PolicyFamily,
  PolicyLifecycleStatus,
  ReferralItem,
  SnapshotAgeResponse,
} from "../types/answer";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, `API ${response.status}: ${text}`);
  }
  return (await response.json()) as T;
}

export interface AnswerQueryPayload {
  question: string;
  task_id?: string;
  governing_date?: string;
  scope?: string;
  allow_future_preview?: boolean;
  o1_context?: CustomerContextO1 | null;
}

/** Synchronous verified Q&A endpoint; never streams unverified LLM tokens. */
export async function askPolicyQuestion(payload: AnswerQueryPayload): Promise<AnswerPackage> {
  return requestJson<AnswerPackage>("/answer", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** Clarified follow-up preserving original task_id. */
export async function askFollowUpQuestion(payload: AnswerQueryPayload): Promise<AnswerPackage> {
  return requestJson<AnswerPackage>("/answer/follow-up", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** Regenerate AnswerPackage preserving task_id after source updates/clarification. */
export async function regenerateAnswerPackage(payload: AnswerQueryPayload): Promise<AnswerPackage> {
  return requestJson<AnswerPackage>("/answer/regenerate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * KNW 01 — Gắn cờ báo lỗi câu trả lời (sai/thiếu ngoại lệ/thiếu căn cứ).
 * Queued as feedback_candidate for Steward & Owner review (never auto-updates rules, KNW 06).
 */
export async function submitKNW01Flag(payload: KNW01FlagRequest): Promise<unknown> {
  return requestJson("/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** Alias kept for backward compatibility. */
export const submitFeedback = submitKNW01Flag;

export async function createLocalReferral(payload: {
  task_id: string;
  answer_package_id?: string;
  target_owner: string;
  policy_family: PolicyFamily;
  question_summary: string;
}): Promise<ReferralItem> {
  return requestJson<ReferralItem>("/referral", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listLocalReferrals(): Promise<ReferralItem[]> {
  return requestJson<ReferralItem[]>("/referral");
}

export async function getAdminOpsSummary(): Promise<AdminOpsSummary> {
  return requestJson<AdminOpsSummary>("/admin/ops-summary");
}

export async function withdrawPolicyImmediately(
  policyVersionId: string,
  reason: string
): Promise<{ status: PolicyLifecycleStatus; stale_answers_marked: number }> {
  return requestJson(`/admin/policies/${encodeURIComponent(policyVersionId)}/withdraw`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

/**
 * Evidence Viewer — Fetch passage guarded by RBAC audience & withdrawal checks (403/409).
 */
export async function getPassageById(
  passageId: string,
  allowHistorical = false
): Promise<PassageSummary> {
  const qs = allowHistorical ? "?allow_historical=true" : "";
  return requestJson<PassageSummary>(`/knowledge/passages/${encodeURIComponent(passageId)}${qs}`);
}

export async function verifyAnswerCurrentState(answer: AnswerPackage): Promise<{
  is_valid: boolean;
  stale: boolean;
  verified_citations_count: number;
  errors: string[];
  active_view_refresh_interval_seconds: number;
}> {
  return requestJson<{
    is_valid: boolean;
    stale: boolean;
    verified_citations_count: number;
    errors: string[];
    active_view_refresh_interval_seconds: number;
  }>("/validation/verify", {
    method: "POST",
    body: JSON.stringify({
      answer_id: answer.answer_id,
      citations: answer.citations.map((citation) => ({
        passage_id: citation.passage_id,
        document_id: citation.document_id,
        document_version_id: citation.document_version_id,
        quoted_text: citation.quoted_text,
      })),
      allow_historical: answer.is_historical,
      allow_future_preview: answer.is_future_preview,
    }),
  });
}

/**
 * Document version lineage guarded by audience & unpublished status filtering.
 */
export async function getDocumentLineage(documentId: string): Promise<DocumentLineageResponse> {
  return requestJson<DocumentLineageResponse>(
    `/knowledge/documents/${encodeURIComponent(documentId)}/lineage`
  );
}

/** Current corpus snapshot freshness telemetry. */
export async function getSnapshotAge(): Promise<SnapshotAgeResponse> {
  return requestJson<SnapshotAgeResponse>("/knowledge/snapshot-age");
}
