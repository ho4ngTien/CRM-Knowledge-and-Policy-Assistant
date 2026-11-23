"""Pydantic schemas for Base Scope 2-CSV validation, manifest reconciliation, and quarantine."""

from pydantic import BaseModel, Field

from src.shared.enums import BatchType


class QuarantineIssue(BaseModel):
    """Detailed quarantine rejection entry explaining why a CSV row was isolated."""

    row_number: int
    record_id: str | None = None
    reason_code: str
    reason_detail: str


class CsvValidationReport(BaseModel):
    """Manifest reconciliation output for passages or critical_fields UTF-8 CSV uploads."""

    batch_type: BatchType
    source_type: str
    expected_rows: int
    received_rows: int
    accepted_rows: int
    rejected_rows: int
    quarantined_rows: int
    quarantine_issues: list[QuarantineIssue] = Field(default_factory=list)
    batch_id: str | None = None
    imported_rows: int = 0
    snapshot_age_seconds: int | None = None


class QuarantineItemResponse(BaseModel):
    """Quarantined row view for steward remediation."""

    id: int
    batch_id: str
    row_number: int
    record_id: str | None = None
    reason_code: str
    reason_detail: str
    resolved: bool
