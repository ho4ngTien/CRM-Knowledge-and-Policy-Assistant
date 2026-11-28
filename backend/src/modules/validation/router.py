"""Validation HTTP router (/api/v1/validation/*) — never trusts unverified LLM outputs."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.answer.models import AnswerPackageRecord
from src.modules.knowledge.change_impact import ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS
from src.modules.knowledge.service import KnowledgeService
from src.modules.validation.schemas import FinalValidationRequest, FinalValidationResponse
from src.modules.validation.service import ValidationService
from src.shared.auth import AuthenticatedUser, get_current_user
from src.shared.exceptions import (
    AccessDenied,
    CitationValidationFailed,
    PolicyNotFound,
    PolicyWithdrawn,
)

router = APIRouter()
validation_service = ValidationService()
knowledge_service = KnowledgeService()


@router.post("/verify", response_model=FinalValidationResponse)
async def verify_authoritative_state(
    payload: FinalValidationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> FinalValidationResponse:
    """Revalidate stored stale state and each citation against authoritative DB rows."""
    stored_package = await db.get(AnswerPackageRecord, payload.answer_id)
    if stored_package is not None and stored_package.user_id != current_user.user_id:
        raise AccessDenied("Answer package is not available to the current user.")
    if stored_package is not None and stored_package.is_stale:
        return FinalValidationResponse(
            is_valid=False,
            stale=True,
            verified_citations_count=0,
            errors=["Answer package was marked stale by a KNW 04 source change."],
            active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
        )

    if not payload.citations:
        return FinalValidationResponse(
            is_valid=False,
            errors=["Citation missing: cannot verify answer without evidence."],
            active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
        )

    authoritative_passages = {}
    errors: list[str] = []
    for citation in payload.citations:
        try:
            authoritative_passages[citation.passage_id] = await knowledge_service.get_passage(
                db,
                current_user,
                citation.passage_id,
                allow_historical=payload.allow_historical,
            )
        except PolicyWithdrawn as exc:
            return FinalValidationResponse(
                is_valid=False,
                stale=True,
                verified_citations_count=0,
                errors=[str(exc)],
                active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
            )
        except AccessDenied:
            return FinalValidationResponse(
                is_valid=False,
                stale=True,
                verified_citations_count=0,
                errors=["Citation is no longer available to the current user."],
                active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
            )
        except PolicyNotFound:
            errors.append(f"Authoritative source not found: {citation.passage_id}")

    if errors:
        return FinalValidationResponse(
            is_valid=False,
            verified_citations_count=0,
            errors=errors,
            active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
        )

    try:
        outcome = validation_service.verify_citations_and_state(
            current_user,
            payload.citations,
            authoritative_passages,
            allow_historical=payload.allow_historical,
            allow_future_preview=payload.allow_future_preview,
        )
    except PolicyWithdrawn as exc:
        return FinalValidationResponse(
            is_valid=False,
            stale=True,
            verified_citations_count=0,
            errors=[str(exc)],
            active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
        )
    except CitationValidationFailed as exc:
        return FinalValidationResponse(
            is_valid=False,
            verified_citations_count=0,
            errors=[str(exc)],
            active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
        )

    return FinalValidationResponse(
        is_valid=outcome.is_valid,
        stale=outcome.is_stale,
        verified_citations_count=len(payload.citations),
        errors=list(outcome.failure_reasons),
        active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
    )
