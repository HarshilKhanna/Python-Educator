"""
risk_policy.py — Phase 19

Standalone, inspectable risk-classification policy for Pedagogical Agent
recommendations. No DB dependency, no side effects — pure function.

    classify_risk(...) -> 'low' | 'medium' | 'high'

Tier definitions:
  low    — same topic, activity_type rotation only (topic & difficulty unchanged)
  medium — standard prerequisite-respecting topic advancement (exactly one step
           forward in CURRICULUM_ORDER), OR standard remediation (staying on the
           same topic while still below mastery threshold). Requires agent
           confidence >= CONFIDENCE_THRESHOLD.
  high   — any of:
           · agent confidence < CONFIDENCE_THRESHOLD (escalates any base tier)
           · next_topic_id would skip a prerequisite (defensive guard)
           · jump > 1 position in CURRICULUM_ORDER (difficulty/topic skip)
           · anything else that doesn't fit low or medium cleanly

This module deliberately has NO imports from the rest of the application so that
it can be tested in complete isolation and changed without touching agent internals.
"""

from __future__ import annotations

from typing import Literal

# Mirror of CURRICULUM_ORDER from agents/pedagogical.py.
# Kept here as a constant rather than imported to preserve the "no agent import"
# isolation guarantee. If the curriculum changes, update both.
CURRICULUM_ORDER: list[str] = [
    "basics-operators",
    "conditionals",
    "loops",
    "lists",
    "strings",
    "dictionaries",
    "files",
]

# Prerequisite DAG — mirrors CURRICULUM_GRAPH in agents/pedagogical.py
CURRICULUM_GRAPH: dict[str, list[str]] = {
    "basics-operators": [],
    "conditionals": ["basics-operators"],
    "loops": ["conditionals"],
    "lists": ["loops"],
    "strings": ["lists"],
    "dictionaries": ["strings"],
    "files": ["dictionaries"],
}

# Agent confidence below this threshold always escalates to 'high' regardless of
# base tier. Configurable via CONFIDENCE_THRESHOLD env var (read in config.py and
# passed in by the caller so this module stays dependency-free).
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5

RiskTier = Literal["low", "medium", "high"]


def _prerequisites_satisfied(
    next_topic_id: str, mastery_map: dict[str, float], mastery_threshold: float = 0.7
) -> bool:
    """Return True if all prerequisites for next_topic_id are at or above threshold."""
    for prereq in CURRICULUM_GRAPH.get(next_topic_id, []):
        if mastery_map.get(prereq, 0.0) < mastery_threshold:
            return False
    return True


def _curriculum_distance(from_topic: str | None, to_topic: str) -> int | None:
    """
    Return the number of steps between from_topic and to_topic in CURRICULUM_ORDER.
    Returns None if either topic is not in the curriculum.
    Positive = forward, negative = backward.
    """
    if from_topic is None:
        return None
    try:
        from_idx = CURRICULUM_ORDER.index(from_topic)
        to_idx = CURRICULUM_ORDER.index(to_topic)
        return to_idx - from_idx
    except ValueError:
        return None


def classify_risk(
    current_topic: str | None,
    next_topic_id: str,
    next_activity_type: str,  # noqa: ARG001  # reserved for future difficulty tiers
    confidence: float,
    mastery_map: dict[str, float],
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    mastery_threshold: float = 0.7,
) -> RiskTier:
    """
    Classify the risk of a Pedagogical Agent recommendation.

    Parameters
    ----------
    current_topic       : the topic the student is currently on (None for brand-new)
    next_topic_id       : the agent's recommended next topic
    next_activity_type  : the recommended activity type (reserved; not yet used for
                          difficulty — kept for forward compatibility)
    confidence          : agent-reported confidence (0.0–1.0)
    mastery_map         : {topic_id: mastery_level} for the student
    confidence_threshold: confidence below this → always escalate to 'high'
    mastery_threshold   : mastery level at which a topic is considered mastered

    Returns
    -------
    'low' | 'medium' | 'high'
    """
    # ------------------------------------------------------------------
    # Rule 1 (highest priority): low confidence always escalates to 'high'
    # ------------------------------------------------------------------
    if confidence < confidence_threshold:
        return "high"

    # ------------------------------------------------------------------
    # Rule 2 (defensive): prerequisite skip → always 'high'
    # This should never happen given existing gating in the pedagogical agent,
    # but we classify it high defensively so a bug there doesn't silently
    # auto-apply an illegal advancement.
    # ------------------------------------------------------------------
    if next_topic_id in CURRICULUM_GRAPH:  # known curriculum topic
        if not _prerequisites_satisfied(next_topic_id, mastery_map, mastery_threshold):
            return "high"

    # ------------------------------------------------------------------
    # Rule 3: same topic → always 'low'
    # The activity_type rotation within a topic is the safest possible change.
    # ------------------------------------------------------------------
    if current_topic is not None and current_topic == next_topic_id:
        return "low"

    # Brand-new student (no current topic) picking up the first topic:
    # treat as 'low' — it's just starting, not advancing
    if current_topic is None:
        return "low"

    # ------------------------------------------------------------------
    # Rule 4: check curriculum distance
    # Exactly 1 step forward → 'medium' (standard advancement)
    # Backward (remediation to an earlier topic) → 'medium'
    # Jump > 1 step forward → 'high'
    # Unknown topic → 'high' (can't reason about it safely)
    # ------------------------------------------------------------------
    distance = _curriculum_distance(current_topic, next_topic_id)

    if distance is None:
        # One or both topics not in the known curriculum — can't classify safely
        return "high"

    if distance == 1:
        # Standard one-step advancement
        return "medium"

    if distance < 0:
        # Backward movement (remediation to an earlier topic) — unusual but safe
        # to flag as medium (it's a deliberate pedagogy choice, not a skip)
        return "medium"

    # distance == 0 is caught above (same topic).
    # distance > 1 → topic skip → high risk
    return "high"
