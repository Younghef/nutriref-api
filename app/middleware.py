"""Structured request/response logging for defect captures.

Emits one JSON line per request to LOG_FILE (default build/requests.jsonl). Each
line carries method, path, query, status, latency_ms, x402 headers, request body
(truncated), and response body (truncated). Designed for diff-able captures of
known defects, not for production observability.

Enable by importing and adding the middleware in app/main.py. Disabled-by-default
elsewhere so it has zero overhead in tests.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


LOG_FILE = Path(os.environ.get("REQUEST_LOG_FILE", "build/requests.jsonl"))
MAX_BODY = int(os.environ.get("REQUEST_LOG_MAX_BODY", "4096"))

X402_HEADERS = ("x-payment", "x-payment-response", "www-authenticate")


def _truncate(b: bytes) -> str:
    if len(b) <= MAX_BODY:
        try:
            return b.decode("utf-8", errors="replace")
        except Exception:
            return repr(b)
    head = b[:MAX_BODY].decode("utf-8", errors="replace")
    return f"{head}\n...[truncated {len(b) - MAX_BODY} bytes]"


def _pick_headers(headers: Any) -> dict[str, str]:
    out = {}
    for k in X402_HEADERS:
        v = headers.get(k)
        if v is not None:
            out[k] = v
    return out


class RequestLogger(BaseHTTPMiddleware):
    """One JSON line per request — captures both the 402 gate and the paid retry."""

    def __init__(self, app, log_file: Path = LOG_FILE) -> None:
        super().__init__(app)
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        rid = uuid.uuid4().hex[:8]
        t0 = time.perf_counter()

        # Buffer the request body so the route still sees it.
        req_body = await request.body()

        async def receive():
            return {"type": "http.request", "body": req_body, "more_body": False}

        request = Request(request.scope, receive)

        response = await call_next(request)

        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        resp_body = b"".join(chunks)

        elapsed = round((time.perf_counter() - t0) * 1000, 2)

        entry = {
            "rid": rid,
            "method": request.method,
            "path": request.url.path,
            "query": request.url.query or None,
            "status": response.status_code,
            "latency_ms": elapsed,
            "req_headers_x402": _pick_headers(request.headers),
            "req_body": _truncate(req_body) if req_body else None,
            "resp_headers_x402": _pick_headers(response.headers),
            "resp_body": _truncate(resp_body) if resp_body else None,
        }

        try:
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

        return Response(
            content=resp_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )
