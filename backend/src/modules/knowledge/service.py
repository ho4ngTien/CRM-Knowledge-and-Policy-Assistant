"""Knowledge repository services enforcing corpus bounds and audience isolation."""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.modules.ingestion.models import ImportBatch
from src.modules.knowledge.models import Document, DocumentVersion, Passage
from src.modules.knowledge.schemas import (
    DocumentLineageResponse,
    PassageSummary,
    SnapshotAgeResponse,
)
from src.shared.auth import AuthenticatedUser, check_policy_audience
from src.shared.enums import AuthorityTier, PolicyFamily, PolicyLifecycleStatus, UserRole
from src.shared.exceptions import AccessDenied, PolicyNotFound, PolicyWithdrawn

_PRIVILEGED_KNOWLEDGE_ROLES: frozenset[UserRole] = frozenset(
    {
        UserRole.POLICY_OWNER,
        UserRole.STEWARD,
        UserRole.ADMINISTRATOR,
    }
)

_UNPUBLISHED_LINEAGE_STATUSES: frozenset[str] = frozenset(
    {
        PolicyLifecycleStatus.DRAFT.value,
        PolicyLifecycleStatus.OWNER_REVIEWED.value,
        PolicyLifecycleStatus.APPROVED.value,
        PolicyLifecycleStatus.QUARANTINED.value,
        PolicyLifecycleStatus.FEEDBACK_CANDIDATE.value,
    }
)

_READER_BLOCKED_PASSAGE_STATUSES: frozenset[str] = frozenset(
    {
        PolicyLifecycleStatus.DRAFT.value,
        PolicyLifecycleStatus.OWNER_REVIEWED.value,
        PolicyLifecycleStatus.APPROVED.value,
        PolicyLifecycleStatus.SCHEDULED.value,
        PolicyLifecycleStatus.QUARANTINED.value,
        PolicyLifecycleStatus.FEEDBACK_CANDIDATE.value,
    }
)


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

        is_reader_only = not bool(user.roles & _PRIVILEGED_KNOWLEDGE_ROLES)
        if is_reader_only and passage.status in _READER_BLOCKED_PASSAGE_STATUSES:
            raise AccessDenied(
                f"Reader cannot access passage in '{passage.status}' lifecycle state."
            )
        if not allow_historical and passage.status == PolicyLifecycleStatus.SUPERSEDED.value:
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
            is_tombstoned=passage.is_tombstoned,
        )

    async def get_document_lineage(
        self, db: AsyncSession, user: AuthenticatedUser, document_id: str
    ) -> DocumentLineageResponse:
        """Return version chain including supersedes links, guarded by audience & lifecycle RBAC."""
        doc = await db.get(Document, document_id)
        if doc is None:
            raise PolicyNotFound(f"Document {document_id} was not found.")

        is_reader_only = not bool(user.roles & _PRIVILEGED_KNOWLEDGE_ROLES)
        if is_reader_only:
            doc_passages = (
                (
                    await db.execute(
                        select(Passage).where(
                            Passage.document_id == document_id,
                            Passage.is_tombstoned.is_(False),
                        )
                    )
                )
                .scalars()
                .all()
            )
            has_permitted_passage = any(
                check_policy_audience(
                    user, [a.strip() for a in p.audience.split(",") if a.strip()]
                )
                for p in doc_passages
            )
            if not has_permitted_passage:
                raise AccessDenied("User lacks audience access to this document lineage.")

        versions = (
            (
                await db.execute(
                    select(DocumentVersion)
                    .where(DocumentVersion.document_id == document_id)
                    .order_by(DocumentVersion.effective_from.desc())
                )
            )
            .scalars()
            .all()
        )
        if is_reader_only:
            versions = [v for v in versions if v.status not in _UNPUBLISHED_LINEAGE_STATUSES]

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

    def compute_snapshot_age(self, last_import_at: datetime | None) -> SnapshotAgeResponse:
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
            snapshot_age_seconds=max(0, int((now_vn - last_vn).total_seconds())),
            staleness_threshold_hours=settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
            is_stale=age_hours > settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
        )

    async def get_latest_snapshot_age(self, db: AsyncSession) -> SnapshotAgeResponse:
        """Query latest completed import timestamp and return VN snapshot freshness."""
        if not hasattr(db, "execute"):
            return self.compute_snapshot_age(None)
        latest_timestamp = (
            await db.execute(
                select(func.max(ImportBatch.batch_timestamp)).where(
                    ImportBatch.status != "rejected"
                )
            )
        ).scalar_one_or_none()
        if latest_timestamp is None:
            return SnapshotAgeResponse(
                last_successful_import_at=None,
                snapshot_age_hours=None,
                snapshot_age_seconds=None,
                staleness_threshold_hours=settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
                is_stale=True,
            )
        tz = ZoneInfo(settings.APP_TIMEZONE)
        last_vn = (
            latest_timestamp.astimezone(tz)
            if latest_timestamp.tzinfo is not None
            else latest_timestamp.replace(tzinfo=tz)
        )
        age_seconds = max(
            0,
            int((datetime.now(tz) - last_vn).total_seconds()),
        )
        age_hours = round(age_seconds / 3600.0, 2)
        return SnapshotAgeResponse(
            last_successful_import_at=last_vn,
            snapshot_age_hours=age_hours,
            snapshot_age_seconds=age_seconds,
            staleness_threshold_hours=settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
            is_stale=age_hours > settings.IMPORT_SNAPSHOT_STALENESS_HOURS,
        )
