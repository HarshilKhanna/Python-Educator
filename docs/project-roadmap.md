# Final Year Project (FYP) Thesis Roadmap
*20-Week Agile Schedule & Division of Labor*

This roadmap ensures the 3-person team achieves the empirical comparison (Direction 1) while balancing systems engineering, learning sciences literature, and rigorous evaluation.

---

## 1. Division of Work 

| Role | Core Responsibilities |
| :--- | :--- |
| **Member A**<br/>*(Learner Modeling & Diagnostic Agent)* | **Literature:** Owns KT/diagnostic literature (Abdelrahman/Wang Kt, "Future-Proofing Programmers").<br/>**Engineering:** Builds `Diagnostic Agent` node, `LearnerModelService`.<br/>**Evaluation:** Owns the Diagnostic-Accuracy ground-truth evaluation pipeline. |
| **Member B**<br/>*(Pedagogical & Multi-Agent Architecture)* | **Literature:** Owns MAS literature (CodeEdu, PersonalPlan, SLOW, EduPlanner).<br/>**Engineering:** Builds `Pedagogical/Content` Agents and the LangGraph orchestration (`agent_orchestrator.py`).<br/>**Evaluation:** Owns the Single-vs-Multi Agent structural comparison design. |
| **Member C**<br/>*(Evaluation, Accessibility & Writing Lead)* | **Literature:** Owns slow-learner/deaf-learner evidence base (Cheng et al. LLM personas, Kulik & Fletcher ITS evaluation).<br/>**Engineering:** Designs modality-agnostic UI/Interface layer placeholder.<br/>**Evaluation:** Runs expert hint-quality rating, leads small user study. Consolidates Thesis write-up. |

*Note: All three members must co-author Section 7 (Research Gap) — it is the intellectual core of the thesis.*

---

## 2. Recommended Reading Order

**Tier 1 — Read together, weeks 1-2 (The Foundation):**
1. Shen et al., "A Survey of Knowledge Tracing" (IEEE TLT 2024)
2. "LLM Agents for Education: Advances and Applications" (ACL Findings 2025)
3. DeepTutor (arXiv 2604.26962) — Focus on related-work section
4. Kazemitabaar et al., CHI 2023 (AI code generators & novices)
5. Batticaloa & Frontiers 2026 adaptive-scaffolding slow-learner studies

**Tier 2 — Divided by role, weeks 3-5 (The Specialization):**
* As defined in the Division of Work table above.

**Tier 3 — Nice to read later (The Periphery):**
* Robot tutoring systems review
* MU4RAAI machine unlearning paper
* DataCamp/Coursera platform documentation

---

## 3. Prerequisite Concepts (Before Writing Code)
- The 4-component ITS architecture (domain/student/pedagogical/interface).
- Performance prediction vs. diagnostic modeling.
- "Agentic" vs. Chatbots (planning, memory, tool use).
- Evidence-based slow-learner behaviors. 
- LangGraph state-machine routing.

---

## 4. 20-Week Execution Milestones

- **Weeks 1–2:** Tier 1 readings complete. Lock in Direction 1.
- **Weeks 3–5:** Tier 2 parallel readings. Draft Lit Review sections.
- **Week 6:** Consolidate Lit Review. Finalize Research Gap/Question.
- **Weeks 7–8:** Spec out Learner Model & Pedagogical Strategies on paper.
- **Weeks 9–11:** Build Single-Agent Baseline & Ground-Truth Misconceptions dataset.
- **Weeks 12–14:** Build Multi-Agent version (LangGraph routing).
- **Weeks 15–16:** Execute Diagnostic-accuracy & expert hint-quality evaluations.
- **Week 17:** Small User Study (if ethics approved).
- **Weeks 18–19:** Analysis and writing Results/Discussion chapters.
- **Week 20:** Buffer, revision, submission.

---

## 5. The Fallback Policy (Closing Note from Advisor)
If Direction 1 (empirical comparison) proves unachievable within this timeline, **do not silently revert to "we built a tutor".** Instead, explicitly report the scoping constraint: document a *"we scoped down from a comparative study to a single well-evaluated system, and here's why"* section. This framing is intellectually honest, defensible in a viva, and demonstrates research maturity. 
