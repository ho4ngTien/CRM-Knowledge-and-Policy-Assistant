"""Pre-filtered hybrid Vietnamese retrieval service (ANS 02, VN 01)."""

import re

from src.config import settings
from src.modules.knowledge.schemas import PassageSummary
from src.modules.retrieval.models import VIETNAMESE_CRM_SYNONYMS
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import PolicyLifecycleStatus


class RetrievalService:
    """Filters by permission/lifecycle before ranking and preserves Vietnamese negations."""

    def normalize_query_vi(self, query: str) -> tuple[str, list[str]]:
        """Normalize whitespace while preserving digits, negations, and CRM synonyms."""
        cleaned = re.sub(r"\s+", " ", query.strip())
        tokens = re.findall(r"[\w]+", cleaned.lower())
        expanded: list[str] = []
        for token in tokens:
            if token in VIETNAMESE_CRM_SYNONYMS:
                expanded.extend(VIETNAMESE_CRM_SYNONYMS[token])
        return cleaned, list(dict.fromkeys(expanded))

    def prefilter_passages(
        self,
        user: AuthenticatedUser,
        candidates: list[PassageSummary],
        *,
        allow_historical: bool = False,
        allow_future_preview: bool = False,
        top_k: int | None = None,
    ) -> list[PassageSummary]:
        """Enforce RBAC, attachment completeness, and status filtering BEFORE ranking."""
        limit = min(top_k or settings.ANSWER_MAX_PASSAGES, settings.ANSWER_MAX_PASSAGES)
        filtered: list[PassageSummary] = []

        for p in candidates:
            if not check_policy_audience(user, p.audience):
                continue
            if not p.has_essential_attachments:
                continue
            if len(p.content) > settings.PASSAGE_MAX_CHARS:
                continue
            if p.status in {
                PolicyLifecycleStatus.DRAFT,
                PolicyLifecycleStatus.OWNER_REVIEWED,
                PolicyLifecycleStatus.APPROVED,
                PolicyLifecycleStatus.WITHDRAWN,
                PolicyLifecycleStatus.QUARANTINED,
                PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
            }:
                continue
            if p.status == PolicyLifecycleStatus.SCHEDULED and not allow_future_preview:
                continue
            if p.status == PolicyLifecycleStatus.SUPERSEDED and not allow_historical:
                continue
            filtered.append(p)
            if len(filtered) >= limit:
                break

        return filtered
