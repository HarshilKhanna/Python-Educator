# Python Educator — Agentic Python Tutor

> A research prototype of an **agentic, adaptive tutoring system** for Python learners.
> Built with FastAPI, LangGraph multi-agent orchestration, RAG over a course handbook, a Flutter student app, and a React/Vite instructor dashboard.

---

## Table of Contents

1. [What This Is](#1-what-this-is)
2. [Architecture Overview](#2-architecture-overview)
3. [Tech Stack](#3-tech-stack)
4. [Repository Layout](#4-repository-layout)
5. [Prerequisites](#5-prerequisites)
6. [Quick Start — Docker](#6-quick-start--docker)
7. [Local Development — No Docker](#7-local-development--no-docker)
8. [Environment Variables](#8-environment-variables)
9. [API Reference](#9-api-reference)
10. [End-to-End Walkthrough](#10-end-to-end-walkthrough)
11. [Running the Tests](#11-running-the-tests)
12. [Instructor Dashboard](#12-instructor-dashboard)
13. [Design Decisions](#13-design-decisions--engineering-trade-offs)
14. [Roadmap](#14-whats-next--staged-roadmap)

---

## 1. What This Is

**Python Educator** is a research prototype of an **agentic intelligent tutoring system (ITS)** targeting slow or struggling Python learners. It combines:

- A **Learner Model** that tracks per-topic mastery and confidence with a strict single-write-path guarantee
- A **RAG pipeline** that chunks the course handbook by subsection heading and retrieves grounded context for every tutoring response
- A **3-node LangGraph Multi-Agent System** (Technical Agent, Pedagogical Agent, Orchestrator) that separates knowledge retrieval from pedagogical decision-making
- A **risk policy** and **manual review queue** so instructors approve high-stakes adaptations before they reach students
- An **Instructor Dashboard** (React/Vite) for monitoring, reviewing adaptations, and uploading supplementary materials
- A **Flutter student app** that consumes the API

The system is scoped as a **research prototype** — not a production service. The architecture is intentionally constrained to remain legible and auditable.

---

## 2. Architecture Overview

```
Student Turn  (Flutter app  -->  POST /tutor/chat)
                       |
            [Orchestrator Node]
            heuristic intent classifier
                       |
          _____________|_____________
         |                           |
 [Technical Agent]         [Pedagogical Agent]
  RAG retrieval               Reads LearnerModel
  + grounded LLM              Decides next activity
  answer                      type and difficulty
         |                           |
          ___________________________
                       |
            [Risk Policy — stateless]
            auto-approve / queue for review
                       |
            [LearnerModelService]   <-- ONLY write path to mastery
                       |
            [PostgreSQL + pgvector]
             mastery  events  RAG chunks
             audit_log  review queue
```

### The 3 LangGraph Nodes

| Node | Role | Context / Tools |
|---|---|---|
| **Orchestrator** | Heuristic intent classifier — routes to Technical or Pedagogical | Regex patterns; no LLM call |
| **Technical Agent** | Answers Python questions grounded in retrieved handbook chunks | `rag.retrieve()`, GPT-4o-mini |
| **Pedagogical Agent** | Decides *how* to respond and which activity to assign next | LearnerModelService, Curriculum Graph, Style Profile |

> **Intentional constraint:** The Orchestrator is a structural router (a conditional edge in LangGraph), not a fourth reasoning LLM. Adding a fourth node requires explicit architectural justification per `AGENTS.md`.

### Single Write Path

All writes to `mastery`, `confidence`, and `adaptation_events` flow exclusively through:

```python
LearnerModelService.record_update(source, student_id, topic_id, signal, delta)
```

Every write is mirrored to an append-only `audit_log` row. No agent, background job, or instructor override can bypass this. Explainability is a structural property — not an aspiration.

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Student app | Flutter (Dart) + Riverpod |
| Instructor dashboard | React 18 + Vite |
| API gateway | FastAPI 0.111+ (async) |
| Agent runtime | LangGraph 0.2+ / LangChain Core |
| LLM | OpenAI GPT-4o-mini |
| RAG embeddings | sentence-transformers (local, CPU-friendly) |
| Vector store | PostgreSQL 16 + pgvector |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Containers | Docker + Docker Compose |
| Tests | pytest + pytest-asyncio + httpx (42 tests, SQLite in-memory) |

---

## 4. Repository Layout

```
python-educator/
├── app/                         Flutter student app
│   └── lib/
│       ├── widgets/             ActivityCard, DifficultyBadge, ...
│       └── main.dart
│
├── backend/                     FastAPI backend (all server-side logic)
│   ├── agents/
│   │   ├── technical.py         Technical Agent node (RAG + LLM)
│   │   ├── pedagogical.py       Pedagogical Agent node
│   │   └── orchestrator.py      LangGraph StateGraph + heuristic router
│   ├── alembic/
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── middleware/
│   │   └── logging_middleware.py   Structured JSON access logs
│   ├── routers/
│   │   ├── auth.py              POST /auth/register, /auth/login
│   │   ├── activities.py        GET /activities
│   │   ├── answers.py           POST /answer  (single write path entry)
│   │   ├── tutor.py             POST /tutor/chat  (agent orchestration)
│   │   ├── review.py            GET/POST /review  (instructor queue)
│   │   ├── materials.py         POST /materials/upload
│   │   ├── students.py          GET /students/{id}/mastery
│   │   └── monitoring.py        GET /monitoring/*
│   ├── services/
│   │   ├── learner_model.py     LearnerModelService -- ONLY write path
│   │   └── monitoring.py        Analytics service
│   ├── tests/                   42 tests
│   ├── config.py                Centralised env config (dotenv)
│   ├── database.py              Async SQLAlchemy engine + session factory
│   ├── models.py                ORM models
│   ├── rag.py                   Chunking, embedding, retrieve()
│   ├── risk_policy.py           Auto-approve / manual-review decision logic
│   ├── seed.py                  Idempotent seed (migrations + demo accounts)
│   ├── main.py                  App factory, middleware, health endpoints
│   ├── Dockerfile               Multi-stage build
│   └── requirements.txt
│
├── instructor-dashboard/        React/Vite instructor web UI
│   └── src/components/          ReviewQueue, MonitoringDashboard, UploadPanel
│
├── docs/handbook/               Course handbook .md files (RAG source)
├── content/uploads/             Instructor-uploaded files (volume-mounted)
├── docker-compose.yml
└── .gitignore
```

---

## 5. Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Docker Desktop | 4.x+ | Required for the Docker quick-start |
| Docker Compose | v2 (bundled) | |
| Python | 3.11+ | Local dev only |
| Node.js | 18+ | Instructor dashboard only |
| Flutter SDK | 3.x+ | Student app only |
| OpenAI API key | any | Optional — agents degrade gracefully without it |

---

## 6. Quick Start — Docker

### Step 1 — Clone and configure

```bash
git clone <repo-url>
cd python-educator
cp backend/.env.example backend/.env.dev
```

Open `backend/.env.dev` and set at minimum:

```env
APP_ENV=dev
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/python_educator
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_hex(32))">
OPENAI_API_KEY=sk-...
```

### Step 2 — Build and start

```bash
docker-compose up --build
```

> **First build note:** Downloads PyTorch (~530 MB) and Nvidia cuDNN (~360 MB) for
> sentence-transformer embeddings. Subsequent starts use the Docker layer cache and are fast.

Wait for the line:
```
backend  | INFO:     Application startup complete.
```

### Step 3 — Seed the database

In a second terminal:

```bash
docker-compose exec backend python seed.py
```

This will:
- Run `alembic upgrade head` (applies all migrations including pgvector)
- Chunk and embed the course handbook into the vector store
- Create demo accounts:
  - Instructor: `instructor@demo.com` / `password123`
  - Student: `student@demo.com` / `password123`

### Step 4 — Verify

```bash
curl http://localhost:8000/health
# {"status": "ok", "service": "python-educator-api"}

curl http://localhost:8000/ready
# {"status": "ready"}
```

Interactive API docs: **http://localhost:8000/docs**

---

## 7. Local Development — No Docker

### Step 1 — Python environment

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Step 2 — Start Postgres (keep Docker db service running)

```bash
docker-compose up db
```

### Step 3 — Configure

```bash
cp .env.example .env.dev
```

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/python_educator
APP_ENV=dev
SECRET_KEY=any-local-dev-string
OPENAI_API_KEY=sk-...
```

### Step 4 — Migrate and seed

```bash
alembic upgrade head
python seed.py
```

### Step 5 — Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 8. Environment Variables

| Variable | Required | Description |
|---|---|---|
| `APP_ENV` | yes | `dev`, `staging`, or `pilot` |
| `DATABASE_URL` | yes | SQLAlchemy async URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | yes | JWT signing secret. Must be changed in staging/pilot. |
| `OPENAI_API_KEY` | no | GPT-4o-mini key. Agents return a safe fallback if blank. |
| `STUDENT_TOKEN_EXPIRE_MINUTES` | no | Default: 480 (8 h) |
| `INSTRUCTOR_TOKEN_EXPIRE_MINUTES` | no | Default: 240 (4 h) |

---

## 9. API Reference

Full interactive docs at `/docs` (Swagger UI) or `/redoc`.

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | none | Register (`role`: `student` or `instructor`) |
| POST | `/auth/login` | none | Returns JWT access token |

### Student Flow

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/activities` | none | List activities. Filter by `?topic_id=loops` |
| POST | `/answer` | Student JWT | Submit answer. `student_id` from JWT — cannot be spoofed. Triggers `LearnerModelService`. |
| POST | `/tutor/chat` | Student JWT | Free-text or "give me next activity" — routed through the 3-node agent graph |
| GET | `/students/{id}/mastery` | JWT | Per-topic mastery + last 10 events with human-readable reasons |

### Instructor Flow

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/review/pending` | Instructor JWT | Adaptations awaiting manual review |
| POST | `/review/{id}/approve` | Instructor JWT | Approve an adaptation |
| POST | `/review/{id}/reject` | Instructor JWT | Reject with a reason — mastery unchanged, audit preserved |
| POST | `/materials/upload` | Instructor JWT | Upload PDF/DOCX/MD — chunked and embedded into RAG store |
| GET | `/monitoring/overview` | Instructor JWT | Cohort-level mastery stats |
| GET | `/monitoring/at-risk` | Instructor JWT | Students below mastery threshold |

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness — always 200 while the process is alive |
| GET | `/ready` | Readiness — 200 if DB reachable, 503 otherwise |

---

## 10. End-to-End Walkthrough

### 1 — Login

```bash
# Get instructor token
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"instructor@demo.com","password":"password123"}'
# Copy access_token -> INSTRUCTOR_TOKEN

# Get student token
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@demo.com","password":"password123"}'
# Copy access_token -> STUDENT_TOKEN
```

### 2 — Fetch activities

```bash
curl "http://localhost:8000/activities?topic_id=loops"
# Note an activity "id" and its "correct_answer"
```

### 3 — Submit a correct answer

```bash
curl -X POST http://localhost:8000/answer \
  -H "Authorization: Bearer <STUDENT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"activity_id":"<ID>","submitted_answer":"<CORRECT>"}'
# {"mastery": 0.1, "correct": true, "explanation": "..."}
```

### 4 — Ask the tutor a Python question (Technical Agent)

```bash
curl -X POST http://localhost:8000/tutor/chat \
  -H "Authorization: Bearer <STUDENT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the difference between a for loop and a while loop?","topic_id":"loops"}'
# RAG-grounded answer citing only course material
```

### 5 — Request the next activity (Pedagogical Agent)

```bash
curl -X POST http://localhost:8000/tutor/chat \
  -H "Authorization: Bearer <STUDENT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"message":"give me the next activity","topic_id":"loops"}'
# Pedagogical Agent selects type + difficulty based on mastery level
```

### 6 — Upload instructor supplementary material

```bash
curl -X POST http://localhost:8000/materials/upload \
  -H "Authorization: Bearer <INSTRUCTOR_TOKEN>" \
  -F "file=@/path/to/notes.pdf" \
  -F "topic_id=loops"
# Chunked + embedded with source_type=instructor_upload
# Students asking about "loops" will now have your notes cited
```

### 7 — Check student mastery

```bash
curl "http://localhost:8000/students/<STUDENT_ID>/mastery" \
  -H "Authorization: Bearer <INSTRUCTOR_TOKEN>"
# {mastery: [{topic_id, mastery_level, confidence}], recent_events: [...]}
```

### 8 — Review and act on pending adaptations

```bash
# View queue
curl "http://localhost:8000/review/pending" \
  -H "Authorization: Bearer <INSTRUCTOR_TOKEN>"

# Approve
curl -X POST "http://localhost:8000/review/1/approve" \
  -H "Authorization: Bearer <INSTRUCTOR_TOKEN>"

# Reject with reason (mastery NOT changed — verifiable)
curl -X POST "http://localhost:8000/review/1/reject" \
  -H "Authorization: Bearer <INSTRUCTOR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Needs more practice examples first"}'
```

### 9 — Verify the audit trail in Postgres

```bash
docker-compose exec db psql -U postgres -d python_educator \
  -c "SELECT id, student_id, before_state, after_state FROM audit_log ORDER BY id DESC LIMIT 5;"
```

### 10 — Deliberate breakage test (readiness vs liveness)

```bash
docker-compose stop db

curl http://localhost:8000/ready
# HTTP 503  {"status": "unavailable", "detail": "database unreachable"}

curl http://localhost:8000/health
# HTTP 200  {"status": "ok"}   (process is alive)

docker-compose start db

curl http://localhost:8000/ready
# HTTP 200  {"status": "ready"}   (auto-recovers)
```

---

## 11. Running the Tests

No Docker or Postgres required. Tests use an in-memory SQLite database.

```bash
cd backend
python -m pytest tests/ -v
```

Expected: **42 passed**

| Test file | What it covers |
|---|---|
| `test_auth.py` | Registration, login, JWT, cross-student/cross-role access rejection |
| `test_integration.py` | Full answer-submission loop: DB verification of mastery + audit_log |
| `test_learner_model.py` | `LearnerModelService` mastery arithmetic, audit trail integrity |
| `test_rag.py` | Retrieval with and without `topic_id` filter |
| `test_technical.py` | Technical Agent grounding (mocked LLM), not-in-material fallback |
| `test_pedagogical.py` | Pedagogical Agent decision logic |
| `test_risk_policy.py` | Auto-approve vs. manual-review thresholds |
| `test_auto_approval.py` | Auto-approval edge cases |
| `test_materials.py` | Instructor material upload + RAG ingestion |
| `test_students.py` | Mastery endpoint shape, reject-with-reason mastery invariant |

---

## 12. Instructor Dashboard

React/Vite dashboard at `instructor-dashboard/`.

```bash
cd instructor-dashboard
npm install
npm run dev
# Opens at http://localhost:5173
```

**Features:**
- **Review Queue** — Approve or reject pending adaptations with one click, with optional reason
- **Monitoring Overview** — Cohort-wide mastery stats per topic
- **At-Risk Students** — Students below threshold, sortable by topic
- **Upload Materials** — Drag-and-drop PDF/DOCX/Markdown into the RAG store per topic

The dashboard proxies API calls to `http://localhost:8000` via `vite.config.js`.

---

## 13. Design Decisions & Engineering Trade-offs

### Why exactly 3 agent nodes?

The SLOW framework and Knowledge Tracing literature justify separating
*learner-state inference* from *instructional action selection*:

- **Technical** answers *what* the student asked — grounded only in course material
- **Pedagogical** decides *how* to respond and *what* to assign next
- **Orchestrator** routes without an LLM call — zero added latency or token cost

The system hard-caps at **3 sequential LLM hops per student turn**. A 4th node needs explicit justification; adding one without it violates the latency/cost trade-off documented in the architecture notes.

### Why a single write path?

Explainability in ITS is typically aspirational. By routing every mastery write through one function, it becomes a structural property: query `audit_log` and you have the complete trace. No agent, background job, or endpoint can bypass it.

### Why RAG instead of fine-tuning?

Course material changes every semester. RAG keeps the knowledge store current without retraining. The Technical Agent is strictly forbidden from answering outside retrieved context — preventing confident hallucinations, which are more harmful to learners than an honest "I don't know."

### Why manual review by default?

This is a research prototype targeting slow learners who need low-friction but **safe** feedback. The risk policy auto-approves low-risk adaptations (small deltas, mid-range mastery) and queues the rest for an instructor. This is an explicit, documented engineering trade-off — not a limitation.

### Why SQLite for tests?

Tests run without Postgres or Docker. SQLAlchemy abstracts the difference safely for business logic. pgvector-specific SQL is isolated to migrations and tested separately against a real Postgres instance.

---

## 14. What's Next — Staged Roadmap

| Stage | Goal |
|---|---|
| Research Prototype (now) | Prove the learner-model + explainability loop on a small cohort |
| Pilot | Real students. Automated approval for calibrated mastery bands. More curriculum topics. |
| Production | Multi-tenancy, CI/CD pipeline, LLM cost monitoring, FERPA compliance |

Near-term items:

- [ ] Knowledge Tracing (BKT or DKT) to replace the linear delta model
- [ ] Student frustration/affect classifier as a stateless Tool (tone signal feeds `LearnerModelService`)
- [ ] Flutter: offline-first answer submission with background sync
- [ ] Alembic migration CI check — fail PRs that cause schema drift

---

## Tear Down

```bash
# Remove containers AND wipe the database volume
docker-compose down -v

# Remove containers but preserve data
docker-compose down
```

---

*Built as a research prototype demonstrating that agentic AI can provide meaningful,
explainable tutoring support for slow Python learners — without sacrificing engineering discipline.*
