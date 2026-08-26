"""
conftest.py — shared pytest configuration for the backend test suite.

Problem this solves: multiple test files each do
  `app.dependency_overrides[get_db] = override_get_db`
at module level, so whichever file is imported last wins, causing 500s in
other test files. This conftest moves all FastAPI dependency overrides into
an autouse session-scoped fixture so every test gets a clean, isolated session.

Phase 14 update: added User model to imports so the users table is created in
the test SQLite DB. Added token-generation helpers for auth tests.
"""

import sys
from pathlib import Path

# Ensure the backend root is on sys.path so imports like `from models import ...`
# work regardless of how pytest is invoked (same pattern as all other test files).
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models import Base, Mastery, AdaptationEvent, AuditLog, PendingAdaptation, User
from main import app
from database import get_db
from auth import create_access_token, hash_password

# ---------------------------------------------------------------------------
# Shared in-memory SQLite engine for all HTTP-layer tests
# ---------------------------------------------------------------------------

# Use an in-memory SQLite DB for tests, or at least clean up the file
import os

TEST_DB_PATH = "./test.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# Remove old test db if it exists
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        pass # Ignore if locked by another process

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


# ---------------------------------------------------------------------------
# Auth helper fixtures — used by test_auth.py and any test that needs tokens
# ---------------------------------------------------------------------------

async def _create_user_and_token(email: str, password: str, role: str) -> tuple[str, str]:
    """
    Create a User row in the test DB and return (user_id, jwt_token).
    Helper used by the fixture factories below.
    """
    async with _HttpSession() as session:
        user = User(email=email, password_hash=hash_password(password), role=role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        token = create_access_token(subject=user.id, role=user.role)
        return user.id, token


@pytest_asyncio.fixture
async def student_auth():
    """
    Returns (student_user_id, jwt_token) for a freshly created student.
    Use this in tests that need an authenticated student.
    """
    return await _create_user_and_token("student@test.example", "testpassword", "student")


@pytest_asyncio.fixture
async def instructor_auth():
    """
    Returns (instructor_user_id, jwt_token) for a freshly created instructor.
    """
    return await _create_user_and_token("instructor@test.example", "testpassword", "instructor")


@pytest_asyncio.fixture
async def http_client():
    """Yields an AsyncClient wired to the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
