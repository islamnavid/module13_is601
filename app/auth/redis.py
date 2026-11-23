
# app/auth/redis.py

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()


async def get_redis():
    """Get or create the asynchronous Redis client."""
    if not hasattr(get_redis, "redis"):
        get_redis.redis = aioredis.from_url(
            settings.REDIS_URL or "redis://localhost:6379/0",
            decode_responses=True
        )

    return get_redis.redis


async def add_to_blacklist(jti: str, exp: int):
    """Add a token's JTI to the Redis blacklist."""
    redis_client = await get_redis()

    await redis_client.set(
        f"blacklist:{jti}",
        "1",
        ex=exp
    )


async def is_blacklisted(jti: str) -> bool:
    """Check whether a token's JTI is blacklisted."""
    redis_client = await get_redis()

    return bool(
        await redis_client.exists(f"blacklist:{jti}")
    )
