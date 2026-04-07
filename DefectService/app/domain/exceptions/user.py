from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class UserWithEmailAlreadyExistsExcception(DomainException):
    email: str
    @property
    def message(self):
        return f'User with email {self.email} already exists'
    
@dataclass(eq=False)
class UserInactiveException(DomainException):
    email: str
    @property
    def message(self):
        return f'User with email {self.email} is inactive'
    
@dataclass(eq=False)
class UserNotFoundException(DomainException):
    email: str
    @property
    def message(self):
        return f'User {self.email} not found'
    
@dataclass(eq=False)
class UserDoesNotHavePermissionException(DomainException):
    permission_code: str
    @property
    def message(self):
        return f'User does not have permission {self.permission_code}'

@dataclass(eq=False)
class UserEmailNotVerifiedException(DomainException):
    @property
    def message(self):
        return f'User is not verified'