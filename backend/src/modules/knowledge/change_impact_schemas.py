"""API schemas for KNW 04 Change Impact reports."""

from datetime import datetime

from pydantic import BaseModel


class ChangeImpactReportResponse(BaseModel):
    id: str
    event_type: str
    source_type: str
    source_id: str | None = None
    document_version_id: str | None = None
    policy_version_id: str | None = None
    actor_id: str | None = None
    reason: str
    stale_answers_marked: int
    active_view_refresh_interval_seconds: int
    created_at: datetime
