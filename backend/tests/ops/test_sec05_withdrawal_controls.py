"""SEC 05 (DEF-CKPA75-02): Verify DB commit before ACK, fail-closed DB error, and Snapshot Age."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.db import Base
from src.modules.admin.service import AdminService
from src.modules.answer.models import AnswerCitationRecord, AnswerPackageRecord
from src.modules.ingestion.models import ImportBatch
from src.modules.knowledge.models import ChangeImpactReport, Document, DocumentVersion, Passage
from src.modules.knowledge.service import KnowledgeService
from src.modules.policy.models import CriticalField, Policy, PolicyLifecycleEvent, PolicyVersion
from src.shared.auth import AuthenticatedUser
from src.shared.enums import PolicyLifecycleStatus, UserRole
from src.shared.exceptions import PolicyWithdrawn

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


class _AsyncSessionAdapter:
    """Expose async DB operations expected by services over an isolated SQLite session."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.commit_count = 0

    async def execute(self, statement: Any) -> Any:
        return self.session.execute(statement)

    async def get(self, entity: Any, identity: Any) -> Any:
        return self.session.get(entity, identity)

    def add(self, entity: Any) -> None:
        self.session.add(entity)

    def add_all(self, entities: list[Any]) -> None:
        self.session.add_all(entities)

    async def commit(self) -> None:
        self.session.commit()
        self.commit_count += 1


class _FailingSession:
    """Inject SQLAlchemyError on DB operations to verify fail-closed SEC 05 behavior."""

    async def execute(self, statement: Any) -> Any:
        raise SQLAlchemyError("Simulated database outage")

    async def get(self, entity: Any, identity: Any) -> Any:
        raise SQLAlchemyError("Simulated database outage")

    def add(self, entity: Any) -> None:
        return None

    async def commit(self) -> None:
        raise SQLAlchemyError("Simulated database commit failure")


class _SpyCachePurger:
    """Capture DB state at exact purge invocation time (after commit, before ACK)."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.purged_calls: list[tuple[str, str | None]] = []
        self.observed_committed_statuses: dict[str, Any] = {}

    async def purge_policy_caches(
        self,
        policy_version_id: str,
        document_version_id: str | None = None,
    ) -> int:
        self.purged_calls.append((policy_version_id, document_version_id))
        pv = self.session.get(PolicyVersion, policy_version_id)
        dv = self.session.get(DocumentVersion, document_version_id) if document_version_id else None
        psg = self.session.get(Passage, "PSG-SEC05-01")
        cf = self.session.get(CriticalField, "CF-SEC05-01")
        ans = self.session.get(AnswerPackageRecord, "ANS-SEC05-01")
        self.observed_committed_statuses = {
            "policy_version": pv.status if pv else None,
            "document_version": dv.status if dv else None,
            "passage": psg.status if psg else None,
            "critical_field": cf.status if cf else None,
            "answer_stale": ans.is_stale if ans else None,
        }
        return 2


def _seed_sec05_data(session: Session) -> None:
    now = datetime.now(UTC)
    session.add(
        Document(
            id="DOC-SEC05",
            title="Chinh sach Thu hoi Khan cap",
            policy_family="quotation",
            authority_tier="company_policy",
            owner="P2",
            source_ref="data/g1/sec05.md",
        )
    )
    session.add(
        DocumentVersion(
            id="VER-SEC05",
            document_id="DOC-SEC05",
            approver="P1",
            status=PolicyLifecycleStatus.EFFECTIVE.value,
            recorded_at=now - timedelta(hours=2),
            effective_from=now - timedelta(hours=1),
            effective_to=None,
            supersedes_version_id=None,
        )
    )
    session.add(
        Policy(
            id="POL-SEC05",
            title="Chinh sach Thu hoi Khan cap",
            policy_family="quotation",
        )
    )
    session.add(
        PolicyVersion(
            id="PV-SEC05",
            policy_id="POL-SEC05",
            document_version_id="VER-SEC05",
            status=PolicyLifecycleStatus.EFFECTIVE.value,
            recorded_at=now - timedelta(hours=2),
            effective_from=now - timedelta(hours=1),
            effective_to=None,
            scope="company:SN",
            audience="reader",
            owner="P2",
            approver="P1",
        )
    )
    session.add(
        Passage(
            id="PSG-SEC05-01",
            document_id="DOC-SEC05",
            document_version_id="VER-SEC05",
            title="Dieu khoan thu hoi",
            content="Noi dung se bi thu hoi khan cap.",
            source_ref="data/g1/sec05.md",
            page_number=1,
            clause_ref="Dieu 1",
            language="vi",
            scope="company:SN",
            audience="reader",
            status=PolicyLifecycleStatus.EFFECTIVE.value,
            has_essential_attachments=True,
            is_tombstoned=False,
        )
    )
    session.add(
        CriticalField(
            id="CF-SEC05-01",
            policy_id="POL-SEC05",
            policy_version_id="PV-SEC05",
            document_version_id="VER-SEC05",
            field_name="discount_limit",
            field_type="number",
            operator="<=",
            value="10",
            unit="%",
            currency=None,
            approval_role="policy_owner",
            time_limit="24h",
            exception_condition=None,
            required_documents="[]",
            source_clause="Dieu 1",
            scope="company:SN",
            audience="reader",
            status=PolicyLifecycleStatus.EFFECTIVE.value,
        )
    )
    session.add(
        AnswerPackageRecord(
            id="ANS-SEC05-01",
            task_id="TASK-SEC05-01",
            user_id="P4-01",
            original_question="Muc chiet khau toi da?",
            governing_date=date(2026, 11, 25),
            scope="company:SN",
            status="answered",
            guidance_text="Muc chiet khau toi da 10%.",
            is_stale=False,
        )
    )
    session.add(
        AnswerCitationRecord(
            answer_package_id="ANS-SEC05-01",
            passage_id="PSG-SEC05-01",
            document_version_id="VER-SEC05",
            page_number=1,
            clause_ref="Dieu 1",
        )
    )
    session.commit()


def _create_isolated_session() -> tuple[Any, Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    tables: list[Any] = [
        Document.__table__,
        DocumentVersion.__table__,
        Policy.__table__,
        PolicyVersion.__table__,
        Passage.__table__,
        CriticalField.__table__,
        AnswerPackageRecord.__table__,
        AnswerCitationRecord.__table__,
        PolicyLifecycleEvent.__table__,
        ChangeImpactReport.__table__,
        ImportBatch.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    return engine, Session(engine)


@pytest.mark.asyncio
async def test_sec05_withdraw_commits_authoritative_db_before_ack_and_purge() -> None:
    """Verify authoritative DB withdrawal is committed before cache purge and ACK return."""
    _, session = _create_isolated_session()
    with session:
        _seed_sec05_data(session)
        db = _AsyncSessionAdapter(session)
        spy = _SpyCachePurger(session)
        admin_service = AdminService()
        knowledge_service = KnowledgeService()

        admin_user = AuthenticatedUser(
            user_id="S5-DUY",
            email="s5@songnhat.vn",
            roles=frozenset({UserRole.ADMINISTRATOR}),
        )
        reader_user = AuthenticatedUser(
            user_id="P4-01",
            email="p4@songnhat.vn",
            roles=frozenset({UserRole.READER}),
        )

        ack = await admin_service.withdraw_policy_immediately(
            db,  # type: ignore[arg-type]
            admin_user,
            "PV-SEC05",
            "SEC 05 emergency withdrawal",
            cache_purger=spy,
        )

        assert ack.status == PolicyLifecycleStatus.WITHDRAWN
        assert ack.stale_answers_marked == 1
        assert db.commit_count == 1
        assert spy.purged_calls == [("PV-SEC05", "VER-SEC05")]
        assert spy.observed_committed_statuses == {
            "policy_version": "withdrawn",
            "document_version": "withdrawn",
            "passage": "withdrawn",
            "critical_field": "withdrawn",
            "answer_stale": True,
        }

        with pytest.raises(PolicyWithdrawn):
            await knowledge_service.get_passage(
                db,  # type: ignore[arg-type]
                reader_user,
                "PSG-SEC05-01",
            )


@pytest.mark.asyncio
async def test_sec05_fail_closed_when_database_raises_error() -> None:
    """Verify SEC 05 fails closed (raises error, no stale read/ACK) when DB fails."""
    failing_db = _FailingSession()
    admin_service = AdminService()
    knowledge_service = KnowledgeService()

    admin_user = AuthenticatedUser(
        user_id="S5-DUY",
        email="s5@songnhat.vn",
        roles=frozenset({UserRole.ADMINISTRATOR}),
    )
    reader_user = AuthenticatedUser(
        user_id="P4-01",
        email="p4@songnhat.vn",
        roles=frozenset({UserRole.READER}),
    )

    with pytest.raises(SQLAlchemyError):
        await knowledge_service.get_passage(
            failing_db,  # type: ignore[arg-type]
            reader_user,
            "PSG-SEC05-01",
        )

    with pytest.raises(SQLAlchemyError):
        await admin_service.withdraw_policy_immediately(
            failing_db,  # type: ignore[arg-type]
            admin_user,
            "PV-SEC05",
            "Should fail closed",
        )

    with pytest.raises(SQLAlchemyError):
        await knowledge_service.get_latest_snapshot_age(failing_db)  # type: ignore[arg-type]

    # Verify OPS 05 emergency disable fallback toggle works independently of DB
    state = await admin_service.set_emergency_disable(admin_user, True, "DB outage fallback")
    assert state["disabled"] is True
    assert await admin_service.is_emergency_disabled() is True


@pytest.mark.asyncio
async def test_sec05_snapshot_age_fresh_stale_and_rejected_boundaries() -> None:
    """Verify Snapshot Age evaluates freshness, >25h staleness, and ignores rejected batches."""
    _, session = _create_isolated_session()
    with session:
        db = _AsyncSessionAdapter(session)
        knowledge_service = KnowledgeService()

        # 1. Empty DB -> fail-closed stale=True
        empty_age = await knowledge_service.get_latest_snapshot_age(db)  # type: ignore[arg-type]
        assert empty_age.is_stale is True
        assert empty_age.last_successful_import_at is None

        # 2. Only rejected batch -> still stale=True
        now_vn = datetime.now(VN_TZ)
        session.add(
            ImportBatch(
                id="batch-rejected-1",
                source_type="passages",
                batch_type="full_snapshot",
                batch_timestamp=now_vn,
                idempotency_key="k-rej",
                submitted_by="S5",
                status="rejected",
            )
        )
        session.commit()
        rej_age = await knowledge_service.get_latest_snapshot_age(db)  # type: ignore[arg-type]
        assert rej_age.is_stale is True

        # 3. Completed batch 26 hours ago (> 25h threshold) -> stale=True
        session.add(
            ImportBatch(
                id="batch-stale-1",
                source_type="passages",
                batch_type="full_snapshot",
                batch_timestamp=now_vn - timedelta(hours=26),
                idempotency_key="k-stale",
                submitted_by="S5",
                status="completed",
            )
        )
        session.commit()
        stale_age = await knowledge_service.get_latest_snapshot_age(db)  # type: ignore[arg-type]
        assert stale_age.is_stale is True
        assert stale_age.snapshot_age_hours is not None
        assert stale_age.snapshot_age_hours >= 25.9

        # 4. Fresh completed batch 1 hour ago -> is_stale=False
        session.add(
            ImportBatch(
                id="batch-fresh-1",
                source_type="passages",
                batch_type="full_snapshot",
                batch_timestamp=now_vn - timedelta(hours=1),
                idempotency_key="k-fresh",
                submitted_by="S5",
                status="completed",
            )
        )
        session.commit()
        fresh_age = await knowledge_service.get_latest_snapshot_age(db)  # type: ignore[arg-type]
        assert fresh_age.is_stale is False
        assert fresh_age.snapshot_age_hours is not None
        assert fresh_age.snapshot_age_hours < 2.0
