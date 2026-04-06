from application.dto.permission import GetPermissionResponseDTO
from domain.exceptions.role import RoleNotFoundException
from domain.exceptions.identifier import InvalidIdentifierException
from domain.repositories.uow import BaseUnitOfWork
from application.dto.role import GetRoleByIdentifierRequestDTO, GetRoleResponseDTO
from application.usecases.base import BaseUseCase


class BaseRoleGetByIdentifierUseCase(BaseUseCase[GetRoleByIdentifierRequestDTO, GetRoleResponseDTO]):
    ...
    
class RoleGetByIdentifierUseCase(BaseRoleGetByIdentifierUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: GetRoleByIdentifierRequestDTO) -> GetRoleResponseDTO:
        async with self.uow as uow:
            role = None
            if request.identifier.startswith("name_"):
                name = request.identifier[5:]
                role = await uow.roles.get_by_name(
                    name=name,
                    load_permissions=request.load_permissions
                )
            elif request.identifier.startswith("oid_"):
                oid = request.identifier[4:]
                role = await uow.roles.get_by_oid(
                    oid=oid,
                    load_permissions=request.load_permissions
                )
            else:
                raise InvalidIdentifierException(request.identifier)
            
            if not role:
                raise RoleNotFoundException(request.identifier)
            
            
            permissions = None
            if request.load_permissions:
                permissions = [GetPermissionResponseDTO(
                    oid=permission.oid,
                    code=permission.code,
                    description=permission.description
                ) for permission in role.permissions]
            
            return GetRoleResponseDTO(
                oid=role.oid,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at,
                permissions=permissions
            )