
from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class PermissionWithCodeAlreadyExistsException(DomainException):
    code: str
    @property
    def message(self):
        #return f'Permission with code {self.code} already exists'
        return f'Разрешение с кодом {self.code} уже существует'
    
@dataclass(eq=False)
class PermissionNotFoundException(DomainException):
    code: str
    @property
    def message(self):
        #return f'Permission {self.code} not found'
        return f'Разрешение {self.code} не найдено'
    
@dataclass(eq=False)
class PermissionCodeMustBeAtLeast3CharactersException(DomainException):
    @property
    def message(self):
        #return f'Permission code must be at least 3 characters'
        return f'Код разрешения должен быть не менее 3 символов'

@dataclass(eq=False)
class PermissionCodeMustContainDotException(DomainException):
    @property
    def message(self):
        #return f'Permission code must contain a dot (e.g., "users.read")'
        return f'Код разрешения должен содержать точку (например, "users.read")'
    
@dataclass(eq=False)
class PermissionCodeMustBeInFormatResourceActionException(DomainException):
    @property
    def message(self):
        #return f'Permission code must be in format "resource.action"'
        return f'Код разрешения должен быть в формате "resource.action"'
    
@dataclass(eq=False)
class PermissionCodeMustHaveNonEmptyResourceAndActionException(DomainException):
    @property
    def message(self):
        #return f'Permission code must have non-empty resource and action'
        return f'Код разрешения должен содержать не пустой ресурс и действие'