from abc import abstractmethod
from typing import Optional

from domain.entities.session import Session


class BaseSessionRepository:
    
    @abstractmethod
    async def create(self, session: Session) -> None:
        ...
    
    @abstractmethod
    async def get_all_by_user_oid(self, user_oid: str) -> list[Session]:
        ...
    
    @abstractmethod
    async def get_by_oid(self, oid: str) -> Optional[Session]:
        ...
    
    @abstractmethod
    async def update(self, session: Session) -> None:
        ...
       
    @abstractmethod
    async def delete_all_by_user_oid(self, user_oid: str) -> None:
        ...
    
    @abstractmethod
    async def delete_by_oid(self, oid: str) -> None:
        ...