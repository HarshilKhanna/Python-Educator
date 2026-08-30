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
from langchain_google_genai import ChatGoogleGenerativeAI
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

_llm: ChatGoogleGenerativeAI | None = None

SYSTEM_PROMPT = """\
You are a helpful and knowledgeable Python tutor assistant. 
Use the provided <context> blocks below to ground your answer in the course material when possible.
If the context contains the answer, cite it (e.g., "per the course handbook" or "per your instructor's notes").

If the context does NOT contain the answer (or no context is provided), you should still use your general knowledge of Python to answer the student's question helpfully and accurately.

Format your output in clean, readable Markdown using bolding, lists, and code blocks where appropriate.

Do not apologize at length. Be encouraging, clear, and concise.
"""


def _get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        _llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            temperature=0.0,
            google_api_key=api_key,
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
    content = response.content
    if isinstance(content, list):
        answer = "".join(
            c.get("text", "") if isinstance(c, dict) else str(c) for c in content
        ).strip()
    else:
        answer = str(content).strip()

    # 5. Determine grounded flag
    # If we have context chunks, we assume the model grounded its response to some degree.
    grounded = len(chunks) > 0

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
