from redis.asyncio.client import Redis

from domain.repositories.email_token import BaseEmailTokenRepository


class RedisEmailTokenRepository(BaseEmailTokenRepository):
    def __init__(self, redis: Redis):
        self.redis = redis
        
    async def create_email_token_with_ttl(self, oid: str, ttl: int) -> None:
        await self.redis.setex(name=f"email:{oid}", time=ttl, value="True")
        
    async def get_email_token_by_oid(self, oid: str) -> str:
        return await self.redis.get(oid)