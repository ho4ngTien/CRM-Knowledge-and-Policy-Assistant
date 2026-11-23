"""Knowledge HTTP router (/api/v1/knowledge/*) enforcing consistent evidence permissions."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.knowledge.schemas import (
    DocumentLineageResponse,
    PassageSummary,
    SnapshotAgeResponse,
)
from src.modules.knowledge.service import KnowledgeService
from src.shared.auth import AuthenticatedUser, get_current_user

router = APIRouter()
service = KnowledgeService()


@router.get("/passages/{passage_id}", response_model=PassageSummary)
async def get_passage_detail(
    passage_id: str,
    allow_historical: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> PassageSummary:
    """Direct URL evidence viewer (enforces identical SEC 01 audience & withdrawal checks)."""
    return await service.get_passage(
        db, current_user, passage_id, allow_historical=allow_historical
    )


@router.get("/documents/{document_id}/lineage", response_model=DocumentLineageResponse)
async def get_document_lineage(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DocumentLineageResponse:
    """View version lineage for a curated policy document."""
    _ = current_user
    return await service.get_document_lineage(db, document_id)


@router.get("/snapshot-age", response_model=SnapshotAgeResponse)
async def get_snapshot_age(
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> SnapshotAgeResponse:
    """Report current corpus snapshot age for evidence banners."""
    _ = current_user
    return await service.get_latest_snapshot_age(db)
