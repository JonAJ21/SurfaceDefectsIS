
from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class PasswordDoesNotMatchException(DomainException):
    @property
    def message(self):
        return 'Confirmation password does not match'
    
@dataclass(eq=False)
class InvalidPasswordOrEmailException(DomainException):
    @property
    def message(self):
        return 'Invalid password or email'