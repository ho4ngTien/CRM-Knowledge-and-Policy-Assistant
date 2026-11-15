import type {
  AdminOpsSummary,
  AnswerPackage,
  FeedbackReason,
  PolicyLifecycleStatus,
  ReferralItem,
} from "../types/answer";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

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
    throw new Error(`API ${response.status}: ${text}`);
  }
  return (await response.json()) as T;
}

/** Synchronous verified Q&A endpoint; never streams unverified LLM tokens. */
export async function askPolicyQuestion(payload: {
  question: string;
  task_id?: string;
  governing_date?: string;
  scope?: string;
  allow_future_preview?: boolean;
}): Promise<AnswerPackage> {
  return requestJson<AnswerPackage>("/answer", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function submitFeedback(payload: {
  task_id: string;
  answer_package_id?: string;
  reason: FeedbackReason;
  comment: string;
  unanswered_topic?: string;
}): Promise<unknown> {
  return requestJson("/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createLocalReferral(payload: {
  task_id: string;
  answer_package_id?: string;
  target_owner: string;
  policy_family:
    | "commercial_quoting_approval"
    | "customer_info_handling"
    | "service_warranty_routing";
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
