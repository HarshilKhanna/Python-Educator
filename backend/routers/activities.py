import json
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException

from schemas import ActivityResponse

router = APIRouter(prefix="/activities", tags=["Activities"])

# Path to the content directory (assuming backend is at e:/Python Educator/backend)
CONTENT_DIR = Path(__file__).parent.parent.parent / "content" / "activities"

@router.get("", response_model=List[ActivityResponse])
async def get_activities(topic_id: str):
    """
    Fetch activities for a given topic directly from disk.
    For the prototype, this reads from /content/activities/{topic_id}.json.
    """
    file_path = CONTENT_DIR / f"{topic_id}.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"No activities found for topic: {topic_id}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "activities" in data:
                return data["activities"]
            if isinstance(data, list):
                return data
            return [data] # Fallback if it's a single object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read activity content: {str(e)}")
