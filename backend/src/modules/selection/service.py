"""Selection Service: Date (UTC+7), 6-Dim Scope, Critical-Field Lookup, Conflict Hold.

Implements CRM-G1-SUB14 (WP03-Selection, DEL02-Working-Core).

RFP requirements covered:
  DAT 04 – 6-Dimension applicability matching + Hold when no governing rule found
  DAT 05 – Source-conflict detection → mandatory Hold
  DAT 06 – Typed deterministic critical-field lookup (≤ 50 rows, 0% LLM)
  DAT 08 – Hold when essential table/annotation is missing
  OPS 03 – Mandatory Hold gate (can_proceed=False propagation)
  OPS 04 – Deterministic numeric threshold (via PolicyService.evaluate_numeric_threshold)
  VN 01  – Vietnamese normalisation through SUB08 dictionary (RetrievalService)

Acceptance Criteria (G1-AC05, G1-AC06):
  Given module SUB07 and VN 01 SUB08 dictionary
  When S3 codes the Selection Date/Scope/Critical-Fields/Hold tier
  Then 0% arithmetic goes through LLM and 100% of missing-date / missing-annotation /
       conflict cases are automatically held.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.config import settings
from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.retrieval.models import (
    VIETNAMESE_CRM_SYNONYMS,
    VIETNAMESE_TECHNICAL_TERMS,
    VIETNAMESE_UNACCENT_MAPPINGS,
)
from src.modules.selection.schemas import (
    CriticalFieldLookupRequest,
    CriticalFieldLookupResult,
    GoverningDateResult,
    HoldTrigger,
    ScopeDimensions,
    ScopeMatchResult,
    SelectionHoldDecision,
    SelectionResult,
)
from src.shared.contracts import PolicyGateDecision
from src.shared.enums import ComparisonOperator, PolicyLifecycleStatus

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_VN_TZ = ZoneInfo(settings.APP_TIMEZONE)

_WILDCARD_VALUES: frozenset[str] = frozenset({"all", "*", "any", "tất cả"})

_DIMENSION_KEYS: tuple[str, ...] = (
    "company",
    "branch",
    "role",
    "customer_category",
    "product",
    "transaction_scope",
)


def _normalize_dim_token(value: str | None) -> str | None:
    """Normalize whitespace and map unaccented phrases using VN 01 SUB08 dictionary."""
    if value is None:
        return None
    val = " ".join(value.strip().lower().split())
    for unacc, acc in VIETNAMESE_UNACCENT_MAPPINGS.items():
        if unacc in val:
            val = val.replace(unacc, acc)
    return val


def _get_synonym_family(value: str) -> set[str]:
    """Retrieve synonym family from SUB08 dictionary (synonyms, technical terms)."""
    norm = _normalize_dim_token(value)
    if not norm:
        return set()
    syns = {norm, value.strip().lower()}

    # Check VIETNAMESE_CRM_SYNONYMS
    for k, v_tuple in VIETNAMESE_CRM_SYNONYMS.items():
        family = {k.lower()} | {item.lower() for item in v_tuple}
        if any(item in syns for item in family):
            syns.update(family)

    # Check VIETNAMESE_TECHNICAL_TERMS
    for k, v in VIETNAMESE_TECHNICAL_TERMS.items():
        pair = {k.lower(), v.lower()}
        if any(item in syns for item in pair):
            syns.update(pair)

    return syns


def _dim_matches(request_val: str | None, policy_val: str | None) -> bool:
    """Return True when the policy dimension is compatible with the requested value.

    Rules (DAT 04 / VN 01 / SUB08):
    1. If the policy dimension is a wildcard → always matches.
    2. If the request did not specify the dimension (None) → always matches.
    3. Exact match after VN 01 unaccent normalization.
    4. Match via approved SUB08 Vietnamese CRM synonym or technical terms glossary.
    """
    if policy_val is None:
        return True
    norm_policy = _normalize_dim_token(policy_val)
    if norm_policy in _WILDCARD_VALUES:
        return True
    if request_val is None:
        return True
    norm_request = _normalize_dim_token(request_val)
    if norm_policy == norm_request:
        return True

    policy_syns = _get_synonym_family(policy_val)
    request_syns = _get_synonym_family(request_val)
    return bool(policy_syns & request_syns)


# ---------------------------------------------------------------------------
# Selection Service
# ---------------------------------------------------------------------------

class SelectionService:
    """Deterministic Selection-layer service (0% LLM, 100% mandatory-hold compliance).

    Designed to be injected via the ``PolicyGatePort`` protocol defined in
    ``src.shared.contracts``; extends the existing ``PolicyService`` logic with
    the richer 6-dimension matching required by CRM-G1-SUB14.
    """

    # ------------------------------------------------------------------
    # 1. Governing Date Resolver (DAT 04 / UTC+7)
    # ------------------------------------------------------------------

    def resolve_governing_date_vn(
        self,
        requested_date: date | None,
    ) -> GoverningDateResult:
        """Resolve the governing calendar date in Asia/Ho_Chi_Minh (UTC+7).

        Returns:
            GoverningDateResult with ``is_historical`` / ``is_future_preview`` flags.

        Determinism guarantee:
            No randomness, no I/O, no LLM call.  ``datetime.now`` is seeded only
            from the system clock, which is the only acceptable non-deterministic
            input for date resolution (OPS 03).
        """
        today_vn: date = datetime.now(_VN_TZ).date()
        if requested_date is not None:
            target = requested_date
            resolved_from = "request"
        else:
            target = today_vn
            resolved_from = "system_now"

        return GoverningDateResult(
            governing_date=target,
            timezone=settings.APP_TIMEZONE,
            is_historical=target < today_vn,
            is_future_preview=target > today_vn,
            resolved_from=resolved_from,  # type: ignore[arg-type]
        )

    # ------------------------------------------------------------------
    # 2. 6-Dimension Scope Matcher (DAT 04)
    # ------------------------------------------------------------------

    def match_scope_6dim(
        self,
        candidate: ApplicabilityCandidate,
        dimensions: ScopeDimensions,
    ) -> ScopeMatchResult:
        """Match a single policy version candidate against 6 applicability dimensions.

        The candidate's ``scope`` field is expected to be a semicolon-delimited
        string with key=value pairs, e.g.::

            "company=SONGNHAT_HN;branch=all;role=sales_executive;
             customer_category=b2b;product=3-phase-motor;transaction_scope=quotation"

        Any dimension absent from the candidate scope string is treated as a
        wildcard (matches any request value).  This follows the DAT 04 partial-match
        rule: a policy that does not declare a dimension applies to all values of
        that dimension.

        Returns:
            ScopeMatchResult – ``matched=True`` only when ALL 6 dimensions pass.
        """
        scope_map: dict[str, str] = {}
        for part in candidate.scope.split(";"):
            part = part.strip()
            if "=" in part:
                key, _, val = part.partition("=")
                scope_map[key.strip().lower()] = val.strip().lower()

        dim_values: dict[str, str | None] = {
            "company": dimensions.company,
            "branch": dimensions.branch,
            "role": dimensions.role,
            "customer_category": dimensions.customer_category,
            "product": dimensions.product,
            "transaction_scope": dimensions.transaction_scope,
        }

        unmatched: list[str] = []
        for dim_key in _DIMENSION_KEYS:
            policy_dim_val = scope_map.get(dim_key)
            request_dim_val = dim_values.get(dim_key)
            if not _dim_matches(request_dim_val, policy_dim_val):
                unmatched.append(dim_key)

        return ScopeMatchResult(
            version_id=candidate.version_id,
            matched=len(unmatched) == 0,
            unmatched_dimensions=unmatched,
        )

    def match_scope_6dim_bulk(
        self,
        candidates: list[ApplicabilityCandidate],
        dimensions: ScopeDimensions,
        governing_date: date,
        *,
        allow_historical: bool = False,
        allow_future_preview: bool = False,
    ) -> list[ScopeMatchResult]:
        """Match all candidates against 6 dimensions, pre-filtered by lifecycle + date.

        Only candidates whose lifecycle status is queryable (EFFECTIVE, SUPERSEDED
        when allow_historical, SCHEDULED when allow_future_preview) are evaluated.
        """
        results: list[ScopeMatchResult] = []
        for c in candidates:
            if not self._is_date_eligible(
                c,
                governing_date=governing_date,
                allow_historical=allow_historical,
                allow_future_preview=allow_future_preview,
            ):
                continue
            results.append(self.match_scope_6dim(c, dimensions))
        return results

    # ------------------------------------------------------------------
    # 3. Deterministic Critical-Field Lookup (DAT 06, DAT 08) ≤ 50 rows
    # ------------------------------------------------------------------

    def lookup_critical_fields(
        self,
        request: CriticalFieldLookupRequest,
        all_critical_fields: list[CriticalFieldItem],
    ) -> list[CriticalFieldLookupResult]:
        """Fetch and validate typed critical fields for each applicable version.

        Rules (DAT 06, DAT 08):
        - Only fields whose ``policy_version_id`` is in ``request.version_ids`` are
          returned.
        - Fields with status WITHDRAWN or any unpublished state are excluded.
        - The result is capped at ``settings.CORPUS_MAX_CRITICAL_FIELDS`` (≤ 50).
        - ``has_missing_annotations`` is set True when any matching field has an
          empty ``source_clause`` or empty ``value`` (DAT 08 annotation check).
        - 0% LLM: all logic is pure Python deterministic code.
        """
        cap = settings.CORPUS_MAX_CRITICAL_FIELDS  # ≤ 50
        version_set = set(request.version_ids)
        results: list[CriticalFieldLookupResult] = []

        for version_id in request.version_ids:
            matching: list[CriticalFieldItem] = []
            for cf in all_critical_fields:
                if cf.policy_version_id not in version_set:
                    continue
                if cf.policy_version_id != version_id:
                    continue
                # Exclude non-queryable lifecycle states (DAT 08)
                if cf.status in {
                    PolicyLifecycleStatus.DRAFT,
                    PolicyLifecycleStatus.OWNER_REVIEWED,
                    PolicyLifecycleStatus.APPROVED,
                    PolicyLifecycleStatus.WITHDRAWN,
                    PolicyLifecycleStatus.QUARANTINED,
                    PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
                }:
                    continue
                matching.append(cf)
                if len(matching) >= cap:
                    break

            # DAT 08: annotation completeness check
            missing_ann = [
                cf.field_id
                for cf in matching
                if not cf.source_clause.strip() or not cf.value.strip()
            ]
            has_missing = len(missing_ann) > 0
            missing_detail: str | None = None
            if has_missing:
                missing_detail = (
                    f"DAT 08: {len(missing_ann)} trường thiếu source_clause / value: "
                    + ", ".join(missing_ann[:5])
                    + ("…" if len(missing_ann) > 5 else "")
                )

            results.append(
                CriticalFieldLookupResult(
                    version_id=version_id,
                    fields_found=len(matching),
                    fields=[cf.model_dump() for cf in matching],
                    has_missing_annotations=has_missing,
                    missing_annotation_detail=missing_detail,
                )
            )

        return results

    # ------------------------------------------------------------------
    # 4. Mandatory Hold Gate (DAT 04, DAT 05, DAT 08, OPS 03)
    # ------------------------------------------------------------------

    def evaluate_numeric_threshold(
        self, operator: ComparisonOperator, actual: Decimal, target: str
    ) -> bool:
        """Compute threshold checks deterministically in Python (OPS 04, 0% LLM)."""
        if operator == ComparisonOperator.BETWEEN:
            low_s, high_s = [part.strip() for part in target.split(";", maxsplit=1)]
            return Decimal(low_s) <= actual <= Decimal(high_s)
        bound = Decimal(target.strip())
        comparators = {
            ComparisonOperator.LE: actual <= bound,
            ComparisonOperator.LT: actual < bound,
            ComparisonOperator.GE: actual >= bound,
            ComparisonOperator.GT: actual > bound,
            ComparisonOperator.EQ: actual == bound,
        }
        return comparators.get(operator, False)

    def evaluate_hold(
        self,
        gate_decision: PolicyGateDecision,
        critical_field_results: list[CriticalFieldLookupResult],
        *,
        missing_tables_or_attachments: bool = False,
        missing_attachment_detail: str | None = None,
    ) -> SelectionHoldDecision:
        """Evaluate all mandatory Hold conditions and return a consolidated decision.

        Hold is triggered (OPS 03) for ANY of:
        1. DAT 04 – No governing date rule found (no applicable versions).
        2. DAT 05 – Source conflict detected between overlapping authority tiers.
        3. DAT 08 – Essential table / annotation missing in matched critical fields
           or missing required tables/attachments.

        The pipeline MUST NOT call the LLM if ``must_hold`` is True.
        """
        triggers: list[HoldTrigger] = []

        # --- DAT 04: No applicable policy version ---
        if not gate_decision.applicable_version_ids:
            triggers.append(
                HoldTrigger(
                    code="DAT04_NO_APPLICABLE_VERSION",
                    reason_vi=(
                        "DAT 04 Hold: Không tìm thấy phiên bản chính sách hiệu lực "
                        "cho ngày chi phối; cần chuyển chủ sở hữu chính sách."
                    ),
                )
            )

        # --- DAT 05: Source conflict ---
        if gate_decision.has_conflict:
            triggers.append(
                HoldTrigger(
                    code="DAT05_SOURCE_CONFLICT",
                    reason_vi=(
                        "DAT 05 Hold: Phát hiện hiệu lực chồng lấn hoặc tương tác "
                        "hợp đồng-chính sách chưa có quy tắc ưu tiên được phê duyệt; "
                        "cần chuyển chủ sở hữu chính sách."
                    ),
                )
            )

        # --- DAT 08: Missing table / annotation in critical fields ---
        for cf_result in critical_field_results:
            if cf_result.has_missing_annotations:
                detail = cf_result.missing_annotation_detail or "Thiếu chú thích hoặc bảng nguồn."
                triggers.append(
                    HoldTrigger(
                        code="DAT08_MISSING_TABLE_OR_ANNOTATION",
                        reason_vi=f"DAT 08 Hold [{cf_result.version_id}]: {detail}",
                    )
                )

        # --- DAT 08: Missing essential tables or attachments flag ---
        if missing_tables_or_attachments:
            detail_att = missing_attachment_detail or "Thiếu bảng số liệu hoặc phụ lục bắt buộc."
            triggers.append(
                HoldTrigger(
                    code="DAT08_MISSING_TABLE_OR_ANNOTATION",
                    reason_vi=f"DAT 08 Hold: {detail_att}",
                )
            )

        # --- OPS 03: Propagate gate-level hold (e.g. stale snapshot) ---
        if gate_decision.hold_reason and not gate_decision.can_proceed:
            # Avoid duplicating DAT 04/05 messages already added above
            already_covered = any(
                t.code in {"DAT04_NO_APPLICABLE_VERSION", "DAT05_SOURCE_CONFLICT"}
                for t in triggers
            )
            if not already_covered:
                triggers.append(
                    HoldTrigger(
                        code="OPS03_MANDATORY_HOLD",
                        reason_vi=gate_decision.hold_reason,
                    )
                )

        must_hold = len(triggers) > 0
        combined: str | None = None
        if must_hold:
            combined = " | ".join(t.reason_vi for t in triggers)

        return SelectionHoldDecision(
            must_hold=must_hold,
            triggers=triggers,
            combined_reason_vi=combined,
        )

    # ------------------------------------------------------------------
    # 5. Composite run_selection (full SUB14 pipeline)
    # ------------------------------------------------------------------

    def run_selection(
        self,
        *,
        task_id: str | None = None,
        candidates: list[ApplicabilityCandidate],
        dimensions: ScopeDimensions,
        all_critical_fields: list[CriticalFieldItem],
        gate_decision: PolicyGateDecision,
        requested_date: date | None = None,
        missing_tables_or_attachments: bool = False,
        missing_attachment_detail: str | None = None,
    ) -> SelectionResult:
        """Execute the full Selection layer pipeline deterministically.

        Steps (all 0% LLM):
        1. Resolve governing date (UTC+7).
        2. Match candidates through 6-dimension scope filter.
        3. Lookup typed critical fields (≤ 50 rows, DAT 06).
        4. Evaluate mandatory Hold (DAT 04/05/08, OPS 03).

        Args:
            task_id: Unique request identifier (auto-generated if None).
            candidates: Policy version candidates to evaluate.
            dimensions: 6-dimension request context (DAT 04).
            all_critical_fields: Pre-fetched critical field rows from DB.
            gate_decision: Layer-2 PolicyGateDecision (from PolicyService).
            requested_date: Optional caller-supplied date; falls back to today UTC+7.

        Returns:
            SelectionResult – fully deterministic, llm_used=False always.
        """
        tid = task_id or str(uuid.uuid4())

        # Step 1: Governing date
        date_result = self.resolve_governing_date_vn(requested_date)
        gov_date = date_result.governing_date

        # Step 2: 6-dim scope matching
        scope_matches = self.match_scope_6dim_bulk(
            candidates,
            dimensions,
            gov_date,
            allow_historical=date_result.is_historical,
            allow_future_preview=date_result.is_future_preview,
        )
        applicable_ids = [m.version_id for m in scope_matches if m.matched]

        # Step 3: Critical field lookup for applicable versions
        cf_lookup_results: list[CriticalFieldLookupResult] = []
        if applicable_ids:
            cf_lookup_results = self.lookup_critical_fields(
                CriticalFieldLookupRequest(
                    version_ids=applicable_ids,
                    governing_date=gov_date,
                ),
                all_critical_fields,
            )

        # Step 4: Hold evaluation
        hold_decision = self.evaluate_hold(
            gate_decision,
            cf_lookup_results,
            missing_tables_or_attachments=missing_tables_or_attachments,
            missing_attachment_detail=missing_attachment_detail,
        )

        return SelectionResult(
            task_id=tid,
            governing_date_result=date_result,
            scope_matches=scope_matches,
            applicable_version_ids=applicable_ids,
            critical_field_lookups=cf_lookup_results,
            hold_decision=hold_decision,
            llm_used=False,
            resolved_at=datetime.now(_VN_TZ),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_date_eligible(
        self,
        candidate: ApplicabilityCandidate,
        *,
        governing_date: date,
        allow_historical: bool,
        allow_future_preview: bool,
    ) -> bool:
        """Return True when the candidate's lifecycle and effective window are eligible."""
        status = candidate.status

        # Blocked states
        if status in {
            PolicyLifecycleStatus.DRAFT,
            PolicyLifecycleStatus.OWNER_REVIEWED,
            PolicyLifecycleStatus.APPROVED,
            PolicyLifecycleStatus.WITHDRAWN,
            PolicyLifecycleStatus.QUARANTINED,
            PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
        }:
            return False

        # Scheduled: only allowed for future preview
        if status == PolicyLifecycleStatus.SCHEDULED and not allow_future_preview:
            return False

        # Superseded: only allowed for historical queries
        if status == PolicyLifecycleStatus.SUPERSEDED and not allow_historical:
            return False

        # Effective date window
        eff_from: date = (
            candidate.effective_from.astimezone(_VN_TZ).date()
            if candidate.effective_from.tzinfo is not None
            else candidate.effective_from.replace(tzinfo=_VN_TZ).date()
        )
        if governing_date < eff_from:
            return False

        if candidate.effective_to is not None:
            eff_to: date = (
                candidate.effective_to.astimezone(_VN_TZ).date()
                if candidate.effective_to.tzinfo is not None
                else candidate.effective_to.replace(tzinfo=_VN_TZ).date()
            )
            if governing_date > eff_to:
                return False

        return True
