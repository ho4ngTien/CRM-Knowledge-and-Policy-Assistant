"""Pydantic schemas for Chinese-Wall evaluation runs and Section 8 threshold gates."""

from pydantic import BaseModel, Field

from src.shared.enums import EvalPartition, ReleaseGate


class EvaluationRunCreateRequest(BaseModel):
    """Submit isolated partition metrics (never mixes challenges with real_200)."""

    release_gate: ReleaseGate
    partition: EvalPartition
    total_cases: int = Field(..., ge=1, le=200)
    critical_control_errors: int = Field(..., ge=0)
    applicability_rate: float = Field(..., ge=0.0, le=1.0)
    grounding_rate: float = Field(..., ge=0.0, le=1.0)
    completeness_rate: float = Field(..., ge=0.0, le=1.0)
    recall_at_5: float = Field(..., ge=0.0, le=1.0)
    usefulness_rate: float = Field(..., ge=0.0, le=1.0)
    fabrication_on_unanswerable_rate: float = Field(..., ge=0.0, le=1.0)
    notes: str | None = Field(default=None, max_length=2000)


class EvaluationRunResponse(BaseModel):
    """Evaluation summary with explicit Section 8 threshold pass/fail checks."""

    id: str
    release_gate: ReleaseGate
    partition: EvalPartition
    total_cases: int
    critical_control_errors: int
    applicability_rate: float
    grounding_rate: float
    completeness_rate: float
    recall_at_5: float
    usefulness_rate: float
    fabrication_on_unanswerable_rate: float
    passed_thresholds: bool
    failed_criteria: list[str] = Field(default_factory=list)
