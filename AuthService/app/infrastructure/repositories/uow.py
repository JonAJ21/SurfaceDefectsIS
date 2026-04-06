from typing import Optional

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.repositories.email_token import RedisEmailTokenRepository
from infrastructure.repositories.session import RedisSessionRepository
from infrastructure.repositories.permission import PermissionRepository
from infrastructure.repositories.role import CachedRoleRepository
from infrastructure.repositories.user import UserRepository
from domain.repositories.uow import BaseUnitOfWork
from core.config.settings import settings

class SQLAlchemyUnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], redis: Redis):
        self.session_factory = session_factory
        self.redis = redis
        self._session: Optional[AsyncSession] = None
        self._user_repository: Optional[UserRepository] = None
        self._role_repository: Optional[CachedRoleRepository] = None
        self._permission_repository: Optional[PermissionRepository] = None
        
    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session is not initialized")
        return self._session

    @property
    def users(self) -> UserRepository:
        if self._user_repository is None:
            self._user_repository = UserRepository(self.session, self.redis)
        return self._user_repository
    
    @property
    def roles(self) -> CachedRoleRepository:
        if self._role_repository is None:
            self._role_repository = CachedRoleRepository(
                session=self.session,
                redis=self.redis,
                cache_ttl=settings.role_cache_ttl_minutes * 60
            )
        return self._role_repository

    @property
    def permissions(self) -> PermissionRepository:
        if self._permission_repository is None:
            self._permission_repository = PermissionRepository(self.session)
        return self._permission_repository
    
    @property
    def sessions(self) -> RedisSessionRepository:
        return RedisSessionRepository(self.redis)
    
    @property
    def email_tokens(self) -> RedisEmailTokenRepository:
        return RedisEmailTokenRepository(self.redis)
    
    async def __aenter__(self) -> 'SQLAlchemyUnitOfWork':
        self._session = self.session_factory()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()
            # self._session.expire_all()
            
        await self._session.close()
        
    async def commit(self) -> None:
        await self._session.commit()
    
    async def rollback(self) -> None:
        await self._session.rollback()
    