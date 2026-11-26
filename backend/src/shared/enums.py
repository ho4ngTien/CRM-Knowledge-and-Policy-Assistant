"""Domain enumerations aligned with the SongNhat CKPA RFP and SRS."""

from enum import StrEnum


class UserRole(StrEnum):
    """Least-privilege organizational roles mandated by SEC 01 & SRS-FR-02.1."""

    READER = "reader"
    STEWARD = "steward"
    POLICY_OWNER = "policy_owner"
    REFERRAL_HANDLER = "referral_handler"
    ADMINISTRATOR = "administrator"
    PRIVACY_SECURITY_OWNER = "privacy_security_owner"
    INDEPENDENT_EVALUATOR = "independent_evaluator"


class PolicyLifecycleStatus(StrEnum):
    """Seven formal lifecycle states plus two governance intake states (KNW 03, KNW 06, DAT 08)."""

    DRAFT = "draft"
    OWNER_REVIEWED = "owner_reviewed"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    EFFECTIVE = "effective"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"
    FEEDBACK_CANDIDATE = "feedback_candidate"
    QUARANTINED = "quarantined"


class PolicyFamily(StrEnum):
    """Three initial Base Scope policy families confirmed at Gate G0 (WP 01)."""

    COMMERCIAL_QUOTING_APPROVAL = "commercial_quoting_approval"
    CUSTOMER_INFO_HANDLING = "customer_info_handling"
    SERVICE_WARRANTY_ROUTING = "service_warranty_routing"


class AnswerStatus(StrEnum):
    """Explicit tri-state/hold outcomes for AnswerPackage (ANS 06, KNW 04, KNW 05)."""

    ANSWERED = "answered"
    ANSWERED_WITH_CONDITIONS = "answered_with_conditions"
    HOLD_AND_REFER = "hold_and_refer"
    HOLD = "hold"
    CLARIFICATION_REQUIRED = "clarification_required"
    REFERRED = "referred"
    STALE = "stale"
    REFUSED_OUT_OF_SCOPE = "refused_out_of_scope"


class FeedbackReason(StrEnum):
    """Five standardized staff feedback categories (KNW 07)."""

    MISSING_SOURCE = "missing_source"
    OUTDATED_RULE = "outdated_rule"
    WRONG_SCOPE = "wrong_scope"
    MISSING_EXCEPTION = "missing_exception"
    REJECTED = "rejected"


class ReferralStatus(StrEnum):
    """Local referral workflow statuses (KNW 05)."""

    REFERRED = "referred"
    OWNER_RESPONDED = "owner_responded"
    CLOSED = "closed"


class ReleaseGate(StrEnum):
    """Five mandatory RFP release gates (DEL 01-06; G3 and G4 remain separate)."""

    G0 = "G0"
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"


class EvalPartition(StrEnum):
    """Chinese Wall evaluation dataset partitions (RFP Section 8 & VN 02)."""

    DEV_60 = "dev_60"
    VAL_40 = "val_40"
    SEALED_100 = "sealed_100"
    CHALLENGES_80 = "challenges_80"


class AuthorityTier(StrEnum):
    """Five separated source authority classes (DAT 03)."""

    POLICY = "policy"
    SOP = "sop"
    MANUFACTURER_TERMS = "manufacturer_terms"
    CUSTOMER_CONTRACT = "customer_contract"
    STAFF_NOTE = "staff_note"


class BatchType(StrEnum):
    """Explicit CSV ingestion batch mode (DAT 02)."""

    FULL_SNAPSHOT = "full_snapshot"
    DELTA = "delta"


class RecordAction(StrEnum):
    """Explicit upsert vs tombstone record intent (DAT 02)."""

    UPSERT = "upsert"
    TOMBSTONE = "tombstone"
    DELETE = "delete"


class CriticalFieldType(StrEnum):
    """Typed critical field categories (DAT 06)."""

    NUMBER = "number"
    CURRENCY = "currency"
    DURATION = "duration"
    ROLE = "role"
    DOCUMENT_LIST = "document_list"
    BOOLEAN = "boolean"
    TEXT_RULE = "text_rule"


class ComparisonOperator(StrEnum):
    """Deterministic threshold comparison operators (DAT 06, OPS 04)."""

    LE = "<="
    LT = "<"
    GE = ">="
    GT = ">"
    EQ = "=="
    IN = "in"
    BETWEEN = "between"
    REQUIRED = "required"
