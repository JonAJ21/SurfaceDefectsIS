from abc import ABC, abstractmethod

class BaseTokenService(ABC):
    
    @abstractmethod
    def verify_access_token(self, token: str) -> dict:
        ...
        