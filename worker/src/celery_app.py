"""Celery application — background jobs for import, indexing, evaluation."""

import os

from celery import Celery

app = Celery(
    "ckpa-worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
    include=["src.tasks.import_task", "src.tasks.index_task", "src.tasks.eval_task"],
)

app.conf.timezone = "Asia/Ho_Chi_Minh"
app.conf.enable_utc = False

app.conf.beat_schedule = {
    # Chạy snapshot staleness check mỗi giờ
    "check-snapshot-staleness": {
        "task": "src.tasks.import_task.check_staleness",
        "schedule": 3600.0,
    },
    # Kích hoạt chính sách scheduled khi tới thời điểm hiệu lực Asia/Ho_Chi_Minh
    "activate-scheduled-policies": {
        "task": "src.tasks.index_task.activate_scheduled_policies",
        "schedule": 60.0,
    },
}
