from domain.exceptions.identifier import InvalidIdentifierException
from domain.exceptions.permission import PermissionNotFoundException, PermissionWithCodeAlreadyExistsException
from domain.repositories.uow import BaseUnitOfWork
from application.dto.permission import PermissionUpdateRequestDTO, PermissionUpdateResponseDTO
from application.usecases.base import BaseUseCase


class BasePermissionUpdateUseCase(BaseUseCase[PermissionUpdateRequestDTO, PermissionUpdateResponseDTO]):
    ...
    
class PermissionUpdateUseCase(BasePermissionUpdateUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: PermissionUpdateRequestDTO) -> PermissionUpdateResponseDTO:
        async with self.uow as uow:
            permission = None
            if request.identifier.startswith("code_"):
                code = request.identifier[5:]
                permission = await uow.permissions.get_by_code(code)
            elif request.identifier.startswith("oid_"):
                oid = request.identifier[4:]
                permission = await uow.permissions.get_by_oid(oid)
            else:
                raise InvalidIdentifierException(request.identifier)
                
            if not permission:
                raise PermissionNotFoundException(request.code)
            
            if request.new_code is not None:
                existing_permission = await uow.permissions.get_by_code(request.new_code)
                if existing_permission and existing_permission.oid != permission.oid:
                    raise PermissionWithCodeAlreadyExistsException(request.new_code)
                permission.change_code(request.new_code)
            if request.new_description is not None:
                permission.change_description(request.new_description)
            
            await uow.permissions.update(permission)
             
            return PermissionUpdateResponseDTO(
                oid=permission.oid,
                code=permission.code,
                description=permission.description
            )