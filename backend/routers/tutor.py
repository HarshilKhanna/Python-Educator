"""
POST /tutor/interact — Phase 9 endpoint, Phase 20 update

Accepts a student turn (student_id + message + optional topic_id).
Routes through the Orchestrator graph.

Phase 20 risk-tiering write path:
  - Kill-switch active (env var OR DB setting) → everything to pending_adaptations
  - 'low' risk → LearnerModelService.record_update, source="pedagogical_agent_auto"
  - 'medium' risk, high confidence → LearnerModelService.record_update, same source
  - 'medium' risk, low confidence → classified 'high' by classify_risk → pending
  - 'high' risk → pending_adaptations (unchanged from Phase 10 behavior)

LearnerModelService.record_update remains the ONLY write path in both branches.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import config
from database import get_db
from dependencies import require_auth
from models import Mastery, PendingAdaptation, SystemSettings, User
from agents.orchestrator import orchestrator_graph, set_session
from risk_policy import classify_risk
from services.learner_model import LearnerModelService
from services.monitoring import MonitoringService

router = APIRouter(prefix="/tutor", tags=["Tutor"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class InteractRequest(BaseModel):
    # student_id intentionally removed — derived from the authenticated JWT
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
    # Phase 20: risk tier of this recommendation (always present for activity_request)
    risk_tier: str | None = None
    auto_applied: bool = False
    # For technical intent
    answer: str | None = None
    grounded: bool | None = None
    source_chunks: list[dict] | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_current_topic(student_id: str, session: AsyncSession) -> str | None:
    """Return the topic the student most recently worked on (highest mastery update time)."""
    stmt = select(Mastery).where(Mastery.student_id == student_id).order_by(
        Mastery.last_updated.desc()
    ).limit(1)
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    return row.topic_id if row else None


async def _get_mastery_map(student_id: str, session: AsyncSession) -> dict[str, float]:
    """Return {topic_id: mastery_level} for the student."""
    stmt = select(Mastery).where(Mastery.student_id == student_id)
    result = await session.execute(stmt)
    rows = result.scalars().all()
    return {row.topic_id: row.mastery_level for row in rows}


async def _kill_switch_active(session: AsyncSession) -> bool:
    """
    Return True if the kill-switch is enabled.

    Checks the DB-backed SystemSettings first (allows live toggle from dashboard),
    then falls back to the env-var config flag.  Either one being True is enough.
    """
    # DB setting takes priority (live toggle without restart)
    try:
        stmt = select(SystemSettings).where(SystemSettings.key == "auto_apply_kill_switch")
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is not None:
            val = row.value
            # value is stored as JSON; can be a bool or the string "true"/"false"
            if isinstance(val, bool):
                if val:
                    return True
            elif str(val).lower() == "true":
                return True
    except Exception:
        pass  # If the table doesn't exist yet, fall through to env var

    return config.AUTO_APPLY_KILL_SWITCH


# AUTO_APPLY_DELTA: small mastery nudge applied when a low/medium-risk
# recommendation is auto-applied.  Same magnitude as the review-approval delta
# so the two paths are comparable.
AUTO_APPLY_DELTA = 0.05


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/interact", response_model=InteractResponse)
async def tutor_interact(
    req: InteractRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> InteractResponse:
    """
    Route a student turn through the Orchestrator.

    student_id is derived from the JWT — the client cannot supply or override it.
    - Activity requests → Pedagogical Agent → risk-tiered write path
    - Free-text questions → Technical Agent → grounded answer
    """
    # Identity comes from the token
    student_id = current_user.id

    # Inject DB session into the orchestrator
    set_session(db)

    try:
        final_state = await orchestrator_graph.ainvoke({
            "student_id": student_id,
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
        confidence = ped.get("confidence", 1.0)

        # Gather context for risk classification
        current_topic = await _get_current_topic(student_id, db)
        mastery_map = await _get_mastery_map(student_id, db)

        risk = classify_risk(
            current_topic=current_topic,
            next_topic_id=next_topic,
            next_activity_type=next_activity,
            confidence=confidence,
            mastery_map=mastery_map,
            confidence_threshold=config.CONFIDENCE_THRESHOLD,
        )

        # Check kill-switch (DB-backed first, then env var)
        kill_switch = await _kill_switch_active(db)

        # Decide: auto-apply or queue for review
        if not kill_switch and risk in ("low", "medium"):
            # -------------------------------------------------------
            # AUTO-APPLY PATH
            # LearnerModelService.record_update is the write path here
            # (same as the review-approval path — no second entry point)
            # -------------------------------------------------------
            try:
                await LearnerModelService.record_update(
                    session=db,
                    source="pedagogical_agent_auto",
                    student_id=student_id,
                    topic_id=next_topic,
                    signal="auto_applied_advancement",
                    delta=AUTO_APPLY_DELTA,
                    risk_tier=risk,
                )
                await db.commit()
            except Exception as e:
                await db.rollback()
                raise HTTPException(status_code=500, detail=f"Auto-apply error: {e}")

            # Run anomaly checks after auto-apply (non-fatal — log and continue)
            try:
                await MonitoringService.check_and_store_anomalies(
                    session=db,
                    student_id=student_id,
                    signal_type="auto_applied_advancement",
                )
                await db.commit()
            except Exception:
                pass  # Anomaly check failure must never block the student

            return InteractResponse(
                intent=intent,
                next_topic_id=next_topic,
                next_activity_type=next_activity,
                reason=reason,
                pending_review=False,
                risk_tier=risk,
                auto_applied=True,
            )

        else:
            # -------------------------------------------------------
            # REVIEW QUEUE PATH (unchanged from Phase 10)
            # kill_switch active OR risk == 'high'
            # -------------------------------------------------------
            pending = PendingAdaptation(
                student_id=student_id,
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
                risk_tier=risk,
                auto_applied=False,
            )

    # --- Technical path ---
    tech = final_state.get("technical_result", {})
    return InteractResponse(
        intent=intent,
        answer=tech.get("answer"),
        grounded=tech.get("grounded"),
        source_chunks=tech.get("source_chunks"),
    )
