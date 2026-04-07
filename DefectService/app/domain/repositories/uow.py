from abc import abstractmethod
from typing import AsyncContextManager

from domain.repositories.photo import BasePhotosRepository
from domain.repositories.road import BaseRoadsRepository
from domain.repositories.defect import BaseDefectsRepository

class BaseUnitOfWork(AsyncContextManager):
    @property
    @abstractmethod
    def defects(self) -> BaseDefectsRepository:
        ...
    
    @property
    @abstractmethod
    def roads(self) -> BaseRoadsRepository:
        ...
        
    @abstractmethod
    async def photos(self) -> BasePhotosRepository:
        ...
        
    @abstractmethod
    async def commit(self) -> None:
        ...
    
    @abstractmethod
    async def flush(self) -> None:
        ...
    
    @abstractmethod
    async def rollback(self) -> None:
        ...
        
    @abstractmethod
    async def __aenter__(self) -> 'BaseUnitOfWork':
        ...
        
    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        ...