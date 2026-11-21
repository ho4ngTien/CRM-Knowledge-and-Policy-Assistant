"""Ingestion HTTP router (/api/v1/ingestion/*) for Base Scope 2-CSV validation & quarantine."""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db
from src.modules.ingestion.schemas import CsvValidationReport, QuarantineItemResponse
from src.modules.ingestion.service import IdempotencyKeyConflict, IngestionService
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
    manifest_file: UploadFile | None = File(default=None),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> CsvValidationReport:
    """Dry-run validate a UTF-8 passages or critical_fields CSV batch with DAT 08 quarantine."""
    _ = current_user
    raw_bytes = await file.read()
    manifest_bytes = await manifest_file.read() if manifest_file is not None else None
    return service.validate_csv_bytes(
        raw_bytes,
        source_type=source_type,
        batch_type=batch_type,
        expected_rows=expected_rows,
        manifest_bytes=manifest_bytes,
    )


@router.post("/csv/import", response_model=CsvValidationReport)
async def import_csv_batch(
    source_type: str = Query(..., pattern="^(passages|critical_fields)$"),
    idempotency_key: str = Query(..., min_length=1, max_length=128),
    batch_type: BatchType = Query(default=BatchType.DELTA),
    expected_rows: int | None = Query(default=None, ge=0),
    file: UploadFile = File(...),
    manifest_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> CsvValidationReport:
    """Validate and durably stage accepted rows and quarantine issues for one CSV batch."""
    try:
        return await service.import_csv_bytes(
            db,
            await file.read(),
            source_type=source_type,
            batch_type=batch_type,
            expected_rows=expected_rows,
            manifest_bytes=await manifest_file.read(),
            idempotency_key=idempotency_key,
            submitted_by=current_user.user_id,
        )
    except IdempotencyKeyConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/quarantine", response_model=list[QuarantineItemResponse])
async def list_quarantined_rows(
    unresolved_only: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    current_user: AuthenticatedUser = Depends(
        require_roles(UserRole.STEWARD, UserRole.POLICY_OWNER, UserRole.ADMINISTRATOR)
    ),
) -> list[QuarantineItemResponse]:
    """Inspect quarantined rows awaiting steward correction."""
    _ = current_user
    return await service.list_quarantine(db, unresolved_only=unresolved_only)
