# Python Educator — Monorepo

An agentic Python tutoring platform.

## Structure

```
/
├── app/        # Flutter mobile/web frontend
├── backend/    # FastAPI backend (LangGraph Agents)
└── docs/       # Architecture & design documents
```

### Key Documentation:
- [Thesis Proposal & Research Direction](docs/thesis-proposal.md)
- [System Architecture v2](docs/agentic-python-tutor-architecture-v2.md)
- [Agent Constraints](AGENTS.md)
- [MVP Specification](docs/mvp-spec.md)
- [Evaluation Protocol](docs/evaluation-protocol.md)
- [20-Week Project Roadmap](docs/project-roadmap.md)

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### App (Flutter)

```bash
cd app
flutter pub get
flutter run
```

## Health Check

Once the backend is running, visit: [http://localhost:8000/health](http://localhost:8000/health)
