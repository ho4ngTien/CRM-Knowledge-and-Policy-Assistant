"""Pre-filtered hybrid Vietnamese retrieval service (ANS 02, VN 01, SEC 01, KNW 03)."""

from datetime import date, datetime
import re
from zoneinfo import ZoneInfo

from src.config import settings
from src.modules.knowledge.schemas import PassageSummary
from src.modules.retrieval.models import (
    VIETNAMESE_CRM_SYNONYMS,
    VIETNAMESE_NEGATIONS,
    VIETNAMESE_UNACCENT_MAPPINGS,
)
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import PolicyLifecycleStatus

UNACCENT_NEGATIONS_MAP: dict[str, str] = {
    "khong duoc": "không được",
    "khong ap dung": "không áp dụng",
    "ngoai tru": "ngoại trừ",
    "loai tru": "loại trừ",
    "vang mat": "vắng mặt",
    "tu choi": "từ chối",
    "khong": "không",
    "chua": "chưa",
    "chang": "chẳng",
    "mien": "miễn",
    "ngoai": "ngoài",
    "cam": "cấm",
    "thieu": "thiếu",
    "huy": "hủy",
}


class RetrievalService:
    """Filters by permission/lifecycle before ranking and preserves Vietnamese negations."""

    def detect_preserved_negations(self, text: str) -> list[str]:
        """Detect and isolate all approved Vietnamese negation markers (ANS 02, ANS 07)."""
        lowered = text.lower()
        # Map unaccented negations first
        for unacc, acc in UNACCENT_NEGATIONS_MAP.items():
            pattern = rf"(?<!\w){re.escape(unacc)}(?!\w)"
            if re.search(pattern, lowered):
                lowered = re.sub(pattern, acc, lowered)

        found: list[str] = []
        for neg in VIETNAMESE_NEGATIONS:
            pattern = rf"(?<!\w){re.escape(neg)}(?!\w)"
            if re.search(pattern, lowered):
                found.append(neg)
        return list(dict.fromkeys(found))

    def normalize_query_vi(self, query: str) -> tuple[str, list[str]]:
        """Normalize whitespace, map unaccented phrases, expand CRM synonyms, and preserve negations."""
        cleaned = re.sub(r"\s+", " ", query.strip())
        normalized = cleaned.lower()

        # Step 1: Map common unaccented CRM terms to standard Vietnamese accented terms (VN 01)
        for unaccent, accented in VIETNAMESE_UNACCENT_MAPPINGS.items():
            pattern = rf"(?<!\w){re.escape(unaccent)}(?!\w)"
            if re.search(pattern, normalized):
                normalized = re.sub(pattern, accented, normalized)

        # Step 1b: Map unaccented negation variants to preserved accented negations
        for unacc, acc in UNACCENT_NEGATIONS_MAP.items():
            pattern = rf"(?<!\w){re.escape(unacc)}(?!\w)"
            if re.search(pattern, normalized):
                normalized = re.sub(pattern, acc, normalized)

        # Step 2: Tokenize and expand approved CRM abbreviations (42 entries in glossary)
        tokens = re.findall(r"[\w]+", normalized)
        expanded: list[str] = []
        for token in tokens:
            if token in VIETNAMESE_CRM_SYNONYMS:
                expanded.extend(VIETNAMESE_CRM_SYNONYMS[token])

        # Step 3: Explicit preservation guarantee - negations are preserved and never stripped
        return normalized, list(dict.fromkeys(expanded))

    def normalize_query_vi_full(self, query: str) -> dict[str, object]:
        """Full audit normalization payload including detected negations (ANS 02)."""
        normalized_query, expanded = self.normalize_query_vi(query)
        negations = self.detect_preserved_negations(query)
        return {
            "original_query": query,
            "normalized_query": normalized_query,
            "expanded_terms": expanded,
            "preserved_negations": negations,
        }

    def prefilter_passages(
        self,
        user: AuthenticatedUser,
        candidates: list[PassageSummary],
        *,
        governing_date: date | None = None,
        scope_filter: str | None = None,
        allow_historical: bool = False,
        allow_future_preview: bool = False,
        top_k: int | None = None,
    ) -> list[PassageSummary]:
        """Enforce RBAC (SEC 01) and strict 7 lifecycle states (KNW 03) BEFORE ranking.
        
        Zero percent leakage guarantee:
        - 4 RBAC Roles: reader, policy_owner, steward, administrator
        - 7 KNW 03 States:
            * Effective: Only active valid version allowed
            * Scheduled: Blocked unless explicit future preview requested
            * Superseded: Blocked unless explicit historical query within validity window
            * Draft, Owner reviewed, Approved: 100% blocked (unpublished)
            * Withdrawn: 100% strictly blocked (fail-closed, emergency withdrawal)
            * Quarantined, Feedback candidate: 100% blocked
        """
        limit = min(top_k or settings.ANSWER_MAX_PASSAGES, settings.ANSWER_MAX_PASSAGES)
        filtered: list[PassageSummary] = []

        target_date = governing_date
        if target_date is None:
            now_tz = datetime.now(ZoneInfo(settings.APP_TIMEZONE))
            target_date = now_tz.date()

        for p in candidates:
            # 1. RBAC & Audience Isolation (SEC 01)
            if not check_policy_audience(user, p.audience):
                continue

            # 2. Complete attachments check (DAT 08)
            if not p.has_essential_attachments:
                continue

            # 3. Maximum character bounding (SRS limit <= 6000 chars)
            if len(p.content) > settings.PASSAGE_MAX_CHARS:
                continue

            # 4. Scope matching (if provided)
            if scope_filter:
                clean_scope_filter = scope_filter.strip().lower()
                clean_p_scope = p.scope.strip().lower()
                if clean_scope_filter not in clean_p_scope and clean_p_scope != "all":
                    continue

            # 5. Strict 7-State Policy Lifecycle Filtering (KNW 03)
            # 5a. Withdrawn is STRICT FAIL-CLOSED (Cấm tuyệt đối - không thể bypass)
            if p.status == PolicyLifecycleStatus.WITHDRAWN:
                continue

            # 5b. Ingestion / Governance / Pre-publication states are 100% rejected
            if p.status in {
                PolicyLifecycleStatus.DRAFT,
                PolicyLifecycleStatus.OWNER_REVIEWED,
                PolicyLifecycleStatus.APPROVED,
                PolicyLifecycleStatus.QUARANTINED,
                PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
            }:
                continue

            # 5c. Scheduled policies (future)
            if p.status == PolicyLifecycleStatus.SCHEDULED:
                if not allow_future_preview:
                    continue
                eff_start = p.effective_from.date() if isinstance(p.effective_from, datetime) else p.effective_from
                if target_date < eff_start and not allow_future_preview:
                    continue

            # 5d. Superseded policies (historical)
            elif p.status == PolicyLifecycleStatus.SUPERSEDED:
                if not allow_historical:
                    continue
                if target_date is not None:
                    eff_start = p.effective_from.date() if isinstance(p.effective_from, datetime) else p.effective_from
                    if target_date < eff_start:
                        continue
                    if p.effective_to is not None:
                        eff_end = p.effective_to.date() if isinstance(p.effective_to, datetime) else p.effective_to
                        if target_date > eff_end:
                            continue

            # 5e. Effective policies (current active)
            elif p.status == PolicyLifecycleStatus.EFFECTIVE:
                if target_date is not None:
                    eff_start = p.effective_from.date() if isinstance(p.effective_from, datetime) else p.effective_from
                    if target_date < eff_start:
                        continue
                    if p.effective_to is not None:
                        eff_end = p.effective_to.date() if isinstance(p.effective_to, datetime) else p.effective_to
                        if target_date > eff_end:
                            continue

            filtered.append(p)
            if len(filtered) >= limit:
                break

        return filtered
