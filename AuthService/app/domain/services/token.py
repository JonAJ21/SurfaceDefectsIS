from abc import ABC, abstractmethod

class BaseTokenService(ABC):
    @abstractmethod
    def create_access_token(
        self,
        user_oid: str,
        session_oid: str,
        permission_codes: list[str],
        is_verified: bool
    ) -> tuple[str, str]:
        ...
        
    @abstractmethod
    def create_refresh_token(
        self,
        user_oid: str,
        session_oid: str,
        permission_codes: list[str]
    ) -> tuple[str, str]:
        ...
        
    @abstractmethod
    def verify_access_token(self, token: str) -> dict:
        ...
        
    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict:
        ...
        