"""Verified synchronous Q&A router (/api/v1/answer/*) — never streams pre-validation."""

from fastapi import APIRouter, Depends

from src.modules.answer.schemas import AnswerPackage, AnswerQueryRequest
from src.modules.answer.service import AnswerOrchestratorService
from src.shared.auth import AuthenticatedUser, get_current_user

router = APIRouter()
service = AnswerOrchestratorService()


@router.post("", response_model=AnswerPackage)
async def ask_policy_question(
    payload: AnswerQueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AnswerPackage:
    """Return a validated 7-part AnswerPackage (synchronous only; no unverified stream)."""
    return service.build_guarded_response(current_user, payload, is_regenerate=False)


@router.post("/follow-up", response_model=AnswerPackage)
async def ask_follow_up_question(
    payload: AnswerQueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AnswerPackage:
    """Process a clarified follow-up question while preserving the original task_id."""
    return service.build_guarded_response(current_user, payload, is_regenerate=False)


@router.post("/regenerate", response_model=AnswerPackage)
async def regenerate_answer_package(
    payload: AnswerQueryRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AnswerPackage:
    """Regenerate an AnswerPackage preserving task_id after source updates/clarification."""
    return service.build_guarded_response(current_user, payload, is_regenerate=True)
