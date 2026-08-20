# Evaluation Protocol
*Aligned to Research Direction 1 (Single vs. Multi-Agent for Slow Learners)*

Evaluating intelligent tutoring systems requires strict definitions of success. Given the constraints of an undergraduate final-year project (a 3-person team with limited time), this evaluation protocol distinguishes between what is ideal in literature and what is executable in practice.

---

## 1. The Three-Tier Evaluation Plan

We explicitly reject large-scale statistical significance claims (which require thousands of student interaction logs) due to low statistical power (small N). We will report effect sizes honestly.

Our evaluation stack falls into three focused tiers:

### Tier 1: Diagnostic Accuracy (Guaranteed Fallback 1)
**Goal:** Does the system correctly identify the actual misconception in code?
- **Methodology:** We will construct a curated offline dataset of Python code samples seeded with known, ground-truth misconceptions (e.g., confusing list index with list value).
- **Metric:** Accuracy % comparing the `Diagnostic Agent` vs. the `Monolith Agent` against the known ground-truth labels.
- **Risk:** Low risk, high rigor. Requires no live users, meaning zero ethics-board delay.

### Tier 2: Expert/Rubric-Based Hint Quality (Guaranteed Fallback 2)
**Goal:** Does the pedagogical agent produce better, more tailored scaffolding for slow learners than the baseline?
- **Methodology:** Blind A/B testing of hint generation. We will pipe the same misconceptional code state through both the Single-Agent baseline and the Multi-Agent architecture.
- **Metric:** Expert rating rubric focusing on slow-learner rules (Did it use an analogy? Was it punishing? Was it scaffolding?). Can be conducted by the team members (blinded) or volunteer CS-education-literate raters.
- **Risk:** Medium risk. Highly viable without ethics-board longitudinal tracking.

### Tier 3: Small User Study (The Stretch Goal)
**Goal:** Short-session learning gain and accessibility satisfaction.
- **Methodology:** 10–20 participants drawn from intro-level programming (representing target cognitive loads). 
- **Metrics:** 
  1. *Time-to-mastery:* Number of attempts until a cumulative concept (variables -> loops) is demonstrated reliably.
  2. *Satisfaction:* Likert-scale System Usability Scale (SUS) querying accessibility and clarity.
- **Risk:** High risk (dependent on ethics approval timeline). This will be framed as a "nice to have" capstone to the thesis if approved in time.

---

## 2. Infrastructure Setup
The backend currently supports routing directly via `agent_orchestrator.py` config flag `use_multi_agent_baseline`. 

We have initialized `backend/tests/ground_truth_misconceptions.json` to begin populating the dataset required for **Tier 1 (Diagnostic Accuracy)**, allowing the team to begin empirical testing immediately without a UI.
