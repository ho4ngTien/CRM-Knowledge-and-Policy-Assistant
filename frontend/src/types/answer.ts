export type AnswerStatus =
  | "answered"
  | "hold"
  | "clarification_required"
  | "referred"
  | "stale"
  | "refused_out_of_scope";

export type FeedbackReason =
  | "missing_source"
  | "outdated_rule"
  | "wrong_scope"
  | "missing_exception"
  | "rejected";

export type ReferralStatus = "referred" | "owner_responded" | "closed";

export type PolicyLifecycleStatus =
  | "draft"
  | "owner_reviewed"
  | "approved"
  | "scheduled"
  | "effective"
  | "superseded"
  | "withdrawn"
  | "feedback_candidate"
  | "quarantined";

export interface AnswerCitation {
  document_id: string;
  document_version_id: string;
  passage_id: string;
  title: string;
  page_number: number;
  clause_ref: string;
  quoted_text: string;
  evidence_url: string;
}

export interface CriticalFieldItem {
  field_id: string;
  policy_id: string;
  policy_version_id: string;
  document_version_id: string;
  field_name: string;
  field_type: string;
  operator: string;
  value: string;
  unit?: string | null;
  currency?: string | null;
  approval_role: string;
  time_limit?: string | null;
  exception_condition?: string | null;
  required_documents: string[];
  source_clause: string;
  status: PolicyLifecycleStatus;
}

/** Mandatory 7-part verified response returned post-validation (SRS-FR-06.1). */
export interface AnswerPackage {
  answer_id: string;
  task_id: string;
  status: AnswerStatus;

  // Part 1
  original_question: string;

  // Part 2
  governing_date: string;
  timezone: string;
  scope: string;
  is_historical: boolean;
  is_future_preview: boolean;

  // Part 3
  guidance_text: string;
  verbatim_quotes: string[];

  // Part 4
  citations: AnswerCitation[];

  // Part 5
  critical_fields: CriticalFieldItem[];

  // Part 6
  missing_facts: string[];
  hold_reason?: string | null;
  uncertainty_note?: string | null;

  // Part 7
  referral_target?: string | null;
  internal_use_warning: string;

  // Governance telemetry
  pii_warning?: string | null;
  snapshot_age_hours?: number | null;
  llm_calls_used: number;
}

export interface AdminOpsSummary {
  timezone: string;
  answer_streaming_enabled: boolean;
  snapshot_staleness_threshold_hours: number;
  cache_withdrawal_max_seconds: number;
  pilot_max_named_users: number;
  pilot_max_concurrent_sessions: number;
  corpus_max_documents: number;
  corpus_max_passages: number;
  corpus_max_critical_fields: number;
}

export interface ReferralItem {
  id: string;
  task_id: string;
  answer_package_id?: string | null;
  requester_id: string;
  target_owner: string;
  policy_family: string;
  question_summary: string;
  status: ReferralStatus;
  owner_response?: string | null;
  resolution_note?: string | null;
  created_at: string;
}
