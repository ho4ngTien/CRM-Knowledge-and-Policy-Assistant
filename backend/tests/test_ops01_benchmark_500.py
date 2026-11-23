"""BDD & Contract Tests for CKPA-60 (OPS 01): 500-row benchmark <= 30m & 100% LKG."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_ckpa60_ops01_500_rows_under_30_minutes_and_lkg_preserved() -> None:
    """Verify 500-row add/update/tombstone/error batch <= 30m and LKG stays 100% intact."""
    backend_root = str(Path(__file__).resolve().parents[1])
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)

    from scripts.benchmark_ops01_500 import OPS01_MAX_MINUTES, run_ops01_benchmark

    result = await run_ops01_benchmark()

    assert result.total_batch_rows == 500
    assert result.added_rows == 380
    assert result.updated_rows == 60
    assert result.tombstone_rows == 30
    assert result.quarantined_rows == 30
    assert result.accepted_rows == 470
    assert result.rejected_rows == 0
    assert result.accepted_rows + result.quarantined_rows == result.total_batch_rows
    assert result.total_minutes <= OPS01_MAX_MINUTES
    assert result.passed_sla_30m is True
    assert result.lkg_quarantine_preserved is True
    assert result.lkg_failed_batch_preserved is True
    assert result.idempotent_zero_duplicates is True
