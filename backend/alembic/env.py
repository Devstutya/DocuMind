# backend/alembic/env.py
"""Alembic environment configuration.

Uses the async engine pattern so that ``alembic upgrade head`` works with the
same ``DATABASE_URL`` (sqlite+aiosqlite or postgresql+asyncpg) used at runtime.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ---------------------------------------------------------------------------
# Make the app package importable when running alembic from backend/
# ---------------------------------------------------------------------------
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Import settings and ORM models so Base.metadata is populated
# ---------------------------------------------------------------------------
from app.config import settings  # noqa: E402
from app.database import Base  # noqa: E402
import app.db_models  # noqa: F401, E402 — registers models with Base

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Override the sqlalchemy.url from settings so the .env file is the single
# source of truth.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Set up Python logging from the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object used for autogenerate support.
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration (generate SQL without a live connection)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Emits the migration SQL to stdout rather than executing it, which is
    useful for generating scripts to review before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (execute against a live database)
# ---------------------------------------------------------------------------

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
