from domain.repositories.uow import BaseUnitOfWork
from application.dto.user import UserLogoutRequestDTO
from application.usecases.base import BaseUseCase


class BaseUserLogoutUseCase(BaseUseCase[UserLogoutRequestDTO, None]):
    ...

class UserLogoutUseCase(BaseUserLogoutUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork,
    ):
        self.uow = uow
        
    async def execute(self, request: UserLogoutRequestDTO) -> None:
        async with self.uow as uow:
            await uow.sessions.delete_by_oid(request.session_oid)
            

                