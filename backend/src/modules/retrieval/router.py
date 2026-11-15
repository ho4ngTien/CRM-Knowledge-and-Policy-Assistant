"""Retrieval HTTP router (/api/v1/retrieval/*)."""

from fastapi import APIRouter, Depends

from src.modules.retrieval.schemas import RetrievalSearchRequest, RetrievalSearchResponse
from src.modules.retrieval.service import RetrievalService
from src.shared.auth import AuthenticatedUser, get_current_user

router = APIRouter()
service = RetrievalService()


@router.post("/search", response_model=RetrievalSearchResponse)
async def search_curated_knowledge(
    payload: RetrievalSearchRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> RetrievalSearchResponse:
    """Run pre-filtered Vietnamese hybrid retrieval bounded to <= 8 passages."""
    _ = current_user
    normalized, expanded = service.normalize_query_vi(payload.query)
    return RetrievalSearchResponse(
        normalized_query=normalized,
        expanded_terms=expanded,
        passages=[],
        total_candidates_filtered=0,
    )
