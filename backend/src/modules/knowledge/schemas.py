"""Pydantic schemas for curated documents, passages, lineage, and snapshot freshness."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.shared.enums import AuthorityTier, PolicyFamily, PolicyLifecycleStatus


class PassageSummary(BaseModel):
    """Curated passage representation guarded by audience & lifecycle filtering."""

    passage_id: str
    document_id: str
    document_version_id: str
    title: str
    content: str = Field(..., max_length=6000)
    source_ref: str
    page_number: int = Field(..., ge=1)
    clause_ref: str
    language: str = "vi"
    scope: str
    audience: list[str]
    status: PolicyLifecycleStatus
    has_essential_attachments: bool
    effective_from: datetime
    effective_to: datetime | None = None
    supersedes: str | None = None


class DocumentLineageResponse(BaseModel):
    """Document header and chronological version lineage (including superseded/withdrawn)."""

    document_id: str
    title: str
    policy_family: PolicyFamily
    authority_tier: AuthorityTier
    owner: str
    versions: list[dict[str, object]] = Field(default_factory=list)


class SnapshotAgeResponse(BaseModel):
    """Latest ingestion freshness metric shown on user & admin screens (DAT 02, OPS 01)."""

    last_successful_import_at: datetime | None = None
    snapshot_age_hours: float | None = None
    staleness_threshold_hours: int
    is_stale: bool
