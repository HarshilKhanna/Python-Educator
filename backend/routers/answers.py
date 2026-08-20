import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import AnswerSubmission, AnswerResponse
from database import get_db
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
    db: AsyncSession = Depends(get_db)
):
    # 1. Lookup activity for correctness
    activity = _find_activity(submission.activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
        
    topic_id = activity.get("topic_id")
    correct_answer = activity.get("correct_answer")
    difficulty = activity.get("difficulty", 1)
    
    is_correct = (submission.submitted_answer == correct_answer)
    
    # 2. Calculate delta
    # e.g., +0.1 * difficulty for correct, -0.05 for incorrect
    if is_correct:
        delta = 0.1 * difficulty
        signal = "correct"
    else:
        delta = -0.05
        signal = "incorrect"
        
    # 3. Call LearnerModelService.recordUpdate
    # This must be the ONLY place that touches mastery/confidence
    try:
        updated_mastery = await LearnerModelService.record_update(
            session=db,
            source="activity_submission",
            student_id=submission.student_id,
            topic_id=topic_id,
            signal=signal,
            delta=delta
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
