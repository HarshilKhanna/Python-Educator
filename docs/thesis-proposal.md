# Research Proposal and Thesis Direction

## 1. The Research Gap

Based on our comprehensive literature review across ITS, Agentic AI, and Special Education, we have identified three converging gaps in the current academic landscape:

1. **The Multi-Agent Efficacy Gap:** Architectures like CodeEdu, PersonalPlan, and DeepTutor propose multi-agent tutoring systems, but rarely *empirically test* whether the multi-agent decomposition itself improves outcomes versus a comparable single-agent baseline. DeepTutor's related-work section explicitly flags this lack of comparative evaluation as an open issue.
2. **The "Slow Learner" Gap:** Most AI tutoring literature targets "novices" broadly. Almost no work in either ITS or LLM-tutoring purposely targets **slow learners** as a defined population with adapted pedagogical strategies (scaffolding, pacing, repetition tolerance).
3. **The Intersection:** There is virtually no research at the intersection of agentic AI + Python programming education + slow learners, and even less establishing architectural extensibility for deaf learners.

## 2. Selected Thesis Direction

**Direction:** A comparative evaluation of Single-Agent vs. Multi-Agent LLM tutoring for slow learners in Python, built on an accessibility-first architectural foundation.

This direction merges the strongest empirical approach (Direction 1) with the architectural foresight of deaf-learner extensibility (Direction 3).

### 2.1 The Core Research Question
*Does isolating the learner-state diagnosis from pedagogical decision-making via a multi-agent decomposition (Diagnostic Agent → Pedagogical Agent → Content Agent) measurably improve diagnostic accuracy and hint quality compared to a single-agent monolith for slow learners?*

### 2.2 Novelty and Value
- **High Novelty:** Directly answers DeepTutor's open question on MAS efficacy while targeting an under-served population (slow learners).
- **High Research Value:** Moves beyond an engineering "system paper" (simply building an app) into empirical computer science research by generating falsifiable A/B evaluation data.
- **Architectural Extensibility:** The `LearnerModelService` content representation is built to be modality-agnostic to act as a proof-of-concept for future deaf-learner (visual/sign-language) output extensions.

## 3. Evaluation Methodology (MVP Constraints)

Since we are prioritizing **research value**, the MVP must support the following comparative protocol:

1. **System Toggling:** The system uses `backend/agent_orchestrator.py` to seamlessly toggle between the Single-Agent control group and the 3-Node experimental group. Both groups share the exact same foundation models, context windows, and tools.
2. **Diagnostic Accuracy Evaluation:** We will construct a curated set of code samples with known ground-truth misconceptions to verify if the Multi-Agent Diagnostic node outperforms the Monolith node.
3. **Hint Quality Evaluation:** Expert/rubric-based blind rating of the instructional scaffolding prompted by both systems.
4. **Small User Study (If ethics timeline permits):** Testing 10-20 participants on short-session learning gains and student satisfaction.

## 4. Division of Work (3-Person Team)

This thesis direction cleanly partitions along the 3-node architecture, allowing parallel development:

*   **Member A (Learner Modeling & Diagnostic Agent):** Owns knowledge-tracing (KT) literature, builds the `Diagnostic Agent`, manages the `LearnerModelService`, and leads the Diagnostic Accuracy ground-truth evaluation.
*   **Member B (Pedagogical & Multi-Agent Architecture):** Owns MAS literature, builds the `Pedagogical Agent` and `Content Agent`, manages the LangGraph orchestration (`agent_orchestrator.py`), and owns the A/B comparison systems design.
*   **Member C (Evaluation, Accessibility & Writing Lead):** Owns the slow-learner/deaf-learner learning sciences literature base. Designs the modality-agnostic interface, runs the Hint Quality evaluation, leads the user study, and drives the consolidation of the thesis results.
