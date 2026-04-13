from dataclasses import dataclass

from domain.exceptions.base import AuthenticationException, DomainException


@dataclass(eq=False)
class UserWithEmailAlreadyExistsExcception(DomainException):
    email: str
    @property
    def message(self):
       # return f'User with email {self.email} already exists'
        return f'Пользователь с email {self.email} уже существует'
    
@dataclass(eq=False)
class UserInactiveException(AuthenticationException):
    email: str
    @property
    def message(self):
        #return f'User with email {self.email} is inactive'
        return f'Пользователь с email {self.email} не активен'
    
@dataclass(eq=False)
class UserNotFoundException(DomainException):
    email: str
    @property
    def message(self):
        #return f'User {self.email} not found'
        return f'Пользователь {self.email} не найден'
    
@dataclass(eq=False)
class UserDoesNotHavePermissionException(AuthenticationException):
    permission_code: str
    @property
    def message(self):
       # return f'User does not have permission {self.permission_code}'
        return f'Пользователь не имеет разрешения {self.permission_code}'

@dataclass(eq=False)
class UserEmailNotVerifiedException(AuthenticationException):
    @property
    def message(self):
        #return f'User is not verified'
        return f'Пользователь не верифицирован'