import asyncio
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentence_transformers import SentenceTransformer

from models import Chunk

HANDBOOK_DIR = Path(__file__).parent.parent / "docs" / "handbook"

# Load model lazily
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def parse_handbook():
    """
    Parses handbook markdown files into chunks by heading.
    Returns a list of dicts: {"topic_id": str, "heading": str, "content": str}
    """
    chunks = []
    
    if not HANDBOOK_DIR.exists():
        return chunks
        
    for filepath in HANDBOOK_DIR.glob("*.md"):
        # e.g., '03-loops.md' -> 'loops'
        filename = filepath.stem
        # Extract topic by splitting off the number prefix if it exists
        parts = filename.split("-", 1)
        topic_id = parts[1] if len(parts) > 1 and parts[0].isdigit() else filename
        
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        current_heading = "Introduction"
        current_content = []
        
        for line in lines:
            if line.startswith("#"):
                # Save previous chunk if it has content
                content_text = "".join(current_content).strip()
                if content_text:
                    chunks.append({
                        "topic_id": topic_id,
                        "heading": current_heading,
                        "content": content_text
                    })
                
                # Start new chunk
                current_heading = line.lstrip("#").strip()
                current_content = [line]  # Keep heading in the content for context
            else:
                current_content.append(line)
                
        # Save last chunk
        content_text = "".join(current_content).strip()
        if content_text:
            chunks.append({
                "topic_id": topic_id,
                "heading": current_heading,
                "content": content_text
            })
            
    return chunks

async def ingest_handbook(session: AsyncSession):
    """
    Embeds parsed handbook chunks and stores them in the database.
    """
    model = get_model()
    raw_chunks = parse_handbook()
    
    for raw_chunk in raw_chunks:
        text_to_embed = f"{raw_chunk['heading']}\n\n{raw_chunk['content']}"
        embedding = model.encode(text_to_embed)
        
        chunk_record = Chunk(
            topic_id=raw_chunk["topic_id"],
            heading=raw_chunk["heading"],
            content=raw_chunk["content"],
            embedding=embedding.tolist()
        )
        session.add(chunk_record)
        
    await session.commit()

async def retrieve(session: AsyncSession, query: str, topic_id: str | None = None, k: int = 4) -> list[Chunk]:
    """
    Retrieves the most relevant chunks using cosine distance.
    Filters by topic_id if provided.
    """
    model = get_model()
    query_embedding = model.encode(query).tolist()
    
    stmt = select(Chunk).order_by(Chunk.embedding.cosine_distance(query_embedding)).limit(k)
    
    if topic_id:
        stmt = stmt.where(Chunk.topic_id == topic_id)
        
    result = await session.execute(stmt)
    return list(result.scalars().all())

if __name__ == "__main__":
    from database import AsyncSessionLocal, engine
    from models import Base
    import sqlalchemy
    
    async def main():
        async with engine.begin() as conn:
            await conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await conn.run_sync(Base.metadata.create_all)
            
        async with AsyncSessionLocal() as session:
            print("Ingesting handbook chunks...")
            await ingest_handbook(session)
            print("Done!")
            
    asyncio.run(main())
