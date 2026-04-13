from dataclasses import dataclass

@dataclass(eq=False)
class DomainException(Exception):
    @property
    def message(self):
        #return 'Domain exception occured'
        return 'Ошибка в домене'
    
@dataclass(eq=False)
class AuthenticationException(Exception):
    @property
    def message(self):
        #return 'Authentication failed'
        return 'Аутентификация не удалась'
        