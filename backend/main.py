"""
main.py — FastAPI application entry point.

Schema is owned by Alembic — run `alembic upgrade head` (or `python seed.py`)
before starting the server for the first time.
"""
from __future__ import annotations

import contextlib
import json
import logging
import logging.config
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

import config
from database import engine
from middleware.logging_middleware import RequestLoggingMiddleware
from routers import activities, answers
from routers.auth import router as auth_router
from routers.tutor import router as tutor_router
from routers.review import router as review_router
from routers.materials import router as materials_router
from routers.students import router as students_router
from routers.monitoring import router as monitoring_router

# ---------------------------------------------------------------------------
# Logging setup — structured JSON to stdout
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # raw JSON lines from RequestLoggingMiddleware
)
logger = logging.getLogger("api")


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is managed by Alembic — run `alembic upgrade head` before starting.
    # Nothing to do at startup beyond letting the engine pool initialise lazily.
    yield
    # Dispose engine on shutdown
    await engine.dispose()


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Python Educator API",
    description="Agentic Python tutoring backend",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware — order matters: logging outermost, then CORS
# ---------------------------------------------------------------------------

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler
#
# In dev: lets FastAPI's default handler surface the full traceback.
# Outside dev: returns a generic error to the client; always logs the full
# traceback with request context server-side so nothing is lost.
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    tb = traceback.format_exc()

    # Always log the full traceback
    logger.error(
        json.dumps(
            {
                "event": "unhandled_exception",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "error": type(exc).__name__,
                "detail": str(exc),
                "traceback": tb,
            }
        )
    )

    # In dev: re-raise so FastAPI's debug output is visible
    if config.APP_ENV == "dev":
        raise exc

    # Outside dev: generic client response — no internals leaked
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "request_id": request_id},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(activities.router)
app.include_router(answers.router)
app.include_router(tutor_router)
app.include_router(review_router)
app.include_router(materials_router)
app.include_router(students_router)
app.include_router(monitoring_router)


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health() -> dict:
    """Liveness — confirms the process is up. Always returns 200 while running."""
    return {"status": "ok", "service": "python-educator-api"}


@app.get("/ready", tags=["Health"])
async def ready() -> JSONResponse:
    """Readiness — checks DB connectivity. Returns 503 if DB is unreachable."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return JSONResponse(content={"status": "ready"})
    except Exception as exc:
        logger.warning(json.dumps({"event": "readiness_check_failed", "error": str(exc)}))
        return JSONResponse(status_code=503, content={"status": "unavailable", "detail": "database unreachable"})
