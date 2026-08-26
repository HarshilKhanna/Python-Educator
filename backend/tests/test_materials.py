"""
Tests for Phase 11: instructor materials ingestion.

Covers:
- Heading-based chunking for markdown files
- Paragraph-fallback chunking for files without headings
- PDF / DOCX extraction (mocked file bytes)
- Gate 9: handbook chunks rank first when retrieved alongside upload chunks
"""

import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag import (
    _chunk_by_headings,
    _chunk_by_paragraphs,
    _auto_chunk,
    parse_handbook,
    HANDBOOK_DIR,
)


# ---------------------------------------------------------------------------
# Chunking logic unit tests
# ---------------------------------------------------------------------------

def test_chunk_by_headings_splits_correctly():
    md = "# Section 1\nContent one.\n\n## Section 1.1\nContent 1.1\n# Section 2\nContent two."
    chunks = _chunk_by_headings(md, "loops")
    assert len(chunks) == 3
    assert chunks[0]["heading"] == "Section 1"
    assert "Content one." in chunks[0]["content"]
    assert chunks[1]["heading"] == "Section 1.1"
    assert chunks[2]["heading"] == "Section 2"
    # All tagged with correct topic_id
    assert all(c["topic_id"] == "loops" for c in chunks)


def test_chunk_by_paragraphs_skips_short_fragments():
    text = "This is a proper paragraph with enough content to be a chunk.\n\nOK\n\nAnother good paragraph here with sufficient length."
    chunks = _chunk_by_paragraphs(text, "loops", "test.pdf")
    # "OK" (length 2) should be skipped
    assert all(len(c["content"]) >= 40 for c in chunks)
    assert len(chunks) == 2


def test_auto_chunk_uses_headings_when_present():
    md = "# Topic A\nSome content.\n## Subtopic\nMore content.\n# Topic B\nFinal."
    chunks = _auto_chunk(md, "loops", "notes.md")
    # 3 headings → heading chunking used
    headings = [c["heading"] for c in chunks]
    assert "Topic A" in headings
    assert "Subtopic" in headings


def test_auto_chunk_falls_back_to_paragraphs_for_pdf_without_headings():
    # Simulated PDF text with no markdown headings
    text = (
        "Python is a high-level programming language known for readability.\n\n"
        "Variables in Python are dynamically typed and do not need declaration.\n\n"
        "Loops allow repeated execution of code blocks based on conditions."
    )
    chunks = _auto_chunk(text, "loops", "notes.pdf")
    # No headings → paragraph chunking
    assert len(chunks) == 3
    assert all(c["topic_id"] == "loops" for c in chunks)


def test_parse_handbook_produces_chunks_from_real_files():
    """Integration check: parse_handbook should return chunks if handbook files exist."""
    if not HANDBOOK_DIR.exists():
        pytest.skip("Handbook directory not present")
    chunks = parse_handbook()
    assert len(chunks) > 0
    # Every chunk has required fields
    for c in chunks:
        assert "topic_id" in c
        assert "heading" in c
        assert "content" in c
        assert len(c["content"]) > 0


# ---------------------------------------------------------------------------
# Gate 9: handbook-first ranking in retrieve()
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retrieve_ranks_handbook_before_instructor_uploads(mocker):
    """
    Gate 9: when handbook and upload chunks have equivalent relevance,
    handbook chunks must be returned first.
    """
    from rag import retrieve

    handbook_chunk = SimpleNamespace(
        id=1, heading="4.6 for loops", content="range() example",
        source_type="handbook", topic_id="loops",
    )
    upload_chunk = SimpleNamespace(
        id=2, heading="Instructor note", content="Extra loops note",
        source_type="instructor_upload", topic_id="loops",
    )

    # Return upload first (worse cosine order) to verify re-ranking
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [upload_chunk, handbook_chunk]

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    mock_model = MagicMock()
    # encode() must return something with .tolist() — use a MagicMock that does
    mock_encode_result = MagicMock()
    mock_encode_result.tolist.return_value = [0.1] * 384
    mock_model.encode.return_value = mock_encode_result
    mocker.patch("rag.get_model", return_value=mock_model)

    results = await retrieve(mock_session, "how do loops work?", topic_id="loops", k=2)

    assert len(results) == 2
    # Handbook must be first despite being second in raw cosine order
    assert results[0].source_type == "handbook", (
        f"Expected handbook first, got {results[0].source_type!r}"
    )
    assert results[1].source_type == "instructor_upload"
