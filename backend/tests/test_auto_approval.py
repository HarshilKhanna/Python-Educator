from contextlib import asynccontextmanager
"""
test_auto_approval.py — Phase 20 integration tests

Verifies the risk-tiered write path end-to-end using the HTTP test client.

Tests:
  1. Low-risk recommendation auto-applies: produces adaptation_events row
     with source="pedagogical_agent_auto", never appears in /review/pending
  2. High-risk recommendation: appears in /review/pending, mastery unchanged
  3. Medium-risk with high confidence auto-applies
  4. Kill-switch active: even low-risk goes to review queue
  5. Kill-switch toggle: disable → re-enable → confirm low-risk auto-applies again

These tests mock out the orchestrator (to control what the pedagogical agent
recommends) while exercising the real DB write path.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from database import get_db
from models import AdaptationEvent, PendingAdaptation, Mastery, SystemSettings
from auth import create_access_token, hash_password
from models import User


# ---------------------------------------------------------------------------
# Helpers — build canonical orchestrator payloads
# ---------------------------------------------------------------------------

def _ped_state(
    student_id: str,
    next_topic: str,
    next_activity: str = "predict_output",
    reason: str = "test recommendation",
    confidence: float = 1.0,
) -> dict:
    return {
        "intent": "activity_request",
        "student_id": student_id,
        "message": "next",
        "topic_id": None,
        "pedagogical_result": {
            "next_topic_id": next_topic,
            "next_activity_type": next_activity,
            "reason": reason,
            "confidence": confidence,
        },
        "technical_result": None,
        "pending_adaptation_id": None,
    }


# ---------------------------------------------------------------------------
# Fixtures — use conftest's shared DB + helpers
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def instructor_token(http_client: AsyncClient) -> str:
    """Create an instructor user and return a JWT."""
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        user = User(email="instructor_auto@test.example", password_hash=hash_password("pw"), role="instructor")
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return create_access_token(subject=user.id, role="instructor")


# ---------------------------------------------------------------------------
# Test 1: LOW-RISK auto-applies, never in review queue
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_low_risk_auto_applies_not_in_review_queue(
    http_client: AsyncClient,
    student_auth: tuple[str, str],
):
    """
    Gate 20 — low-risk scenario:
    Same topic returned: student is on 'loops', agent recommends 'loops'.
    classify_risk → 'low' → auto-apply via LearnerModelService.record_update.
    Confirm:
      - adaptation_events row with source='pedagogical_agent_auto'
      - NOT in /review/pending
    """
    student_id, student_token = student_auth

    # Pre-seed mastery so the student is "currently on" loops
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        mastery = Mastery(student_id=student_id, topic_id="loops", mastery_level=0.4, confidence=0.0)
        session.add(mastery)
        await session.commit()

    fake_state = _ped_state(student_id, "loops", confidence=1.0)

    with patch("routers.tutor.orchestrator_graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=fake_state)
        resp = await http_client.post(
            "/tutor/interact",
            json={"message": "next"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["auto_applied"] is True
    assert data["pending_review"] is False
    assert data["risk_tier"] == "low"
    assert data["pending_adaptation_id"] is None

    # Verify DB: adaptation_events row with source="pedagogical_agent_auto"
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        stmt = select(AdaptationEvent).where(
            AdaptationEvent.student_id == student_id,
            AdaptationEvent.source == "pedagogical_agent_auto",
        )
        result = await session.execute(stmt)
        events = result.scalars().all()
        assert len(events) == 1, f"Expected 1 auto-applied event, got {len(events)}"
        assert events[0].risk_tier == "low"

    # Verify NOT in review queue
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        stmt = select(PendingAdaptation).where(
            PendingAdaptation.student_id == student_id,
            PendingAdaptation.status == "pending",
        )
        result = await session.execute(stmt)
        pending = result.scalars().all()
        assert len(pending) == 0, f"Low-risk should NOT appear in review queue, got {len(pending)}"


# ---------------------------------------------------------------------------
# Test 2: HIGH-RISK → review queue, mastery unchanged
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_high_risk_goes_to_review_queue_no_mastery_change(
    http_client: AsyncClient,
    student_auth: tuple[str, str],
):
    """
    Gate 20 — high-risk scenario:
    Student on 'conditionals', agent recommends jumping to 'lists' (2 steps).
    classify_risk → 'high' → pending_adaptations.
    Mastery must NOT change.
    """
    student_id, student_token = student_auth

    # Pre-seed mastery: student has conditionals at 0.4 (below threshold)
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        mastery = Mastery(student_id=student_id, topic_id="conditionals", mastery_level=0.4, confidence=0.0)
        session.add(mastery)
        await session.commit()

    # Jump 2 steps: conditionals → lists (skips loops) — high risk
    fake_state = _ped_state(student_id, "lists", confidence=1.0)

    with patch("routers.tutor.orchestrator_graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=fake_state)
        resp = await http_client.post(
            "/tutor/interact",
            json={"message": "next"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["pending_review"] is True
    assert data["auto_applied"] is False
    assert data["risk_tier"] == "high"
    assert data["pending_adaptation_id"] is not None

    # Verify mastery NOT changed
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        stmt = select(Mastery).where(
            Mastery.student_id == student_id, Mastery.topic_id == "conditionals"
        )
        result = await session.execute(stmt)
        mastery_row = result.scalar_one()
        assert mastery_row.mastery_level == 0.4, "Mastery must not change for high-risk"

    # Verify in review queue
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        stmt = select(PendingAdaptation).where(
            PendingAdaptation.student_id == student_id,
            PendingAdaptation.status == "pending",
        )
        result = await session.execute(stmt)
        pending = result.scalars().all()
        assert len(pending) == 1, f"High-risk must appear in review queue, got {len(pending)}"


# ---------------------------------------------------------------------------
# Test 3: MEDIUM-RISK with high confidence auto-applies
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_medium_risk_high_confidence_auto_applies(
    http_client: AsyncClient,
    student_auth: tuple[str, str],
):
    """
    Medium-risk (one-step advancement) with high confidence → auto-applied.
    """
    student_id, student_token = student_auth

    # Student has mastered basics-operators, currently on conditionals
    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        for tid, ml in [("basics-operators", 0.9), ("conditionals", 0.85)]:
            mastery = Mastery(student_id=student_id, topic_id=tid, mastery_level=ml, confidence=0.0)
            session.add(mastery)
        await session.commit()

    # One-step advance: conditionals → loops (medium risk)
    fake_state = _ped_state(student_id, "loops", confidence=1.0)

    with patch("routers.tutor.orchestrator_graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=fake_state)
        resp = await http_client.post(
            "/tutor/interact",
            json={"message": "next"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["auto_applied"] is True, "Medium+high-confidence must auto-apply"
    assert data["risk_tier"] == "medium"
    assert data["pending_review"] is False


# ---------------------------------------------------------------------------
# Test 4: MEDIUM-RISK with LOW confidence → review queue (critical boundary)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_medium_risk_low_confidence_goes_to_review(
    http_client: AsyncClient,
    student_auth: tuple[str, str],
):
    """
    CRITICAL BOUNDARY: medium base tier + low confidence (< threshold) must go
    to the review queue. This tests the exact boundary the prompt calls out as
    the one that matters most.
    """
    student_id, student_token = student_auth

    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        for tid, ml in [("basics-operators", 0.9), ("conditionals", 0.85)]:
            mastery = Mastery(student_id=student_id, topic_id=tid, mastery_level=ml, confidence=0.0)
            session.add(mastery)
        await session.commit()

    # Same one-step advance but with low confidence — classify_risk escalates to 'high'
    fake_state = _ped_state(student_id, "loops", confidence=0.3)

    with patch("routers.tutor.orchestrator_graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=fake_state)
        resp = await http_client.post(
            "/tutor/interact",
            json={"message": "next"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["pending_review"] is True, (
        "Medium+low-confidence must go to review queue — confidence override must beat base tier"
    )
    assert data["auto_applied"] is False
    assert data["risk_tier"] == "high", (
        "classify_risk must escalate medium→high when confidence < threshold"
    )


# ---------------------------------------------------------------------------
# Test 5: KILL-SWITCH active → low-risk goes to review queue
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_kill_switch_forces_all_to_review_queue(
    http_client: AsyncClient,
    student_auth: tuple[str, str],
    instructor_auth: tuple[str, str],
):
    """
    Gate 21 — kill-switch test.

    1. Start with kill-switch off (default): low-risk auto-applies.
    2. Enable kill-switch via POST /monitoring/kill-switch.
    3. Re-trigger same low-risk case → must appear in review queue.
    """
    student_id, student_token = student_auth
    _, instructor_token = instructor_auth

    async with asynccontextmanager(app.dependency_overrides[get_db])() as session:
        mastery = Mastery(student_id=student_id, topic_id="loops", mastery_level=0.4, confidence=0.0)
        session.add(mastery)
        await session.commit()

    fake_state = _ped_state(student_id, "loops", confidence=1.0)  # would be low-risk

    # Confirm default: auto-applies without kill-switch
    with patch("routers.tutor.orchestrator_graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=fake_state)
        resp = await http_client.post(
            "/tutor/interact",
            json={"message": "next"},
            headers={"Authorization": f"Bearer {student_token}"},
        )
    assert resp.json()["auto_applied"] is True, "Baseline: must auto-apply before kill-switch"

    # Enable kill-switch
    ks_resp = await http_client.post(
        "/monitoring/kill-switch",
        json={"active": True},
        headers={"Authorization": f"Bearer {instructor_token}"},
    )
    assert ks_resp.status_code == 200
    assert ks_resp.json()["active"] is True

    # Re-trigger same low-risk case — must now go to review queue
    with patch("routers.tutor.orchestrator_graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=fake_state)
        resp2 = await http_client.post(
            "/tutor/interact",
            json={"message": "next"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

    assert resp2.status_code == 200, resp2.text
    data2 = resp2.json()
    assert data2["pending_review"] is True, (
        "Kill-switch must force low-risk to review queue — "
        "a kill-switch that fails this test is a false sense of security"
    )
    assert data2["auto_applied"] is False

    # Cleanup: disable kill-switch so it doesn't affect other tests
    await http_client.post(
        "/monitoring/kill-switch",
        json={"active": False},
        headers={"Authorization": f"Bearer {instructor_token}"},
    )
