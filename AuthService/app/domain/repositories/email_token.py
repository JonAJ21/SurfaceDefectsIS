from abc import ABC, abstractmethod


class BaseEmailTokenRepository(ABC):
    @abstractmethod
    async def create_email_token_with_ttl(self, oid: str, ttl: int) -> None:
        ...
        
    @abstractmethod
    async def get_email_token_by_oid(self, oid: str) -> str:
        ...