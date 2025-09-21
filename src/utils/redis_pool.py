import os
from redis.asyncio import Redis, from_url

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_redis = None

def get_redis():
    """
    Get a singleton Redis client instance.

    If the Redis client is not already created, it initializes a new connection
    using the URL specified in the `REDIS_URL` environment variable.

    Returns:
        aioredis.Redis: Async Redis client instance.
    """
    global _redis
    if _redis is None:
        _redis = from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis

