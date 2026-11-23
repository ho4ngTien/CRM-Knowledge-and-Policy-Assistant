"""Shared 5-layer architecture value objects and runtime-checkable module ports."""

from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.answer.schemas import AnswerCitation, AnswerPackage
from src.modules.knowledge.schemas import PassageSummary
from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.shared.auth import AuthenticatedUser


@dataclass(frozen=True, slots=True)
class QuotaStatus:
    """Common Bid Basis monthly package and LLM call budget check (OPS 06)."""

    month_key: str
    packages_used: int
    package_quota: int
    llm_calls_used: int
    llm_call_quota: int
    allowed: bool
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class PolicyGateDecision:
    """Layer 2 deterministic applicability, conflict, and critical-field gate result."""

    governing_date: date
    timezone: str
    is_historical: bool
    is_future_preview: bool
    applicable_version_ids: tuple[str, ...]
    has_conflict: bool
    can_proceed: bool
    hold_reason: str | None = None
    critical_fields: tuple[CriticalFieldItem, ...] = ()
    snapshot_age_hours: float | None = None
    is_snapshot_stale: bool = False


@dataclass(frozen=True, slots=True)
class HybridQuerySpec:
    """Layer 3 pre-filtered Vietnamese hybrid retrieval specification (ANS 02, VN 01)."""

    query: str
    governing_date: date | None = None
    scope_filter: str | None = None
    applicable_version_ids: tuple[str, ...] = ()
    allow_historical: bool = False
    allow_future_preview: bool = False
    top_k: int = 8


@dataclass(frozen=True, slots=True)
class LLMGenerationRequest:
    """Layer 4 bounded, prompt-isolated generation payload (ANS 04, ANS 08)."""

    task_id: str
    question: str
    system_prompt: str
    user_prompt_envelope: str
    governing_date: date
    passages: tuple[PassageSummary, ...]
    critical_fields: tuple[CriticalFieldItem, ...] = ()
    max_input_tokens: int = 6000
    max_output_tokens: int = 900
    timeout_seconds: int = 20


@dataclass(frozen=True, slots=True)
class LLMGenerationResult:
    """Layer 4 raw LLM response prior to Layer 5 deterministic validation."""

    guidance_text: str
    verbatim_quotes: tuple[str, ...] = ()
    citations: tuple[AnswerCitation, ...] = ()
    missing_facts: tuple[str, ...] = ()
    hold_reason: str | None = None
    uncertainty_note: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    llm_calls_used: int = 1
    model_name: str = ""


@runtime_checkable
class PolicyGatePort(Protocol):
    """Layer 2 port for VN governing date, applicability conflict hold, and critical fields."""

    def resolve_governing_date_vn(self, requested_date: date | None) -> tuple[date, bool, bool]: ...

    def evaluate_policy_gate(
        self,
        candidates: list[ApplicabilityCandidate],
        *,
        requested_date: date | None = None,
        allow_future_preview: bool = False,
        critical_fields: list[CriticalFieldItem] | None = None,
        snapshot_age_hours: float | None = None,
        is_snapshot_stale: bool = False,
    ) -> PolicyGateDecision: ...


@runtime_checkable
class RetrievalPort(Protocol):
    """Layer 3 port for permission-prefiltered hybrid Vietnamese retrieval."""

    def compute_rrf_score(
        self,
        vector_rank: int | None,
        fts_rank: int | None,
        trgm_rank: int | None = None,
        *,
        k: int = 60,
    ) -> float: ...

    async def search_hybrid(
        self,
        user: AuthenticatedUser,
        spec: HybridQuerySpec,
    ) -> list[PassageSummary]: ...

    async def fetch_authoritative_passages(
        self,
        user: AuthenticatedUser,
        passage_ids: list[str],
        db: object | None = None,
    ) -> dict[str, PassageSummary]: ...


@runtime_checkable
class LLMGeneratorPort(Protocol):
    """Layer 4 port for bounded non-streamed constrained RAG generation (Gate G1)."""

    async def generate(self, request: LLMGenerationRequest) -> LLMGenerationResult: ...


@runtime_checkable
class ValidationGatePort(Protocol):
    """Layer 5 port for post-generation citation, permission, and withdrawal checks."""

    def verify_critical_fields_integrity(
        self,
        guidance_text: str,
        critical_fields: list[CriticalFieldItem],
    ) -> tuple[str, ...]: ...

    def verify_final_delivery(
        self,
        user: AuthenticatedUser,
        package: AnswerPackage,
        authoritative_passages: dict[str, PassageSummary],
        *,
        emergency_disabled: bool = False,
    ) -> AnswerPackage: ...


@runtime_checkable
class AuditMeterPort(Protocol):
    """Layer 5 / OPS 06 port for monthly quota enforcement, cost metering, and audit logging."""

    async def check_monthly_quota(
        self,
        db: AsyncSession | None = None,
        month_key: str | None = None,
    ) -> QuotaStatus: ...

    async def record_usage_meter(
        self,
        db: AsyncSession | None = None,
        *,
        task_id: str,
        answer_package_id: str | None = None,
        llm_calls: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        is_hold: bool = False,
        is_error: bool = False,
        estimated_cost_vnd: float = 0.0,
    ) -> None: ...

    async def record_audit_event(
        self,
        db: AsyncSession | None = None,
        *,
        actor_id: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        outcome: str,
        detail: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None: ...


@runtime_checkable
class CachePurgePort(Protocol):
    """Port for invalidating cached retrieval/answer entries within <= 5 minutes (KNW 04)."""

    async def purge_policy_caches(
        self,
        policy_version_id: str,
        document_version_id: str,
    ) -> int: ...
