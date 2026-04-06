from domain.repositories.uow import BaseUnitOfWork
from application.dto.role import GetRoleResponseDTO, GetRolesRequestDTO
from application.usecases.base import BaseUseCase


class BaseRolesGetListUseCase(BaseUseCase[GetRolesRequestDTO, list[GetRoleResponseDTO]]):
    ...
    
class RolesGetListUseCase(BaseRolesGetListUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: GetRolesRequestDTO) -> list[GetRoleResponseDTO]:
        async with self.uow as uow:
            roles = await uow.roles.get(
               limit=request.limit,
               offset=request.offset
            )
            return [GetRoleResponseDTO(
                oid=role.oid,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at
            ) for role in roles]