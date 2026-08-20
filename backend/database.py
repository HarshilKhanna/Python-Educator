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

async def get_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    async with AsyncSessionLocal() as session:
        yield session
