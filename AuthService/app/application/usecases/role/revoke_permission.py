from domain.exceptions.permission import PermissionNotFoundException
from domain.exceptions.role import RoleDoesNotHavePermissionException, RoleNotFoundException
from domain.exceptions.identifier import InvalidIdentifierException
from domain.repositories.uow import BaseUnitOfWork
from application.dto.role import RoleRevokePermissionRequestDTO
from application.usecases.base import BaseUseCase


class BaseRoleRevokePermissionUseCase(BaseUseCase[RoleRevokePermissionRequestDTO, None]):
    ...
    
class RoleRevokePermissionUseCase(BaseRoleRevokePermissionUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: RoleRevokePermissionRequestDTO) -> None:
        async with self.uow as uow:
            role = None
            if request.role_identifier.startswith("name_"):
                name = request.role_identifier[5:]
                role = await uow.roles.get_by_name(
                    name=name,
                    load_permissions=True
                )
            elif request.role_identifier.startswith("oid_"):
                oid = request.role_identifier[4:]
                role = await uow.roles.get_by_oid(
                    oid=oid,
                    load_permissions=True
                )
            else:
                raise InvalidIdentifierException(request.role_identifier)
                
            if not role:
                raise RoleNotFoundException(request.role_identifier)
            
            permission = None
            if request.permission_identifier.startswith("code_"):
                code = request.permission_identifier[5:]                
                permission = await uow.permissions.get_by_code(code)
            elif request.permission_identifier.startswith("oid_"):
                oid = request.permission_identifier[4:]
                permission = await uow.permissions.get_by_oid(oid)
            else:
                raise InvalidIdentifierException(request.permission_identifier)
                
            if not permission:
                raise PermissionNotFoundException(request.permission_identifier) 

            if not role.has_permission(permission):
                raise RoleDoesNotHavePermissionException(
                    role_name=role.name,
                    permission_code=permission.code
                )
            
            role.revoke_permission(permission)
            
            await uow.roles.update(role)
             