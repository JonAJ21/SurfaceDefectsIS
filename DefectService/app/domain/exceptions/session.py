

from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class AccessTokenIsRequiredException(DomainException):
    @property
    def message(self):
        return 'Access token is required'

@dataclass(eq=False)
class TokenExpiredException(DomainException):
    jti: str
    @property
    def message(self):
        return 'Token {self.jti} expired'
    
@dataclass(eq=False)
class UserAgentOrProviderMismatchException(DomainException):
    @property
    def message(self):
        return 'User agent or provider mismatch'
    
@dataclass(eq=False)
class SessionNotFoundException(DomainException):
    @property
    def message(self):
        return 'Session not found'
    
@dataclass(eq=False)
class SessionAlredyRefreshedWithTokenException(DomainException):
    @property
    def message(self):
        return 'Session already refreshed with this token'