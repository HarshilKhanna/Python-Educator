"""
conftest.py — shared pytest configuration for the backend test suite.

Problem this solves: multiple test files each do
  `app.dependency_overrides[get_db] = override_get_db`
at module level, so whichever file is imported last wins, causing 500s in
other test files. This conftest moves all FastAPI dependency overrides into
an autouse session-scoped fixture so every test gets a clean, isolated session.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import Base, Mastery, AdaptationEvent, AuditLog, PendingAdaptation
from main import app
from database import get_db

# ---------------------------------------------------------------------------
# Shared in-memory SQLite engine for all HTTP-layer tests
# ---------------------------------------------------------------------------

# We can create all tables; SQLite ignores unknown column types like VECTOR(384).

import os

TEST_DB_PATH = "./test.db"
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

_http_engine = create_async_engine(
    f"sqlite+aiosqlite:///{TEST_DB_PATH}", 
    echo=False,
)
_HttpSession = async_sessionmaker(bind=_http_engine, class_=AsyncSession, expire_on_commit=False)


async def _override_get_db():
    async with _HttpSession() as session:
        yield session


@pytest_asyncio.fixture(autouse=True, scope="function")
async def _setup_http_db():
    """
    Ensures the shared HTTP-layer SQLite DB is created before each test and
    the FastAPI dependency override always points to it.
    """
    app.dependency_overrides[get_db] = _override_get_db
    async with _http_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _http_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.pop(get_db, None)
