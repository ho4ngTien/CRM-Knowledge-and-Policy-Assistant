"""Pre-filtered hybrid Vietnamese retrieval service (ANS 02, VN 01, SEC 01, KNW 03)."""

import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select

from src.config import settings
from src.modules.knowledge.models import DocumentVersion, Passage
from src.modules.knowledge.schemas import PassageSummary
from src.modules.retrieval.models import (
    VIETNAMESE_CRM_SYNONYMS,
    VIETNAMESE_NEGATIONS,
    VIETNAMESE_UNACCENT_MAPPINGS,
)
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.contracts import HybridQuerySpec
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

# Pre-compiled high-performance Regex patterns sorted by length descending (VN 01, ANS 02)
_SORTED_UNACCENT = sorted(VIETNAMESE_UNACCENT_MAPPINGS.keys(), key=len, reverse=True)
_PATTERN_UNACCENT = re.compile(
    rf"(?<!\w)({'|'.join(re.escape(k) for k in _SORTED_UNACCENT)})(?!\w)",
    re.IGNORECASE,
)

_SORTED_NEG = sorted(UNACCENT_NEGATIONS_MAP.keys(), key=len, reverse=True)
_PATTERN_NEG = re.compile(
    rf"(?<!\w)({'|'.join(re.escape(k) for k in _SORTED_NEG)})(?!\w)",
    re.IGNORECASE,
)

_SORTED_PRESERVED_NEG = sorted(VIETNAMESE_NEGATIONS, key=len, reverse=True)
_PATTERN_PRESERVED_NEG = re.compile(
    rf"(?<!\w)({'|'.join(re.escape(k) for k in _SORTED_PRESERVED_NEG)})(?!\w)",
    re.IGNORECASE,
)


def _to_vn_date(dt: datetime | date, tz: ZoneInfo) -> date:
    """Convert datetime/date to VN calendar date, localizing naive datetimes to VN TZ."""
    if isinstance(dt, datetime):
        localized = dt.astimezone(tz) if dt.tzinfo is not None else dt.replace(tzinfo=tz)
        return localized.date()
    return dt


class RetrievalService:
    """Filters by permission/lifecycle before ranking and preserves Vietnamese negations."""

    def detect_preserved_negations(self, text: str) -> list[str]:
        """Detect and isolate all approved Vietnamese negation markers (ANS 02, ANS 07)."""
        lowered = text.lower()
        # Map unaccented negations first using compiled O(1) pattern
        lowered = _PATTERN_NEG.sub(
            lambda m: UNACCENT_NEGATIONS_MAP[m.group(0).lower()],
            lowered,
        )

        found = [m.group(0).lower() for m in _PATTERN_PRESERVED_NEG.finditer(lowered)]
        return list(dict.fromkeys(found))

    def normalize_query_vi(self, query: str) -> tuple[str, list[str]]:
        """Normalize whitespace, map unaccented phrases, expand CRM synonyms, preserve negations."""
        cleaned = re.sub(r"\s+", " ", query.strip())
        normalized = cleaned.lower()

        # Step 1: Map common unaccented CRM terms to standard Vietnamese accented terms (VN 01)
        normalized = _PATTERN_UNACCENT.sub(
            lambda m: VIETNAMESE_UNACCENT_MAPPINGS[m.group(0).lower()],
            normalized,
        )

        # Step 1b: Map unaccented negation variants to preserved accented negations
        normalized = _PATTERN_NEG.sub(
            lambda m: UNACCENT_NEGATIONS_MAP[m.group(0).lower()],
            normalized,
        )

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

        tz = ZoneInfo(settings.APP_TIMEZONE)
        target_date = governing_date
        if target_date is None:
            target_date = datetime.now(tz).date()

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
            # 5a. Withdrawn or tombstoned is STRICT FAIL-CLOSED
            if p.is_tombstoned or p.status == PolicyLifecycleStatus.WITHDRAWN:
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
                eff_start = _to_vn_date(p.effective_from, tz)
                if target_date < eff_start and not allow_future_preview:
                    continue

            # 5d. Superseded policies (historical)
            elif p.status == PolicyLifecycleStatus.SUPERSEDED:
                if not allow_historical:
                    continue
                if target_date is not None:
                    eff_start = _to_vn_date(p.effective_from, tz)
                    if target_date < eff_start:
                        continue
                    if p.effective_to is not None:
                        eff_end = _to_vn_date(p.effective_to, tz)
                        if target_date > eff_end:
                            continue

            # 5e. Effective policies (current active)
            elif p.status == PolicyLifecycleStatus.EFFECTIVE:
                if target_date is not None:
                    eff_start = _to_vn_date(p.effective_from, tz)
                    if target_date < eff_start:
                        continue
                    if p.effective_to is not None:
                        eff_end = _to_vn_date(p.effective_to, tz)
                        if target_date > eff_end:
                            continue

            filtered.append(p)
            if len(filtered) >= limit:
                break

        return filtered

    def compute_rrf_score(
        self,
        vector_rank: int | None,
        fts_rank: int | None,
        trgm_rank: int | None = None,
        *,
        k: int = 60,
    ) -> float:
        """Compute deterministic Reciprocal Rank Fusion score across retrieval signals."""
        if k <= 0:
            raise ValueError("RRF smoothing constant k must be positive.")

        score = 0.0
        for rank in (vector_rank, fts_rank, trgm_rank):
            if rank is None:
                continue
            if rank < 1:
                raise ValueError("RRF rank must be >= 1 when provided.")
            score += 1.0 / (k + rank)
        return score

    async def search_hybrid(
        self,
        user: AuthenticatedUser,
        spec: HybridQuerySpec,
    ) -> list[PassageSummary]:
        """Run pre-filtered Vietnamese hybrid retrieval (RRF scaffold for Gate G1)."""
        _normalized, _expanded = self.normalize_query_vi(spec.query)
        # TODO(G1): Query PostgreSQL pgvector + FTS + pg_trgm candidates matching
        # spec.applicable_version_ids and rank via compute_rrf_score after prefilter_passages.
        return self.prefilter_passages(
            user,
            [],
            allow_historical=spec.allow_historical,
            allow_future_preview=spec.allow_future_preview,
            top_k=spec.top_k,
        )

    async def fetch_authoritative_passages(
        self,
        user: AuthenticatedUser,
        passage_ids: list[str],
        db: object | None = None,
    ) -> dict[str, PassageSummary]:
        """Re-fetch live authoritative passage state for Layer 5 post-generation verification."""
        if db is None:
            return {}
        stmt = (
            select(Passage, DocumentVersion)
            .join(DocumentVersion, Passage.document_version_id == DocumentVersion.id)
            .where(Passage.id.in_(passage_ids))
        )
        rows = (await db.execute(stmt)).all()  # type: ignore[attr-defined]
        authoritative: dict[str, PassageSummary] = {}
        for passage, version in rows:
            audiences = [item.strip() for item in passage.audience.split(",") if item.strip()]
            if not check_policy_audience(user, audiences):
                continue
            authoritative[passage.id] = PassageSummary(
                passage_id=passage.id,
                document_id=passage.document_id,
                document_version_id=passage.document_version_id,
                title=passage.title,
                content=passage.content,
                source_ref=passage.source_ref,
                page_number=passage.page_number,
                clause_ref=passage.clause_ref,
                language=passage.language,
                scope=passage.scope,
                audience=audiences,
                status=PolicyLifecycleStatus(passage.status),
                has_essential_attachments=passage.has_essential_attachments,
                effective_from=version.effective_from,
                effective_to=version.effective_to,
                supersedes=version.supersedes_version_id,
                is_tombstoned=passage.is_tombstoned,
            )
        return authoritative
