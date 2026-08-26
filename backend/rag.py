"""
RAG module — Phase 6.1 (retrieve) + Phase 11 (instructor uploads, source ranking)

Public API:
  parse_handbook() -> list[dict]
  ingest_handbook(session) -> None
  ingest_upload(session, file_bytes, filename, topic_id, uploaded_by) -> int
  retrieve(session, query, topic_id, k, include_instructor_uploads) -> list[Chunk]
"""

import asyncio
import io
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

from models import Chunk

HANDBOOK_DIR = Path(__file__).parent.parent / "docs" / "handbook"

# ---------------------------------------------------------------------------
# Embedding model (lazy singleton)
# ---------------------------------------------------------------------------

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file using pypdf."""
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def _extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a .docx file using python-docx."""
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())


def _extract_text(file_bytes: bytes, filename: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return _extract_text_from_docx(file_bytes)
    elif ext == ".md":
        return file_bytes.decode("utf-8", errors="replace")
    else:
        # Generic: try UTF-8 text
        return file_bytes.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Chunking strategies
# ---------------------------------------------------------------------------

def _chunk_by_headings(text: str, topic_id: str) -> list[dict]:
    """
    Split markdown-style text by heading lines (lines starting with #).
    Returns list of {topic_id, heading, content}.
    """
    chunks = []
    current_heading = "Introduction"
    current_lines: list[str] = []

    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("#"):
            content = "".join(current_lines).strip()
            if content:
                chunks.append({"topic_id": topic_id, "heading": current_heading, "content": content})
            current_heading = line.lstrip("#").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    # flush last chunk
    content = "".join(current_lines).strip()
    if content:
        chunks.append({"topic_id": topic_id, "heading": current_heading, "content": content})

    return chunks


def _chunk_by_paragraphs(text: str, topic_id: str, filename: str) -> list[dict]:
    """
    Fallback: split on blank lines (paragraph chunking).
    Used for PDFs/DOCX that have no heading markers.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for i, para in enumerate(paragraphs):
        if len(para) < 40:          # skip very short fragments
            continue
        chunks.append({
            "topic_id": topic_id,
            "heading": f"{Path(filename).stem} — paragraph {i + 1}",
            "content": para,
        })
    return chunks


def _auto_chunk(text: str, topic_id: str, filename: str) -> list[dict]:
    """
    Use heading-based chunking if ≥2 headings are detected; otherwise paragraph chunking.
    """
    heading_count = sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))
    if heading_count >= 2:
        chunks = _chunk_by_headings(text, topic_id)
    else:
        chunks = _chunk_by_paragraphs(text, topic_id, filename)
    return chunks


# ---------------------------------------------------------------------------
# Handbook ingestion
# ---------------------------------------------------------------------------

def parse_handbook() -> list[dict]:
    """
    Parse handbook markdown files into chunks.
    Returns list of {topic_id, heading, content}.
    """
    chunks = []
    if not HANDBOOK_DIR.exists():
        return chunks

    for filepath in sorted(HANDBOOK_DIR.glob("*.md")):
        filename = filepath.stem
        parts = filename.split("-", 1)
        topic_id = parts[1] if len(parts) > 1 and parts[0].isdigit() else filename

        text = filepath.read_text(encoding="utf-8")
        chunks.extend(_chunk_by_headings(text, topic_id))

    return chunks


async def ingest_handbook(session: AsyncSession) -> None:
    """Embed handbook chunks and upsert into DB with source_type='handbook'."""
    model = get_model()
    for raw in parse_handbook():
        text_to_embed = f"{raw['heading']}\n\n{raw['content']}"
        embedding = model.encode(text_to_embed).tolist()
        session.add(Chunk(
            topic_id=raw["topic_id"],
            heading=raw["heading"],
            content=raw["content"],
            source_type="handbook",
            embedding=embedding,
        ))
    await session.commit()


# ---------------------------------------------------------------------------
# Instructor upload ingestion
# ---------------------------------------------------------------------------

async def ingest_upload(
    session: AsyncSession,
    file_bytes: bytes,
    filename: str,
    topic_id: str,
    uploaded_by: str,
) -> int:
    """
    Parse, chunk, embed, and store an instructor-uploaded file.
    Returns the number of chunks inserted.
    """
    model = get_model()
    text = _extract_text(file_bytes, filename)
    raw_chunks = _auto_chunk(text, topic_id, filename)

    now = datetime.now(timezone.utc)
    count = 0
    for raw in raw_chunks:
        text_to_embed = f"{raw['heading']}\n\n{raw['content']}"
        embedding = model.encode(text_to_embed).tolist()
        session.add(Chunk(
            topic_id=raw["topic_id"],
            heading=raw["heading"],
            content=raw["content"],
            source_type="instructor_upload",
            uploaded_by=uploaded_by,
            uploaded_at=now,
            embedding=embedding,
        ))
        count += 1

    await session.commit()
    return count


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

async def retrieve(
    session: AsyncSession,
    query: str,
    topic_id: str | None = None,
    k: int = 4,
    include_instructor_uploads: bool = True,
) -> list[Chunk]:
    """
    Retrieve the most relevant chunks using cosine distance.

    Ranking rule (Gate 9):
      - Fetch k*2 candidates
      - Handbook chunks rank ahead of instructor_upload chunks at equal relevance
      - Result is capped at k

    Filters by topic_id when provided.
    """
    model = get_model()
    query_embedding = model.encode(query).tolist()

    # Fetch more candidates than needed so we can re-rank by source_type
    fetch_k = k * 2 if include_instructor_uploads else k

    stmt = (
        select(Chunk)
        .order_by(Chunk.embedding.cosine_distance(query_embedding))
        .limit(fetch_k)
    )

    if topic_id:
        stmt = stmt.where(Chunk.topic_id == topic_id)

    if not include_instructor_uploads:
        stmt = stmt.where(Chunk.source_type == "handbook")

    result = await session.execute(stmt)
    candidates = list(result.scalars().all())

    if not include_instructor_uploads:
        return candidates[:k]

    # Stable sort: handbook chunks first (preserves cosine-distance order within each tier)
    handbook_chunks = [c for c in candidates if c.source_type == "handbook"]
    upload_chunks = [c for c in candidates if c.source_type != "handbook"]
    ranked = (handbook_chunks + upload_chunks)[:k]
    return ranked


# ---------------------------------------------------------------------------
# CLI ingestion entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from database import AsyncSessionLocal, engine, run_migrations
    from models import Base
    import sqlalchemy

    async def main():
        async with engine.begin() as conn:
            await run_migrations(conn)
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            print("Ingesting handbook chunks...")
            await ingest_handbook(session)
            print("Done!")

    asyncio.run(main())
