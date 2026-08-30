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
    
    sub = submission.submitted_answer.strip()
    cor = (correct_answer or "").strip()
    is_correct = (sub == cor) or (sub.replace('"', "'") == cor.replace('"', "'"))
    if not is_correct and cor.startswith("[") and cor.endswith("]"):
        try:
            import ast
            parsed = ast.literal_eval(cor)
            if isinstance(parsed, list):
                pipe_cor = "|".join(str(p).strip() for p in parsed)
                is_correct = (sub == pipe_cor) or (sub.replace('"', "'") == pipe_cor.replace('"', "'"))
        except Exception:
            pass
    
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
        
        # Streak and XP logic
        current_user.streak += 1
        if current_user.streak > current_user.best_streak:
            current_user.best_streak = current_user.streak
        
        # XP formula: base (10) * difficulty + streak bonus (up to 50)
        streak_bonus = min(50, current_user.streak * 5)
        current_user.xp += (10 * difficulty) + streak_bonus
        
    else:
        # Penalize more if they are already considered "mastered"
        # Confident and wrong -> big penalty (1.5x). Unsure and wrong -> normal penalty (1.0x).
        confidence_factor = 1.5 if confidence > 0.6 else 1.0
        delta = -0.10 * difficulty * max(0.2, current_mastery) * confidence_factor
        signal = "incorrect"
        
        # Break streak
        current_user.streak = 0
        # Optional: grant a tiny 2 XP just for attempting
        current_user.xp += 2
        
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
            activity_type=activity.get("type"),
        )
        
        db.add(current_user)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update learner model: {str(e)}")
        
    # 5. Return explanation (only if they got it wrong, or unconditionally?)
    # Usually you return the explanation if they got it wrong so they can learn.
    explanation = activity.get("explanation") if not is_correct else "Correct!"
    
    return AnswerResponse(
        correct=is_correct,
        explanation=explanation,
        mastery=updated_mastery,
        streak=current_user.streak,
        xp=current_user.xp,
    )
