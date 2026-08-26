"""
test_risk_policy.py — Phase 19 (Prompt 19.2)

Unit tests for classify_risk(). No DB, no async — pure function.

Coverage:
  - low tier: same-topic activity rotation
  - medium tier: standard one-step topic advancement
  - medium tier: backward remediation to earlier topic
  - high tier: prerequisite-skipping (defensive guard)
  - high tier: topic jump > 1 step
  - CRITICAL BOUNDARY: medium base tier + low confidence → escalates to high
  - CRITICAL BOUNDARY: low base tier + low confidence → also escalates to high
    (confidence override beats every base tier)

The medium/high boundary is the line that matters most: low is obviously safe,
high is obviously not, but a wrong medium→auto-apply for a real student is a
real consequence. Every branch of the medium/high split is tested explicitly.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from risk_policy import classify_risk, CURRICULUM_ORDER, DEFAULT_CONFIDENCE_THRESHOLD


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

HIGH_CONF = 1.0   # well above threshold
LOW_CONF = 0.3    # well below threshold

# A fully-mastered mastery map for clean prerequisite tests
FULLY_MASTERED: dict[str, float] = {t: 0.9 for t in CURRICULUM_ORDER}

# Partial mastery — student has basics + conditionals mastered, working on loops
PARTIAL_MASTERY: dict[str, float] = {
    "basics-operators": 0.9,
    "conditionals": 0.8,
    "loops": 0.3,   # below threshold
}


# ---------------------------------------------------------------------------
# LOW tier
# ---------------------------------------------------------------------------

def test_low_risk_same_topic_activity_rotation():
    """
    Same topic, different activity_type only.
    This is the trivially safe case — no change to topic or difficulty.
    """
    risk = classify_risk(
        current_topic="loops",
        next_topic_id="loops",
        next_activity_type="fill_blank",  # different from whatever was last
        confidence=HIGH_CONF,
        mastery_map=PARTIAL_MASTERY,
    )
    assert risk == "low", f"Same-topic rotation must be 'low', got {risk!r}"


def test_low_risk_brand_new_student():
    """
    Brand-new student (no current topic) starting the first curriculum node.
    No prerequisite risk — entry point is always safe.
    """
    risk = classify_risk(
        current_topic=None,
        next_topic_id="basics-operators",
        next_activity_type="predict_output",
        confidence=HIGH_CONF,
        mastery_map={},
    )
    assert risk == "low", f"Brand-new student start must be 'low', got {risk!r}"


# ---------------------------------------------------------------------------
# MEDIUM tier
# ---------------------------------------------------------------------------

def test_medium_risk_standard_topic_advancement():
    """
    Student mastered conditionals, agent recommends loops (exactly 1 step forward).
    Prerequisites are met. Standard advancement → medium.
    """
    mastery = {"basics-operators": 0.9, "conditionals": 0.85}
    risk = classify_risk(
        current_topic="conditionals",
        next_topic_id="loops",
        next_activity_type="predict_output",
        confidence=HIGH_CONF,
        mastery_map=mastery,
    )
    assert risk == "medium", (
        f"One-step prerequisite-respecting advancement must be 'medium', got {risk!r}"
    )


def test_medium_risk_remediation_backward():
    """
    Student regresses: currently on 'lists', agent recommends going back to
    'loops' (one step backward) for remediation. Backward moves are medium-risk —
    a deliberate pedagogical choice, not a skip.
    """
    mastery = {"basics-operators": 0.9, "conditionals": 0.8, "loops": 0.4, "lists": 0.2}
    risk = classify_risk(
        current_topic="lists",
        next_topic_id="loops",
        next_activity_type="fill_blank",
        confidence=HIGH_CONF,
        mastery_map=mastery,
    )
    assert risk == "medium", (
        f"Backward remediation must be 'medium', got {risk!r}"
    )


# ---------------------------------------------------------------------------
# HIGH tier
# ---------------------------------------------------------------------------

def test_high_risk_prerequisite_skip_defensive():
    """
    DEFENSIVE GUARD: next_topic_id is 'loops' but 'conditionals' isn't mastered.
    The pedagogical agent's gating should prevent this, but classify_risk catches
    it defensively so a bug in the agent can't silently auto-apply an illegal move.
    """
    mastery = {"basics-operators": 0.9, "conditionals": 0.2}  # conditionals not mastered
    risk = classify_risk(
        current_topic="basics-operators",
        next_topic_id="loops",  # skips unmastered conditionals
        next_activity_type="predict_output",
        confidence=HIGH_CONF,  # even with high confidence, prerequisite skip → high
        mastery_map=mastery,
    )
    assert risk == "high", (
        f"Prerequisite skip must always be 'high' regardless of confidence, got {risk!r}"
    )


def test_high_risk_topic_jump_more_than_one_step():
    """
    Agent recommends jumping from 'basics-operators' directly to 'loops'
    (skipping 'conditionals'). Even if prerequisites happened to be met
    (mastery_map includes conditionals), jumping > 1 step is high risk.
    """
    mastery = {"basics-operators": 0.9, "conditionals": 0.85}  # prereqs met
    risk = classify_risk(
        current_topic="basics-operators",
        next_topic_id="loops",    # 2 steps ahead
        next_activity_type="predict_output",
        confidence=HIGH_CONF,
        mastery_map=mastery,
    )
    # NOTE: 'loops' prereq is 'conditionals' which IS mastered here.
    # But the jump of 2 curriculum positions is still high risk.
    # (classify_risk checks prereqs first — conditionals is mastered so that
    # check passes, then the distance check catches the 2-step jump.)
    assert risk == "high", (
        f"A 2-step topic jump must be 'high' even with prereqs met, got {risk!r}"
    )


# ---------------------------------------------------------------------------
# CRITICAL BOUNDARY: confidence override
# The key assertion: low confidence escalates any base tier to 'high'.
# This is the line that has real consequences if wrong.
# ---------------------------------------------------------------------------

def test_high_risk_low_confidence_escalates_medium_to_high():
    """
    CRITICAL BOUNDARY TEST.

    Base tier would be 'medium' (one-step advancement, prerequisites met),
    but the agent has flagged low confidence (< threshold).
    Confidence override must win: result must be 'high'.

    This is the test that guards the medium→auto-apply decision against
    cases where the agent itself is uncertain about its recommendation.
    """
    mastery = {"basics-operators": 0.9, "conditionals": 0.85}
    risk = classify_risk(
        current_topic="conditionals",
        next_topic_id="loops",           # would be medium at high confidence
        next_activity_type="predict_output",
        confidence=LOW_CONF,             # agent explicitly signals uncertainty
        mastery_map=mastery,
        confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD,
    )
    assert risk == "high", (
        f"Medium base tier + low confidence must escalate to 'high', got {risk!r}. "
        f"Confidence {LOW_CONF} < threshold {DEFAULT_CONFIDENCE_THRESHOLD}."
    )


def test_high_risk_low_confidence_escalates_low_to_high():
    """
    Even a same-topic rotation (base tier = 'low') escalates to 'high' when
    the agent signals low confidence. Confidence override is unconditional.
    """
    risk = classify_risk(
        current_topic="loops",
        next_topic_id="loops",           # would be low at high confidence
        next_activity_type="fill_blank",
        confidence=LOW_CONF,
        mastery_map=PARTIAL_MASTERY,
        confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD,
    )
    assert risk == "high", (
        f"Low base tier + low confidence must escalate to 'high', got {risk!r}."
    )


def test_medium_remains_medium_at_exactly_confidence_threshold():
    """
    Confidence exactly at the threshold (not below it) should NOT escalate.
    Medium base tier with confidence == threshold → still 'medium'.
    This verifies the boundary is exclusive (< not <=).
    """
    mastery = {"basics-operators": 0.9, "conditionals": 0.85}
    risk = classify_risk(
        current_topic="conditionals",
        next_topic_id="loops",
        next_activity_type="predict_output",
        confidence=DEFAULT_CONFIDENCE_THRESHOLD,  # exactly at threshold, not below
        mastery_map=mastery,
        confidence_threshold=DEFAULT_CONFIDENCE_THRESHOLD,
    )
    assert risk == "medium", (
        f"Confidence == threshold (not below) must not escalate. "
        f"Expected 'medium', got {risk!r}."
    )


def test_high_risk_unknown_topic_is_safe_default():
    """
    next_topic_id is not in the curriculum at all.
    Can't reason about safety → always 'high'.
    """
    risk = classify_risk(
        current_topic="loops",
        next_topic_id="advanced-metaclasses",  # not in curriculum
        next_activity_type="predict_output",
        confidence=HIGH_CONF,
        mastery_map=FULLY_MASTERED,
    )
    assert risk == "high", (
        f"Unknown curriculum topic must default to 'high', got {risk!r}"
    )
