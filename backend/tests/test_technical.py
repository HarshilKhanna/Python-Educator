"""
Phase 7 — Technical Agent tests.

(a) A question the handbook clearly answers → grounded=True, answer references content
(b) A question about something NOT in the handbook (decorators) → grounded=False, no hallucination

Gate 5 rule: actually READ the output of test (b) before trusting grounded=False.
A Technical Agent that answers a decorator question correctly-sounding is the exact
failure mode this test is supposed to prevent.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.technical import technical_agent_node, TechnicalResponse
from models import Chunk


# ---------------------------------------------------------------------------
# Helpers — build a fake Chunk object without needing a real DB
# ---------------------------------------------------------------------------

from types import SimpleNamespace


def make_chunk(heading: str, content: str, topic_id: str = "loops") -> SimpleNamespace:
    """Build a lightweight fake Chunk without the SQLAlchemy ORM machinery."""
    return SimpleNamespace(
        id=1,
        heading=heading,
        content=content,
        topic_id=topic_id,
        embedding=None,
    )


# ---------------------------------------------------------------------------
# Test (a): question the handbook clearly answers
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_technical_grounded_question(mocker):
    """
    'What does range() do in a for loop?' should retrieve the loops section
    and return grounded=True with a relevant answer.
    """
    mock_session = AsyncMock()
    loops_chunk = make_chunk(
        heading="4.6  for loops",
        content=(
            "range(a, b) produces a range of numbers from a to b-1. "
            "Its general format is: range(start, stop+1, step). "
            "step is assumed as 1 when not specified. Start is assumed as 0."
        ),
    )

    # Mock rag.retrieve to return our fake chunk
    mocker.patch("agents.technical.retrieve", return_value=[loops_chunk])

    # Mock the LLM response
    mock_llm = MagicMock()
    mock_message = MagicMock()
    mock_message.content = (
        "The range() function produces a sequence of numbers. "
        "range(a, b) generates numbers from a to b-1."
    )
    mock_llm.ainvoke = AsyncMock(return_value=mock_message)
    mocker.patch("agents.technical._get_llm", return_value=mock_llm)

    result: TechnicalResponse = await technical_agent_node(
        question="What does range() do in a for loop?",
        topic_id="loops",
        session=mock_session,
    )

    assert result.grounded is True
    assert "range" in result.answer.lower()
    assert len(result.source_chunks) == 1
    assert result.source_chunks[0]["heading"] == "4.6  for loops"


# ---------------------------------------------------------------------------
# Test (b): question outside the handbook (decorators)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_technical_ungrounded_question_returns_no_hallucination(mocker):
    """
    A question about Python decorators (not in our handbook) must return:
      - grounded=False
      - answer must NOT attempt to explain decorators (i.e. the "I don't have that"
        phrase must be in the answer)

    Gate 5: Read this output by hand before trusting the assertion.
    If the LLM answered the decorator question correctly-sounding, the system failed.
    """
    mock_session = AsyncMock()
    decorator_chunk = make_chunk(
        heading="4.6  for loops",
        content="range(a, b) produces numbers from a to b-1.",
    )

    # Retrieval returns a chunk — but it's about loops, not decorators.
    # The LLM should recognize the mismatch and say "I don't have that."
    mocker.patch("agents.technical.retrieve", return_value=[decorator_chunk])

    # Mock the LLM — simulates correct behavior: the model says it can't answer
    mock_llm = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "I don't have that in the course material yet."
    mock_llm.ainvoke = AsyncMock(return_value=mock_message)
    mocker.patch("agents.technical._get_llm", return_value=mock_llm)

    result: TechnicalResponse = await technical_agent_node(
        question="How do Python decorators work?",
        topic_id=None,
        session=mock_session,
    )

    assert result.grounded is False, (
        f"Expected grounded=False for decorator question, got True. "
        f"Answer was: {result.answer!r}"
    )
    assert "I don't have that" in result.answer, (
        f"Expected the 'I don't have that' phrase, got: {result.answer!r}"
    )


@pytest.mark.asyncio
async def test_technical_empty_retrieval_returns_not_grounded(mocker):
    """
    If retrieval returns nothing, the agent must return grounded=False immediately
    (short-circuit before LLM call).
    """
    mock_session = AsyncMock()

    mocker.patch("agents.technical.retrieve", return_value=[])
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock()
    mocker.patch("agents.technical._get_llm", return_value=mock_llm)

    result: TechnicalResponse = await technical_agent_node(
        question="How do metaclasses work?",
        topic_id="loops",
        session=mock_session,
    )

    assert result.grounded is False
    assert "I don't have that in the course material yet" in result.answer
    # LLM should NOT have been called — no chunks to ground on
    mock_llm.ainvoke.assert_not_called()
