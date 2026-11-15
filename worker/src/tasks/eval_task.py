"""Celery offline evaluation task isolating Chinese Wall partitions (RFP Section 8)."""

from datetime import datetime
from zoneinfo import ZoneInfo

from src.celery_app import app

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


@app.task(name="src.tasks.eval_task.run_evaluation")
def run_evaluation(run_id: str, partition: str) -> dict[str, object]:
    """Execute independent batch evaluation for dev_60, val_40, sealed_100, or challenges_80."""
    return {
        "run_id": run_id,
        "partition": partition,
        "status": "scheduled_scaffold",
        "started_at_vn": datetime.now(VN_TZ).isoformat(),
    }
