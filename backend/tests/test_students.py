"""
Tests for Phase 12: student mastery endpoint and reject-with-reason.

Covers:
- GET /students/{id}/mastery response shape + reason surfacing
- POST /review/{id}/reject with a reason stores it and doesn't touch mastery
"""

import pytest
import pytest_asyncio
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from models import Mastery, AdaptationEvent, PendingAdaptation

# Use conftest.py's shared HTTP session for DB assertions
from tests.conftest import _HttpSession as TestSession



# ---------------------------------------------------------------------------
# Test: mastery endpoint response shape
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_student_mastery_endpoint_returns_correct_shape(instructor_auth):
    """GET /students/{id}/mastery returns mastery list and recent_events."""
    _, token = instructor_auth
    headers = {"Authorization": f"Bearer {token}"}
    student = "test_student_mastery"

    async with TestSession() as session:
        session.add(Mastery(student_id=student, topic_id="loops", mastery_level=0.6, confidence=0.5))
        session.add(AdaptationEvent(
            student_id=student, topic_id="loops",
            source="activity_submission", signal="correct", delta=0.1,
        ))
        session.add(PendingAdaptation(
            student_id=student, next_topic_id="loops", next_activity_type="fill_blank",
            reason="Student is stuck on loops (mastery=0.30). Recommending remediation.",
            status="pending",
        ))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"/students/{student}/mastery", headers=headers)

    assert resp.status_code == 200
    data = resp.json()

    assert data["student_id"] == student
    assert len(data["mastery"]) == 1
    assert data["mastery"][0]["topic_id"] == "loops"
    assert data["mastery"][0]["mastery_level"] == pytest.approx(0.6, abs=0.001)

    assert len(data["recent_events"]) == 1
    event = data["recent_events"][0]
    assert event["signal"] == "correct"
    # reason should be populated from pending_adaptations
    assert "stuck" in event["reason"].lower() or "remediat" in event["reason"].lower(), (
        f"Expected human-readable reason, got: {event['reason']!r}"
    )


@pytest.mark.asyncio
async def test_student_mastery_endpoint_returns_empty_for_unknown_student(instructor_auth):
    _, token = instructor_auth
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/students/nonexistent_xyz/mastery", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["mastery"] == []
    assert data["recent_events"] == []


# ---------------------------------------------------------------------------
# Test: reject with reason — mastery unchanged
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reject_with_reason_does_not_touch_mastery(instructor_auth):
    """
    Rejecting a pending adaptation must:
    1. Mark it as rejected with the provided reason
    2. NOT create any AdaptationEvent or change Mastery rows
    """
    _, token = instructor_auth
    headers = {"Authorization": f"Bearer {token}"}
    student = "test_reject_student"

    async with TestSession() as session:
        # Start with known mastery
        session.add(Mastery(student_id=student, topic_id="loops", mastery_level=0.4, confidence=0.3))
        pending = PendingAdaptation(
            student_id=student, next_topic_id="loops", next_activity_type="predict_output",
            reason="Stuck on loops", status="pending",
        )
        session.add(pending)
        await session.commit()
        pending_id = pending.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/review/{pending_id}/reject",
            headers=headers,
            json={"reason": "Student actually needs more examples first"},
        )

    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"
    assert resp.json()["reason"] == "Student actually needs more examples first"

    # Verify mastery is unchanged
    async with TestSession() as session:
        mastery = (await session.execute(
            select(Mastery).where(Mastery.student_id == student, Mastery.topic_id == "loops")
        )).scalar_one()
        assert mastery.mastery_level == pytest.approx(0.4, abs=0.001), (
            "Mastery changed after rejection — the single write path was violated."
        )

        # Verify NO new AdaptationEvent was written
        events = (await session.execute(
            select(AdaptationEvent).where(AdaptationEvent.student_id == student)
        )).scalars().all()
        assert len(events) == 0, (
            f"Expected 0 adaptation events after rejection, got {len(events)}"
        )

        # Verify the note was stored
        pa = (await session.execute(
            select(PendingAdaptation).where(PendingAdaptation.id == pending_id)
        )).scalar_one()
        assert pa.status == "rejected"
        assert pa.review_note == "Student actually needs more examples first"
