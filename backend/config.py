"""
config.py — Central settings loader.

Reads APP_ENV (default "dev") and loads the matching .env.{APP_ENV} file from the
backend directory using python-dotenv. All other modules import from here instead
of calling os.getenv directly, so switching environments requires only setting
APP_ENV — no code changes.

Load order (later values win):
  1. System / shell environment variables
  2. .env.{APP_ENV} file in the backend directory
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Determine which environment file to load
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent  # backend/

APP_ENV: str = os.getenv("APP_ENV", "dev")

_env_file = _HERE / f".env.{APP_ENV}"
if _env_file.exists():
    load_dotenv(_env_file, override=False)  # don't override shell env vars

# ---------------------------------------------------------------------------
# Typed settings — fail loudly on missing required keys in non-dev envs
# ---------------------------------------------------------------------------

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/python_educator",
)

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-please")

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

STUDENT_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("STUDENT_TOKEN_EXPIRE_MINUTES", "480")  # 8 hours
)
INSTRUCTOR_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("INSTRUCTOR_TOKEN_EXPIRE_MINUTES", "240")  # 4 hours
)

# Warn loudly if the default dev secret leaks into non-dev environments
if APP_ENV != "dev" and SECRET_KEY == "dev-secret-key-change-in-production-please":
    raise RuntimeError(
        f"SECRET_KEY is still the development default in APP_ENV={APP_ENV!r}. "
        "Set a real SECRET_KEY in your environment file."
    )

# ---------------------------------------------------------------------------
# Phase 20 — Risk tiering & auto-approval
# ---------------------------------------------------------------------------

# When True, every recommendation goes to pending_adaptations regardless of
# risk tier.  Set AUTO_APPLY_KILL_SWITCH=true in the environment (or toggle
# from the dashboard via the SystemSettings DB-backed flag) to instantly revert
# to full manual review without a code deploy.
AUTO_APPLY_KILL_SWITCH: bool = (
    os.getenv("AUTO_APPLY_KILL_SWITCH", "false").lower() == "true"
)

# Agent confidence below this value escalates the risk tier to 'high'.
# Default 0.5 — agent must be at least 50% confident to allow auto-apply.
CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
