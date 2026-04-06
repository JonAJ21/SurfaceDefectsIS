from dataclasses import dataclass
import re

from domain.services.password import BasePasswordService

@dataclass(frozen=True)
class Password:
    value: str
    
    @classmethod
    def from_plain(cls, plain_password: str, password_service: BasePasswordService) -> "Password":
        cls._validate_length(plain_password)
        cls._validate_complexity(plain_password)
        return cls(value=password_service.hash(plain_password))
    
    @classmethod
    def _validate_length(cls, plain_password: str):
        if len(plain_password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(plain_password) > 64:
            raise ValueError("Password must not exceed 64 characters")
    @classmethod
    def _validate_complexity(cls, plain_password: str):
        if not re.search(r'[A-Z]', plain_password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', plain_password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', plain_password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', plain_password):
            raise ValueError("Password must contain at least one special character")
    
    def verify(self, plain_password: str, password_service: BasePasswordService) -> bool:
        return password_service.verify(plain_password, self.value)
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Password):
            return self.value == other.value
        return self.value == other
    
