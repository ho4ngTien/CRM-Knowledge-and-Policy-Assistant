import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name:
    fileConfig(config.config_file_name)

import src.modules.answer.models  # noqa: E402, F401
import src.modules.audit.models  # noqa: E402, F401
import src.modules.evaluation.models  # noqa: E402, F401
import src.modules.feedback.models  # noqa: E402, F401
import src.modules.identity.models  # noqa: E402, F401
import src.modules.ingestion.models  # noqa: E402, F401
import src.modules.knowledge.models  # noqa: E402, F401
import src.modules.policy.models  # noqa: E402, F401
import src.modules.referral.models  # noqa: E402, F401
from src.db import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
