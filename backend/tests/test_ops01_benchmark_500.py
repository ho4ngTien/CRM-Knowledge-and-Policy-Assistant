"""BDD & Contract Tests for CKPA-60 / CKPA-75 (OPS 01): 500-row benchmark, LKG & PostgreSQL."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


def _load_benchmark_module() -> tuple[float, object]:
    backend_root = str(Path(__file__).resolve().parents[1])
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)

    from scripts.benchmark_ops01_500 import OPS01_MAX_MINUTES, run_ops01_benchmark

    return OPS01_MAX_MINUTES, run_ops01_benchmark


@pytest.mark.asyncio
async def test_ckpa60_ops01_500_rows_under_30_minutes_and_lkg_preserved() -> None:
    """Verify 500-row add/update/tombstone/error batch <= 30m and LKG stays 100% intact."""
    max_minutes, run_ops01_benchmark = _load_benchmark_module()
    result = await run_ops01_benchmark()  # type: ignore[operator]

    assert result.total_batch_rows == 500
    assert result.added_rows == 380
    assert result.updated_rows == 60
    assert result.tombstone_rows == 30
    assert result.quarantined_rows == 30
    assert result.accepted_rows == 470
    assert result.rejected_rows == 0
    assert result.accepted_rows + result.quarantined_rows == result.total_batch_rows
    assert result.total_minutes <= max_minutes
    assert result.passed_sla_30m is True
    assert result.lkg_quarantine_preserved is True
    assert result.lkg_failed_batch_preserved is True
    assert result.lkg_checksum_mismatch_preserved is True
    assert result.idempotent_zero_duplicates is True


@pytest.mark.asyncio
async def test_ckpa75_ops01_500_rows_and_checksum_fault_on_postgresql() -> None:
    """Run OPS 01 500-row benchmark + checksum fault injection on real PostgreSQL when available."""
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url.startswith("postgresql"):
        pytest.skip("PostgreSQL DATABASE_URL not configured in this environment.")

    max_minutes, run_ops01_benchmark = _load_benchmark_module()
    result = await run_ops01_benchmark(database_url=db_url)  # type: ignore[operator]

    assert result.backend_engine == "PostgreSQL 16 + pgvector"
    assert result.total_batch_rows == 500
    assert result.accepted_rows == 470
    assert result.quarantined_rows == 30
    assert result.total_minutes <= max_minutes
    assert result.passed_sla_30m is True
    assert result.lkg_quarantine_preserved is True
    assert result.lkg_failed_batch_preserved is True
    assert result.lkg_checksum_mismatch_preserved is True
    assert result.idempotent_zero_duplicates is True
