"""Forensic RBAC regression tests for CKPA-70 (SEC 01, KNW 03, effective_from VN boundary)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import cast
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Table, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.db import Base, get_db
from src.main import app
from src.modules.knowledge.models import Document, DocumentVersion, Passage
from src.modules.knowledge.service import KnowledgeService
from src.shared.auth import AuthenticatedUser, create_access_token
from src.shared.enums import PolicyLifecycleStatus, UserRole
from src.shared.exceptions import AccessDenied, PolicyWithdrawn

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


class _AsyncSessionAdapter:
    """Minimal AsyncSession adapter over an isolated in-memory SQLite Session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def execute(self, statement):
        return self.session.execute(statement)

    async def get(self, entity, identity):
        return self.session.get(entity, identity)


def _create_knowledge_session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            cast(Table, Document.__table__),
            cast(Table, DocumentVersion.__table__),
            cast(Table, Passage.__table__),
        ],
    )
    return Session(engine)


def _reader_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id="reader-ckpa70",
        email="reader@songnhat.vn",
        roles=frozenset({UserRole.READER}),
        allowed_audiences=frozenset({"reader"}),
    )


def _owner_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id="owner-ckpa70",
        email="owner@songnhat.vn",
        roles=frozenset({UserRole.POLICY_OWNER}),
        allowed_audiences=frozenset({"policy_owner", "reader"}),
    )


async def test_lineage_blocks_draft_scheduled_withdrawn_only_documents_for_reader() -> None:
    """Reader MUST NOT see title/owner/versions of DRAFT, SCHEDULED, or WITHDRAWN documents."""
    svc = KnowledgeService()
    reader = _reader_user()
    owner = _owner_user()
    now_vn = datetime.now(VN_TZ)

    with _create_knowledge_session() as session:
        db = cast(AsyncSession, _AsyncSessionAdapter(session))
        for doc_id, ver_id, pas_id, status_val, eff_from in (
            (
                "DOC-DFT",
                "VER-DFT",
                "PAS-DFT",
                PolicyLifecycleStatus.DRAFT.value,
                now_vn - timedelta(days=1),
            ),
            (
                "DOC-SCH",
                "VER-SCH",
                "PAS-SCH",
                PolicyLifecycleStatus.SCHEDULED.value,
                now_vn + timedelta(days=5),
            ),
            (
                "DOC-WTD",
                "VER-WTD",
                "PAS-WTD",
                PolicyLifecycleStatus.WITHDRAWN.value,
                now_vn - timedelta(days=10),
            ),
        ):
            session.add(
                Document(
                    id=doc_id,
                    title=f"Secret {status_val} Policy",
                    policy_family="commercial_quoting_approval",
                    authority_tier="policy",
                    owner="Owner X",
                    source_ref=f"data/{doc_id}.md",
                )
            )
            session.add(
                DocumentVersion(
                    id=ver_id,
                    document_id=doc_id,
                    status=status_val,
                    recorded_at=now_vn - timedelta(days=2),
                    effective_from=eff_from,
                )
            )
            session.add(
                Passage(
                    id=pas_id,
                    document_id=doc_id,
                    document_version_id=ver_id,
                    title=f"Passage {status_val}",
                    content="Restricted content.",
                    source_ref=f"data/{doc_id}.md",
                    page_number=1,
                    clause_ref="Điều 1",
                    language="vi",
                    scope="company:SN",
                    audience="reader",
                    status=status_val,
                    has_essential_attachments=True,
                    is_tombstoned=False,
                )
            )
        session.commit()

        for doc_id in ("DOC-DFT", "DOC-SCH", "DOC-WTD"):
            with pytest.raises(AccessDenied):
                await svc.get_document_lineage(db, reader, doc_id)

            # Privileged owner can still inspect full lineage
            owner_res = await svc.get_document_lineage(db, owner, doc_id)
            assert owner_res.document_id == doc_id
            assert len(owner_res.versions) == 1


async def test_lineage_filters_out_scheduled_draft_withdrawn_from_mixed_document() -> None:
    """On a document with an EFFECTIVE version, reader lineage only lists EFFECTIVE/SUPERSEDED."""
    svc = KnowledgeService()
    reader = _reader_user()
    owner = _owner_user()
    now_vn = datetime.now(VN_TZ)

    with _create_knowledge_session() as session:
        db = cast(AsyncSession, _AsyncSessionAdapter(session))
        session.add(
            Document(
                id="DOC-MIXED",
                title="Mixed Lifecycle Policy",
                policy_family="commercial_quoting_approval",
                authority_tier="policy",
                owner="Lý Hữu Tài",
                source_ref="data/DOC-MIXED.md",
            )
        )
        versions_spec = [
            ("VER-EFF", PolicyLifecycleStatus.EFFECTIVE.value, now_vn - timedelta(days=5)),
            ("VER-SUP", PolicyLifecycleStatus.SUPERSEDED.value, now_vn - timedelta(days=30)),
            ("VER-DFT", PolicyLifecycleStatus.DRAFT.value, now_vn - timedelta(days=1)),
            ("VER-SCH", PolicyLifecycleStatus.SCHEDULED.value, now_vn + timedelta(days=7)),
            ("VER-WTD", PolicyLifecycleStatus.WITHDRAWN.value, now_vn - timedelta(days=20)),
            # Future effective_from even if marked effective must also be hidden from reader
            ("VER-FUT-EFF", PolicyLifecycleStatus.EFFECTIVE.value, now_vn + timedelta(days=2)),
        ]
        for idx, (ver_id, status_val, eff_from) in enumerate(versions_spec, start=1):
            session.add(
                DocumentVersion(
                    id=ver_id,
                    document_id="DOC-MIXED",
                    status=status_val,
                    recorded_at=now_vn - timedelta(days=10),
                    effective_from=eff_from,
                )
            )
            session.add(
                Passage(
                    id=f"PAS-MIX-{idx}",
                    document_id="DOC-MIXED",
                    document_version_id=ver_id,
                    title=f"Title {ver_id}",
                    content=f"Content {ver_id}",
                    source_ref="data/DOC-MIXED.md",
                    page_number=idx,
                    clause_ref=f"Điều {idx}",
                    language="vi",
                    scope="company:SN",
                    audience="reader",
                    status=status_val,
                    has_essential_attachments=True,
                    is_tombstoned=False,
                )
            )
        session.commit()

        reader_lineage = await svc.get_document_lineage(db, reader, "DOC-MIXED")
        visible_ids = {v["document_version_id"] for v in reader_lineage.versions}
        assert visible_ids == {"VER-EFF", "VER-SUP"}

        owner_lineage = await svc.get_document_lineage(db, owner, "DOC-MIXED")
        assert len(owner_lineage.versions) == 6


async def test_get_passage_blocks_future_effective_from_and_withdrawn_version() -> None:
    """Reader cannot fetch a passage when version.effective_from > today_vn or version withdrawn."""
    svc = KnowledgeService()
    reader = _reader_user()
    owner = _owner_user()
    now_vn = datetime.now(VN_TZ)

    with _create_knowledge_session() as session:
        db = cast(AsyncSession, _AsyncSessionAdapter(session))
        session.add(
            Document(
                id="DOC-FUT",
                title="Future Effective Policy",
                policy_family="service_warranty_routing",
                authority_tier="policy",
                owner="Lý Hữu Tài",
                source_ref="data/DOC-FUT.md",
            )
        )
        session.add_all(
            [
                DocumentVersion(
                    id="VER-FUT",
                    document_id="DOC-FUT",
                    status=PolicyLifecycleStatus.EFFECTIVE.value,
                    recorded_at=now_vn,
                    effective_from=now_vn + timedelta(days=2),
                ),
                DocumentVersion(
                    id="VER-WTD-VER",
                    document_id="DOC-FUT",
                    status=PolicyLifecycleStatus.WITHDRAWN.value,
                    recorded_at=now_vn - timedelta(days=3),
                    effective_from=now_vn - timedelta(days=3),
                ),
                Passage(
                    id="PAS-FUT",
                    document_id="DOC-FUT",
                    document_version_id="VER-FUT",
                    title="Future Effective Passage",
                    content="Chưa tới ngày hiệu lực.",
                    source_ref="data/DOC-FUT.md",
                    page_number=1,
                    clause_ref="Điều 1",
                    language="vi",
                    scope="company:SN",
                    audience="reader",
                    status=PolicyLifecycleStatus.EFFECTIVE.value,
                    has_essential_attachments=True,
                    is_tombstoned=False,
                ),
                Passage(
                    id="PAS-VER-WTD",
                    document_id="DOC-FUT",
                    document_version_id="VER-WTD-VER",
                    title="Version Withdrawn Passage",
                    content="Phiên bản cha đã bị thu hồi.",
                    source_ref="data/DOC-FUT.md",
                    page_number=2,
                    clause_ref="Điều 2",
                    language="vi",
                    scope="company:SN",
                    audience="reader",
                    status=PolicyLifecycleStatus.EFFECTIVE.value,
                    has_essential_attachments=True,
                    is_tombstoned=False,
                ),
            ]
        )
        session.commit()

        with pytest.raises(AccessDenied, match="effective_from"):
            await svc.get_passage(db, reader, "PAS-FUT")

        # Privileged owner can preview future-effective version
        owner_res = await svc.get_passage(db, owner, "PAS-FUT")
        assert owner_res.passage_id == "PAS-FUT"

        # Withdrawn parent version fails closed with PolicyWithdrawn
        with pytest.raises(PolicyWithdrawn):
            await svc.get_passage(db, reader, "PAS-VER-WTD")


def test_http_endpoints_fail_closed_for_ckpa70() -> None:
    """Verify HTTP 403/409 responses on /api/v1/knowledge/* endpoints for reader."""
    now_vn = datetime.now(VN_TZ)
    reader = _reader_user()
    token = create_access_token(reader)
    headers = {"Authorization": f"Bearer {token}"}

    with _create_knowledge_session() as session:
        session.add(
            Document(
                id="DOC-HTTP-SCH",
                title="Hidden Scheduled Doc",
                policy_family="commercial_quoting_approval",
                authority_tier="policy",
                owner="Owner",
                source_ref="data/http.md",
            )
        )
        session.add(
            DocumentVersion(
                id="VER-HTTP-SCH",
                document_id="DOC-HTTP-SCH",
                status=PolicyLifecycleStatus.SCHEDULED.value,
                recorded_at=now_vn,
                effective_from=now_vn + timedelta(days=3),
            )
        )
        session.add(
            Passage(
                id="PAS-HTTP-SCH",
                document_id="DOC-HTTP-SCH",
                document_version_id="VER-HTTP-SCH",
                title="Hidden Scheduled Passage",
                content="Nội dung tương lai.",
                source_ref="data/http.md",
                page_number=1,
                clause_ref="Điều 1",
                language="vi",
                scope="company:SN",
                audience="reader",
                status=PolicyLifecycleStatus.EFFECTIVE.value,
                has_essential_attachments=True,
                is_tombstoned=False,
            )
        )
        session.commit()

        async def _override_db():
            yield _AsyncSessionAdapter(session)

        app.dependency_overrides[get_db] = _override_db
        try:
            client = TestClient(app)
            lin_res = client.get(
                "/api/v1/knowledge/documents/DOC-HTTP-SCH/lineage", headers=headers
            )
            assert lin_res.status_code == 403
            assert "Hidden Scheduled Doc" not in lin_res.text

            pas_res = client.get("/api/v1/knowledge/passages/PAS-HTTP-SCH", headers=headers)
            assert pas_res.status_code == 403
            assert "Nội dung tương lai" not in pas_res.text
        finally:
            app.dependency_overrides.pop(get_db, None)
