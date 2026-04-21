import redis.asyncio as aioredis
from typing import Optional
from app.core.config import settings

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def redis_set(key: str, value: str, ttl_seconds: int) -> None:
    client = await get_redis()
    await client.setex(key, ttl_seconds, value)


async def redis_get(key: str) -> Optional[str]:
    client = await get_redis()
    return await client.get(key)


async def redis_delete(key: str) -> None:
    client = await get_redis()
    await client.delete(key)


async def redis_exists(key: str) -> bool:
    client = await get_redis()
    result = await client.exists(key)
    return bool(result)


async def redis_incr(key: str) -> int:
    client = await get_redis()
    return await client.incr(key)


async def redis_expire(key: str, ttl_seconds: int) -> None:
    client = await get_redis()
    await client.expire(key, ttl_seconds)


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
