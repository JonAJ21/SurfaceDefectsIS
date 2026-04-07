from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class RoleWithNameAlreadyExistsException(DomainException):
    name: str
    @property
    def message(self):
        return f'Role {self.name} already exists'
    
@dataclass(eq=False)
class RoleNotFoundException(DomainException):
    name: str
    @property
    def message(self):
        return f'Role {self.name} not found'

@dataclass(eq=False)
class RoleAlreadyHasPermissionException(DomainException):
    role_name: str
    permission_code: str
    @property
    def message(self):
        return f'Role {self.role_name} already has permission with code {self.permission_code}'
   
@dataclass(eq=False)
class RoleDoesNotHavePermissionException(DomainException):
    role_name: str
    permission_code: str
    @property
    def message(self):
        return f'Role {self.role_name} does not have permission with code {self.permission_code}'