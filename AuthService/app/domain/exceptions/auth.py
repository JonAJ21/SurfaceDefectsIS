
from dataclasses import dataclass

from domain.exceptions.base import AuthenticationException, DomainException


@dataclass(eq=False)
class PasswordDoesNotMatchException(AuthenticationException):
    @property
    def message(self):
        #return 'Confirmation password does not match'
        return 'Пароли не совпадают'
    
@dataclass(eq=False)
class InvalidPasswordOrEmailException(AuthenticationException):
    @property
    def message(self):
        #return 'Invalid password or email'
        return 'Неверный пароль или email'
    
@dataclass(eq=False)
class OldPasswordIsRequiredException(DomainException):
    @property
    def message(self):
        #return 'Old password is required'
        return 'Старый пароль обязателен'
    
@dataclass(eq=False)
class NewPasswordIsRequiredException(DomainException):
    @property
    def message(self):
        #return 'Old password is required'
        return 'Новый пароль обязателен'