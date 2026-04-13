

from dataclasses import dataclass

from domain.exceptions.base import AuthenticationException


@dataclass(eq=False)
class AccessTokenIsRequiredException(AuthenticationException):
    @property
    def message(self):
        #return 'Access token is required'
        return 'Токен доступа обязателен'

@dataclass(eq=False)
class TokenExpiredException(AuthenticationException):
    jti: str
    @property
    def message(self):
        #return 'Token {self.jti} expired'
        return 'Токен {self.jti} истек'
    
@dataclass(eq=False)
class UserAgentOrProviderMismatchException(AuthenticationException):
    @property
    def message(self):
        #return 'User agent or provider mismatch'
        return 'Пользовательский агент или провайдер не совпадают'
    
@dataclass(eq=False)
class SessionNotFoundException(AuthenticationException):
    @property
    def message(self):
        #return 'Session not found'
        return 'Сессия не найдена'
    
@dataclass(eq=False)
class SessionAlredyRefreshedWithTokenException(AuthenticationException):
    @property
    def message(self):
        #return 'Session already refreshed with this token'
        return 'Сессия уже обновлена с этим токеном'