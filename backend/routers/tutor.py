"""
POST /tutor/interact — Phase 9 endpoint

Accepts a student turn (student_id + message + optional topic_id).
Routes through the Orchestrator graph.

Phase 10 guardrail: if the Pedagogical Agent recommends a topic change or
remediation (anything other than the student's current topic), the decision
is written to pending_adaptations for human review rather than auto-applied.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import Mastery, PendingAdaptation
from agents.orchestrator import orchestrator_graph, set_session

router = APIRouter(prefix="/tutor", tags=["Tutor"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class InteractRequest(BaseModel):
    student_id: str
    message: str
    topic_id: str | None = None


class InteractResponse(BaseModel):
    intent: str
    # For pedagogical intent
    next_topic_id: str | None = None
    next_activity_type: str | None = None
    reason: str | None = None
    pending_review: bool = False
    pending_adaptation_id: int | None = None
    # For technical intent
    answer: str | None = None
    grounded: bool | None = None
    source_chunks: list[dict] | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAME_TOPIC_ACTIVITIES = {"predict_output", "fill_blank", "reorder_lines"}


async def _get_current_topic(student_id: str, session: AsyncSession) -> str | None:
    """Return the topic the student most recently worked on (highest mastery update time)."""
    stmt = select(Mastery).where(Mastery.student_id == student_id).order_by(
        Mastery.last_updated.desc()
    ).limit(1)
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    return row.topic_id if row else None


def _needs_review(
    current_topic: str | None,
    next_topic_id: str,
    next_activity_type: str,
) -> bool:
    """
    Returns True if the Pedagogical Agent's recommendation requires human review.

    Any topic change or remediation signal (i.e. switching to a different topic
    than the student is currently on) goes to the pending queue.
    'Continue with same topic at same difficulty' does NOT need review.
    """
    if current_topic is None:
        # Brand-new student — no review needed for the first topic
        return False
    return current_topic != next_topic_id


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/interact", response_model=InteractResponse)
async def tutor_interact(
    req: InteractRequest,
    db: AsyncSession = Depends(get_db),
) -> InteractResponse:
    """
    Route a student turn through the Orchestrator.

    - Activity requests → Pedagogical Agent → (maybe) pending_adaptations queue
    - Free-text questions → Technical Agent → grounded answer
    """
    # Inject DB session into the orchestrator
    set_session(db)

    try:
        final_state = await orchestrator_graph.ainvoke({
            "student_id": req.student_id,
            "message": req.message,
            "topic_id": req.topic_id,
            "intent": None,
            "pedagogical_result": None,
            "technical_result": None,
            "pending_adaptation_id": None,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestrator error: {e}")

    intent = final_state.get("intent", "question")

    # --- Pedagogical path ---
    if intent == "activity_request":
        ped = final_state.get("pedagogical_result", {})
        next_topic = ped.get("next_topic_id")
        next_activity = ped.get("next_activity_type")
        reason = ped.get("reason", "")

        current_topic = await _get_current_topic(req.student_id, db)
        needs_review = _needs_review(current_topic, next_topic, next_activity)

        if needs_review:
            # Write to the pending queue; don't auto-apply
            pending = PendingAdaptation(
                student_id=req.student_id,
                next_topic_id=next_topic,
                next_activity_type=next_activity,
                reason=reason,
                status="pending",
            )
            db.add(pending)
            await db.commit()
            await db.refresh(pending)

            return InteractResponse(
                intent=intent,
                next_topic_id=next_topic,
                next_activity_type=next_activity,
                reason=reason,
                pending_review=True,
                pending_adaptation_id=pending.id,
            )

        return InteractResponse(
            intent=intent,
            next_topic_id=next_topic,
            next_activity_type=next_activity,
            reason=reason,
            pending_review=False,
        )

    # --- Technical path ---
    tech = final_state.get("technical_result", {})
    return InteractResponse(
        intent=intent,
        answer=tech.get("answer"),
        grounded=tech.get("grounded"),
        source_chunks=tech.get("source_chunks"),
    )
