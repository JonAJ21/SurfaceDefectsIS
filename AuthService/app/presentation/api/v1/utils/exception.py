
from functools import wraps

from fastapi import HTTPException, status

from domain.exceptions.auth import AuthenticationException
from domain.exceptions.base import DomainException


def handle_domain_exception(e: DomainException) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=e.message)
    
def handle_auth_exception(e: AuthenticationException) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=e.message)

def handle_exception(e: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(e))
    
def handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AuthenticationException as e:
            raise handle_auth_exception(e)
        except DomainException as e:
            raise handle_domain_exception(e)
        except Exception as e:
            raise handle_exception(e)
    return wrapper