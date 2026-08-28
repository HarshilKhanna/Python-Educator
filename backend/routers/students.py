"""
GET /students/{student_id}/mastery

Returns current mastery/confidence per topic and the last 10 adaptation events
with human-readable reasons. Read-only — no new write path.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from dependencies import require_auth
from models import Mastery, AdaptationEvent, PendingAdaptation, User

router = APIRouter(prefix="/students", tags=["Students"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TopicMastery(BaseModel):
    topic_id: str
    mastery_level: float
    confidence: float
    last_updated: str | None


class RecentEvent(BaseModel):
    timestamp: str | None
    topic_id: str
    source: str
    signal: str
    delta: float
    # Human-readable reason from the Pedagogical Agent (if available)
    reason: str | None


class StudentMasteryResponse(BaseModel):
    student_id: str
    mastery: list[TopicMastery]
    recent_events: list[RecentEvent]


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("/{student_id}/mastery", response_model=StudentMasteryResponse)
async def get_student_mastery(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """
    Returns per-topic mastery state and last 10 adaptation events with reasons.

    Authorization:
    - Students may only read their own mastery (student_id must match token).
    - Instructors may read any student's mastery.

    Reasons are sourced from the Pedagogical Agent's recommendation stored in
    pending_adaptations — matched by student_id and topic_id/timestamp proximity.
    This gives instructors a human-readable explanation of *why* the system
    recommended what it did, not just *what* it did.
    """
    # Cross-student authorization gate
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(
            status_code=403,
            detail="Students may only access their own mastery data.",
        )
    # 1. Mastery rows
    stmt = select(Mastery).where(Mastery.student_id == student_id).order_by(
        Mastery.last_updated.desc()
    )
    result = await db.execute(stmt)
    mastery_rows = result.scalars().all()

    # 2. Recent adaptation events (last 10)
    stmt2 = (
        select(AdaptationEvent)
        .where(AdaptationEvent.student_id == student_id)
        .order_by(AdaptationEvent.timestamp.desc())
        .limit(10)
    )
    result2 = await db.execute(stmt2)
    events = result2.scalars().all()

    # 3. Pending adaptations for reason lookup
    stmt3 = (
        select(PendingAdaptation)
        .where(PendingAdaptation.student_id == student_id)
        .order_by(PendingAdaptation.created_at.desc())
        .limit(20)
    )
    result3 = await db.execute(stmt3)
    pending_rows = result3.scalars().all()

    # Build a topic→reason map from the most recent pending adaptation per topic
    reason_map: dict[str, str] = {}
    for p in pending_rows:
        if p.next_topic_id not in reason_map:
            reason_map[p.next_topic_id] = p.reason

    # Build response
    mastery_out = [
        TopicMastery(
            topic_id=m.topic_id,
            mastery_level=round(m.mastery_level, 4),
            confidence=round(m.confidence, 4),
            last_updated=m.last_updated.isoformat() if m.last_updated else None,
        )
        for m in mastery_rows
    ]

    events_out = [
        RecentEvent(
            timestamp=e.timestamp.isoformat() if e.timestamp else None,
            topic_id=e.topic_id,
            source=e.source,
            signal=e.signal,
            delta=e.delta,
            reason=reason_map.get(e.topic_id),
        )
        for e in events
    ]

    return StudentMasteryResponse(
        student_id=student_id,
        mastery=mastery_out,
        recent_events=events_out,
    )

class StyleProfileUpdate(BaseModel):
    style_profile: dict

@router.patch("/{student_id}/style")
async def update_style_profile(
    student_id: str,
    payload: StyleProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    stmt = select(User).where(User.id == student_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.style_profile = payload.style_profile
    await db.commit()
    return {"status": "ok"}
