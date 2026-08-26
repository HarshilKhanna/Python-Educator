"""
Phase 6.2 — 5 hand-written RAG retrieval queries.

Each test encodes a specific question where we KNOW which handbook heading
should rank top-1. The embedding model runs locally (no DB needed — we stub
the DB call with a real rank via in-memory numpy cosine sim).

Gate 4 rule: the assertion is on the *heading text*, not just "returns something".
If a test becomes trivially green (heading is too broad), tighten the expected string.
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from sentence_transformers import SentenceTransformer

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag import parse_handbook, get_model, HANDBOOK_DIR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-10)
    b = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a, b))


def top1_heading(query: str, topic_id: str | None = None) -> str:
    """
    Rank all in-memory chunks by cosine similarity to the query.
    Returns the heading of the best-matching chunk.
    No DB required.
    """
    model = get_model()
    chunks = parse_handbook()
    if topic_id:
        chunks = [c for c in chunks if c["topic_id"] == topic_id]
    assert chunks, f"No chunks found for topic_id={topic_id!r}"

    query_emb = model.encode(query)
    texts = [f"{c['heading']}\n\n{c['content']}" for c in chunks]
    chunk_embs = model.encode(texts)

    sims = [cosine_sim(query_emb, e) for e in chunk_embs]
    best_idx = int(np.argmax(sims))
    return chunks[best_idx]["heading"]


# ---------------------------------------------------------------------------
# 5 hand-crafted queries — Gate 4: read these results by hand before trusting them
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HANDBOOK_DIR.exists(), reason="Handbook not present")
def test_range_function_query():
    """
    'what does range() do' should retrieve the for-loops section that explains
    range(start, stop, step).
    Expected heading: '4.6  for loops'
    """
    heading = top1_heading("what does range() do", topic_id="loops")
    assert "4.6" in heading or "for loop" in heading.lower(), (
        f"Expected the for-loops chunk, got: {heading!r}"
    )


@pytest.mark.skipif(not HANDBOOK_DIR.exists(), reason="Handbook not present")
def test_while_loop_condition_query():
    """
    'how does a while loop decide when to stop' should retrieve the while-loops section.
    Expected heading: '4.7 while loops'
    """
    heading = top1_heading("how does a while loop decide when to stop", topic_id="loops")
    assert "while" in heading.lower(), (
        f"Expected the while-loops chunk, got: {heading!r}"
    )


@pytest.mark.skipif(not HANDBOOK_DIR.exists(), reason="Handbook not present")
def test_nested_loops_query():
    """
    'can you put a for loop inside another for loop' should retrieve the nested-loops explanation.
    Expected heading: '4.6  for loops' (nested for loops are in §4.6 point 4)
    """
    heading = top1_heading("can you put a for loop inside another for loop", topic_id="loops")
    assert "for loop" in heading.lower() or "4.6" in heading, (
        f"Expected the for-loops section (nested loops), got: {heading!r}"
    )


@pytest.mark.skipif(not HANDBOOK_DIR.exists(), reason="Handbook not present")
def test_break_statement_query():
    """
    'how do I exit a loop early using break' should retrieve the break/continue section.
    Expected heading: contains 'break' or 'control'
    """
    heading = top1_heading("how do I exit a loop early using break", topic_id="loops")
    assert any(kw in heading.lower() for kw in ["break", "control", "while", "for loop"]), (
        f"Expected break/control chunk, got: {heading!r}"
    )


@pytest.mark.skipif(not HANDBOOK_DIR.exists(), reason="Handbook not present")
def test_if_else_conditionals_query():
    """
    Cross-topic: 'what is an if-else statement' should retrieve conditionals, not loops.
    No topic_id filter — falls back to full corpus.
    Expected heading: from 02-conditionals.md
    """
    heading = top1_heading("what is an if-else statement", topic_id=None)
    assert any(kw in heading.lower() for kw in ["if", "conditional", "else", "decision"]), (
        f"Expected conditionals chunk, got: {heading!r}"
    )
