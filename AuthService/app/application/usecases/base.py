from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Request = TypeVar('Request')
Response = TypeVar('Response')

class BaseUseCase(ABC, Generic[Request, Response]):
    
    @abstractmethod
    async def execute(self, request: Request) -> Response:
        ...
    