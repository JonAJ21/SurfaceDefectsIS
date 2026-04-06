from domain.exceptions.identifier import InvalidIdentifierException
from domain.exceptions.permission import PermissionNotFoundException
from domain.repositories.uow import BaseUnitOfWork
from application.dto.permission import GetPermissionByIdentifierRequestDTO, GetPermissionResponseDTO
from application.usecases.base import BaseUseCase


class BasePermissionGetByIdentifierUseCase(BaseUseCase[GetPermissionByIdentifierRequestDTO, GetPermissionResponseDTO]):
    ...
    
class PermissionGetByIdentifierUseCase(BasePermissionGetByIdentifierUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: GetPermissionByIdentifierRequestDTO) -> GetPermissionResponseDTO:
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
                raise PermissionNotFoundException(request.identifier)
            
            return GetPermissionResponseDTO(
                oid=permission.oid,
                code=permission.code,
                description=permission.description
            )