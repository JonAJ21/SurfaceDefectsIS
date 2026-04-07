from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.repositories.photo import MinioPhotosRepository
from infrastructure.repositories.road import SQLAlchemyRoadsRepository
from infrastructure.repositories.defect import SQLAlchemyDefectsRepository
from domain.repositories.uow import BaseUnitOfWork
from core.config.settings import settings

class SQLAlchemyUnitOfWork(BaseUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self._defects_repository: Optional[SQLAlchemyDefectsRepository] = None
        self._roads_repository: Optional[SQLAlchemyRoadsRepository] = None
        self._photos_repository: Optional[MinioPhotosRepository] = None
   
    @property
    def defects(self) -> SQLAlchemyDefectsRepository:
        if self._defects_repository is None:
            self._defects_repository = SQLAlchemyDefectsRepository(self._session)
        return self._defects_repository
    
    @property
    def roads(self) -> SQLAlchemyRoadsRepository:
        if self._roads_repository is None:
            self._roads_repository = SQLAlchemyRoadsRepository(self._session)
        return self._roads_repository
    
    @property
    def photos(self) -> MinioPhotosRepository:
        if self._photos_repository is None:
            self._photos_repository = MinioPhotosRepository()
        return self._photos_repository
    
    async def __aenter__(self) -> 'SQLAlchemyUnitOfWork':
        self._session = self.session_factory()
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()
            
        await self._session.close()
        
    async def commit(self) -> None:
        await self._session.commit()
    
    async def flush(self) -> None:
        await self._session.flush()
    
    async def rollback(self) -> None:
        await self._session.rollback()
    