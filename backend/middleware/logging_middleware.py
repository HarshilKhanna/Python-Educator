"""
logging_middleware.py — Structured JSON request/response logging.

Every HTTP request produces exactly one log line on completion:

    {
        "ts":          "2026-08-27T01:23:45.678Z",
        "request_id":  "550e8400-e29b-41d4-a716-446655440000",
        "user_id":     "uuid-of-authenticated-user | null",
        "method":      "POST",
        "path":        "/answer",
        "status_code": 200,
        "latency_ms":  42.7
    }

The request_id is stored in request.state so exception handlers and
other middleware can reference it for correlation.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("api.access")


def _extract_user_id(authorization: str | None) -> str | None:
    """Best-effort JWT decode to extract the 'sub' claim (user UUID).

    Returns None on any error — never raises. We don't validate the
    signature here (that's the auth dependency's job); we just read the
    payload for logging context.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    try:
        # JWT is base64url(header).base64url(payload).signature
        # We decode the payload without verification for logging only.
        import base64
        payload_b64 = token.split(".")[1]
        # Pad to a multiple of 4
        padding = 4 - len(payload_b64) % 4
        payload_b64 += "=" * (padding % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        return payload.get("sub")
    except Exception:
        return None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Emit one structured JSON access-log line per request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        user_id = _extract_user_id(request.headers.get("authorization"))

        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - start) * 1000, 1)

        log_record = {
            "ts": _utc_now(),
            "request_id": request_id,
            "user_id": user_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        }
        logger.info(json.dumps(log_record))

        # Propagate request_id to clients for debugging
        response.headers["X-Request-ID"] = request_id
        return response


def _utc_now() -> str:
    """Return current UTC time in ISO-8601 format."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
