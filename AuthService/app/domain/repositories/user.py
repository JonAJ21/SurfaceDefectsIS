
from abc import ABC, abstractmethod
from typing import Optional

from domain.values.email import Email
from domain.entities.user import User


class BaseUserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> None:
        ...
    
    @abstractmethod
    async def get(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[User]:
        ...
     
    @abstractmethod
    async def get_by_oid(
        self,
        oid: str,
        load_sessions: bool = False,
        load_roles: bool = False,
        load_permissions: bool = False,
        load_login_history: bool = False,
        login_history_limit: int = 10,
        login_history_offset: int = 0
    ) -> Optional[User]:
        ...
       
    @abstractmethod
    async def get_by_email(
        self,
        email: Email,
        load_sessions: bool = False,
        load_roles: bool = False,
        load_permissions: bool = False,
        load_login_history: bool = False,
        login_history_limit: int = 10,
        login_history_offset: int = 0
    ) -> Optional[User]:
        ...
    
    @abstractmethod
    async def update(self, user: User) -> None:
        ...
     
    @abstractmethod
    async def delete(self, user: User) -> None:
        ...
        