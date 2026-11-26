/**
 * CKPA-91 · G2-AC01 · feat/CKPA-91-answer-pkg-o1-flag-fields
 * Answer Package TypeScript types synced 1:1 with FastAPI Pydantic schemas.
 * RFP: ANS 01, ANS 03, ANS 04, KNW 01, KNW 02, KNW 07, VN 01, VN 03
 * Assignee: [S3] Phạm Lương Yến Nhi
 */

// ---------------------------------------------------------------------------
// Enums & Literals (aligned with backend/src/shared/enums.py)
// ---------------------------------------------------------------------------

export type AnswerStatus =
  | "answered"
  | "answered_with_conditions"
  | "hold_and_refer"
  | "hold"
  | "clarification_required"
  | "referred"
  | "stale"
  | "refused_out_of_scope";

/** Exact 5 standardized KNW 07 / KNW 01 feedback categories in FeedbackReason. */
export type FeedbackReason =
  | "missing_source"
  | "outdated_rule"
  | "wrong_scope"
  | "missing_exception"
  | "rejected";

export type KNW01FlagReason = FeedbackReason;

export type ReferralStatus = "referred" | "owner_responded" | "closed";

export type PolicyFamily =
  | "commercial_quoting_approval"
  | "customer_info_handling"
  | "service_warranty_routing";

export type AuthorityTier =
  | "policy"
  | "sop"
  | "manufacturer_terms"
  | "customer_contract"
  | "staff_note";

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

// ---------------------------------------------------------------------------
// Citation (Part 4) — hộp nguyên văn trích dẫn
// ---------------------------------------------------------------------------

export interface AnswerCitation {
  document_id: string;
  document_version_id: string;
  passage_id: string;
  title: string;
  page_number: number;
  clause_ref: string;
  quoted_text: string;
  evidence_url: string;
  effective_date?: string | null;
  owner?: string | null;
}

// ---------------------------------------------------------------------------
// Critical Field (Part 5) — Deterministic, 0% LLM
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Option O1 Selected CRM Context (aligned with selection/o1_context.py)
// ---------------------------------------------------------------------------

export interface CustomerContextO1 {
  customer_id: string;
  customer_tier: string;
  industry_code?: string | null;
  assigned_branch?: string | null;
  assigned_company?: string | null;
}

// ---------------------------------------------------------------------------
// Answer Package — 7 phần bắt buộc (G2-AC01, ANS 01, ANS 03, ANS 04)
// ---------------------------------------------------------------------------

/** Mandatory 7-part verified response returned post-validation (SRS-FR-06.1, G2-AC01). */
export interface AnswerPackage {
  answer_id: string;
  task_id: string;
  status: AnswerStatus;

  // Part 1: Original question
  original_question: string;

  // Part 2: Governing date (Asia/Ho_Chi_Minh) & 6-dimension scope
  governing_date: string;
  timezone: string;
  scope: string;
  scope_matched_dimensions?: Record<string, string>;
  is_historical: boolean;
  is_future_preview: boolean;

  // Part 3: Concise Vietnamese explanation (normally 100-250 words) & verbatim quotes
  guidance_text: string;
  guidance_word_count?: number;
  verbatim_quotes: string[];

  // Part 4: Grounded source citations (<= 8 entries)
  citations: AnswerCitation[];

  // Part 5: Deterministic structured critical fields (<= 8 entries / <= 6000 Unicode chars)
  critical_fields: CriticalFieldItem[];
  critical_field_cap_warning?: string | null;

  // Part 6: Missing facts, Hold reason & uncertainty/clarification guidance
  missing_facts: string[];
  hold_reason?: string | null;
  uncertainty_note?: string | null;

  // Part 7: Local referral target & mandatory internal-use disclaimer (KNW 02)
  referral_target?: string | null;
  internal_use_warning: string;

  // Option O1 (only populated when ENABLE_O1_CONTEXT_IMPORT is True)
  o1_enabled?: boolean;
  o1_record?: CustomerContextO1 | null;

  // Governance telemetry
  pii_warning?: string | null;
  snapshot_age_hours?: number | null;
  llm_calls_used: number;
}

// ---------------------------------------------------------------------------
// KNW 01 / KNW 07 Feedback Request
// ---------------------------------------------------------------------------

export interface KNW01FlagRequest {
  task_id: string;
  answer_package_id?: string;
  reason: FeedbackReason;
  comment: string;
  unanswered_topic?: string;
}

// ---------------------------------------------------------------------------
// Knowledge & Lineage types (aligned with backend/src/modules/knowledge/schemas.py)
// ---------------------------------------------------------------------------

export interface PassageSummary {
  passage_id: string;
  document_id: string;
  document_version_id: string;
  title: string;
  content: string;
  source_ref: string;
  page_number: number;
  clause_ref: string;
  language: string;
  scope: string;
  audience: string[];
  status: PolicyLifecycleStatus;
  has_essential_attachments: boolean;
  effective_from: string;
  effective_to?: string | null;
  supersedes?: string | null;
  is_tombstoned: boolean;
}

export interface DocumentLineageVersion {
  document_version_id: string;
  status: PolicyLifecycleStatus;
  recorded_at: string;
  effective_from: string;
  effective_to?: string | null;
  supersedes?: string | null;
}

export interface DocumentLineageResponse {
  document_id: string;
  title: string;
  policy_family: PolicyFamily;
  authority_tier: AuthorityTier;
  owner: string;
  versions: DocumentLineageVersion[];
}

export interface SnapshotAgeResponse {
  last_successful_import_at?: string | null;
  snapshot_age_hours?: number | null;
  snapshot_age_seconds?: number | null;
  staleness_threshold_hours: number;
  is_stale: boolean;
}

// ---------------------------------------------------------------------------
// Admin & Referral shared types
// ---------------------------------------------------------------------------

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
  policy_family: PolicyFamily;
  question_summary: string;
  status: ReferralStatus;
  owner_response?: string | null;
  resolution_note?: string | null;
  created_at: string;
}
