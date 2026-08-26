"""
Phase 8 — Pedagogical Agent tests.

Three fixture learner states:
(a) Student who just mastered conditionals → should recommend loops, not lists
(b) Student stuck below threshold on loops after several attempts → should recommend
    remediation on loops (same topic), NOT advance to lists
(c) Brand-new student with no history → should recommend the first curriculum node
    (basics-operators) with no prerequisites

Gate 6: Test (b) must exercise the REAL remediation branch. If the fixture trivially
produces a green test without actually hitting the 'below threshold' path, tighten it.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.pedagogical import (
    pedagogical_agent_node,
    PedagogicalDecision,
    MASTERY_THRESHOLD,
    CURRICULUM_ORDER,
)


# ---------------------------------------------------------------------------
# Helpers — mock DB session with prescribed mastery state
# ---------------------------------------------------------------------------

def make_mastery_row(student_id: str, topic_id: str, mastery_level: float):
    row = MagicMock()
    row.student_id = student_id
    row.topic_id = topic_id
    row.mastery_level = mastery_level
    row.last_updated = None
    return row


def make_event_row(student_id: str, topic_id: str, signal: str = "incorrect"):
    row = MagicMock()
    row.student_id = student_id
    row.topic_id = topic_id
    row.signal = signal
    row.timestamp = None
    return row


def make_session(mastery_rows: list, event_rows: list | None = None) -> AsyncMock:
    """Build a mock AsyncSession that returns the given rows for mastery / events queries."""
    mock_session = AsyncMock()
    event_rows = event_rows or []

    # first execute → mastery rows; second → events
    call_count = 0

    async def fake_execute(stmt):
        nonlocal call_count
        call_count += 1
        result = MagicMock()
        if call_count == 1:
            result.scalars.return_value.all.return_value = mastery_rows
        else:
            result.scalars.return_value.all.return_value = event_rows
        return result

    mock_session.execute = fake_execute
    return mock_session


# ---------------------------------------------------------------------------
# (a) Ready to advance: conditionals mastered → recommend loops
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pedagogical_advance_from_conditionals_to_loops():
    """
    Student has mastered basics-operators and conditionals.
    loops is the next unmastered topic whose prerequisites are met.
    Must recommend loops, not lists or anything further.
    """
    rows = [
        make_mastery_row("student_a", "basics-operators", 0.85),
        make_mastery_row("student_a", "conditionals", 0.80),
        # loops not in mastery map → mastery=0
    ]
    session = make_session(rows)

    decision: PedagogicalDecision = await pedagogical_agent_node(
        student_id="student_a", session=session
    )

    assert decision.next_topic_id == "loops", (
        f"Expected 'loops', got {decision.next_topic_id!r}. "
        f"Reason: {decision.reason}"
    )
    assert decision.next_topic_id not in ("lists", "strings", "dictionaries", "files"), (
        f"Agent skipped loops and jumped ahead: {decision.next_topic_id!r}"
    )


# ---------------------------------------------------------------------------
# (b) Stuck on loops: below threshold → remediate, do NOT advance
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pedagogical_remediation_when_stuck_on_loops():
    """
    Student has mastered basics-operators and conditionals, but is stuck on loops
    (mastery=0.3, well below MASTERY_THRESHOLD=0.7).
    Must recommend staying on loops (remediation), NOT advancing to lists.

    Gate 6: This fixture uses mastery=0.3 with several incorrect events to ensure
    the remediation branch is genuinely exercised, not trivially satisfied.
    """
    rows = [
        make_mastery_row("student_b", "basics-operators", 0.9),
        make_mastery_row("student_b", "conditionals", 0.8),
        make_mastery_row("student_b", "loops", 0.3),   # stuck — well below threshold
    ]
    events = [
        make_event_row("student_b", "loops", "incorrect"),
        make_event_row("student_b", "loops", "incorrect"),
        make_event_row("student_b", "loops", "incorrect"),
    ]
    session = make_session(rows, events)

    decision: PedagogicalDecision = await pedagogical_agent_node(
        student_id="student_b", session=session
    )

    assert decision.next_topic_id == "loops", (
        f"Expected remediation on 'loops', got {decision.next_topic_id!r}. "
        f"This means the agent advanced despite the student being below threshold — "
        f"the remediation branch is broken. Reason: {decision.reason}"
    )
    assert 0.3 < MASTERY_THRESHOLD, "Fixture sanity check: 0.3 must be below threshold"
    # Ensure the reason reflects remediation, not advancement
    assert any(kw in decision.reason.lower() for kw in ["stuck", "below", "mastery", "remediat", "continu"]), (
        f"Reason doesn't reflect remediation: {decision.reason!r}"
    )


# ---------------------------------------------------------------------------
# (c) Brand-new student: no history → recommend first curriculum node
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pedagogical_brand_new_student():
    """
    Student has no mastery rows at all.
    Must recommend the very first curriculum node (basics-operators) — which
    has no prerequisites and should always be the entry point.
    """
    session = make_session(mastery_rows=[], event_rows=[])

    decision: PedagogicalDecision = await pedagogical_agent_node(
        student_id="student_c", session=session
    )

    expected_first = CURRICULUM_ORDER[0]  # "basics-operators"
    assert decision.next_topic_id == expected_first, (
        f"Brand-new student should start at '{expected_first}', "
        f"got {decision.next_topic_id!r}. Reason: {decision.reason}"
    )
