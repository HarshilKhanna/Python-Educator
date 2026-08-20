# Agentic AI-Based Adaptive Python Tutor
## System Architecture & Research Design Document — v2

Role assumed: Principal Software Architect / AI Systems Engineer / EdTech Research Consultant.

---

## 0. Thesis & Primary Research Question

**The Core System Thesis:**
> A transparent learner model — combining knowledge tracing, confidence estimation, a prerequisite-aware curriculum graph, and explainable decision-making — generates and justifies personalized interventions for slow learners in introductory Python.

**The Empirical Research Question (Section 6.4 & 7):**
> *Does multi-agent decomposition measurably improve diagnostic accuracy and hint quality for slow learners compared to a single-agent baseline using the exact same LLM, tasks, and prompt budget?*

Anyone can build an AI tutor with an LLM and RAG. The research contribution here is twofold: 
1. The **decision layer**: *why* the system recommends a topic and *how* it adapts to the slow learner (pace and teaching style).
2. The **architectural evaluation**: A rigorous A/B comparison challenging the current literature's unproven assumption that Multi-Agent Systems are inherently superior to Single-Agent prompting.

**Staging, not a single target:** this is engineered in three distinct phases...

---

## 1. Overall Architecture (System Context)

```
┌─────────────────────────┐        ┌──────────────────────────┐
│   Flutter Student App    │        │  React/TS Instructor Web  │
└────────────┬─────────────┘        └─────────────┬─────────────┘
             │  HTTPS / WebSocket                   │ HTTPS
             ▼                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                     │
└───────┬───────────────┬───────────────┬───────────────────────┘
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌─────────────┐ ┌──────────────────────┐
│ Core Domain    │ │ Agent        │ │ Analytics /           │
│ Services       │ │ Orchestration│ │ Explainability Service│
│ (content,      │ │ (LangGraph,  │ │ (reads adaptation_    │
│ quiz, curric.) │ │ 3 nodes only)│ │  events / audit_log)  │
└───────┬────────┘ └──────┬───────┘ └──────────┬─────────────┘
        │                 │                     │
        └─────────┬───────┘                     │
                   ▼                             │
        ┌───────────────────────┐                │
        │   LearnerModelService   │◄──────────────┘
        │  (sole write path to     │
        │   mastery/confidence/    │
        │   style — validates,     │
        │   versions, logs)        │
        └───────────┬─────────────┘
                     ▼
        ┌───────────────────────────┐
        │ PostgreSQL: mastery tables  │
        │ + adaptation_events (append)│
        │ + audit_log (append)         │
        └───────────────────────────┘
```

**Key discipline (unchanged from v1, now structurally enforced rather than just conventional):** the Agent Orchestration layer is a sibling of Core Domain, not a wrapper around it — and *every* writer of learner state, whether an agent, a background KT job, a tone classifier, or an instructor's manual override, goes through `LearnerModelService`. There is no second write path to mastery/confidence tables. This single rule is what makes explainability and auditability actually true rather than aspirational.

---

## 2. Component Diagram

```
api-gateway
 ├─ auth (JWT, RBAC)
 ├─ students-bff
 └─ instructor-bff

core-domain (FastAPI service, hexagonal)
 ├─ curriculum domain (curriculum DAG — see §4)
 ├─ content/quiz domain
 ├─ revision/spaced-repetition domain
 └─ ports: LearnerModelService client, EventPublisher

learner-model-service   ◄── promoted to first-class component (see §5)
 ├─ write API: recordUpdate(source, signal, delta)
 ├─ conflict resolution (instructor override > algorithmic estimate)
 ├─ versioning (event-sourced; mastery/confidence are materialized views)
 └─ emits: adaptation_events, audit_log

agent-orchestration (LangGraph runtime — 3 nodes)
 ├─ graph router (conditional edge, not a distinct LLM node)
 ├─ diagnostic/learner-state agent node
 ├─ pedagogical/tutoring agent node
 ├─ content/exercise agent node
 └─ tools (not graph nodes):
     ├─ RAG retriever tool
     ├─ tone/frustration classifier tool  (was: Empathy Agent)
     ├─ python execution sandbox (for diagnostic agent)
     ├─ KT update tool → LearnerModelService
     └─ learner-model read tool → LearnerModelService

rag-service
 ├─ ingestion pipeline
 ├─ retriever (pgvector + rerank)
 └─ citation resolver

analytics-explainability
 ├─ decision-trace reader (adaptation_events)
 ├─ cohort aggregation jobs
 └─ cost/usage monitor
```

---

## 3. AI Architecture — Three Agents, Everything Else Is a Tool or Service

The bar for "this deserves to be a LangGraph node with its own reasoning turn" is: *does it need autonomous multi-step reasoning over conversational context?* Judged against Section 6.3 of the Literature Review:

| Component | v2 status | Why |
|---|---|---|
| **Diagnostic/Learner-State** | **Agent** | Inferring misconceptions requires specialized KT-style reasoning over code submissions and errors. |
| **Pedagogical/Tutoring** | **Agent** | Multi-signal reasoning (mastery + curriculum graph + style) to decide instructional action (how to respond). |
| **Content/Exercise** | **Agent** | Generates or selects practice items dynamically to match pace, requiring specific evaluation loop. |
| Orchestrator | **Router Edge** | Routing should be structural/conditional edges in LangGraph, not a dedicated LLM node that adds latency. |
| UI/Greeting/Motivation | **Anti-Pattern** | These are responsibilities to be folded into Pedagogical and Interface layers, not separate reasoning modes. |
| Empathy / Frustration | **Tool** | Stateless classifier call per turn, output written to LearnerModelService. |
| Knowledge-Tracing Updater | **Service function** | Deterministic graph update; explicitly modeled as a service called via `LearnerModelService`. |

### Agent Interaction (per turn)

```
Student message
   │
   ▼
Router (Conditional Edge) 
   │
   ├─(code review/debugging)──► Diagnostic Agent (reasons over code, infers KT gaps)
   │                                  │
   │                                  ▼
   │                            (Writes diagnosis to LearnerModelService)
   │
   ├─(needs instruction)──────► Pedagogical Agent (decides *how* to teach via Socratic/Scaffold actions)
   │
   └─(needs practice)─────────► Content Agent (finds/generates precise python problem)
```

### 3.1 The Single-Agent Baseline (The Control Group for Section 6.4)
To answer our empirical research question, the architecture must support a **Single-Agent Baseline Mode**. 
- The single agent receives the concatenated prompts of the Diagnostic, Pedagogical, and Content agents. 
- It is given the same exact context window, the same underlying model (e.g., GPT-4o or Claude 3.5 Sonnet), and the same access to the Python Sandbox tools and `LearnerModelService`.
- A configuration flag (e.g., `USE_MULTI_AGENT=true|false`) at the LangGraph Router dictates whether the graph branches out to the 3-node decomposition or funnels everything into the Monolith Agent. 
- This ensures the evaluation tests strictly the *architectural decomposition*, not prompt engineering or model differences.

Every arrow into `LearnerModelService` looks identical regardless of caller — that uniformity is the whole point.

---

## 4. Curriculum Graph (promoted to first-class component)

This existed in v1 as a schema detail (`topics.prerequisite_topic_ids[]`); it's promoted here because it's one of the two things (alongside the learner model) the entire system is actually organized around.

```
Variables → Operators → Conditionals → Loops → Functions → Lists → Strings → Files → OOP → Recursion
                                          │
                                          └──► (branch) Nested Loops → prerequisite for Recursion
```

- Stored as a DAG (`topics` table, `prerequisite_topic_ids[]`), not a flat list.
- The Pedagogical Agent navigates this graph as its source of truth for sequencing — mastery drops on a downstream topic propagate a "check prerequisite" signal backward through the graph (this is the graph-based KT augmentation from v1 §4, now explicitly tied to this component rather than buried in the KT section).
- Curriculum authors (instructors) edit the graph via the dashboard; edits are versioned like everything else touching the learner model's frame of reference, since changing prerequisites retroactively changes what a given mastery vector *means*.

---

## 5. LearnerModelService (new central component)

This is the actual heart of the system per the thesis in §0. Responsibilities:

- **Sole write path.** `recordUpdate(source, student_id, topic_id, signal, delta)` is the only way mastery, confidence, or style fields change. Pedagogical Agent, Technical Agent (indirectly, via KT tool), the tone classifier, and instructor manual overrides all call the same method.
- **Validation.** Enforces invariants once: mastery ∈ [0,1], confidence updates bounded per-call, instructor overrides tagged `source=instructor_override` and given priority weight until new evidence accumulates.
- **Event-sourced versioning.** Every `recordUpdate` call first appends to `adaptation_events` (immutable), then updates a materialized `mastery`/`confidence`/`style` table transactionally. This gets "what did the learner model look like at time T" almost for free — replay events up to T rather than maintaining a separate snapshot mechanism.
- **Audit log.** Every write, human or agent-originated, also lands in `audit_log` with before/after state — this is what answers "why" for the explainability dashboard without needing to interrogate an LLM after the fact.
- **Conflict resolution.** Central place for the "override outranks algorithm until contradicted" rule — previously implied, now enforced in exactly one function instead of duplicated across write paths.

**Deployment shape (deliberate, not default):** in-process library shared by `core-domain` and `agent-orchestration` for the prototype — same deployable, no network hop, one code path. It only becomes a candidate for a standalone networked service once `agent-orchestration` is split out for independent horizontal scaling (see §17 of v1 roadmap), at which point it sits behind the same internal API agents already call. Don't take the network-service step early; it adds latency and a second failure mode for no benefit at prototype/pilot scale.

**Why this matters for research, concretely:** running two KT algorithms in shadow mode (e.g., BKT vs. an experimental DKT variant) means the experimental component just calls `recordUpdate` with `source=dkt_experimental` behind a flag, and you diff the resulting event streams for evaluation — no schema changes, no logging code duplicated, no risk of the experimental path silently skipping the audit trail.

---

## 6. Learner Model — Expanded Fields

Beyond mastery/confidence/mistake-history/velocity/revision-schedule (v1 §4), add an explicit **style profile**, since adaptation isn't only difficulty:

- `preferred_explanation_style`: worked-example vs. formal-definition-first vs. analogy-driven
- `uses_analogies_well`: inferred from engagement/success after analogy-based explanations
- `visual_preference`: inferred from engagement with diagram-augmented vs. text-only content
- `repetition_need`: how many exposures before mastery typically stabilizes for this student
- `response_verbosity_preference`: short/direct vs. detailed explanations
- `average_reading_time`: informs pacing, not just content selection

These are **inferred over time from behavior**, not self-reported at onboarding — asking a struggling student to accurately self-assess their own learning style tends to produce noisy, unreliable signal. All writes to these fields go through `LearnerModelService` like everything else, tagged with their inferring source, so a research question like "does inferred visual-preference correlate with mastery velocity" is answerable directly from the event log.

---

## 7. Everything Else (RAG, KT algorithm choice, DB schema shape, deployment, security, roadmap)

Unchanged from v1 — those sections (RAG pipeline, BKT+graph-hybrid KT recommendation, Flutter/React/backend architecture, deployment path, security considerations, scalability roadmap) hold. The changes in this revision are scoped specifically to: agent count, the introduction of `LearnerModelService` as the mandatory write boundary, promotion of the curriculum graph to a first-class component, and the expanded style-profile fields. Refer to v1 (`agentic-python-tutor-architecture.md`) for the full detail on those unchanged sections — this document should be read as a diff plus the consolidated reasoning above, not a full restatement.

---

## Summary of What Changed from v1 → v2

| Area | v1 | v2 |
|---|---|---|
| Agent count | 6 nodes | **3 nodes** (Orchestrator, Pedagogical, Technical) — rest are tools/services |
| Empathy | Standalone agent | **Classifier tool**, writes to learner model |
| Assessment Generation | Standalone agent | **Tool** invoked by Pedagogical |
| KT Updater | "Agent" (non-conversational) | **Service function** via LearnerModelService |
| Learner state writes | Multiple use-cases, convention-enforced logging | **Single `LearnerModelService`**, structurally enforced, event-sourced, versioned |
| Curriculum graph | Schema detail | **First-class component**, source of truth for Pedagogical sequencing |
| Learner model fields | mastery, confidence, mistakes, velocity, revision | **+ style profile** (explanation style, visual/analogy preference, repetition need, verbosity, reading time) |
| Framing | "Production-ready" architecture | **Research Prototype → Pilot → Production**, explicit staged goals |
| Central thesis | Implicit in the tech choices | **Explicit**: transparent learner model is the research contribution; everything else is infrastructure |

