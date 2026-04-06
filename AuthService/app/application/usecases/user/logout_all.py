from domain.repositories.uow import BaseUnitOfWork
from application.dto.user import UserLogoutRequestDTO
from application.usecases.base import BaseUseCase


class BaseUserLogoutAllUseCase(BaseUseCase[UserLogoutRequestDTO, None]):
    ...

class UserLogoutAllUseCase(BaseUserLogoutAllUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork,
    ):
        self.uow = uow
        
    async def execute(self, request: UserLogoutRequestDTO) -> None:
        async with self.uow as uow:
            await uow.sessions.delete_all_by_user_oid(request.user_oid)
            

                