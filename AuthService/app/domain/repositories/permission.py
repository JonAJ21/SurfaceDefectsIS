from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.permission import Permission


class BasePermissionRepository(ABC):
    @abstractmethod
    async def create(self, permission: Permission) -> None:
        ...
    
    @abstractmethod
    async def get(self, limit: int = 100, offset: int = 0) -> list[Permission]:
        ...
    
    @abstractmethod
    async def get_by_oid(self, oid: str) -> Optional[Permission]:
        ...
          
    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Permission]:
        ...
    
    @abstractmethod
    async def update(self, permission: Permission) -> None:
        ...
    
    @abstractmethod
    async def delete(self, permission: Permission) -> None:
        ...     
    