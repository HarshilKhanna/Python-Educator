# Minimum Viable Prototype (MVP) Specification
*Aligned to Research Direction 1 (Single vs. Multi-Agent for Slow Learners)*

## 1. Core Mandate
This MVP is **research-value-first**. It is designed to be the exact smallest system that enables the empirical comparative evaluation laid out in the Thesis Proposal. 

## 2. IN SCOPE Requirements

### A. The Baseline vs. Experimental Orchesration
- **Single-Agent Monolith:** A fully working control grouped wrapped in one LLM node containing a massive system prompt (diagnose + instruct + generate).
- **Multi-Agent 3-Node split:** The `Diagnostic Agent`, `Pedagogical Agent`, and `Content Agent` successfully handing off context inside LangGraph.
- Both systems share the exact same tools (Python execution sandbox) and write to the same `LearnerModelService`.

### B. Curated Python Curriculum
To test the handling of cumulative concepts (and compounding gaps), the content payload must strictly walk through:
1. Variables & Mutability
2. Loops & Flow Control
3. Functions (Scope/Parameters)
4. Basic Recursion

### C. Slow-Learner Promoted Behaviors
The system prompts belonging to the `Pedagogical Agent` (and Monolith) MUST explicitly encode evidence-based slow-learner tactics:
- **Repetition Without Penalty:** Do not rush mastery. If a student fails 3 times, provide 3 different angles, but do not drop the mastery score heavily nor "fail" them out of the module.
- **Concrete before Abstract:** Force LLMs to use analogies (e.g., "Variables are like named boxes") before throwing formal computer science definitions at the user.
- **Mastery-gated Progression:** Prevent movement to Topic 2 until Topic 1 hits `0.85` mastery in the database.

### D. Deep Event Logging
- `AdaptationEvent` and `AuditLog` in the PostgreSQL database must log exactly *why* a decision was made. The `LearnerModelService` architecture already handles this transactionally.

---

## 3. EXPLICITLY OUT OF SCOPE (Do Not Build for MVP)
To guarantee the thesis is executable in the timeframe of an undergraduate project, the following are strictly disabled for the prototype phase:

1. **Deaf-Learner Specific Output (Sign Language Generation):** The architecture guarantees that the content output is abstracted enough to handle this later. But for MVP, DO NOT build sign-language generation avatars. Just leave UI placeholders.
2. **Local/Offline Open-Weight LLMs (Qwen/Gemma):** We will use high-capacity cloud APIs (GPT-4o or Claude) to remove "model capability" as a failure point while testing the architectural decomposition. Local models are a stretch goal.
3. **Statistical Knowledge Tracing (DKT/BKT):** We do not have 10,000 students to train a deep knowledge tracing model. KT is handled via **LLM-based qualitative diagnosis** of code logic holes exclusively.
