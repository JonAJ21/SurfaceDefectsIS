
from dataclasses import dataclass

from domain.exceptions.base import DomainException

@dataclass
class InvalidIdentifierException(DomainException):
    identifier: str
    
    @property
    def message(self):
        #return f'Invalid identifier {self.identifier}'
        return f'Неверный идентификатор {self.identifier}'
    