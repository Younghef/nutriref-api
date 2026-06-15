"""Server-side exception handlers.

Without these, a Redis ConnectionError (or any other unhandled exception) bubbles
past FastAPI's routing into fastapi_x402's middleware, which catches *everything*
and rebadges as `402 Payment processing failed: ...`. That hides real failures
behind a payment-shaped error and makes the MCP client (and curl probes) think
the server is asking for money when it's actually broken.

These handlers convert non-payment exceptions into JSONResponses with truthful
status codes BEFORE the middleware sees them. fastapi_x402's middleware then
sees `response.status_code >= 400` and falls through to its
"route failed, skipping settlement" branch, which preserves the original status.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError


log = logging.getLogger(__name__)


def _json(status: int, code: str, message: str, *, hint: str | None = None) -> JSONResponse:
    body: dict[str, str] = {"error": code, "message": message}
    if hint:
        body["hint"] = hint
    return JSONResponse(status_code=status, content=body)


async def _redis_error_handler(request: Request, exc: RedisError) -> JSONResponse:
    log.exception("redis_error path=%s", request.url.path)
    return _json(
        503,
        "cache_unavailable",
        f"Cache backend unavailable: {exc.__class__.__name__}",
        hint="Verify REDIS_URL is reachable; see /health for liveness.",
    )


def install_exception_handlers(app: FastAPI) -> None:
    """Register handlers. Order matters: more-specific first."""
    app.add_exception_handler(RedisError, _redis_error_handler)
