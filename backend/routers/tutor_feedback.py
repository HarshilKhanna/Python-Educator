from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import TutorFeedback, User
from schemas import TutorFeedbackRequest
from dependencies import require_auth

router = APIRouter(prefix="/tutor", tags=["tutor"])

@router.post("/feedback")
async def submit_tutor_feedback(
    request: TutorFeedbackRequest,
    current_user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit thumbs up/down feedback for a tutor message.
    """
    student_id = current_user.id
    
    if request.rating not in ('up', 'down'):
        raise HTTPException(status_code=422, detail="rating must be 'up' or 'down'")

    # Store the feedback
    feedback = TutorFeedback(
        student_id=student_id,
        topic_id=request.topic_id,
        message_id=request.message_id,
        rating=request.rating
    )
    db.add(feedback)
    await db.commit()
    
    return {"status": "success"}
