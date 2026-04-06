from domain.repositories.uow import BaseUnitOfWork
from application.dto.permission import GetPermissionResponseDTO, GetPermissionsRequestDTO
from application.usecases.base import BaseUseCase


class BasePermissionsGetListUseCase(BaseUseCase[GetPermissionsRequestDTO, list[GetPermissionResponseDTO]]):
    ...
    
class PermissionsGetListUseCase(BasePermissionsGetListUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: GetPermissionsRequestDTO) -> list[GetPermissionResponseDTO]:
        async with self.uow as uow:
            permissions = await uow.permissions.get(
               limit=request.limit,
               offset=request.offset
            )
            return [GetPermissionResponseDTO(
                oid=permission.oid,
                code=permission.code,
                description=permission.description
            ) for permission in permissions]