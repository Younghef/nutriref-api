import json
from typing import Any

from redis.asyncio import Redis

from app.config import settings


_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def make_key(namespace: str, *parts: Any) -> str:
    joined = ":".join(str(p) for p in parts)
    return f"nutriref:v1:{namespace}:{joined}"


async def get_json(key: str) -> Any | None:
    raw = await get_redis().get(key)
    if raw is None:
        return None
    return json.loads(raw)


async def set_json(key: str, value: Any, ttl_seconds: int) -> None:
    await get_redis().set(key, json.dumps(value), ex=ttl_seconds)
