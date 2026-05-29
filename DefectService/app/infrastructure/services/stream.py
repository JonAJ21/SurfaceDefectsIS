import json

from redis.asyncio.client import Redis

from domain.services.stream import BaseStreamService

redis: Redis | None = None

def get_redis() -> Redis:
    return redis

class RedisStreamService(BaseStreamService):
    def __init__(self, redis: Redis, stream_key: str = "defects:stream", maxlen: int= 10000):
        self.redis = redis
        self.stream_key = stream_key
        self.maxlen = maxlen
    
    async def publish_defect(self, defect_id: str, media_paths: list[str]) -> None:
        message = {
            "defect_id": defect_id,
            "media_paths": json.dumps(media_paths),
        }
        
        await self.redis.xadd(
            self.stream_key,
            message,
            maxlen=self.maxlen,
            approximate=True
        )