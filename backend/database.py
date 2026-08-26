from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

# Use an async Postgres URL for real usage, e.g., "postgresql+asyncpg://user:pass@localhost/db"
# For testing and local development without a DB running, we'll configure it via environment variables.
# But since this is a prototype, we'll default to a local Postgres instance.

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# ---------------------------------------------------------------------------
# Schema migrations (idempotent ADD COLUMN IF NOT EXISTS)
# Run once at startup before any request is handled.
# Alembic is the right tool at production scale; for the research prototype
# we keep it simple with explicit ALTER TABLE statements.
# ---------------------------------------------------------------------------

_MIGRATIONS = [
    # Phase 11: source provenance on chunks
    "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS source_type VARCHAR DEFAULT 'handbook' NOT NULL",
    "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS uploaded_by VARCHAR",
    "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS uploaded_at TIMESTAMPTZ",
    # Phase 12: rejection reason on pending adaptations
    "ALTER TABLE pending_adaptations ADD COLUMN IF NOT EXISTS review_note VARCHAR",
]


async def run_migrations(conn) -> None:
    """Run idempotent column-level migrations. Safe to call every startup.
    
    Migrations are skipped for SQLite (used in tests) — SQLite's ALTER TABLE
    has limited syntax and the test fixtures use create_all() instead.
    """
    # Skip for SQLite (test environments)
    dialect_name = conn.engine.dialect.name if hasattr(conn, "engine") else ""
    if not dialect_name:
        try:
            dialect_name = conn.dialect.name
        except Exception:
            dialect_name = ""
    if "sqlite" in dialect_name.lower():
        return

    # Enable pgvector first
    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    for sql in _MIGRATIONS:
        try:
            await conn.execute(text(sql))
        except Exception:
            pass  # table may not exist yet on first boot — create_all handles it


async def get_db():
    async with engine.begin() as conn:
        await run_migrations(conn)
    async with AsyncSessionLocal() as session:
        yield session
