# Backend — FastAPI

Minimal FastAPI service for the Python Educator platform.

## Setup

```bash
# Create a virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run (development)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

| Method | Path      | Description            |
|--------|-----------|------------------------|
| GET    | `/health` | Service health check   |
| GET    | `/docs`   | Swagger UI (auto-gen)  |
| GET    | `/redoc`  | ReDoc UI (auto-gen)    |
