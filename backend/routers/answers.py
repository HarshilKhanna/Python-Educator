import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import AnswerSubmission, AnswerResponse
from database import get_db
from dependencies import require_auth
from sqlalchemy.future import select
from models import User, Mastery
from services.learner_model import LearnerModelService

router = APIRouter(prefix="/answer", tags=["Answers"])

CONTENT_DIR = Path(__file__).parent.parent.parent / "content" / "activities"

def _find_activity(activity_id: str):
    """Scan all local JSON files to find the activity by ID."""
    if not CONTENT_DIR.exists():
        return None
        
    for file_path in CONTENT_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "activities" in data:
                    data = data["activities"]
                if isinstance(data, list):
                    for act in data:
                        if act.get("id") == activity_id:
                            return act
        except Exception:
            pass
    return None


@router.post("", response_model=AnswerResponse)
async def submit_answer(
    submission: AnswerSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """
    Submit an answer for the authenticated student.

    student_id is derived from the JWT — the client cannot supply or override it.
    """
    # Identity comes from the token, not the request body
    student_id = current_user.id

    # 1. Lookup activity for correctness
    activity = _find_activity(submission.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
        
    topic_id = activity.get("topic_id")
    correct_answer = activity.get("correct_answer")
    difficulty = activity.get("difficulty", 1)
    
    is_correct = (submission.submitted_answer == correct_answer)
    
    # 2. Fetch current mastery to calculate scaled delta
    stmt = select(Mastery).where(Mastery.student_id == student_id, Mastery.topic_id == topic_id)
    result = await db.execute(stmt)
    mastery_record = result.scalar_one_or_none()
    current_mastery = mastery_record.mastery_level if mastery_record else 0.0

    # 3. Calculate delta with diminishing returns and confidence scaling
    confidence = submission.confidence if submission.confidence is not None else 0.5
    
    if is_correct:
        # Diminishing returns: the closer to 1.0, the smaller the bump
        distance = 1.0 - current_mastery
        # Confident and correct -> normal bump (1.0). Unsure and correct -> smaller bump (0.5).
        confidence_factor = 0.5 + (0.5 * confidence) 
        delta = 0.15 * difficulty * distance * confidence_factor
        signal = "correct"
    else:
        # Penalize more if they are already considered "mastered"
        # Confident and wrong -> big penalty (1.5x). Unsure and wrong -> normal penalty (1.0x).
        confidence_factor = 1.5 if confidence > 0.6 else 1.0
        delta = -0.10 * difficulty * max(0.2, current_mastery) * confidence_factor
        signal = "incorrect"
        
    # 4. Call LearnerModelService.recordUpdate
    # This must be the ONLY place that touches mastery/confidence
    try:
        updated_mastery = await LearnerModelService.record_update(
            session=db,
            source="activity_submission",
            student_id=student_id,
            topic_id=topic_id,
            signal=signal,
            delta=delta,
            student_confidence=submission.confidence,
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update learner model: {str(e)}")

    return AnswerResponse(
        mastery=updated_mastery,
        correct=is_correct,
        explanation=activity.get("explanation", "")
    )
