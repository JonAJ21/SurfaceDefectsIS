from dataclasses import dataclass, field
from datetime import datetime
from typing import Set, Optional
from domain.exceptions.role import RoleNameIsEmptyException
from domain.entities.base import BaseEntity
from domain.entities.permission import Permission


@dataclass
class Role(BaseEntity):
    name: str = field(kw_only=True)
    description: Optional[str] = field(default=None, kw_only=True)
    created_at: datetime = field(default_factory=datetime.now, kw_only=True)
    updated_at: datetime = field(default_factory=datetime.now, kw_only=True)
    permissions: Optional[Set[Permission]] = None
    
    def _validate_name(self) -> None:
        if not self.name:
            raise RoleNameIsEmptyException("Role name cannot be empty")

    def __post_init__(self):
        self._validate_name()
        
    def change_name(self, new_name: str) -> None:
        self.name = new_name
        self.updated_at = datetime.now()
        self._validate_name()
        
    def change_description(self, new_description: str) -> None:
        self.description = new_description
        self.updated_at = datetime.now()
    
    def assign_permission(self, permission: Permission) -> None:
        if self.permissions is None:
            raise ValueError("Permissions have not been loaded. Use load_permissions=True")
        self.permissions.add(permission)
        self.updated_at = datetime.now()
        
    def revoke_permission(self, permission: Permission) -> None:
        if self.permissions is None:
            raise ValueError("Permissions have not been loaded. Use load_permissions=True")
        self.permissions.discard(permission)
        self.updated_at = datetime.now()
    
    def has_permission(self, permission: Permission) -> bool:
        if self.permissions is None:
            raise ValueError("Permissions have not been loaded. Use load_permissions=True")
        return permission in self.permissions
    
    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Role):
            return self.name == other.name
        return False