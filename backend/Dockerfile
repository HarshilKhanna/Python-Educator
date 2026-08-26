# =============================================================================
# Dockerfile — Python Educator Backend
# Multi-stage build: build dependencies in a fat image, copy to slim runtime.
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: build — install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS build

WORKDIR /install

# Install build tools needed for some wheels (e.g. asyncpg, bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --prefix=/install/deps --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: runtime — slim image with only what's needed to run
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Runtime system deps only (libpq for asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy installed packages from build stage
COPY --from=build /install/deps /usr/local

# Copy application source
COPY . .

# Alembic migrations are NOT run at build time — seed.py or the operator
# should run `alembic upgrade head` before or alongside the first startup.
# The entrypoint below starts uvicorn directly.

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
