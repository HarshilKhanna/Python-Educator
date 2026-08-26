"""
env.py — Alembic migration environment for async SQLAlchemy + pgvector.

Reads the database URL from config.DATABASE_URL so no credentials are
stored in alembic.ini. Uses asyncio/asyncpg for the connection.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ---------------------------------------------------------------------------
# Make the backend package importable when running `alembic` from backend/
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

import config as app_config  # noqa: E402 — must come after sys.path insert

# Import Base + all models so Alembic can see the full metadata
from database import Base  # noqa: E402
import models  # noqa: E402, F401 — registers all table metadata on Base

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
alembic_cfg = context.config

# Override the sqlalchemy.url from our config module (not alembic.ini)
alembic_cfg.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)

# Set up Python logging from the ini file if present
if alembic_cfg.config_file_name is not None:
    fileConfig(alembic_cfg.config_file_name)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline mode — generates SQL without a live DB connection
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generates SQL script)."""
    url = alembic_cfg.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — connects to a real database
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Connect asynchronously and run migrations."""
    connectable = async_engine_from_config(
        alembic_cfg.get_section(alembic_cfg.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
