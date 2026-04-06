from abc import abstractmethod
from typing import AsyncContextManager

from domain.repositories.email_token import BaseEmailTokenRepository
from domain.repositories.session import BaseSessionRepository
from domain.repositories.permission import BasePermissionRepository
from domain.repositories.role import BaseRoleRepository
from domain.repositories.user import BaseUserRepository

class BaseUnitOfWork(AsyncContextManager):
    @property
    @abstractmethod
    def users(self) -> BaseUserRepository:
        ...
    
    @property
    @abstractmethod
    def roles(self) -> BaseRoleRepository:
        ...
    
    @property
    @abstractmethod
    def permissions(self) -> BasePermissionRepository:
        ...
    
    @property
    @abstractmethod
    def sessions(self) -> BaseSessionRepository:
        ...
    
    @property
    @abstractmethod
    def email_tokens(self) -> BaseEmailTokenRepository:
        ...
        
    @abstractmethod
    async def commit(self) -> None:
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