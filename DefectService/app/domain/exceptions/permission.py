
from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class PermissionWithCodeAlreadyExistsException(DomainException):
    code: str
    @property
    def message(self):
        return f'Permission with code {self.code} already exists'
    
@dataclass(eq=False)
class PermissionNotFoundException(DomainException):
    code: str
    @property
    def message(self):
        return f'Permission {self.code} not found'
    
