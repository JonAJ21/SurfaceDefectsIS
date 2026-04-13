import re
from dataclasses import dataclass

from domain.exceptions.email import InvalidEmailFormat

@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise InvalidEmailFormat(self.value)
        object.__setattr__(self, 'value', self.value.lower())
    
    def __str__(self):
        return self.value
    
    def __hash__(self):
        return hash(self.value)
    
    def __eq__(self, other):
        if isinstance(other, Email):
            return self.value == other.value
        return self.value == other