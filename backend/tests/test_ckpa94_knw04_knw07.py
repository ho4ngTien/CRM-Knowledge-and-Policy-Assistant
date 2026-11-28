"""Focused CKPA-94 regression tests for stale invalidation and anonymous feedback topics."""

from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db import Base
from src.modules.answer.models import AnswerCitationRecord, AnswerPackageRecord
from src.modules.answer.schemas import AnswerCitation, AnswerPackage
from src.modules.answer.service import AnswerOrchestratorService
from src.modules.feedback.models import FeedbackCandidate
from src.modules.feedback.service import FeedbackService
from src.modules.knowledge.change_impact import ChangeImpactService
from src.modules.knowledge.models import ChangeImpactReport
from src.shared.auth import AuthenticatedUser
from src.shared.enums import AnswerStatus, FeedbackReason, UserRole
from src.shared.exceptions import AccessDenied


class _SessionAdapter:
    """Expose sync SQLite session methods through the async service interface."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def get(self, entity: type, identity: str):
        return self.session.get(entity, identity)

    async def execute(self, statement):
        return self.session.execute(statement)

    def add(self, entity: object) -> None:
        self.session.add(entity)


def _create_session(tables: list[object]) -> tuple[object, Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine, tables=tables)
    return engine, Session(engine)


@pytest.mark.asyncio
async def test_answer_citations_are_persisted_and_change_impact_marks_answer_stale() -> None:
    tables = [
        AnswerPackageRecord.__table__,
        AnswerCitationRecord.__table__,
        ChangeImpactReport.__table__,
    ]
    engine, session = _create_session(tables)
    try:
        db = _SessionAdapter(session)
        package = AnswerPackage(
            answer_id="ANS-CKPA94-01",
            task_id="TASK-CKPA94",
            status=AnswerStatus.ANSWERED,
            original_question="Quy trình hiện hành là gì?",
            governing_date=date(2026, 12, 28),
            scope="company:SN",
            guidance_text="Thực hiện theo nguồn được phê duyệt.",
            citations=[
                AnswerCitation(
                    document_id="DOC-94",
                    document_version_id="DOC-94:VER-1",
                    passage_id="PAS-94",
                    title="Policy 94",
                    page_number=1,
                    clause_ref="1.1",
                    quoted_text="Nguồn được phê duyệt.",
                    evidence_url="/evidence?passage_id=PAS-94",
                )
            ],
            internal_use_warning="Nội bộ.",
        )
        user = AuthenticatedUser(
            user_id="USER-94",
            email="user@example.test",
            roles=frozenset({UserRole.READER}),
            allowed_audiences=frozenset({"reader"}),
        )

        await AnswerOrchestratorService()._persist_answer_package(db, user, package)
        session.flush()
        citation = session.execute(select(AnswerCitationRecord)).scalar_one()
        assert citation.document_version_id == "DOC-94:VER-1"

        report = await ChangeImpactService().record_impact(
            db,
            event_type="source_updated",
            source_type="ingestion_passages",
            source_id="BATCH-94",
            document_version_id="DOC-94:VER-1",
            policy_version_id=None,
            actor_id="STEWARD-94",
            reason="Authoritative passage changed.",
        )
        session.flush()

        stored_answer = session.get(AnswerPackageRecord, "ANS-CKPA94-01")
        assert stored_answer is not None and stored_answer.is_stale
        assert report.stale_answers_marked == 1
        assert session.get(ChangeImpactReport, report.id) is not None
    finally:
        session.close()
        engine.dispose()


@pytest.mark.asyncio
async def test_unanswered_topic_counts_are_suppressed_until_k_five_and_redact_pii() -> None:
    engine, session = _create_session([FeedbackCandidate.__table__])
    try:
        for index in range(4):
            session.add(
                FeedbackCandidate(
                    id=f"FBK-{index}",
                    task_id=f"TASK-{index}",
                    reporter_id=f"USER-{index}",
                    reason=FeedbackReason.MISSING_SOURCE.value,
                    unanswered_topic="Hỏi chính sách qua email staff@example.com",
                    comment="Thiếu nguồn căn cứ.",
                    auto_applied=False,
                )
            )
        session.flush()
        service = FeedbackService()
        db = _SessionAdapter(session)
        assert await service.unanswered_topic_counts(db) == []

        session.add(
            FeedbackCandidate(
                id="FBK-4",
                task_id="TASK-4",
                reporter_id="USER-4",
                reason=FeedbackReason.MISSING_SOURCE.value,
                unanswered_topic="Hỏi chính sách qua email staff@example.com",
                comment="Thiếu nguồn căn cứ.",
                auto_applied=False,
            )
        )
        session.flush()

        topics = await service.unanswered_topic_counts(db)
        assert len(topics) == 1
        assert topics[0].count == 5
        assert "staff@example.com" not in topics[0].topic
        assert "[redacted_email]" in topics[0].topic
    finally:
        session.close()
        engine.dispose()


@pytest.mark.asyncio
async def test_validation_does_not_disclose_another_users_answer_state() -> None:
    from src.modules.validation.router import verify_authoritative_state
    from src.modules.validation.schemas import FinalValidationRequest

    engine, session = _create_session([AnswerPackageRecord.__table__])
    try:
        session.add(
            AnswerPackageRecord(
                id="ANS-PRIVATE",
                task_id="TASK-PRIVATE",
                user_id="OWNER",
                original_question="Private question",
                governing_date=date(2026, 12, 28),
                scope="company:SN",
                status=AnswerStatus.ANSWERED.value,
                guidance_text="Private answer",
            )
        )
        session.flush()
        user = AuthenticatedUser(
            user_id="OTHER",
            email="other@example.test",
            roles=frozenset({UserRole.READER}),
            allowed_audiences=frozenset({"reader"}),
        )

        with pytest.raises(AccessDenied):
            await verify_authoritative_state(
                FinalValidationRequest(answer_id="ANS-PRIVATE"),
                _SessionAdapter(session),
                user,
            )
    finally:
        session.close()
        engine.dispose()
