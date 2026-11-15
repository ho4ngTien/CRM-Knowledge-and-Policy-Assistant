"""Knowledge repository services enforcing corpus bounds and audience isolation."""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.knowledge.models import Document, DocumentVersion, Passage
from src.modules.knowledge.schemas import (
    DocumentLineageResponse,
    PassageSummary,
    SnapshotAgeResponse,
)
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import AuthorityTier, PolicyFamily, PolicyLifecycleStatus
from src.shared.exceptions import AccessDenied, PolicyNotFound, PolicyWithdrawn


class KnowledgeService:
    """Provides audience-filtered access to approved documents, versions, and passages."""

    async def get_passage(
        self,
        db: AsyncSession,
        user: AuthenticatedUser,
        passage_id: str,
        *,
        allow_historical: bool = False,
    ) -> PassageSummary:
        """Fetch a passage by ID after verifying audience permission and lifecycle state."""
        stmt = (
            select(Passage, DocumentVersion)
            .join(DocumentVersion, Passage.document_version_id == DocumentVersion.id)
            .where(Passage.id == passage_id)
        )
        row = (await db.execute(stmt)).first()
        if row is None:
            raise PolicyNotFound(f"Passage {passage_id} was not found.")
        passage, version = row
        audiences = [a.strip() for a in passage.audience.split(",") if a.strip()]
        if not check_policy_audience(user, audiences):
            raise AccessDenied("User lacks audience access to this passage.")
        if passage.is_tombstoned or passage.status == PolicyLifecycleStatus.WITHDRAWN.value:
            raise PolicyWithdrawn(f"Passage {passage_id} is withdrawn and cannot be viewed.")
        if (
            not allow_historical
            and passage.status == PolicyLifecycleStatus.SUPERSEDED.value
        ):
            raise AccessDenied("Superseded passage requires explicit historical mode.")
        return PassageSummary(
            passage_id=passage.id,
            document_id=passage.document_id,
            document_version_id=passage.document_version_id,
            title=passage.title,
            content=passage.content,
            source_ref=passage.source_ref,
            page_number=passage.page_number,
            clause_ref=passage.clause_ref,
            language=passage.language,
            scope=passage.scope,
            audience=audiences,
            status=PolicyLifecycleStatus(passage.status),
            has_essential_attachments=passage.has_essential_attachments,
            effective_from=version.effective_from,
            effective_to=version.effective_to,
            supersedes=version.supersedes_version_id,
        )

    async def get_document_lineage(
        self, db: AsyncSession, document_id: str
    ) -> DocumentLineageResponse:
        """Return full version chain including supersedes links for auditability."""
        doc = await db.get(Document, document_id)
        if doc is None:
            raise PolicyNotFound(f"Document {document_id} was not found.")
        versions = (
            await db.execute(
                select(DocumentVersion)
                .where(DocumentVersion.document_id == document_id)
                .order_by(DocumentVersion.effective_from.desc())
            )
        ).scalars().all()
        return DocumentLineageResponse(
            document_id=doc.id,
            title=doc.title,
            policy_family=PolicyFamily(doc.policy_family),
            authority_tier=AuthorityTier(doc.authority_tier),
            owner=doc.owner,
            versions=[
                {
                    "document_version_id": v.id,
                    "status": v.status,
                    "recorded_at": v.recorded_at.isoformat(),
                    "effective_from": v.effective_from.isoformat(),
                    "effective_to": v.effective_to.isoformat() if v.effective_to else None,
                    "supersedes": v.supersedes_version_id,
                }
                for v in versions
            ],
        )

    def compute_snapshot_age(
        self, last_import_at: datetime | None
    ) -> SnapshotAgeResponse:
        """Compute snapshot staleness against IMPORT_SNAPSHOT_STALENESS_HOURS in VN time."""
        if last_import_at is None:
            return SnapshotAgeResponse(
                last_successful_import_at=None,
                snapshot_age_hours=None,
                staleness_threshold_hours=settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
                is_stale=True,
            )
        tz = ZoneInfo(settings.APP_TIMEZONE)
        now_vn = datetime.now(tz)
        last_vn = (
            last_import_at.astimezone(tz)
            if last_import_at.tzinfo is not None
            else last_import_at.replace(tzinfo=tz)
        )
        age_hours = round((now_vn - last_vn).total_seconds() / 3600.0, 2)
        return SnapshotAgeResponse(
            last_successful_import_at=last_vn,
            snapshot_age_hours=max(age_hours, 0.0),
            staleness_threshold_hours=settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
            is_stale=age_hours > settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
        )
