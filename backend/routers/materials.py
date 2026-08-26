"""
POST /materials/upload  — instructor file ingestion
GET  /curriculum/topics — ordered topic list from the curriculum DAG

Both endpoints require an instructor JWT. The dev-only INSTRUCTOR_TOKEN stub
has been removed entirely in Phase 14.2.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import require_role
from models import User
from rag import ingest_upload
from agents.pedagogical import CURRICULUM_ORDER

router = APIRouter(tags=["Materials"])


@router.post("/materials/upload")
async def upload_material(
    file: UploadFile = File(...),
    topic_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("instructor")),
):
    """
    Accept a PDF, DOCX, or Markdown file from an instructor.
    Extracts text, chunks it, embeds each chunk, and stores with
    source_type='instructor_upload'.

    uploaded_by is derived from the authenticated user's email — not a
    client-supplied form field — so attribution cannot be spoofed.

    Returns chunk count and confirmation metadata.
    """
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/markdown",
        "text/plain",
    }
    content_type = file.content_type or ""
    filename = file.filename or "upload"

    # Also allow by extension if content-type is generic
    ext = filename.rsplit(".", 1)[-1].lower()
    if content_type not in allowed_types and ext not in ("pdf", "docx", "md", "txt"):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {content_type!r}. Accepted: pdf, docx, md, txt",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file.")

    # Derive attribution from the authenticated user, not the request body
    uploaded_by = current_user.email

    try:
        chunk_count = await ingest_upload(
            session=db,
            file_bytes=file_bytes,
            filename=filename,
            topic_id=topic_id,
            uploaded_by=uploaded_by,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return {
        "filename": filename,
        "topic_id": topic_id,
        "source_type": "instructor_upload",
        "chunk_count": chunk_count,
        "uploaded_by": uploaded_by,
    }


@router.get("/curriculum/topics")
async def get_curriculum_topics(
    _: User = Depends(require_role("instructor")),
):
    """
    Return the ordered list of curriculum topic IDs from the prerequisite DAG.
    Used by the instructor dashboard's topic_id dropdown.
    """
    return {"topics": CURRICULUM_ORDER}
