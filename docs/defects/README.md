# NutriRef defect captures — 2026-06-15

Reproduction host: Windows 11, Python 3.11, `uvicorn app.main:app` on
`127.0.0.1:8000`, payer wallet `0xd7c0...6ca7` on `base-sepolia`. Captures and
the full request/response log live in this directory and `build/requests.jsonl`.

Captures are numbered chronologically:

| # | Run                                           | Outcome     | File |
|---|-----------------------------------------------|-------------|------|
| 01 | search, default Windows cp1252 stdout         | 402 charmap | `01_search_control.txt` |
| 02 | detail 2012128, cp1252                        | 402 charmap | `02_detail_paid.txt` |
| 03 | compare [2012128,2011468], cp1252             | 402 charmap | `03_compare_paid.txt` |
| 04 | recipe, cp1252                                | 402 charmap | `04_recipe_paid.txt` |
| 05 | search, PYTHONUTF8=1                          | 402 redis   | `05_utf8_search.txt` |
| 06 | detail 2012128, PYTHONUTF8=1                  | 402 redis   | `06_utf8_detail.txt` |
| 07 | compare, PYTHONUTF8=1                         | 402 redis   | `07_utf8_compare.txt` |
| 08 | recipe, PYTHONUTF8=1                          | 402 redis   | `08_utf8_recipe.txt` |
| 09 | search, UTF-8 + REDIS_URL=localhost           | **200 OK**  | `09_search_redis_ok.txt` |
| 10 | detail 2012128, UTF-8 + localhost redis       | **200 OK**  | `10_detail_redis_ok.txt` |
| 11 | compare, UTF-8 + localhost redis              | **200 OK**  | `11_compare_redis_ok.txt` |
| 12 | recipe, UTF-8 + localhost redis               | **200 OK**  | `12_recipe_redis_ok.txt` |

## Investigation summary

All four endpoints work end-to-end (200 + on-chain settlement) when (a) the
server has a reachable Redis and (b) stdout can encode UTF-8. The reports of
"`nutrition_detail` 404", "`nutrition_compare` 404", and "EIP-712 verification
failure" all resolved to one of two underlying faults, **not actual 404s**:

1. fastapi_x402's middleware wraps the entire `call_next()` in a blanket
   `except Exception: return JSONResponse(402, ...)` — see
   `fastapi_x402/middleware.py:209-225`. Any exception inside payment
   verification, settlement, or the route handler is rebadged as a 402 with the
   exception string embedded in `error`. The MCP client calls
   `response.raise_for_status()`, which raises `HTTPStatusError: 402`, and
   the agent surfaces this as a tool failure that previous notes labelled "404".
   No FastAPI route is actually 404-ing; this is a labelling/reporting bug in
   how we read MCP failures, plus a 402-as-catchall in the dep.

2. With cp1252 stdout, the *specific* exception is a `UnicodeEncodeError` from
   `fastapi_x402/facilitator.py:164-178` (`print(f"🔍 ...")` debug lines).
   With Redis unreachable, the *specific* exception is `redis.ConnectionError`
   from `app/cache.py:get_redis()` during the route handler.

The on-chain EIP-712 patch in `app/main.py:20-22` does land on `NETWORK_CONFIGS["base"]`
(`name = eip712_name = "USD Coin"`). `base-sepolia` is untouched but already
matches its on-chain `USDC` name. No live EIP-712 mismatch on either network
in current code; flagged as **D5 (regression risk)** below.

## Defect list

| ID  | Defect                                                                                  | Severity | Pass criterion |
|-----|-----------------------------------------------------------------------------------------|----------|----------------|
| D1  | `fastapi_x402/facilitator.py:164-178` prints emoji to stdout, crashing under cp1252.    | P1       | Paid retry succeeds in a stock Windows shell (no `PYTHONUTF8=1`/`PYTHONIOENCODING=utf-8` needed). Verified by re-running capture 01–04 without UTF-8 env and seeing HTTP 200 + valid `X-PAYMENT-RESPONSE`. |
| D2  | Default `REDIS_URL=redis://redis:6379/0` only works inside the Docker network; host-launched uvicorn cannot connect, every paid call returns 402 with `Error 11001 connecting to redis:6379`. | P1       | `python -m uvicorn app.main:app` against a host-local Redis returns 200 on all four endpoints without env overrides. Either (a) default the URL to localhost, or (b) fail fast at startup with a clear "Redis unreachable" message instead of a generic 402. |
| D3  | fastapi_x402 middleware swallows every exception from `call_next()` as a 402, so route-side bugs (Redis, USDA outage, validation) all look like payment failures. The MCP client then raises `HTTPStatusError: 402` which prior notes mislabelled "404". | P2       | Non-payment failures keep their original status: a USDA 404 propagates as 404 (not 402), a Redis ConnectionError surfaces as 503 with a `cache_unavailable` error code. Add a server-side audit log distinguishing `verify_failed`, `settle_failed`, and `route_raised`. |
| D4  | MCP server (`mcp_server/server.py`) calls `r.raise_for_status()` and lets `httpx.HTTPStatusError` bubble to the agent, producing a confusing tool error that hides the upstream `error` body. | P2       | When the API returns a 402/4xx/5xx with a JSON `error` field, the MCP tool surfaces a structured `{status, error, hint}` payload, not a stack trace. The agent-facing message must include the upstream error string. |
| D5  | EIP-712 name patch in `app/main.py:20-22` is a runtime monkey-patch against `fastapi_x402.networks.NETWORK_CONFIGS["base"]`. A library update or import-order change silently breaks Base mainnet payments. | P2       | A startup assertion verifies `NETWORK_CONFIGS["base"].assets["usdc"].eip712_name == "USD Coin"`. CI runs a sanity check against the lib version pinned in `pyproject.toml`. |
| D6  | OneDrive sync periodically reverts `.env` (see CLAUDE memory `env-file-instability`). Today's reproduction surfaced `REDIS_URL=redis://redis:6379/0` even though local dev should be `localhost`. | P3       | `.env` is moved out of the OneDrive-synced tree (e.g., `%USERPROFILE%\.nutriref\.env`) and `app/config.py` reads from `${NUTRIREF_ENV_FILE:-.env}`. |
| D7  | `app/main.py:44` `version="0.2.0"` is stale (MCPB bundle and `server.json` already at 0.2.1). Discovery endpoints will advertise the wrong version. | P3       | `app.version` is sourced from `pyproject.toml` (single source of truth) or matched by a release-check script. |

## Logging middleware

Defect-capture middleware lives at `app/middleware.py` and is wired in
`app/main.py:55-60`. It is **opt-in** — only active when `REQUEST_LOG_FILE`
is set, so prod and the test suite are unaffected. Each request emits one JSON
line containing method, path, query, status, latency, x402 headers, and
truncated request/response bodies. Example reproduction:

```powershell
$env:REQUEST_LOG_FILE = "build/requests.jsonl"
$env:REDIS_URL        = "redis://localhost:6379/0"
$env:PYTHONUTF8       = "1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# in another shell:
$env:BASE_URL = "http://127.0.0.1:8000"
python scripts/pay_and_call.py detail 2012128
Get-Content build/requests.jsonl | Select-Object -Last 2
```

Full sample output is in `build/requests.jsonl` (last run kept for reference).

## Order to fix

1. D2 (config default) — unblocks all paid local repro and CI.
2. D1 (fastapi_x402 debug print) — upstream a PR or vendor a patch; until then,
   document `PYTHONUTF8=1` as a Windows requirement.
3. D5 (mainnet EIP-712 assertion) — cheap guardrail; do it before any mainnet promo.
4. D3 (status-code semantics) — needs an upstream fix in fastapi_x402; local
   workaround is a custom exception handler that catches `RedisError` and
   `HTTPException` before the middleware does.
5. D4 (MCP error surface) — small change in `mcp_server/server.py`; ship with
   the next MCPB bump.
6. D6 (.env location), D7 (single version source) — clean-ups.
