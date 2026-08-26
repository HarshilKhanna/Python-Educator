from pydantic import BaseModel
from typing import List, Optional

class SourceSection(BaseModel):
    file: str
    heading: str

class ActivityResponse(BaseModel):
    id: str
    topic_id: str
    activity_type: str
    prompt_text: str
    code_snippet: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    difficulty: int
    source_section: SourceSection

class AnswerSubmission(BaseModel):
    # student_id intentionally removed — derived from the authenticated JWT
    activity_id: str
    submitted_answer: str

class AnswerResponse(BaseModel):
    mastery: float
    correct: bool
    explanation: str
