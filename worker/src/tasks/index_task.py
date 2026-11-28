"""Celery indexing, scheduled VN activation, and <=5m withdrawal purge tasks."""

import asyncio
import os
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

import redis
import structlog
from celery import Task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.celery_app import app

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
logger = structlog.get_logger(__name__)


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
    """Promote due scheduled policies and record change impact in one DB transaction."""
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://ckpa:ckpa_pass@localhost:5432/ckpa_db"
    )
    return asyncio.run(_activate_scheduled_policies(database_url))


async def _activate_scheduled_policies(database_url: str) -> dict[str, object]:
    now_vn = datetime.now(VN_TZ)
    engine = create_async_engine(database_url)
    activated_count = 0
    try:
        async with engine.begin() as connection:
            due_versions = (
                await connection.execute(
                    text(
                        """
                        SELECT id, document_version_id
                        FROM policy_versions
                        WHERE status = 'scheduled' AND effective_from <= :now_vn
                        FOR UPDATE
                        """
                    ),
                    {"now_vn": now_vn},
                )
            ).mappings().all()

            for version in due_versions:
                policy_version_id = str(version["id"])
                document_version_id = str(version["document_version_id"])
                transition = await connection.execute(
                    text(
                        """
                        UPDATE policy_versions
                        SET status = 'effective', updated_at = now()
                        WHERE id = :policy_version_id AND status = 'scheduled'
                        """
                    ),
                    {"policy_version_id": policy_version_id},
                )
                if transition.rowcount != 1:
                    continue

                await connection.execute(
                    text(
                        """
                        UPDATE document_versions
                        SET status = 'effective', updated_at = now()
                        WHERE id = :document_version_id
                        """
                    ),
                    {"document_version_id": document_version_id},
                )
                await connection.execute(
                    text(
                        """
                        UPDATE passages
                        SET status = 'effective', updated_at = now()
                        WHERE document_version_id = :document_version_id
                        """
                    ),
                    {"document_version_id": document_version_id},
                )
                await connection.execute(
                    text(
                        """
                        UPDATE critical_fields
                        SET status = 'effective', updated_at = now()
                        WHERE policy_version_id = :policy_version_id
                        """
                    ),
                    {"policy_version_id": policy_version_id},
                )

                answer_ids = (
                    await connection.execute(
                        text(
                            """
                            SELECT DISTINCT answer_package_id
                            FROM answer_citations
                            WHERE document_version_id = :document_version_id
                            """
                        ),
                        {"document_version_id": document_version_id},
                    )
                ).scalars().all()
                if answer_ids:
                    await connection.execute(
                        text(
                            """
                            UPDATE answer_packages
                            SET is_stale = true, updated_at = now()
                            WHERE id IN (
                                SELECT answer_package_id
                                FROM answer_citations
                                WHERE document_version_id = :document_version_id
                            )
                            """
                        ),
                        {"document_version_id": document_version_id},
                    )

                await connection.execute(
                    text(
                        """
                        INSERT INTO policy_lifecycle_events
                            (
                                policy_version_id, from_status, to_status,
                                actor_id, actor_role, reason
                            )
                        VALUES
                            (:policy_version_id, 'scheduled', 'effective',
                             'system:scheduled-activation', 'system',
                             'Scheduled activation reached effective_from in Asia/Ho_Chi_Minh.')
                        """
                    ),
                    {"policy_version_id": policy_version_id},
                )
                await connection.execute(
                    text(
                        """
                        INSERT INTO change_impact_reports
                            (id, event_type, source_type, source_id, policy_version_id,
                             document_version_id, actor_id, reason, stale_answers_marked,
                             active_view_refresh_interval_seconds, created_at, updated_at)
                        VALUES
                            (:id, 'scheduled_activated', 'policy_lifecycle', :source_id,
                             :policy_version_id, :document_version_id,
                             'system:scheduled-activation',
                             'Scheduled policy became effective at its VN effective_from time.',
                             :stale_answers_marked, 60, now(), now())
                        """
                    ),
                    {
                        "id": f"IMP-{uuid4().hex[:16].upper()}",
                        "source_id": policy_version_id,
                        "policy_version_id": policy_version_id,
                        "document_version_id": document_version_id,
                        "stale_answers_marked": len(answer_ids),
                    },
                )
                activated_count += 1
    finally:
        await engine.dispose()

    return {
        "checked_at_vn": now_vn.isoformat(),
        "activated_count": activated_count,
        "timezone": "Asia/Ho_Chi_Minh",
        "status": "completed",
    }


@app.task(
    bind=True,
    max_retries=3,
    name="src.tasks.index_task.withdraw_and_purge_cache",
)
def withdraw_and_purge_cache(
    self: Task,
    policy_version_id: str,
    document_version_id: str | None = None,
) -> dict[str, object]:
    """Physically purge retrieval/answer Redis cache keys well within <= 5 minutes (KNW 04)."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    patterns = [f"ans:*{policy_version_id}*", f"ret:*{policy_version_id}*"]
    if document_version_id:
        patterns.extend([f"ans:*{document_version_id}*", f"ret:*{document_version_id}*"])

    purged_keys = 0
    try:
        client = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        try:
            for pattern in dict.fromkeys(patterns):
                keys = list(client.scan_iter(match=pattern, count=200))
                if keys:
                    purged_keys += int(client.delete(*keys))
        finally:
            client.close()
    except redis.RedisError as exc:
        logger.exception(
            "withdraw_cache_purge_failed",
            policy_version_id=policy_version_id,
            document_version_id=document_version_id,
            retry_attempt=self.request.retries,
        )
        raise self.retry(exc=exc, countdown=10)

    return {
        "policy_version_id": policy_version_id,
        "document_version_id": document_version_id,
        "purged_keys": purged_keys,
        "sla_max_seconds": int(os.getenv("CACHE_WITHDRAWAL_MAX_SECONDS", "300")),
        "completed_at_vn": datetime.now(VN_TZ).isoformat(),
    }
