"""Independent G1 regression controls for CKPA-75."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.db import AsyncSessionLocal, Base, engine
from src.main import app
from src.modules.knowledge.models import Document, DocumentVersion, Passage
from src.modules.knowledge.schemas import PassageSummary
from src.modules.knowledge.service import KnowledgeService
from src.modules.policy.schemas import ApplicabilityCandidate, CriticalFieldItem
from src.modules.policy.service import PolicyService
from src.modules.retrieval.service import RetrievalService
from src.modules.selection.schemas import ScopeDimensions
from src.modules.selection.service import SelectionService
from src.shared.auth import AuthenticatedUser, check_policy_audience, create_access_token
from src.shared.enums import (
    AuthorityTier,
    ComparisonOperator,
    CriticalFieldType,
    PolicyLifecycleStatus,
    UserRole,
)
from src.shared.exceptions import PolicyWithdrawn

_EFFECTIVE_FROM = datetime(2026, 1, 1, tzinfo=ZoneInfo(settings.APP_TIMEZONE))


def _candidate(version_id: str = "CKPA75-V1") -> ApplicabilityCandidate:
    return ApplicabilityCandidate(
        version_id=version_id,
        authority_tier=AuthorityTier.POLICY,
        status=PolicyLifecycleStatus.EFFECTIVE,
        effective_from=_EFFECTIVE_FROM,
        scope="branch=all;customer_category=all",
    )


def _critical_field(
    *,
    field_id: str = "CKPA75-CF-1",
    unit: str | None = "%",
    currency: str | None = None,
    field_type: CriticalFieldType = CriticalFieldType.NUMBER,
) -> CriticalFieldItem:
    return CriticalFieldItem(
        field_id=field_id,
        policy_id="CKPA75-POLICY",
        policy_version_id="CKPA75-V1",
        document_version_id="CKPA75-DOC-V1",
        field_name="Discount limit",
        field_type=field_type,
        operator=ComparisonOperator.LE,
        value="15",
        unit=unit,
        currency=currency,
        approval_role="sales_director",
        source_clause="3.2",
        status=PolicyLifecycleStatus.EFFECTIVE,
    )


def _user(role: UserRole, audience: str) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=f"ckpa75-{role.value}",
        email=f"{role.value}@example.test",
        roles=frozenset({role}),
        allowed_audiences=frozenset({audience}),
    )


@pytest.mark.asyncio
async def test_ops01_500_row_reconciliation_sla_and_lkg() -> None:
    """Run the 500-row benchmark and assert the G1 reconciliation/LKG controls."""
    backend_root = str(Path(__file__).resolve().parents[1])
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)
    from scripts.benchmark_ops01_500 import OPS01_MAX_MINUTES, run_ops01_benchmark

    result = await run_ops01_benchmark()
    assert result.total_batch_rows == 500
    assert result.accepted_rows + result.quarantined_rows == 500
    assert result.total_minutes <= OPS01_MAX_MINUTES
    assert result.lkg_quarantine_preserved
    assert result.lkg_failed_batch_preserved


def test_sec01_four_core_roles_have_explicit_audience_boundaries() -> None:
    """Check all four RFP roles against their allowed and cross-role audiences."""
    role_audience = {
        UserRole.READER: "reader",
        UserRole.POLICY_OWNER: "policy_owner",
        UserRole.STEWARD: "steward",
        UserRole.ADMINISTRATOR: "administrator",
    }
    users = {role: _user(role, audience) for role, audience in role_audience.items()}
    for role, audience in role_audience.items():
        assert check_policy_audience(users[role], [audience])
    for role in (UserRole.READER, UserRole.POLICY_OWNER, UserRole.STEWARD):
        other_audiences = set(role_audience.values()) - {role_audience[role]}
        for audience in other_audiences:
            assert not check_policy_audience(users[role], [audience])
    assert check_policy_audience(users[UserRole.ADMINISTRATOR], ["steward"])


def test_sec01_audience_filter_does_not_leak_between_owner_and_steward() -> None:
    owner = _user(UserRole.POLICY_OWNER, "policy_owner")
    steward = _user(UserRole.STEWARD, "steward")
    assert not check_policy_audience(owner, ["steward"])
    assert not check_policy_audience(steward, ["policy_owner"])


def test_knw03_only_effective_lifecycle_state_is_retrievable_by_default() -> None:
    svc = RetrievalService()
    role_audience = {
        UserRole.READER: "reader",
        UserRole.POLICY_OWNER: "policy_owner",
        UserRole.STEWARD: "steward",
        UserRole.ADMINISTRATOR: "administrator",
    }
    states = [
        PolicyLifecycleStatus.DRAFT,
        PolicyLifecycleStatus.OWNER_REVIEWED,
        PolicyLifecycleStatus.APPROVED,
        PolicyLifecycleStatus.SCHEDULED,
        PolicyLifecycleStatus.EFFECTIVE,
        PolicyLifecycleStatus.SUPERSEDED,
        PolicyLifecycleStatus.WITHDRAWN,
        PolicyLifecycleStatus.QUARANTINED,
        PolicyLifecycleStatus.FEEDBACK_CANDIDATE,
    ]
    passages = [
        PassageSummary(
            passage_id=f"CKPA75-{role.value}-{state.value}",
            document_id="CKPA75-DOC",
            document_version_id="CKPA75-DOC-V1",
            title="G1 lifecycle test",
            content="policy content",
            source_ref="test",
            page_number=1,
            clause_ref="1",
            language="vi",
            scope="all",
            audience=[audience],
            status=state,
            has_essential_attachments=True,
            effective_from=_EFFECTIVE_FROM,
        )
        for role, audience in role_audience.items()
        for state in states
    ]
    for role, audience in role_audience.items():
        filtered = svc.prefilter_passages(
            _user(role, audience),
            passages,
            governing_date=date(2026, 11, 24),
        )
        expected_count = len(role_audience) if role == UserRole.ADMINISTRATOR else 1
        assert len(filtered) == expected_count
        assert all(item.status == PolicyLifecycleStatus.EFFECTIVE for item in filtered)


@pytest.mark.asyncio
async def test_sec05_withdrawn_passage_is_denied_by_database_backed_knowledge_service() -> None:
    """Exercise KnowledgeService against inserted rows, rolling back all fixture data."""
    suffix = uuid.uuid4().hex
    document_id = f"CKPA75-DOC-{suffix}"
    version_id = f"CKPA75-VERSION-{suffix}"
    passage_id = f"CKPA75-PASSAGE-{suffix}"
    now = datetime.now(UTC)
    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all,
            tables=[Document.__table__, DocumentVersion.__table__, Passage.__table__],
        )
    async with AsyncSessionLocal() as db:
        try:
            db.add(
                Document(
                    id=document_id,
                    title="CKPA-75 withdrawn control",
                    policy_family="commercial",
                    authority_tier="policy",
                    owner="test",
                    source_ref="test",
                )
            )
            db.add(
                DocumentVersion(
                    id=version_id,
                    document_id=document_id,
                    approver="test",
                    recorded_at=now,
                    published_at=now,
                    effective_from=now,
                    status=PolicyLifecycleStatus.WITHDRAWN.value,
                )
            )
            db.add(
                Passage(
                    id=passage_id,
                    document_id=document_id,
                    document_version_id=version_id,
                    title="Withdrawn",
                    content="must not be returned",
                    source_ref="test",
                    page_number=1,
                    clause_ref="1",
                    language="vi",
                    scope="all",
                    audience="reader",
                    status=PolicyLifecycleStatus.WITHDRAWN.value,
                    is_tombstoned=True,
                )
            )
            await db.flush()
            with pytest.raises(PolicyWithdrawn):
                await KnowledgeService().get_passage(
                    db,
                    _user(UserRole.ADMINISTRATOR, "administrator"),
                    passage_id,
                    allow_historical=True,
                )
        finally:
            await db.rollback()


def test_sec05_redis_withdrawal_task_purges_version_cache_keys() -> None:
    """Invoke the worker task against Redis and verify actual matching keys are removed."""
    import redis

    policy_version_id = f"CKPA75-{uuid.uuid4().hex}"
    cache = redis.from_url(settings.REDIS_URL)
    keys = [f"ans:ckpa75:{policy_version_id}", f"ret:ckpa75:{policy_version_id}"]
    try:
        cache.mset({key: "cached" for key in keys})
        worker_root = str(Path(__file__).resolve().parents[2] / "worker")
        env = os.environ.copy()
        env["PYTHONPATH"] = worker_root
        script = (
            "from src.tasks.index_task import withdraw_and_purge_cache; "
            f"result = withdraw_and_purge_cache.run({policy_version_id!r}); "
            "print(result['purged_keys'])"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=False,
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
            cwd=worker_root,
        )
        assert completed.returncode == 0, completed.stderr
        assert completed.stdout.strip().endswith("2")
        assert not any(cache.exists(key) for key in keys)
    finally:
        cache.delete(*keys)
        cache.close()


def test_ops03_policy_gate_fails_closed_without_requested_date() -> None:
    gate = PolicyService().evaluate_policy_gate(
        [_candidate()],
        requested_date=None,
    )
    assert not gate.can_proceed
    assert gate.hold_reason is not None
    assert "Thiếu ngày chi phối" in gate.hold_reason


def test_ops03_selection_holds_when_requested_date_is_missing() -> None:
    svc = SelectionService()
    gate = PolicyService().evaluate_policy_gate([_candidate()], requested_date=None)
    result = svc.run_selection(
        candidates=[_candidate()],
        dimensions=ScopeDimensions(),
        all_critical_fields=[],
        gate_decision=gate,
        requested_date=None,
    )
    assert result.hold_decision.must_hold
    assert any(
        trigger.code == "DAT04_NO_GOVERNING_DATE"
        for trigger in result.hold_decision.triggers
    )


def test_ops03_selection_holds_number_field_missing_unit() -> None:
    svc = SelectionService()
    fields = [
        _critical_field(field_id="CKPA75-NUMBER", unit=None),
        _critical_field(
            field_id="CKPA75-DURATION",
            unit=None,
            field_type=CriticalFieldType.DURATION,
        ),
        _critical_field(
            field_id="CKPA75-CURRENCY",
            unit="currency",
            currency=None,
            field_type=CriticalFieldType.CURRENCY,
        ),
    ]
    for field in fields:
        gate = PolicyService().evaluate_policy_gate(
            [_candidate()],
            requested_date=date(2026, 11, 24),
        )
        result = svc.run_selection(
            candidates=[_candidate()],
            dimensions=ScopeDimensions(),
            all_critical_fields=[field],
            gate_decision=gate,
            requested_date=date(2026, 11, 24),
        )
        assert result.hold_decision.must_hold, field.field_id
        assert any(
            trigger.code == "DAT08_MISSING_TABLE_OR_ANNOTATION"
            for trigger in result.hold_decision.triggers
        ), field.field_id


def test_ops04_numeric_threshold_is_deterministic_at_boundary() -> None:
    svc = SelectionService()
    assert svc.evaluate_numeric_threshold(ComparisonOperator.LE, "5", "5") is True
    assert svc.evaluate_numeric_threshold(ComparisonOperator.LE, "5.01", "5") is False


def test_ops03_selection_holds_when_no_candidate_applies() -> None:
    gate = PolicyService().evaluate_policy_gate(
        [],
        requested_date=date(2026, 11, 24),
    )
    assert not gate.can_proceed
    assert gate.applicable_version_ids == ()
    assert gate.hold_reason is not None


def test_o1_context_import_remains_disabled_in_base_scope() -> None:
    assert settings.ENABLE_O1_CONTEXT_IMPORT is False
    user = _user(UserRole.STEWARD, "steward")
    token = create_access_token(user)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ingestion/o1/context/import",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 403
    assert response.json()["detail"] == "O1_OPTION_DISABLED_IN_BASE_SCOPE"
