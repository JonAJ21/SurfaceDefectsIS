
from datetime import datetime
import json
from typing import Optional

from redis.asyncio.client import Redis

from domain.entities.session import Session
from domain.repositories.session import BaseSessionRepository
from core.config.settings import settings

class RedisSessionRepository(BaseSessionRepository):
    def __init__(self, redis: Redis):
        self.redis = redis
    
    def _get_session_key(self, session_oid: str) -> str:
        return f"session:{session_oid}"
    
    def _get_user_sessions_key(self, user_oid: str) -> str:
        return f"user:sessions:{user_oid}"
    
    def _serialize_session(self, session: Session) -> str:
        data = {
            "oid": session.oid,
            "user_oid": session.user_oid,
            "user_agent": session.user_agent,
            "provider": session.provider,
            "refresh_token_oid": session.refresh_token_oid,
            "refreshed_at": session.refreshed_at.isoformat(),
            "created_at": session.created_at.isoformat(),
        }
        return json.dumps(data)
    
    def _deserialize_session(self, cached: str) -> Session:
        data = json.loads(cached)
        return Session(
            oid=data["oid"],
            user_oid=data["user_oid"],
            user_agent=data["user_agent"],
            provider=data["provider"],
            refresh_token_oid=data["refresh_token_oid"],
            refreshed_at=datetime.fromisoformat(data["refreshed_at"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
        
    async def create(self, session: Session) -> None:
        session_key = self._get_session_key(session.oid)
        ttl = settings.refresh_token_expire_days * 86400
        await self.redis.setex(
            name=session_key,
            time=ttl,
            value=self._serialize_session(session)
        )
        
        user_key = self._get_user_sessions_key(session.user_oid)
        await self.redis.sadd(user_key, session.oid)
        await self.redis.expire(user_key, ttl)
    
    async def get_all_by_user_oid(self, user_oid: str) -> list[Session]:
        user_key = self._get_user_sessions_key(user_oid)
        session_oids = await self.redis.smembers(user_key)
        
        if not session_oids:
            return []
        
        sessions = []
        
        for session_oid in session_oids:
            session = await self.get_by_oid(session_oid)
            if session:
                sessions.append(session)
        
        return sessions
       
    async def get_by_oid(self, oid) -> Optional[Session]:
        key = self._get_session_key(oid)
        cached = await self.redis.get(key)
        
        if not cached:
            return None
        
        return self._deserialize_session(cached)
    
    async def update(self, session: Session) -> None:
        await self.delete_by_oid(session.oid)
        await self.create(session)
    
    async def delete_by_oid(self, oid: str) -> None:
        session = await self.get_by_oid(oid)
        
        if not session:
            return
        
        key = self._get_session_key(session.oid)
        await self.redis.delete(key)
        
        user_key = self._get_user_sessions_key(session.user_oid)
        await self.redis.srem(user_key, session.oid)
       
    async def delete_all_by_user_oid(self, user_oid: str) -> None:
        user_key = self._get_user_sessions_key(user_oid)
        session_oids = await self.redis.smembers(user_key)
        
        if not session_oids:
            return
        
        keys = [self._get_session_key(oid) for oid in session_oids]
        await self.redis.delete(*keys)
        
        await self.redis.delete(user_key)