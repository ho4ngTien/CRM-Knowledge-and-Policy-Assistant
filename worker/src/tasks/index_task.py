"""Celery indexing, scheduled VN activation, and <=5m withdrawal purge tasks."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import redis

from src.celery_app import app

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


@app.task(name="src.tasks.index_task.index_passages")
def index_passages(document_version_id: str) -> dict[str, object]:
    """Recompute pgvector embeddings for curated passages belonging to a document version."""
    return {
        "document_version_id": document_version_id,
        "status": "indexed_scaffold",
        "indexed_at": datetime.now(VN_TZ).isoformat(),
    }


@app.task(name="src.tasks.index_task.activate_scheduled_policies")
def activate_scheduled_policies() -> dict[str, object]:
    """Promote scheduled policies whose Asia/Ho_Chi_Minh effective_from <= now_vn (KNW 03)."""
    return {
        "checked_at_vn": datetime.now(VN_TZ).isoformat(),
        "activated_count": 0,
        "status": "checked_scaffold",
    }


@app.task(name="src.tasks.index_task.withdraw_and_purge_cache")
def withdraw_and_purge_cache(policy_version_id: str) -> dict[str, object]:
    """Physically purge retrieval/answer Redis cache keys well within <= 5 minutes (KNW 04)."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    purged_keys = 0
    try:
        client = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        for pattern in (f"ans:*{policy_version_id}*", f"ret:*{policy_version_id}*"):
            keys = list(client.scan_iter(match=pattern, count=200))
            if keys:
                purged_keys += int(client.delete(*keys))
        client.close()
    except redis.RedisError:
        purged_keys = -1

    return {
        "policy_version_id": policy_version_id,
        "purged_keys": purged_keys,
        "sla_max_seconds": int(os.getenv("CACHE_WITHDRAWAL_MAX_SECONDS", "300")),
        "completed_at_vn": datetime.now(VN_TZ).isoformat(),
    }
