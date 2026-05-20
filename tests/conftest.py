import os
import sys
import types

# Ensure env is set before app modules import config.
os.environ.setdefault("USDA_API_KEY", "test-key")
os.environ.setdefault("USDA_BASE_URL", "https://api.nal.usda.gov/fdc/v1")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("X402_NETWORK", "base-sepolia")
os.environ.setdefault("X402_RECEIVER_ADDRESS", "0x0000000000000000000000000000000000000001")
os.environ.setdefault("X402_FACILITATOR_URL", "https://x402.org/facilitator")


# Stub `fastapi_x402` so route imports don't gate on the real package or wrap handlers in a
# payment check. The decorator becomes a no-op pass-through; init_x402 is a no-op.
if "fastapi_x402" not in sys.modules:
    stub = types.ModuleType("fastapi_x402")

    def pay(_price):
        def decorator(fn):
            return fn
        return decorator

    def init_x402(*_args, **_kwargs):
        return None

    stub.pay = pay
    stub.init_x402 = init_x402
    sys.modules["fastapi_x402"] = stub


import fakeredis.aioredis  # noqa: E402
import pytest  # noqa: E402

from app import cache, usda  # noqa: E402


@pytest.fixture(autouse=True)
async def fake_redis(monkeypatch):
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache, "_redis", fake)
    monkeypatch.setattr(cache, "get_redis", lambda: fake)
    yield fake
    await fake.aclose()
    monkeypatch.setattr(cache, "_redis", None)


@pytest.fixture(autouse=True)
def reset_usda_client():
    yield
    usda._client = None
