"""KNW 03 lifecycle transition and VN scheduled-activation boundary tests."""

from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

import src.modules.admin.service as admin_service_module
from src.modules.admin.models import ALLOWED_LIFECYCLE_TRANSITIONS, KNW03_LIFECYCLE_STATUSES
from src.modules.admin.service import AdminService
from src.shared.auth import AuthenticatedUser
from src.shared.enums import PolicyLifecycleStatus, UserRole
from src.shared.exceptions import SourceConflict

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
VN_NOW = datetime(2026, 12, 28, 9, 0, tzinfo=VN_TZ)
KNW03_STATES = tuple(
    status
    for status in PolicyLifecycleStatus
    if status in KNW03_LIFECYCLE_STATUSES
)


class _FakeAdminSession:
    def __init__(self, version: SimpleNamespace) -> None:
        self.version = version
        self.added: list[object] = []
        self.commit_count = 0

    async def get(self, entity: type, identity: str) -> SimpleNamespace:
        _ = entity, identity
        return self.version

    def add(self, entity: object) -> None:
        self.added.append(entity)

    async def commit(self) -> None:
        self.commit_count += 1


class _FakeCachePurger:
    async def purge_policy_caches(self, policy_version_id: str, document_version_id: str) -> None:
        _ = policy_version_id, document_version_id


def _policy_version(status: PolicyLifecycleStatus, effective_from: datetime) -> SimpleNamespace:
    return SimpleNamespace(
        id="PVER-CKPA94",
        policy_id="POL-CKPA94",
        document_version_id="DVER-CKPA94",
        status=status.value,
        effective_from=effective_from,
    )


def _policy_owner() -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id="OWNER-CKPA94",
        email="owner@example.test",
        roles=frozenset({UserRole.POLICY_OWNER}),
    )


def _stub_impact_recording(service: AdminService) -> None:
    async def record_impact(*args: object, **kwargs: object) -> SimpleNamespace:
        _ = args, kwargs
        return SimpleNamespace(id="IMP-CKPA94")

    async def sync_status(*args: object, **kwargs: object) -> None:
        _ = args, kwargs

    service._change_impact.record_impact = record_impact
    service._sync_authoritative_status = sync_status


def _freeze_admin_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz: ZoneInfo | None = None) -> datetime:
            assert tz == VN_TZ
            return VN_NOW

    monkeypatch.setattr(admin_service_module, "datetime", FrozenDateTime)


@pytest.mark.parametrize(
    ("current_status", "target_status"),
    [(current, target) for current in KNW03_STATES for target in KNW03_STATES],
)
@pytest.mark.asyncio
async def test_transition_policy_status_enforces_the_complete_seven_state_matrix(
    monkeypatch: pytest.MonkeyPatch,
    current_status: PolicyLifecycleStatus,
    target_status: PolicyLifecycleStatus,
) -> None:
    _freeze_admin_clock(monkeypatch)
    service = AdminService()
    _stub_impact_recording(service)
    version = _policy_version(current_status, VN_NOW - timedelta(days=1))
    session = _FakeAdminSession(version)
    should_transition = target_status in ALLOWED_LIFECYCLE_TRANSITIONS[current_status]

    if should_transition:
        response = await service.transition_policy_status(
            session,  # type: ignore[arg-type]
            _policy_owner(),
            version.id,
            target_status,
            "Unit test transition.",
            cache_purger=_FakeCachePurger(),
        )
        assert version.status == target_status.value
        assert session.commit_count == 1
        assert response.previous_status == current_status
        assert response.current_status == target_status
    else:
        with pytest.raises(SourceConflict, match="Illegal transition"):
            await service.transition_policy_status(
                session,  # type: ignore[arg-type]
                _policy_owner(),
                version.id,
                target_status,
                "Unit test invalid transition.",
                cache_purger=_FakeCachePurger(),
            )
        assert version.status == current_status.value
        assert session.commit_count == 0


@pytest.mark.parametrize("target_status", KNW03_STATES)
@pytest.mark.asyncio
async def test_transition_policy_status_rejects_quarantined_target_with_clear_error(
    target_status: PolicyLifecycleStatus,
) -> None:
    service = AdminService()
    version = _policy_version(target_status, VN_NOW - timedelta(days=1))
    session = _FakeAdminSession(version)

    with pytest.raises(SourceConflict, match="QUARANTINED.*DAT 02"):
        await service.transition_policy_status(
            session,  # type: ignore[arg-type]
            _policy_owner(),
            version.id,
            PolicyLifecycleStatus.QUARANTINED,
            "Must not enter quarantine through lifecycle.",
        )

    assert version.status == target_status.value
    assert session.commit_count == 0


@pytest.mark.parametrize("target_status", KNW03_STATES)
@pytest.mark.asyncio
async def test_transition_policy_status_rejects_quarantined_source_with_clear_error(
    target_status: PolicyLifecycleStatus,
) -> None:
    service = AdminService()
    version = _policy_version(PolicyLifecycleStatus.QUARANTINED, VN_NOW - timedelta(days=1))
    session = _FakeAdminSession(version)

    with pytest.raises(SourceConflict, match="QUARANTINED.*DAT 02"):
        await service.transition_policy_status(
            session,  # type: ignore[arg-type]
            _policy_owner(),
            version.id,
            target_status,
            "Must not exit quarantine through lifecycle.",
        )

    assert version.status == PolicyLifecycleStatus.QUARANTINED.value
    assert session.commit_count == 0


@pytest.mark.parametrize(
    ("effective_offset", "expected_activated"),
    [
        (timedelta(microseconds=1), False),
        (timedelta(0), True),
        (timedelta(microseconds=-1), True),
    ],
    ids=("before-effective-time", "at-effective-time", "after-effective-time"),
)
@pytest.mark.asyncio
async def test_scheduled_transition_uses_exact_vietnam_effective_time(
    monkeypatch: pytest.MonkeyPatch,
    effective_offset: timedelta,
    expected_activated: bool,
) -> None:
    _freeze_admin_clock(monkeypatch)
    service = AdminService()
    _stub_impact_recording(service)
    version = _policy_version(
        PolicyLifecycleStatus.SCHEDULED,
        VN_NOW + effective_offset,
    )
    session = _FakeAdminSession(version)

    if expected_activated:
        await service.transition_policy_status(
            session,  # type: ignore[arg-type]
            _policy_owner(),
            version.id,
            PolicyLifecycleStatus.EFFECTIVE,
            "Effective time boundary test.",
            cache_purger=_FakeCachePurger(),
        )
        assert version.status == PolicyLifecycleStatus.EFFECTIVE.value
        assert session.commit_count == 1
    else:
        with pytest.raises(SourceConflict, match="prior to VN effective_from"):
            await service.transition_policy_status(
                session,  # type: ignore[arg-type]
                _policy_owner(),
                version.id,
                PolicyLifecycleStatus.EFFECTIVE,
                "Effective time boundary test.",
                cache_purger=_FakeCachePurger(),
            )
        assert version.status == PolicyLifecycleStatus.SCHEDULED.value
        assert session.commit_count == 0

def test_knw03_transition_table_contains_exactly_seven_states() -> None:
    assert set(ALLOWED_LIFECYCLE_TRANSITIONS) == KNW03_LIFECYCLE_STATUSES
    assert all(
        target in KNW03_LIFECYCLE_STATUSES
        for targets in ALLOWED_LIFECYCLE_TRANSITIONS.values()
        for target in targets
    )
    assert PolicyLifecycleStatus.QUARANTINED not in ALLOWED_LIFECYCLE_TRANSITIONS
