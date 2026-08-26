"""
tests/test_auth.py — Phase 14 authorization test suite.

Gate 14: a system with login but no enforcement isn't meaningfully more
secure than the stub. These tests verify enforcement, not just authentication.

The tests that matter most:
  - test_student_a_cannot_read_student_b_mastery  ← the cross-user gate
  - test_student_gets_403_on_instructor_endpoints ← role enforcement
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

from main import app
from models import User
from auth import hash_password, create_access_token

# Import helpers from conftest — pytest makes conftest symbols available
# but we need explicit imports for the helper functions used directly in tests.
from tests.conftest import _HttpSession as TestSession, _create_user_and_token


# ---------------------------------------------------------------------------
# 14.1 — Auth primitives: register and login
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_creates_account_and_returns_token(http_client: AsyncClient):
    """POST /auth/register with valid data returns a token and the correct role."""
    resp = await http_client.post("/auth/register", json={
        "email": "alice@example.com",
        "password": "securepass123",
        "role": "student",
    })
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "student"
    assert data["token_type"] == "bearer"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_login_returns_token_on_correct_credentials(http_client: AsyncClient):
    """POST /auth/login succeeds with correct credentials after registration."""
    # Register first
    await http_client.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "pass1234",
        "role": "student",
    })
    # Now login
    resp = await http_client.post("/auth/login", json={
        "email": "bob@example.com",
        "password": "pass1234",
    })
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_returns_401_on_wrong_password(http_client: AsyncClient):
    """Wrong password gives 401, not 404 — avoids email enumeration."""
    await http_client.post("/auth/register", json={
        "email": "carol@example.com",
        "password": "rightpassword",
        "role": "student",
    })
    resp = await http_client.post("/auth/login", json={
        "email": "carol@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_returns_401_for_unknown_email(http_client: AsyncClient):
    """Unknown email gives 401, not 404 — avoids email enumeration."""
    resp = await http_client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_duplicate_registration_rejected(http_client: AsyncClient):
    """Registering the same email twice returns 409 Conflict."""
    payload = {"email": "dup@example.com", "password": "abc", "role": "student"}
    await http_client.post("/auth/register", json=payload)
    resp = await http_client.post("/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_invalid_role_rejected(http_client: AsyncClient):
    """Registering with role='admin' (not in allowed set) returns 400."""
    resp = await http_client.post("/auth/register", json={
        "email": "hacker@example.com",
        "password": "pass",
        "role": "admin",
    })
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 14.2 — Authentication enforcement: unauthenticated requests rejected
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_submit_answer_requires_auth(http_client: AsyncClient):
    """POST /answer without a token returns 401."""
    resp = await http_client.post("/answer", json={
        "activity_id": "some-activity",
        "submitted_answer": "A",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_tutor_interact_requires_auth(http_client: AsyncClient):
    """POST /tutor/interact without a token returns 401."""
    resp = await http_client.post("/tutor/interact", json={
        "message": "give me a question",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_student_mastery_requires_auth(http_client: AsyncClient):
    """GET /students/{id}/mastery without a token returns 401."""
    resp = await http_client.get("/students/some-id/mastery")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Gate 14 — Authorization: the tests that actually matter
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_student_a_cannot_read_student_b_mastery(http_client: AsyncClient):
    """
    GATE 14: Log in as student A, attempt to read student B's mastery data.
    Must be 403, not 200.

    This is the cross-user authorization gate. A system that passes auth but
    not this test isn't meaningfully more secure than the original stub.
    """
    # Create two students
    student_a_id, token_a = await _create_user_and_token("a@test.example", "pass", "student")
    student_b_id, _token_b = await _create_user_and_token("b@test.example", "pass", "student")

    # Student A tries to read Student B's mastery
    resp = await http_client.get(
        f"/students/{student_b_id}/mastery",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert resp.status_code == 403, (
        f"Expected 403 when student A reads student B's mastery, got {resp.status_code}: {resp.text}"
    )


@pytest.mark.asyncio
async def test_student_can_read_own_mastery(http_client: AsyncClient):
    """Positive case: student can read their own mastery."""
    student_id, token = await _create_user_and_token("self@test.example", "pass", "student")

    resp = await http_client.get(
        f"/students/{student_id}/mastery",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["student_id"] == student_id


@pytest.mark.asyncio
async def test_student_gets_403_on_review_pending(http_client: AsyncClient):
    """Student token is rejected on instructor-only GET /review/pending."""
    _, token = await _create_user_and_token("stu2@test.example", "pass", "student")

    resp = await http_client.get(
        "/review/pending",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403, (
        f"Expected 403 for student on /review/pending, got {resp.status_code}"
    )


@pytest.mark.asyncio
async def test_student_gets_403_on_review_approve(http_client: AsyncClient):
    """Student token is rejected on instructor-only POST /review/{id}/approve."""
    _, token = await _create_user_and_token("stu3@test.example", "pass", "student")

    resp = await http_client.post(
        "/review/9999/approve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_student_gets_403_on_review_reject(http_client: AsyncClient):
    """Student token is rejected on instructor-only POST /review/{id}/reject."""
    _, token = await _create_user_and_token("stu4@test.example", "pass", "student")

    resp = await http_client.post(
        "/review/9999/reject",
        headers={"Authorization": f"Bearer {token}"},
        json={"reason": "attempting escalation"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_student_gets_403_on_curriculum_topics(http_client: AsyncClient):
    """Student token is rejected on instructor-only GET /curriculum/topics."""
    _, token = await _create_user_and_token("stu5@test.example", "pass", "student")

    resp = await http_client.get(
        "/curriculum/topics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_instructor_can_read_any_student_mastery(http_client: AsyncClient):
    """Instructor token passes the cross-student authorization check."""
    student_id, _ = await _create_user_and_token("mystudent@test.example", "pass", "student")
    _, instr_token = await _create_user_and_token("prof@test.example", "pass", "instructor")

    resp = await http_client.get(
        f"/students/{student_id}/mastery",
        headers={"Authorization": f"Bearer {instr_token}"},
    )
    assert resp.status_code == 200, (
        f"Expected instructor to read student mastery, got {resp.status_code}: {resp.text}"
    )


@pytest.mark.asyncio
async def test_instructor_can_access_review_queue(http_client: AsyncClient):
    """Instructor token is accepted on /review/pending."""
    _, instr_token = await _create_user_and_token("prof2@test.example", "pass", "instructor")

    resp = await http_client.get(
        "/review/pending",
        headers={"Authorization": f"Bearer {instr_token}"},
    )
    assert resp.status_code == 200, resp.text


@pytest.mark.asyncio
async def test_expired_token_rejected(http_client: AsyncClient):
    """An expired JWT (expires_minutes=0) is rejected with 401."""
    async with TestSession() as session:
        user = User(email="expired@test.example", password_hash=hash_password("p"), role="student")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        # Create a token that expires immediately (0 minutes = already expired by the time it's checked)
        token = create_access_token(subject=user.id, role=user.role, expires_minutes=-1)

    resp = await http_client.get(
        f"/students/{user.id}/mastery",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401, (
        f"Expected 401 for expired token, got {resp.status_code}"
    )
