# AGENTS.md — Hard Constraints for Every Session

> Full architecture detail: [docs/agentic-python-tutor-architecture-v2.md](docs/agentic-python-tutor-architecture-v2.md)

---

## Agent Count — Exactly 3 LangGraph Nodes

**Alignment with Literature Review (Section 6: Agentic AI Trade-offs):**
To align our V2 architecture with the theoretical separation discussed in the literature (e.g., SLOW framework's separation of learner-state inference from instructional action selection), we constrain our Multi-Agent System (MAS) to the following targeted roles:

| Component | Status | Literature Role Mapping & Justification |
|---|---|---|
| **Diagnostic/Learner-State** | Agent (graph node) | Reasons over code submissions, chat history, and error patterns to infer specific misconceptions (KT-style reasoning). |
| **Pedagogical/Tutoring** | Agent (graph node) | Decides *how* to respond given the diagnosis (Socratic, worked example, repetition) based on slow-learner strategies. |
| **Content/Exercise** | Agent (graph node) | Generates or selects the next practice item at the right difficulty and pace. |

**What is NOT a separate agent (Rule: Responsibilities != distinct reasoning tasks):**
- **UI Agent** (Should be handled by the interface layer)
- **Motivation/Gamification Agent** (Should live inside the Pedagogical Agent's prompt)
- **Greeting Agent** (Should live inside the Pedagogical Agent or simple interface logic)
- **Orchestrator** (Relegated to a non-agentic structural router/conditional edge in LangGraph, rather than a distinct reasoning LLM)

| Sub-system | Implementation |
|---|---|
| Tone/frustration classifier | **Tool** (stateless) |
| KT updater | **Service function** (Write path into `LearnerModelService`) |

**Rule:** Do not add a fourth graph node without explicit approval. Doing so violates the latency/cost/complexity trade-offs outlined in Literature Review Section 6.2.

---

## When Agentic / Multi-Agent Design Provides Real Value (Section 6.1)
**Architectural Constraints:**
1. **Different Reasoning Modes:** We separate the Diagnostic node (inferring *what* the student misunderstands via code) from the Pedagogical node (deciding *how* to explain it using slow-learner strategies).
2. **Distinct Context Windows/Tools:** The Diagnostic node requires execution sandbox tools and error trace contexts, whereas the Pedagogical node requires the Curriculum Graph, Style Profile, and LearnerModelService context.

## When It Does NOT Help (Anti-Patterns & Engineering Trade-offs - Section 6.2)
To prove this architecture is engineered, not just academic, the following strict rules apply to avoid unnecessary complexity:

1. **NO Decomposition Theater:** 
   - If two "agents" would share near-identical prompts/context and could be trivially squashed into one API call with a longer system prompt, **do not separate them.** 
   - We must justify every split. (e.g., Content generation is just a tool call, *not* a standalone agent, because its prompt relies on the exact same context the Pedagogical agent already holds).

2. **NO Strictly Sequential, Stateless Agent Chains:** 
   - If Agent A always feeds Agent B exactly once, with no branching and no re-invocation memory, they must be merged into a single prompt or a direct function-calling pipeline.
   - *Example:* Tone classification is an isolated, sequential pass. We explicitly model it as a stateless `Tool` call returning into `LearnerModelService`, rather than an agent node, for this very reason.

3. **Latency, Cost, and User Friction (The Trade-off Rule):** 
   - We are building for slow learners who need immediate, low-friction feedback. Every extra agent hop adds inference time and token cost. 
   - **Constraint:** The LangGraph state machine must never exceed a depth of 3 sequential autonomous LLM hops for a single user turn. If a response requires 4 hops, the orchestrator logic must be refactored to parallelize or merge nodes. The final thesis will explicitly cite this latency cap as a weighed engineering trade-off.

Do not add a fourth graph node without explicit approval.

---

## Single Write Path — LearnerModelService

**All** writes to mastery, confidence, and style fields must go through
`LearnerModelService.recordUpdate(source, student_id, topic_id, signal, delta)`.
No exceptions — not agents, not background jobs, not instructor overrides.
This rule is what makes explainability structurally true rather than aspirational.

---

## Tech Stack

- **Frontend:** Flutter mobile app (students) · React/TS web (instructors)
- **Backend:** FastAPI (API gateway + core domain + agent orchestration)
- **Database:** PostgreSQL — mastery tables + `adaptation_events` (append-only) + `audit_log` (append-only)
- **Agent runtime:** LangGraph · RAG via pgvector + rerank

---

## Current Phase: Research Prototype

- Small cohort only.
- Manual-approval defaults for agent-generated interventions.
- Goal: prove the learner-model + explainability loop works — not production scale.
- Staged path: **Research Prototype → Pilot → Production**. Do not over-engineer for later stages.
