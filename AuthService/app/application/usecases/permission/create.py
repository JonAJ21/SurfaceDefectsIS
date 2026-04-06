from domain.entities.permission import Permission
from domain.exceptions.permission import PermissionWithCodeAlreadyExistsException
from application.dto.permission import PermissionCreateRequestDTO, PermissionCreateResponseDTO
from domain.repositories.uow import BaseUnitOfWork
from application.usecases.base import BaseUseCase


class BasePermissionCreateUseCase(BaseUseCase[PermissionCreateRequestDTO, PermissionCreateResponseDTO]):
    ...
    
class PermissionCreateUseCase(BasePermissionCreateUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: PermissionCreateRequestDTO) -> PermissionCreateResponseDTO:
        async with self.uow as uow:
            existing_permission = await uow.permissions.get_by_code(request.code)
            if existing_permission:
                raise PermissionWithCodeAlreadyExistsException(request.code)
            
            permission = Permission(
                code=request.code,
                description=request.description
            )
            
            await uow.permissions.create(permission)
            
            return PermissionCreateResponseDTO(
                oid=permission.oid,
                code=permission.code,
                description=permission.description
            )