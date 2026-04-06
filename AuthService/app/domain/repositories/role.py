from abc import abstractmethod
from typing import Optional

from domain.entities.role import Role

class BaseRoleRepository:
    @abstractmethod
    async def create(self, role: Role) -> None:
        ...
        
    @abstractmethod
    async def get(self, limit: int = 100, offset: int = 0) -> list[Role]:
        ...

    @abstractmethod
    async def get_by_oid(self, oid: str, load_permissions: bool = False) -> Optional[Role]:
        ...
    
    @abstractmethod
    async def get_by_name(self, name: str, load_permissions: bool = False) -> Optional[Role]:
        ...
    
    @abstractmethod
    async def update(self, role: Role) -> None:
        ...
     
    @abstractmethod
    async def delete(self, role: Role) -> None:
        ...