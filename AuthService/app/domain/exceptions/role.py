from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class RoleWithNameAlreadyExistsException(DomainException):
    name: str
    @property
    def message(self):
        #return f'Role {self.name} already exists'
        return f'Роль {self.name} уже существует'
    
@dataclass(eq=False)
class RoleNotFoundException(DomainException):
    name: str
    @property
    def message(self):
        #return f'Role {self.name} not found'
        return f'Роль {self.name} не найдена'

@dataclass(eq=False)
class RoleAlreadyHasPermissionException(DomainException):
    role_name: str
    permission_code: str
    @property
    def message(self):
        #return f'Role {self.role_name} already has permission with code {self.permission_code}'
        return f'Роль {self.role_name} уже имеет разрешение с кодом {self.permission_code}'
   
@dataclass(eq=False)
class RoleDoesNotHavePermissionException(DomainException):
    role_name: str
    permission_code: str
    @property
    def message(self):
        #return f'Role {self.role_name} does not have permission with code {self.permission_code}'
        return f'Роль {self.role_name} не имеет разрешения с кодом {self.permission_code}'
    
@dataclass(eq=False)
class RoleNameIsEmptyException(DomainException):
    @property
    def message(self):
        #return f'Role name cannot be empty'
        return f'Название роли не может быть пустым'
   