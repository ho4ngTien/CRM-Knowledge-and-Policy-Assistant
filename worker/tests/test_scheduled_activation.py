"""Scheduled-policy activation boundary tests using the worker's own Python package."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from src.tasks import index_task

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
VN_NOW = datetime(2026, 12, 28, 9, 0, tzinfo=VN_TZ)


class _FakeResult:
    def __init__(self, rows: list[dict[str, object]] | None = None, rowcount: int = 1) -> None:
        self._rows = rows or []
        self.rowcount = rowcount

    def mappings(self) -> _FakeResult:
        return self

    def scalars(self) -> _FakeResult:
        return self

    def all(self) -> list[dict[str, object]]:
        return self._rows


class _FakeScheduledConnection:
    def __init__(self, effective_from: datetime) -> None:
        self.effective_from = effective_from
        self.activated_ids: list[str] = []
        self.cutoff: datetime | None = None

    async def execute(
        self,
        statement: object,
        parameters: dict[str, object] | None = None,
    ) -> _FakeResult:
        sql = str(statement)
        params = parameters or {}
        if "SELECT id, document_version_id" in sql:
            assert "effective_from <= :now_vn" in sql
            cutoff = params["now_vn"]
            assert isinstance(cutoff, datetime)
            self.cutoff = cutoff
            due_rows = (
                [{"id": "PVER-DUE", "document_version_id": "DVER-DUE"}]
                if self.effective_from <= cutoff
                else []
            )
            return _FakeResult(due_rows)
        if "UPDATE policy_versions" in sql:
            self.activated_ids.append(str(params["policy_version_id"]))
        if "SELECT DISTINCT answer_package_id" in sql:
            return _FakeResult()
        return _FakeResult()


class _FakeEngine:
    def __init__(self, connection: _FakeScheduledConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> _FakeScheduledConnection:
        return self.connection

    async def __aexit__(self, *args: object) -> None:
        _ = args

    def begin(self) -> _FakeEngine:
        return self

    async def dispose(self) -> None:
        return None


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
async def test_worker_activates_only_at_or_after_vietnam_effective_time(
    monkeypatch: pytest.MonkeyPatch,
    effective_offset: timedelta,
    expected_activated: bool,
) -> None:
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz: ZoneInfo | None = None) -> datetime:
            assert tz == VN_TZ
            return VN_NOW

    connection = _FakeScheduledConnection(VN_NOW + effective_offset)
    engine = _FakeEngine(connection)
    monkeypatch.setattr(index_task, "datetime", FrozenDateTime)
    monkeypatch.setattr(index_task, "create_async_engine", lambda _: engine)

    result = await index_task._activate_scheduled_policies("postgresql+asyncpg://unit-test")

    assert connection.cutoff == VN_NOW
    assert connection.cutoff.tzinfo == VN_TZ
    assert connection.activated_ids == (["PVER-DUE"] if expected_activated else [])
    assert result["activated_count"] == (1 if expected_activated else 0)
    assert result["timezone"] == "Asia/Ho_Chi_Minh"
    assert result["checked_at_vn"] == VN_NOW.isoformat()
