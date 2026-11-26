"""Post-generation citation, permission, and authoritative withdrawal guard (KNW 04)."""

import re

from src.config import settings
from src.modules.answer.schemas import AnswerPackage
from src.modules.knowledge.schemas import PassageSummary
from src.modules.policy.schemas import CriticalFieldItem
from src.modules.validation.models import ValidationOutcome
from src.modules.validation.schemas import CitationCheckInput
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import (
    AnswerStatus,
    ComparisonOperator,
    CriticalFieldType,
    PolicyLifecycleStatus,
)
from src.shared.exceptions import AccessDenied, CitationValidationFailed, PolicyWithdrawn

_FAIL_CLOSED_HOLD_GUIDANCE_VI = (
    "Không thể xác minh đầy đủ nguồn chính sách hoặc thông số trọng yếu hiện hành; "
    "hệ thống HOLD kết luận an toàn và đề nghị chuyển chủ sở hữu chính sách."
)
_FAIL_CLOSED_STALE_GUIDANCE_VI = (
    "Nguồn chính sách dẫn chiếu đã bị thu hồi hoặc hết hiệu lực trong quá trình xử lý "
    "(KNW 04); kết luận tạm giữ để tránh sử dụng quy định cũ."
)
_EMERGENCY_DISABLE_GUIDANCE_VI = (
    "Trợ lý đang tạm dừng theo chế độ khẩn cấp (OPS 05); vui lòng tra cứu "
    "nguồn CSV nội bộ hoặc liên hệ chủ sở hữu chính sách."
)


def _normalize_numeric_token(text: str) -> str:
    return re.sub(r"[.,_\s]", "", text.lower())


def _contains_numeric_token(normalized_text: str, norm_val: str) -> bool:
    """Match a normalized numeric token only on non-digit boundaries (prevents '5' in '15'/'50')."""
    return bool(re.search(rf"(?<!\d){re.escape(norm_val)}(?!\d)", normalized_text))


_UNPUBLISHED_VALIDATION_STATUSES: frozenset[PolicyLifecycleStatus] = frozenset(
    {
        PolicyLifecycleStatus.DRAFT,
        PolicyLifecycleStatus.OWNER_REVIEWED,
        PolicyLifecycleStatus.APPROVED,
        PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
    }
)


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
            if (
                passage is None
                or passage.document_id != c.document_id
                or passage.document_version_id != c.document_version_id
            ):
                reasons.append(f"Unverified citation document/passage/version: {c.passage_id}")
                continue
            if not check_policy_audience(user, passage.audience):
                raise AccessDenied(f"Audience permission revoked for passage {c.passage_id}.")
            if passage.is_tombstoned or passage.status == PolicyLifecycleStatus.WITHDRAWN:
                stale = True
                reasons.append(f"Source withdrawn or tombstoned mid-answer: {c.passage_id}")
                continue
            if passage.status == PolicyLifecycleStatus.QUARANTINED or (
                not passage.has_essential_attachments
            ):
                stale = True
                reasons.append(f"Source quarantined or incomplete: {c.passage_id}")
                continue
            if passage.status in _UNPUBLISHED_VALIDATION_STATUSES:
                reasons.append(
                    f"Unpublished source cannot be cited ({passage.status.value}): {c.passage_id}"
                )
                continue
            if passage.status == PolicyLifecycleStatus.SCHEDULED and not allow_future_preview:
                reasons.append(f"Scheduled future source cannot govern present: {c.passage_id}")
                continue
            if passage.status == PolicyLifecycleStatus.SUPERSEDED and not allow_historical:
                stale = True
                reasons.append(f"Superseded source without historical mode: {c.passage_id}")
                continue
            quote = c.quoted_text.strip()
            if not quote:
                reasons.append(f"Missing verbatim quoted_text for passage {c.passage_id}")
                continue
            if quote not in passage.content:
                reasons.append(f"Verbatim quote mismatch for passage {c.passage_id}")

        if stale:
            raise PolicyWithdrawn("; ".join(reasons))
        if reasons:
            raise CitationValidationFailed("; ".join(reasons))

        return ValidationOutcome(is_valid=True, is_stale=False, failure_reasons=())

    def verify_critical_fields_integrity(
        self,
        guidance_text: str,
        critical_fields: list[CriticalFieldItem],
    ) -> tuple[str, ...]:
        """Verify deterministic critical fields are active and reflected in guidance."""
        if not critical_fields:
            return ()

        errors: list[str] = []
        normalized_guidance = _normalize_numeric_token(guidance_text)

        for cf in critical_fields:
            if cf.status in (
                {
                    PolicyLifecycleStatus.WITHDRAWN,
                    PolicyLifecycleStatus.QUARANTINED,
                }
                | _UNPUBLISHED_VALIDATION_STATUSES
            ):
                errors.append(
                    f"Critical field {cf.field_id} ({cf.field_name}) is {cf.status.value}."
                )
                continue

            if not guidance_text.strip():
                errors.append(
                    f"Guidance text missing while critical field {cf.field_name} is required."
                )
                continue

            raw_val = cf.value.strip()
            if (
                cf.field_type
                in {
                    CriticalFieldType.NUMBER,
                    CriticalFieldType.CURRENCY,
                    CriticalFieldType.DURATION,
                }
                and raw_val
            ):
                if cf.operator == ComparisonOperator.BETWEEN:
                    if ";" not in raw_val:
                        errors.append(
                            f"Critical field {cf.field_name} BETWEEN value "
                            f"'{raw_val}' is malformed."
                        )
                        continue
                    low_s, high_s = [part.strip() for part in raw_val.split(";", maxsplit=1)]
                    low_norm = _normalize_numeric_token(low_s)
                    high_norm = _normalize_numeric_token(high_s)
                    if (
                        not low_norm
                        or not high_norm
                        or not _contains_numeric_token(normalized_guidance, low_norm)
                        or not _contains_numeric_token(normalized_guidance, high_norm)
                    ):
                        errors.append(
                            f"Critical field {cf.field_name} range '{raw_val}' "
                            "missing or altered in guidance."
                        )
                else:
                    normalized_val = _normalize_numeric_token(raw_val)
                    if normalized_val and not _contains_numeric_token(
                        normalized_guidance, normalized_val
                    ):
                        errors.append(
                            f"Critical field {cf.field_name} value '{raw_val}' "
                            "missing or altered in guidance."
                        )

        return tuple(errors)

    def verify_final_delivery(
        self,
        user: AuthenticatedUser,
        package: AnswerPackage,
        authoritative_passages: dict[str, PassageSummary],
        *,
        emergency_disabled: bool = False,
    ) -> AnswerPackage:
        """Enforce non-streaming, emergency disable, citation state, and critical-field checks."""
        if settings.ENABLE_ANSWER_STREAMING:
            raise ValueError(
                "Pre-verification token streaming is forbidden in Base Scope (KNW 04)."
            )

        if emergency_disabled:
            return self._fail_closed_package(
                package,
                status=AnswerStatus.HOLD,
                reason="OPS 05 Emergency Disable active; live AI delivery blocked.",
                guidance_text=_EMERGENCY_DISABLE_GUIDANCE_VI,
            )

        if package.status not in {AnswerStatus.ANSWERED, AnswerStatus.ANSWERED_WITH_CONDITIONS}:
            return package.model_copy(
                update={
                    "citations": [],
                    "verbatim_quotes": [],
                }
            )

        citation_inputs = [
            CitationCheckInput(
                passage_id=c.passage_id,
                document_id=c.document_id,
                document_version_id=c.document_version_id,
                quoted_text=c.quoted_text,
            )
            for c in package.citations
        ]

        try:
            outcome = self.verify_citations_and_state(
                user,
                citation_inputs,
                authoritative_passages,
                allow_historical=package.is_historical,
                allow_future_preview=package.is_future_preview,
            )
        except PolicyWithdrawn as exc:
            return self._fail_closed_package(
                package,
                status=AnswerStatus.STALE,
                reason=str(exc),
                guidance_text=_FAIL_CLOSED_STALE_GUIDANCE_VI,
                uncertainty_note=(
                    "Nguồn chính sách đã bị thu hồi hoặc hết hiệu lực "
                    "trong quá trình xử lý (KNW 04)."
                ),
            )
        except CitationValidationFailed as exc:
            return self._fail_closed_package(
                package,
                status=AnswerStatus.HOLD,
                reason=str(exc),
                guidance_text=_FAIL_CLOSED_HOLD_GUIDANCE_VI,
            )

        if not outcome.is_valid:
            target_status = AnswerStatus.STALE if outcome.is_stale else AnswerStatus.HOLD
            return self._fail_closed_package(
                package,
                status=target_status,
                reason="; ".join(outcome.failure_reasons),
                guidance_text=(
                    _FAIL_CLOSED_STALE_GUIDANCE_VI
                    if outcome.is_stale
                    else _FAIL_CLOSED_HOLD_GUIDANCE_VI
                ),
            )

        cited_passages = [
            authoritative_passages[c.passage_id]
            for c in package.citations
            if c.passage_id in authoritative_passages
        ]
        for raw_quote in package.verbatim_quotes:
            quote = raw_quote.strip()
            if not quote:
                continue
            if not any(quote in passage.content for passage in cited_passages):
                return self._fail_closed_package(
                    package,
                    status=AnswerStatus.HOLD,
                    reason="Unverified verbatim quote not found in cited authoritative passages.",
                    guidance_text=_FAIL_CLOSED_HOLD_GUIDANCE_VI,
                )

        cf_errors = self.verify_critical_fields_integrity(
            package.guidance_text, package.critical_fields
        )
        if cf_errors:
            return self._fail_closed_package(
                package,
                status=AnswerStatus.HOLD,
                reason="; ".join(cf_errors),
                guidance_text=_FAIL_CLOSED_HOLD_GUIDANCE_VI,
            )

        return package

    def _fail_closed_package(
        self,
        package: AnswerPackage,
        *,
        status: AnswerStatus,
        reason: str,
        guidance_text: str,
        uncertainty_note: str | None = None,
    ) -> AnswerPackage:
        updates: dict[str, object] = {
            "status": status,
            "guidance_text": guidance_text,
            "verbatim_quotes": [],
            "citations": [],
            "critical_fields": [],
            "hold_reason": reason,
            "referral_target": package.referral_target or "policy_owner",
        }
        if uncertainty_note is not None:
            updates["uncertainty_note"] = uncertainty_note
        return package.model_copy(update=updates)
