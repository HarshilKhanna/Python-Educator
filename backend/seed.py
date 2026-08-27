#!/usr/bin/env python
"""
seed.py — Idempotent seed script for the Python Educator backend.

Safe to re-run without duplicating data. Run this once after `alembic upgrade head`
to put the system in a fully functional state for development or pilot.

What this script does (in order):
  1. Runs `alembic upgrade head` — ensures the schema is current.
  2. Ingests docs/handbook/*.md via the RAG pipeline — skips if handbook
     chunks already exist (idempotent by source_type check).
  3. Creates one demo instructor account — no-op if the email already exists.

What this script does NOT do:
  - Call any OpenAI / LLM API (no API key required to run seed.py).
  - Create real pilot credentials (use your secrets manager for those).

Demo credentials (clearly fake — do not use for real pilots):
  Email:    demo-instructor@example.edu
  Password: Demo1234!
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Make backend importable when run from the repo root or from backend/
# ---------------------------------------------------------------------------
_BACKEND = Path(__file__).parent
sys.path.insert(0, str(_BACKEND))

import config  # noqa: E402 — loads .env.{APP_ENV}
from database import AsyncSessionLocal, engine, Base  # noqa: E402
from models import User, Chunk  # noqa: E402
from auth import hash_password  # noqa: E402
from sqlalchemy import select, func  # noqa: E402


# ---------------------------------------------------------------------------
# Step 1: run Alembic migrations
# ---------------------------------------------------------------------------

def run_migrations() -> None:
    print("[seed] Step 1: running alembic upgrade head …")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(_BACKEND),
        capture_output=False,
    )
    if result.returncode != 0:
        print("[seed] ERROR: alembic upgrade head failed — aborting.")
        sys.exit(1)
    print("[seed] Migrations complete.")


# ---------------------------------------------------------------------------
# Step 2: ingest handbook chunks (idempotent)
# ---------------------------------------------------------------------------

async def ingest_handbook() -> None:
    print("[seed] Step 2: ingesting handbook …")

    async with AsyncSessionLocal() as session:
        # Check if handbook chunks already exist
        result = await session.execute(
            select(func.count()).select_from(Chunk).where(Chunk.source_type == "handbook")
        )
        count = result.scalar_one()

    if count > 0:
        print(f"[seed] Handbook already ingested ({count} chunks). Skipping.")
        return

    # Import here to avoid loading sentence-transformers at the top of the file
    # (heavy import — only needed if we actually need to ingest)
    try:
        from rag import ingest_handbook as _ingest_handbook  # type: ignore
    except ImportError as exc:
        print(f"[seed] WARNING: could not import rag.ingest_handbook: {exc}")
        print("[seed] Skipping handbook ingestion.")
        return

    handbook_dir = _BACKEND.parent / "docs" / "handbook"
    if not handbook_dir.exists():
        print(f"[seed] WARNING: handbook directory not found at {handbook_dir}")
        print("[seed] Skipping handbook ingestion.")
        return

    async with AsyncSessionLocal() as session:
        await _ingest_handbook(session)
        await session.commit()

    print("[seed] Handbook ingestion complete.")


# ---------------------------------------------------------------------------
# Step 3: create demo instructor account (idempotent)
# ---------------------------------------------------------------------------

# DEMO CREDENTIALS — clearly fake, documented here, never used for real pilots.
_DEMO_EMAIL = "demo-instructor@example.edu"
_DEMO_PASSWORD = "Demo1234!"  # noqa: S105 — intentionally fake/documented


async def create_demo_instructor() -> None:
    print(f"[seed] Step 3: creating demo instructor ({_DEMO_EMAIL}) …")

    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(User).where(User.email == _DEMO_EMAIL)
        )
        if existing.scalar_one_or_none() is not None:
            print("[seed] Demo instructor already exists. Skipping.")
            return

        user = User(
            email=_DEMO_EMAIL,
            password_hash=hash_password(_DEMO_PASSWORD),
            role="instructor",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    print(f"[seed] Demo instructor created (id={user.id}).")
    print(f"[seed]   Email:    {_DEMO_EMAIL}")
    print(f"[seed]   Password: {_DEMO_PASSWORD}")
    print("[seed]   ⚠  These are fake credentials — never use for real pilots.")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def main() -> None:
    run_migrations()  # sync subprocess call
    await ingest_handbook()
    await create_demo_instructor()
    await engine.dispose()
    print("[seed] Done.")


if __name__ == "__main__":
    asyncio.run(main())
