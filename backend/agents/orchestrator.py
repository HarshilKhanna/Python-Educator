"""
Orchestrator — Phase 9

The top-level LangGraph StateGraph. Receives a student turn and routes it:
  - "give me the next activity" (or similar) → Pedagogical Agent
  - free-text question → Technical Agent

Routing uses a heuristic classifier (no LLM call). The heuristic is:
  - If the message matches ACTIVITY_REQUEST_PATTERNS → route to pedagogical
  - Otherwise → route to technical

Architecture rule (§3): The Orchestrator itself does NOT call
LearnerModelService.record_update. Writes only happen in POST /answer.
This graph is read-and-decide only.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal, TypedDict

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from agents.technical import technical_agent_node, TechnicalResponse
from agents.pedagogical import pedagogical_agent_node, PedagogicalDecision


# ---------------------------------------------------------------------------
# Intent classification (heuristic, no LLM)
# ---------------------------------------------------------------------------

ACTIVITY_REQUEST_PATTERNS = [
    r"\bnext\s+(activity|question|exercise|problem)\b",
    r"\bgive\s+me\s+(a|an|the)\s+(next|new)?\s*(activity|question|exercise|problem)\b",
    r"\bstart\s+(the|a)?\s*(next|new)?\s*(activity|question|exercise)\b",
    r"\bwhat('s|\s+is)\s+(the\s+)?next\b",
    r"\bpractice\b",
    r"\bquiz\s+me\b",
    r"\bmore\s+(questions|exercises|problems)\b",
    r"\bcontinue\b",
    r"\bbegin\b",
    r"\bready\b",
    r"^next$",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in ACTIVITY_REQUEST_PATTERNS]


def classify_intent(message: str) -> Literal["activity_request", "question"]:
    """
    Classify a student turn as an activity-request or a free-text question.
    Returns 'activity_request' if any pattern matches, else 'question'.
    """
    for pattern in _COMPILED:
        if pattern.search(message):
            return "activity_request"
    return "question"


# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------

class OrchestratorState(TypedDict):
    student_id: str
    message: str
    topic_id: str | None
    intent: str | None
    # Only one of these will be set depending on routing
    pedagogical_result: dict | None
    technical_result: dict | None
    # Set by Phase 10 guardrail logic
    pending_adaptation_id: int | None


# ---------------------------------------------------------------------------
# Node wrappers (nodes must accept and return state dicts)
# ---------------------------------------------------------------------------

# We can't pass the AsyncSession through the graph state (it's not JSON-serialisable),
# so we use a module-level reference set by the caller before invoking the graph.
# This is standard practice for injecting non-serializable dependencies into LangGraph.
_session_ref: AsyncSession | None = None


def set_session(session: AsyncSession) -> None:
    """Call this before invoking the graph to inject the DB session."""
    global _session_ref
    _session_ref = session


async def _classify_node(state: OrchestratorState) -> OrchestratorState:
    """Classify the intent of the student message."""
    intent = classify_intent(state["message"])
    return {**state, "intent": intent}


async def _pedagogical_node(state: OrchestratorState) -> OrchestratorState:
    """Run the Pedagogical Agent and store its decision."""
    assert _session_ref is not None, "DB session not set — call set_session() first"
    decision: PedagogicalDecision = await pedagogical_agent_node(
        student_id=state["student_id"],
        session=_session_ref,
    )
    return {**state, "pedagogical_result": decision.to_dict()}


async def _technical_node(state: OrchestratorState) -> OrchestratorState:
    """Run the Technical Agent and store its response."""
    assert _session_ref is not None, "DB session not set — call set_session() first"
    response: TechnicalResponse = await technical_agent_node(
        question=state["message"],
        topic_id=state.get("topic_id"),
        session=_session_ref,
    )
    return {
        **state,
        "technical_result": {
            "answer": response.answer,
            "grounded": response.grounded,
            "source_chunks": response.source_chunks,
        },
    }


def _route_intent(state: OrchestratorState) -> str:
    """Conditional edge: decide which agent node to invoke."""
    if state.get("intent") == "activity_request":
        return "pedagogical"
    return "technical"


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    builder = StateGraph(OrchestratorState)

    builder.add_node("classify", _classify_node)
    builder.add_node("pedagogical", _pedagogical_node)
    builder.add_node("technical", _technical_node)

    builder.set_entry_point("classify")

    builder.add_conditional_edges(
        "classify",
        _route_intent,
        {
            "pedagogical": "pedagogical",
            "technical": "technical",
        },
    )

    builder.add_edge("pedagogical", END)
    builder.add_edge("technical", END)

    return builder.compile()


# Singleton compiled graph
orchestrator_graph = build_graph()
