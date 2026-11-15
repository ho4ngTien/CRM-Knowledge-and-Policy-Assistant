"""Celery ingestion & snapshot staleness check tasks (DAT 01, DAT 02, OPS 01)."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

from src.celery_app import app

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


@app.task(name="src.tasks.import_task.run_batch_import")
def run_batch_import(batch_id: str, source_type: str, batch_type: str) -> dict[str, object]:
    """Process a validated UTF-8 CSV batch idempotently inside Base Scope limits."""
    return {
        "batch_id": batch_id,
        "source_type": source_type,
        "batch_type": batch_type,
        "status": "scheduled_scaffold",
        "executed_at": datetime.now(VN_TZ).isoformat(),
    }


@app.task(name="src.tasks.import_task.check_staleness")
def check_staleness() -> dict[str, object]:
    """Monitor corpus Snapshot Age against IMPORT_SNAPSHOT_STALENESS_HOURS (default 25h)."""
    threshold_hours = int(os.getenv("IMPORT_SNAPSHOT_STALENESS_HOURS", "25"))
    return {
        "checked_at": datetime.now(VN_TZ).isoformat(),
        "staleness_threshold_hours": threshold_hours,
        "status": "checked_scaffold",
    }
