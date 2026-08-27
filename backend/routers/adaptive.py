"""
GET /activities/next — Adaptive activity recommendation.

Calls the Pedagogical Agent for the authenticated student and returns a
single recommendation: {topic_id, activity_type, reason, risk_tier}.

The Flutter app uses this to seed adaptive sessions instead of walking
a fixed list ordered by JSON file position.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import require_auth
from models import User
from agents.pedagogical import pedagogical_agent_node

router = APIRouter(prefix="/activities", tags=["Activities"])


class NextActivityRecommendation(BaseModel):
    topic_id: str
    activity_type: str
    reason: str
    confidence: float


@router.get("/next", response_model=NextActivityRecommendation)
async def get_next_activity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
) -> NextActivityRecommendation:
    """
    Return the Pedagogical Agent's recommendation for what to practice next.

    Identity is derived from the JWT token — no student_id parameter needed.
    The agent reads mastery from the DB (read-only) and walks the curriculum
    prerequisite DAG to find the optimal next step.
    """
    decision = await pedagogical_agent_node(
        student_id=current_user.id,
        session=db,
    )
    return NextActivityRecommendation(
        topic_id=decision.next_topic_id,
        activity_type=decision.next_activity_type,
        reason=decision.reason,
        confidence=decision.confidence,
    )
