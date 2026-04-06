from dataclasses import dataclass
from typing import Optional

from domain.entities.base import BaseEntity

@dataclass
class Permission(BaseEntity):
    code: str
    description: Optional[str] = None

    def __post_init__(self) -> None:
        self._validate_code()

    def _validate_code(self) -> None:
        if not self.code or len(self.code) < 3:
            raise ValueError("Permission code must be at least 3 characters")
        if "." not in self.code:
            raise ValueError("Permission code must contain a dot (e.g., 'users.read')")
        parts = self.code.split(".")
        if len(parts) != 2:
            raise ValueError("Permission code must be in format 'resource.action'")
        if not parts[0] or not parts[1]:
            raise ValueError("Permission code must have non-empty resource and action")

    def __hash__(self) -> int:
        return hash(self.code)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Permission):
            return self.code == other.code
        return self.code == other

    def __str__(self) -> str:
        return self.code

    @property
    def resource(self) -> str:
        return self.code.split(".")[0]

    @property
    def action(self) -> str:
        return self.code.split(".")[1]

    @classmethod
    def create(cls, code: str, description: Optional[str] = None) -> "Permission":
        return cls(code=code, description=description)
    
    def change_code(self, code: str) -> None:
        self.code = code
        self._validate_code()
    
    def change_description(self, description: str) -> None:
        self.description = description