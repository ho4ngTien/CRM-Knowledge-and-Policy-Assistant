"""Change Impact report creation and query helpers (KNW 04)."""

from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.answer.models import AnswerCitationRecord, AnswerPackageRecord
from src.modules.knowledge.models import ChangeImpactReport

ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS = 60


class ChangeImpactService:
    """Persist change events and synchronously mark cited answer packages stale."""

    async def record_impact(
        self,
        db: AsyncSession,
        *,
        event_type: str,
        source_type: str,
        source_id: str | None,
        document_version_id: str | None,
        policy_version_id: str | None,
        actor_id: str | None,
        reason: str,
    ) -> ChangeImpactReport:
        answer_ids: list[str] = []
        if document_version_id:
            answer_ids = list(
                (
                    await db.execute(
                        select(AnswerCitationRecord.answer_package_id)
                        .where(
                            AnswerCitationRecord.document_version_id == document_version_id
                        )
                        .distinct()
                    )
                )
                .scalars()
                .all()
            )
        if answer_ids:
            await db.execute(
                update(AnswerPackageRecord)
                .where(AnswerPackageRecord.id.in_(answer_ids))
                .values(is_stale=True)
            )

        report = ChangeImpactReport(
            id=f"IMP-{uuid4().hex[:16].upper()}",
            event_type=event_type,
            source_type=source_type,
            source_id=source_id,
            document_version_id=document_version_id,
            policy_version_id=policy_version_id,
            actor_id=actor_id,
            reason=reason,
            stale_answers_marked=len(answer_ids),
            active_view_refresh_interval_seconds=ACTIVE_VIEW_REFRESH_INTERVAL_SECONDS,
        )
        db.add(report)
        return report
