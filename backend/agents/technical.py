"""
Technical Agent — Phase 7

A single LangGraph node function (not a full graph yet).
Given (question, topic_id, session), it:
  1. Calls rag.retrieve() to ground the answer
  2. Calls the LLM with a strict system prompt that forbids answering from general knowledge
  3. Returns a structured TechnicalResponse

Grounding rule: if retrieval returns nothing relevant, the agent must say so
rather than hallucinating from parametric knowledge.
"""

from __future__ import annotations

import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from rag import retrieve, Chunk


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

class TechnicalResponse(BaseModel):
    answer: str
    grounded: bool
    source_chunks: list[dict[str, Any]]  # [{"heading": ..., "content": ...}]


# ---------------------------------------------------------------------------
# LLM setup (lazy — only initialized when first called)
# ---------------------------------------------------------------------------

_llm: ChatOpenAI | None = None

SYSTEM_PROMPT = """\
You are a Python tutor assistant. You MUST answer using ONLY the information
provided in the <context> blocks below. Do NOT use any knowledge from your training
data that is not present in the context.

Each context block is tagged with its source:
  - source="handbook": This is the official course handbook. Cite it as course material.
  - source="instructor_upload": This is a supplementary note from your instructor.
    When citing it, explicitly say "per your instructor's notes on this topic".

If the context does not contain enough information to answer the question, respond
with exactly:
  "I don't have that in the course material yet."

Do not speculate, do not add examples not in the context, and do not apologize at length.
"""


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=api_key,
        )
    return _llm


# ---------------------------------------------------------------------------
# Node function
# ---------------------------------------------------------------------------

async def technical_agent_node(
    *,
    question: str,
    topic_id: str | None,
    session: AsyncSession,
    k: int = 4,
) -> TechnicalResponse:
    """
    The Technical Agent node.

    Retrieves relevant handbook chunks, then calls the LLM with a grounding
    constraint. Returns a structured TechnicalResponse.

    This function is testable in isolation — pass a mock `session` for unit tests.
    """
    # 1. Retrieve relevant chunks
    chunks: list[Chunk] = await retrieve(session, query=question, topic_id=topic_id, k=k)

    if not chunks:
        return TechnicalResponse(
            answer="I don't have that in the course material yet.",
            grounded=False,
            source_chunks=[],
        )

    # 2. Build context from retrieved chunks (tagged with source_type for the LLM)
    context_blocks = "\n\n".join(
        f'<context source="{getattr(c, "source_type", "handbook")}" heading="{c.heading}">\n{c.content}\n</context>'
        for c in chunks
    )

    # 3. Heuristic grounding check: if the best chunk is about a wildly different
    #    topic, we can short-circuit before the LLM call.
    # (A more robust approach would be to check cosine similarity threshold here.)

    # 4. Call the LLM
    llm = _get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"{context_blocks}\n\nQuestion: {question}"),
    ]
    response = await llm.ainvoke(messages)
    answer: str = response.content.strip()

    # 5. Determine grounded flag
    not_grounded_phrase = "I don't have that in the course material yet"
    grounded = not_grounded_phrase.lower() not in answer.lower()

    return TechnicalResponse(
        answer=answer,
        grounded=grounded,
        source_chunks=[
            {
                "heading": c.heading,
                "content": c.content[:300],
                "source_type": getattr(c, "source_type", "handbook"),
            }
            for c in chunks
        ],
    )
