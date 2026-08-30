"""
Pedagogical Agent — Phase 8 / Phase 19 update

A single LangGraph node function (testable in isolation).

Given a student_id and a DB session, it:
  1. Reads current mastery for all topics from the DB (read-only)
  2. Walks the prerequisite curriculum graph
  3. Returns a decision: {next_topic_id, next_activity_type, reason}

Rules (from architecture doc §4 and §8):
  - Never recommend a topic whose prerequisites are not at mastery_threshold
  - Prefer activity types not seen recently to avoid repetition fatigue
  - Does NOT call LearnerModelService.record_update — read only

The curriculum DAG matches §4 of the architecture doc:
  basics-operators → conditionals → loops → lists → strings → dictionaries → files
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Mastery, AdaptationEvent


# ---------------------------------------------------------------------------
# Curriculum graph (prerequisite DAG)
# ---------------------------------------------------------------------------

# topic_id -> [prerequisite topic_ids that must be mastered first]
CURRICULUM_GRAPH: dict[str, list[str]] = {
    "basics-operators": [],
    "conditionals": ["basics-operators"],
    "loops": ["conditionals"],
    "lists": ["loops"],
    "strings": ["lists"],
    "dictionaries": ["strings"],
    "files": ["dictionaries"],
}

# Topological order (first = entry point for new students)
CURRICULUM_ORDER = list(CURRICULUM_GRAPH.keys())

# Mastery level at which a topic is considered "mastered" for prerequisite purposes
MASTERY_THRESHOLD = 0.7

# Activity types the system can recommend
ACTIVITY_TYPES = ["predict_output", "fill_blank", "reorder_lines"]


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

@dataclass
class PedagogicalDecision:
    next_topic_id: str
    next_activity_type: str
    reason: str
    # 0.0–1.0. The agent sets this to < 0.5 when it is uncertain about its
    # recommendation (e.g. edge-case curriculum states). The risk policy uses
    # this to escalate otherwise-medium recommendations to 'high'.
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {
            "next_topic_id": self.next_topic_id,
            "next_activity_type": self.next_activity_type,
            "reason": self.reason,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prerequisites_met(topic_id: str, mastery_map: dict[str, float]) -> bool:
    """Return True if all prerequisites for topic_id are at or above MASTERY_THRESHOLD."""
    for prereq in CURRICULUM_GRAPH.get(topic_id, []):
        if mastery_map.get(prereq, 0.0) < MASTERY_THRESHOLD:
            return False
    return True


def _recent_activity_types(recent_events: list[Any]) -> list[str]:
    """Extract the activity types from recent signals for repetition-avoidance."""
    types = []
    for e in recent_events:
        if getattr(e, "activity_type", None):
            types.append(e.activity_type)
    return types


def _pick_activity_type(recent_types: list[str]) -> str:
    """
    Pick the least-recently-used activity type to avoid repetition fatigue.
    Falls back to 'predict_output' if all have been used equally.
    """
    for at in ACTIVITY_TYPES:
        if at not in recent_types:
            return at
    return ACTIVITY_TYPES[0]


# ---------------------------------------------------------------------------
# Node function
# ---------------------------------------------------------------------------

async def pedagogical_agent_node(
    *,
    student_id: str,
    session: AsyncSession,
) -> PedagogicalDecision:
    """
    The Pedagogical Agent node. Read-only: never calls LearnerModelService.record_update.

    Returns a PedagogicalDecision with next_topic_id, next_activity_type, reason.
    """
    # 1. Read all mastery rows for this student
    stmt = select(Mastery).where(Mastery.student_id == student_id)
    result = await session.execute(stmt)
    mastery_rows = result.scalars().all()
    mastery_map = {row.topic_id: row.mastery_level for row in mastery_rows}

    # 2. Read recent adaptation events for repetition-avoidance and stuck-detection
    stmt2 = (
        select(AdaptationEvent)
        .where(AdaptationEvent.student_id == student_id)
        .order_by(AdaptationEvent.timestamp.desc())
        .limit(10)
    )
    result2 = await session.execute(stmt2)
    recent_events = result2.scalars().all()
    recent_topic_id = recent_events[0].topic_id if recent_events else None
    recent_activity_types = _recent_activity_types(recent_events)

    # Detect if student is stuck: 3 consecutive wrong answers on the most recent topic
    stuck_on_topic = None
    if len(recent_events) >= 3:
        first_topic = recent_events[0].topic_id
        if all(e.topic_id == first_topic and e.signal == "incorrect" for e in recent_events[:3]):
            stuck_on_topic = first_topic

    # 3. Walk curriculum in prerequisite order to find the right topic
    for topic_id in CURRICULUM_ORDER:
        mastery = mastery_map.get(topic_id, 0.0)

        # Skip if prerequisites aren't met
        if not _prerequisites_met(topic_id, mastery_map):
            continue

        # If student is below threshold on this topic → remediate here
        if mastery < MASTERY_THRESHOLD:
            activity_type = _pick_activity_type(recent_activity_types)

            if stuck_on_topic == topic_id:
                reason = (
                    f"Student is stuck on '{topic_id}' "
                    f"(3 consecutive wrong answers). Recommending remediation."
                )
                return PedagogicalDecision(
                    next_topic_id=topic_id,
                    next_activity_type=activity_type,
                    reason=reason,
                    confidence=0.4, # Low confidence triggers high risk -> pending queue
                )
            elif mastery == 0.0 and topic_id not in mastery_map:
                # Brand new topic with no history
                reason = f"Student has not started '{topic_id}' yet. Starting with basics."
            else:
                reason = (
                    f"Student has not mastered '{topic_id}' "
                    f"(mastery={mastery:.2f}). Continuing practice."
                )

            return PedagogicalDecision(
                next_topic_id=topic_id,
                next_activity_type=activity_type,
                reason=reason,
            )

    # 4. All topics mastered → loop back to the last topic for advanced practice.
    # Confidence is set lower here because this is an unusual state; the risk
    # policy will treat it as medium-risk, pending instructor config.
    last_topic = CURRICULUM_ORDER[-1]
    return PedagogicalDecision(
        next_topic_id=last_topic,
        next_activity_type="predict_output",
        reason="All curriculum topics mastered. Revisiting final topic for advanced practice.",
        confidence=0.6,
    )
