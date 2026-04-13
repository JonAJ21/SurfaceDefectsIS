

from dataclasses import dataclass

from domain.exceptions.base import DomainException


@dataclass(eq=False)
class PasswordMustBeAtLeast8CharactersLongException(DomainException):
    @property
    def message(self):
       # return 'Password must be at least 8 characters long'
        return 'Пароль должен быть не менее 8 символов'
    
@dataclass(eq=False)
class PasswordMustNotExceed64CharactersException(DomainException):
    @property
    def message(self):
       # return 'Password must not exceed 64 characters'
        return 'Пароль не должен превышать 64 символов'
    
@dataclass(eq=False)
class PasswordMustContainUppercaseLetterException(DomainException):
    @property
    def message(self):
        #return 'Password must contain at least one uppercase letter'
        return 'Пароль должен содержать хотя бы одну заглавную букву'
    
@dataclass(eq=False)
class PasswordMustContainLowercaseLetterException(DomainException):
    @property
    def message(self):
        #return 'Password must contain at least one lowercase letter'
        return 'Пароль должен содержать хотя бы одну строчную букву'
    
@dataclass(eq=False)
class PasswordMustContainDigitException(DomainException):
    @property
    def message(self):
        #return 'Password must contain at least one digit'
        return 'Пароль должен содержать хотя бы одну цифру'
    
@dataclass(eq=False)
class PasswordMustContainSpecialCharacterException(DomainException):
    @property
    def message(self):
       # return 'Password must contain at least one special character'
        return 'Пароль должен содержать хотя бы один специальный символ'