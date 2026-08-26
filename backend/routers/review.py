"""
GET /review/pending — list all pending adaptation recommendations
POST /review/{id}/approve — approve one, triggering LearnerModelService.record_update
POST /review/{id}/reject — reject one (no state change)
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import PendingAdaptation
from services.learner_model import LearnerModelService

router = APIRouter(prefix="/review", tags=["Review"])

APPROVAL_DELTA = 0.05   # small positive nudge when an instructor approves an advancement


class PendingAdaptationSchema(BaseModel):
    id: int
    student_id: str
    next_topic_id: str
    next_activity_type: str
    reason: str
    status: str


@router.get("/pending", response_model=list[PendingAdaptationSchema])
async def list_pending(db: AsyncSession = Depends(get_db)):
    """Return all pending (not yet reviewed) adaptation recommendations."""
    stmt = select(PendingAdaptation).where(PendingAdaptation.status == "pending").order_by(
        PendingAdaptation.created_at.asc()
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        PendingAdaptationSchema(
            id=r.id,
            student_id=r.student_id,
            next_topic_id=r.next_topic_id,
            next_activity_type=r.next_activity_type,
            reason=r.reason,
            status=r.status,
        )
        for r in rows
    ]


@router.post("/{adaptation_id}/approve")
async def approve_adaptation(
    adaptation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a pending adaptation.

    This is the ONLY place that triggers a mastery write from the review queue.
    It goes through LearnerModelService.record_update — the single write path.
    """
    stmt = select(PendingAdaptation).where(PendingAdaptation.id == adaptation_id)
    result = await db.execute(stmt)
    pending = result.scalar_one_or_none()

    if not pending:
        raise HTTPException(status_code=404, detail="Pending adaptation not found.")
    if pending.status != "pending":
        raise HTTPException(status_code=409, detail=f"Already reviewed: status={pending.status!r}")

    # Apply the adaptation: give a small mastery nudge on the recommended topic
    # so the system knows the instructor has validated this path.
    try:
        new_mastery = await LearnerModelService.record_update(
            session=db,
            source="instructor_review_approval",
            student_id=pending.student_id,
            topic_id=pending.next_topic_id,
            signal="approved_advancement",
            delta=APPROVAL_DELTA,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"LearnerModelService error: {e}")

    # Mark as approved
    pending.status = "approved"
    pending.reviewed_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "id": adaptation_id,
        "status": "approved",
        "new_mastery": new_mastery,
        "topic_id": pending.next_topic_id,
    }


class RejectRequest(BaseModel):
    reason: str | None = None


@router.post("/{adaptation_id}/reject")
async def reject_adaptation(
    adaptation_id: int,
    body: RejectRequest = RejectRequest(),
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending adaptation — no state change to mastery.
    
    Rejected items are kept in the table for audit purposes.
    They will NEVER propagate to LearnerModelService.
    """
    stmt = select(PendingAdaptation).where(PendingAdaptation.id == adaptation_id)
    result = await db.execute(stmt)
    pending = result.scalar_one_or_none()

    if not pending:
        raise HTTPException(status_code=404, detail="Pending adaptation not found.")
    if pending.status != "pending":
        raise HTTPException(status_code=409, detail=f"Already reviewed: status={pending.status!r}")

    pending.status = "rejected"
    pending.reviewed_at = datetime.now(timezone.utc)
    pending.review_note = body.reason
    await db.commit()

    return {"id": adaptation_id, "status": "rejected", "reason": body.reason}

