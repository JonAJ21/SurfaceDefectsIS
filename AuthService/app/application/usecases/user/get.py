from domain.entities.user import User
from domain.repositories.uow import BaseUnitOfWork
from application.dto.user import GetUserResponseDTO, GetUsersRequestDTO
from application.usecases.base import BaseUseCase


class BaseUsersGetUseCase(BaseUseCase[GetUsersRequestDTO, list[GetUserResponseDTO]]):
    ...
    
class UsersGetUseCase(BaseUsersGetUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: GetUsersRequestDTO) -> GetUserResponseDTO:
        async with self.uow as uow:
            users: list[User] = await uow.users.get(
                limit=request.limit,
                offset=request.offset
            )
            
            return [GetUserResponseDTO(
                oid=user.oid,
                email=user.email.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
            ) for user in users]
