from dataclasses import dataclass

@dataclass(eq=False)
class DomainException(Exception):
    @property
    def message(self):
        return 'Domain exception occured'