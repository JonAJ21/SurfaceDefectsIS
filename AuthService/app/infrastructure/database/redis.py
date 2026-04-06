from redis.asyncio.client import Redis

redis: Redis | None = None

def get_redis() -> Redis:
    return redis