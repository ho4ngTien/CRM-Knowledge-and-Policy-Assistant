"""Independent evaluation HTTP router (/api/v1/evaluation/*) enforcing Chinese Wall."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.evaluation.schemas import EvaluationRunCreateRequest, EvaluationRunResponse
from src.modules.evaluation.service import EvaluationService
from src.shared.auth import AuthenticatedUser, get_current_user, require_roles
from src.shared.enums import EvalPartition, UserRole

router = APIRouter()
service = EvaluationService()


@router.post("/runs", response_model=EvaluationRunResponse, status_code=201)
async def create_evaluation_run(
    payload: EvaluationRunCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.INDEPENDENT_EVALUATOR, UserRole.ADMINISTRATOR)
    ),
) -> EvaluationRunResponse:
    """Record a Chinese-Wall-isolated evaluation run against Section 8 thresholds."""
    return await service.record_run(db, current_user, payload)


@router.get("/runs", response_model=list[EvaluationRunResponse])
async def list_evaluation_runs(
    partition: EvalPartition = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[EvaluationRunResponse]:
    """Read evaluation metrics for a requested partition (blocks dev access to sealed_100)."""
    return await service.list_runs(db, current_user, partition)
