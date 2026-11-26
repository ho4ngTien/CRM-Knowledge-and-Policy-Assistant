"""FastAPI router for the Selection layer (CRM-G1-SUB14, WP03-Selection)."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.selection.schemas import ScopeDimensions, SelectionResult
from src.modules.selection.service import SelectionService
from src.shared.auth import AuthenticatedUser, get_current_user
from src.shared.contracts import PolicyGateDecision
from src.shared.enums import UserRole

router = APIRouter(tags=["Selection"])

_FUTURE_PREVIEW_ALLOWED_ROLES: frozenset[UserRole] = frozenset(
    {
        UserRole.POLICY_OWNER,
        UserRole.STEWARD,
        UserRole.ADMINISTRATOR,
    }
)


class SelectionRequest(BaseModel):
    """Body for POST /selection/run."""

    task_id: str | None = None
    requested_date: date | None = Field(
        default=None,
        description="Caller-supplied governing date (UTC+7). Falls back to today.",
    )
    dimensions: ScopeDimensions
    candidates: list[ApplicabilityCandidate] = Field(default_factory=list)
    critical_fields: list[CriticalFieldItem] = Field(default_factory=list)
    missing_tables_or_attachments: bool = Field(
        default=False,
        description="Flag indicating missing essential tables or attachments (DAT 08).",
    )
    missing_attachment_detail: str | None = Field(
        default=None,
        description="Detail of missing table or attachment (DAT 08).",
    )
    allow_historical: bool = Field(
        default=True,
        description="Allow query on SUPERSEDED historical versions.",
    )
    allow_future_preview: bool = Field(
        default=False,
        description="Allow preview of SCHEDULED future versions (requires explicit permission).",
    )
    # Caller may supply a pre-computed gate decision from the policy layer
    gate_decision: PolicyGateDecision | None = Field(
        default=None,
        description="Pre-computed Layer-2 gate decision. Auto-synthesised when absent.",
    )


def _synthesise_gate(
    candidates: list[ApplicabilityCandidate],
    requested_date: date | None,
    *,
    allow_future_preview: bool = False,
) -> PolicyGateDecision:
    """Synthesise a minimal PolicyGateDecision when the caller omits one."""
    from src.modules.policy.service import PolicyService

    svc = PolicyService()
    return svc.evaluate_policy_gate(
        candidates,
        requested_date=requested_date,
        allow_future_preview=allow_future_preview,
    )


@router.post(
    "/run",
    response_model=SelectionResult,
    summary="Run Selection layer: Date/6-Dim/CriticalFields/Hold (SUB14)",
    status_code=status.HTTP_200_OK,
)
async def run_selection(
    body: SelectionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> SelectionResult:
    """Execute the full Selection pipeline deterministically (0% LLM).

    Returns a ``SelectionResult`` with:
    - Resolved governing date (UTC+7)
    - 6-dimension scope matches for each candidate
    - Typed critical-field lookup (≤ 50 rows)
    - Mandatory Hold decision (DAT 04/05/08, OPS 03)
    """
    if body.allow_future_preview and not (current_user.roles & _FUTURE_PREVIEW_ALLOWED_ROLES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "FUTURE_PREVIEW_FORBIDDEN: Chỉ policy_owner, steward hoặc "
                "administrator mới được xem trước phiên bản SCHEDULED."
            ),
        )

    gate = body.gate_decision or _synthesise_gate(
        body.candidates,
        body.requested_date,
        allow_future_preview=body.allow_future_preview,
    )

    svc = SelectionService()
    result = svc.run_selection(
        task_id=body.task_id,
        candidates=body.candidates,
        dimensions=body.dimensions,
        all_critical_fields=body.critical_fields,
        gate_decision=gate,
        requested_date=body.requested_date,
        allow_historical=body.allow_historical,
        allow_future_preview=body.allow_future_preview,
        missing_tables_or_attachments=body.missing_tables_or_attachments,
        missing_attachment_detail=body.missing_attachment_detail,
    )
    return result


@router.get(
    "/health",
    summary="Selection layer health (SUB14)",
    status_code=status.HTTP_200_OK,
)
async def selection_health() -> dict[str, str]:
    """Return health confirmation for the Selection layer."""
    return {"status": "ok", "module": "selection", "sub": "CRM-G1-SUB14"}
