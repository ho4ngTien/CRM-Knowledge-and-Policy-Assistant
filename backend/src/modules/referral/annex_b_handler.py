"""Annex B 9-Scenario Hold & Local Referral Handler (CKPA-92 / G2-AC01).

Maps the 9 Annex B feature contracts (SC-01..SC-09 / B-01..B-09) in
CKPA-29_SUB19_AnnexB_9_Feature_Contracts_Matrix.csv to deterministic HOLD codes,
accountable owner roles, PII-free minimal context, and KNW 05 Local Referrals.

Invariants:
- 100% Hold/exception outcomes create a Local Referral in state `referred`.
- 0% CRM writeback, 0% message dispatch, 0% auto-approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.referral.schemas import (
    AnnexBHandlingResult,
    AnnexBReferralRequest,
    ReferralCreateRequest,
)
from src.modules.referral.service import ReferralService
from src.shared.auth import AuthenticatedUser
from src.shared.enums import AnswerStatus, PolicyFamily
from src.shared.exceptions import PolicyNotFound

_REFERRAL_TRIGGER_STATUSES: frozenset[str] = frozenset(
    {
        AnswerStatus.HOLD.value,
        AnswerStatus.CLARIFICATION_REQUIRED.value,
        AnswerStatus.REFERRED.value,
        AnswerStatus.STALE.value,
        AnswerStatus.REFUSED_OUT_OF_SCOPE.value,
    }
)


class AnnexBCaseId(StrEnum):
    """Canonical Annex B scenario identifiers (SC-01..SC-09 / B-01..B-09)."""

    SC_01 = "SC-01"
    SC_02 = "SC-02"
    SC_03 = "SC-03"
    SC_04 = "SC-04"
    SC_05 = "SC-05"
    SC_06 = "SC-06"
    SC_07 = "SC-07"
    SC_08 = "SC-08"
    SC_09 = "SC-09"


@dataclass(frozen=True, slots=True)
class AnnexBContract:
    """Feature contract metadata aligned with CKPA-29 Annex B matrix."""

    case_id: AnnexBCaseId
    matrix_id: str
    rfp_map_id: str
    feature_name: str
    policy_family: PolicyFamily
    canonical_scope: str
    default_hold_reason: str
    allowed_hold_reasons: frozenset[str]
    owner_role: str
    target_owner: str
    mandatory_referral_on_exception: bool = True


ANNEX_B_CONTRACTS: dict[AnnexBCaseId, AnnexBContract] = {
    AnnexBCaseId.SC_01: AnnexBContract(
        case_id=AnnexBCaseId.SC_01,
        matrix_id="B-01",
        rfp_map_id="RFP-ANXB-01",
        feature_name="General CRM question",
        policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
        canonical_scope=(
            "company:SN;branch:all;role:sales;customer_category:b2b_enterprise;"
            "product:industrial;transaction_scope:quotation_standard"
        ),
        default_hold_reason="HOLD_ANS06",
        allowed_hold_reasons=frozenset({"HOLD_ANS06"}),
        owner_role="policy_owner",
        target_owner="p2-huu-tai",
    ),
    AnnexBCaseId.SC_02: AnnexBContract(
        case_id=AnnexBCaseId.SC_02,
        matrix_id="B-02",
        rfp_map_id="RFP-ANXB-02",
        feature_name="Commercial exception",
        policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
        canonical_scope=(
            "company:SN;branch:all;role:sales;customer_category:b2b_enterprise;"
            "product:industrial;transaction_scope:quotation_exception"
        ),
        default_hold_reason="HOLD_ANS07",
        allowed_hold_reasons=frozenset({"HOLD_ANS06", "HOLD_ANS07"}),
        owner_role="policy_owner",
        target_owner="p2-huu-tai",
    ),
    AnnexBCaseId.SC_03: AnnexBContract(
        case_id=AnnexBCaseId.SC_03,
        matrix_id="B-03",
        rfp_map_id="RFP-ANXB-03",
        feature_name="Dated transaction",
        policy_family=PolicyFamily.SERVICE_WARRANTY_ROUTING,
        canonical_scope=(
            "company:SN;branch:all;role:cskh;customer_category:b2b_factory;"
            "product:motor_3phase;transaction_scope:warranty_intake"
        ),
        default_hold_reason="HOLD_ANS06",
        allowed_hold_reasons=frozenset({"HOLD_ANS06", "HOLD_DAT05"}),
        owner_role="policy_owner",
        target_owner="p2-huu-tai",
    ),
    AnnexBCaseId.SC_04: AnnexBContract(
        case_id=AnnexBCaseId.SC_04,
        matrix_id="B-04",
        rfp_map_id="RFP-ANXB-04",
        feature_name="Scheduled replacement",
        policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
        canonical_scope=(
            "company:SN;branch:all;role:sales;customer_category:b2b_distributor;"
            "product:industrial;transaction_scope:quotation_standard"
        ),
        default_hold_reason="HOLD_DAT05",
        allowed_hold_reasons=frozenset({"HOLD_DAT05", "HOLD_ANS06"}),
        owner_role="steward",
        target_owner="p3-chi-kha",
    ),
    AnnexBCaseId.SC_05: AnnexBContract(
        case_id=AnnexBCaseId.SC_05,
        matrix_id="B-05",
        rfp_map_id="RFP-ANXB-05",
        feature_name="Conflicting contract",
        policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
        canonical_scope=(
            "company:SN;branch:all;role:sales;customer_category:b2b_enterprise;"
            "product:industrial;transaction_scope:quotation_exception"
        ),
        default_hold_reason="HOLD_DAT05",
        allowed_hold_reasons=frozenset({"HOLD_DAT05"}),
        owner_role="policy_owner",
        target_owner="p2-huu-tai",
    ),
    AnnexBCaseId.SC_06: AnnexBContract(
        case_id=AnnexBCaseId.SC_06,
        matrix_id="B-06",
        rfp_map_id="RFP-ANXB-06",
        feature_name="Old CRM note",
        policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
        canonical_scope=(
            "company:SN;branch:all;role:sales;customer_category:b2b_enterprise;"
            "product:industrial;transaction_scope:quotation_exception"
        ),
        default_hold_reason="HOLD_ANS07",
        allowed_hold_reasons=frozenset({"HOLD_ANS07", "HOLD_DAT05"}),
        owner_role="policy_owner",
        target_owner="p2-huu-tai",
    ),
    AnnexBCaseId.SC_07: AnnexBContract(
        case_id=AnnexBCaseId.SC_07,
        matrix_id="B-07",
        rfp_map_id="RFP-ANXB-07",
        feature_name="Missing footnote",
        policy_family=PolicyFamily.COMMERCIAL_QUOTING_APPROVAL,
        canonical_scope=(
            "company:SN;branch:all;role:sales;customer_category:b2b_project;"
            "product:inverter_mv;transaction_scope:quotation_exception"
        ),
        default_hold_reason="HOLD_DAT08",
        allowed_hold_reasons=frozenset({"HOLD_DAT08"}),
        owner_role="steward",
        target_owner="p3-chi-kha",
    ),
    AnnexBCaseId.SC_08: AnnexBContract(
        case_id=AnnexBCaseId.SC_08,
        matrix_id="B-08",
        rfp_map_id="RFP-ANXB-08",
        feature_name="Data correction",
        policy_family=PolicyFamily.CUSTOMER_INFO_HANDLING,
        canonical_scope=(
            "company:SN;branch:all;role:crm;customer_category:b2b_enterprise;"
            "product:all;transaction_scope:crm_legal_update"
        ),
        default_hold_reason="HOLD_ANS07",
        allowed_hold_reasons=frozenset({"HOLD_ANS07", "HOLD_DAT08", "HOLD_DAT05"}),
        owner_role="policy_owner",
        target_owner="p2-huu-tai",
    ),
    AnnexBCaseId.SC_09: AnnexBContract(
        case_id=AnnexBCaseId.SC_09,
        matrix_id="B-09",
        rfp_map_id="RFP-ANXB-09",
        feature_name="Withdrawal mid answer",
        policy_family=PolicyFamily.SERVICE_WARRANTY_ROUTING,
        canonical_scope=(
            "company:SN;branch:all;role:cskh;customer_category:b2b_factory;"
            "product:inverter_mv;transaction_scope:warranty_tier2_vendor"
        ),
        default_hold_reason="HOLD_SEC05",
        allowed_hold_reasons=frozenset({"HOLD_SEC05"}),
        owner_role="policy_owner",
        target_owner="p2-huu-tai",
    ),
}

_CASE_ALIAS_MAP: dict[str, AnnexBCaseId] = {
    **{c.value: c for c in AnnexBCaseId},
    **{spec.matrix_id: cid for cid, spec in ANNEX_B_CONTRACTS.items()},
    **{spec.rfp_map_id: cid for cid, spec in ANNEX_B_CONTRACTS.items()},
}


def resolve_annex_b_contract(case_id: str) -> AnnexBContract:
    """Resolve an Annex B contract from SC-01..SC-09, B-01..B-09, or RFP-ANXB-01..09."""
    normalized = case_id.strip().upper()
    cid = _CASE_ALIAS_MAP.get(normalized)
    if cid is None:
        raise PolicyNotFound(f"Unknown Annex B contract id: {case_id!r}.")
    return ANNEX_B_CONTRACTS[cid]


class AnnexBReferralHandler:
    """Deterministic handler routing Hold/exception events across 9 Annex B contracts."""

    def __init__(self, referral_service: ReferralService | None = None) -> None:
        self._referral_service = referral_service or ReferralService()

    def classify_hold_reason(
        self,
        contract: AnnexBContract,
        request: AnnexBReferralRequest,
    ) -> str:
        """Select canonical HOLD code for the Annex B scenario without LLM guessing."""
        if request.hold_reason:
            upper_reason = request.hold_reason.strip().upper()
            if upper_reason in contract.allowed_hold_reasons:
                return upper_reason

        if request.is_withdrawn or request.answer_status == AnswerStatus.STALE.value:
            if "HOLD_SEC05" in contract.allowed_hold_reasons:
                return "HOLD_SEC05"
        if not request.has_essential_attachments and "HOLD_DAT08" in contract.allowed_hold_reasons:
            return "HOLD_DAT08"
        if request.has_contract_conflict and "HOLD_DAT05" in contract.allowed_hold_reasons:
            return "HOLD_DAT05"
        if (
            request.is_auto_approve_request
            or request.is_crm_writeback_request
            or request.is_staff_note_rule_request
            or request.answer_status == AnswerStatus.REFUSED_OUT_OF_SCOPE.value
        ) and "HOLD_ANS07" in contract.allowed_hold_reasons:
            return "HOLD_ANS07"
        return contract.default_hold_reason

    def build_minimal_context(
        self,
        contract: AnnexBContract,
        request: AnnexBReferralRequest,
        hold_reason: str,
    ) -> dict[str, Any]:
        """Build minimal non-PII escalation context for KNW 05 referral storage."""
        return {
            "case_id": contract.case_id.value,
            "matrix_id": contract.matrix_id,
            "rfp_map_id": contract.rfp_map_id,
            "feature_name": contract.feature_name,
            "scope": request.scope or contract.canonical_scope,
            "governing_date": request.governing_date,
            "answer_status": request.answer_status,
            "hold_reason": hold_reason,
            "missing_facts": list(request.missing_facts),
            "source_refs": list(request.source_refs),
            "crm_writeback": False,
            "external_message_sent": False,
            "auto_approved": False,
        }

    async def handle_case(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        request: AnnexBReferralRequest,
    ) -> AnnexBHandlingResult:
        """Evaluate an Annex B scenario and persist a KNW 05 Local Referral when on Hold."""
        contract = resolve_annex_b_contract(request.case_id)
        normalized_status = request.answer_status.strip().lower()
        is_exception = (
            normalized_status in _REFERRAL_TRIGGER_STATUSES
            or not request.has_essential_attachments
            or request.has_contract_conflict
            or request.is_staff_note_rule_request
            or request.is_crm_writeback_request
            or request.is_auto_approve_request
            or request.is_withdrawn
        )

        if not is_exception:
            return AnnexBHandlingResult(
                case_id=contract.case_id.value,
                matrix_id=contract.matrix_id,
                rfp_map_id=contract.rfp_map_id,
                referral_created=False,
                hold_reason=None,
                owner_role=contract.owner_role,
                target_owner=contract.target_owner,
                referral=None,
                crm_writeback_count=0,
                messages_dispatched=0,
                auto_approved=False,
            )

        hold_reason = self.classify_hold_reason(contract, request)
        minimal_context = self.build_minimal_context(contract, request, hold_reason)
        referral = await self._referral_service.create_referral(
            db,
            user,
            ReferralCreateRequest(
                task_id=request.task_id,
                answer_package_id=request.answer_package_id,
                owner_role=contract.owner_role,
                target_owner=contract.target_owner,
                policy_family=contract.policy_family,
                question_summary=request.question,
                minimal_context=minimal_context,
                hold_reason=hold_reason,
            ),
        )
        return AnnexBHandlingResult(
            case_id=contract.case_id.value,
            matrix_id=contract.matrix_id,
            rfp_map_id=contract.rfp_map_id,
            referral_created=True,
            hold_reason=hold_reason,
            owner_role=contract.owner_role,
            target_owner=contract.target_owner,
            referral=referral,
            crm_writeback_count=0,
            messages_dispatched=0,
            auto_approved=False,
        )
