"""Ingestion HTTP router (/api/v1/ingestion/*) for Base Scope 2-CSV validation & quarantine."""

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.ingestion.schemas import CsvValidationReport, QuarantineItemResponse
from src.modules.ingestion.service import IngestionService
from src.shared.auth import AuthenticatedUser, require_roles
from src.shared.enums import BatchType, UserRole

router = APIRouter()
service = IngestionService()


@router.post("/csv/validate", response_model=CsvValidationReport)
async def validate_csv_batch(
    source_type: str = Query(..., pattern="^(passages|critical_fields)$"),
    batch_type: BatchType = Query(default=BatchType.DELTA),
    expected_rows: int | None = Query(default=None, ge=0),
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            UserRole.STEWARD,
            UserRole.POLICY_OWNER,
            UserRole.PUBLISHER,
            UserRole.ADMINISTRATOR,
        )
    ),
) -> CsvValidationReport:
    """Dry-run validate a UTF-8 passages or critical_fields CSV batch with DAT 08 quarantine."""
    _ = current_user
    raw_bytes = await file.read()
    return service.validate_csv_bytes(
        raw_bytes,
        source_type=source_type,
        batch_type=batch_type,
        expected_rows=expected_rows,
    )


@router.get("/quarantine", response_model=list[QuarantineItemResponse])
async def list_quarantined_rows(
    unresolved_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(
            UserRole.STEWARD,
            UserRole.POLICY_OWNER,
            UserRole.PUBLISHER,
            UserRole.ADMINISTRATOR,
        )
    ),
) -> list[QuarantineItemResponse]:
    """Inspect quarantined rows awaiting steward correction."""
    _ = current_user
    return await service.list_quarantine(db, unresolved_only=unresolved_only)
