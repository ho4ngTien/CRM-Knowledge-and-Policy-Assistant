"""Post-generation citation, permission, and authoritative withdrawal guard (KNW 04)."""

from src.modules.knowledge.schemas import PassageSummary
from src.modules.validation.models import ValidationOutcome
from src.modules.validation.schemas import CitationCheckInput
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import PolicyLifecycleStatus
from src.shared.exceptions import AccessDenied, CitationValidationFailed, PolicyWithdrawn


class ValidationService:
    """Blocks delivery if any citation is unverified, unauthorized, or withdrawn mid-flight."""

    def verify_citations_and_state(
        self,
        user: AuthenticatedUser,
        citations: list[CitationCheckInput],
        authoritative_passages: dict[str, PassageSummary],
        *,
        allow_historical: bool = False,
        allow_future_preview: bool = False,
    ) -> ValidationOutcome:
        """Execute final DB/state re-check prior to releasing AnswerPackage (Worked Case 9)."""
        if not citations:
            return ValidationOutcome(
                is_valid=False,
                is_stale=False,
                failure_reasons=("Citation missing: cannot emit factual answer without evidence.",),
            )

        reasons: list[str] = []
        stale = False

        for c in citations:
            passage = authoritative_passages.get(c.passage_id)
            if passage is None or passage.document_version_id != c.document_version_id:
                reasons.append(f"Unverified citation passage/version: {c.passage_id}")
                continue
            if not check_policy_audience(user, passage.audience):
                raise AccessDenied(f"Audience permission revoked for passage {c.passage_id}.")
            if passage.status == PolicyLifecycleStatus.WITHDRAWN:
                stale = True
                reasons.append(f"Source withdrawn mid-answer: {c.passage_id}")
                continue
            if passage.status == PolicyLifecycleStatus.QUARANTINED or (
                not passage.has_essential_attachments
            ):
                stale = True
                reasons.append(f"Source quarantined or incomplete: {c.passage_id}")
                continue
            if passage.status == PolicyLifecycleStatus.SCHEDULED and not allow_future_preview:
                reasons.append(f"Scheduled future source cannot govern present: {c.passage_id}")
                continue
            if passage.status == PolicyLifecycleStatus.SUPERSEDED and not allow_historical:
                stale = True
                reasons.append(f"Superseded source without historical mode: {c.passage_id}")
                continue
            if c.quoted_text.strip() and c.quoted_text.strip() not in passage.content:
                reasons.append(f"Verbatim quote mismatch for passage {c.passage_id}")

        if stale:
            raise PolicyWithdrawn("; ".join(reasons))
        if reasons:
            raise CitationValidationFailed("; ".join(reasons))

        return ValidationOutcome(is_valid=True, is_stale=False, failure_reasons=())
