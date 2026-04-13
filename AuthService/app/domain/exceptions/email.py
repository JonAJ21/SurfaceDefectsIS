
from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class InvalidEmailFormat(DomainException):
    email: str
    @property
    def message(self):
        #return f'Invalid email format: {self.email}'
        return f'Неверный формат email: {self.email}'