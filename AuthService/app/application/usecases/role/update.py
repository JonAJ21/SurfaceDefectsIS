from domain.exceptions.role import RoleNotFoundException, RoleWithNameAlreadyExistsException
from domain.exceptions.identifier import InvalidIdentifierException
from domain.repositories.uow import BaseUnitOfWork
from application.dto.role import RoleUpdateRequestDTO, RoleUpdateResponseDTO
from application.usecases.base import BaseUseCase


class BaseRoleUpdateUseCase(BaseUseCase[RoleUpdateRequestDTO, RoleUpdateResponseDTO]):
    ...
    
class RoleUpdateUseCase(BaseRoleUpdateUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: RoleUpdateRequestDTO) -> RoleUpdateResponseDTO:
        async with self.uow as uow:
            role = None
            if request.identifier.startswith("name_"):
                name = request.identifier[5:]
                role = await uow.roles.get_by_name(name)
            elif request.identifier.startswith("oid_"):
                oid = request.identifier[4:]
                role = await uow.roles.get_by_oid(oid)
            else:
                raise InvalidIdentifierException(request.identifier)
                
            if not role:
                raise RoleNotFoundException(request.identifier)
            
            if request.new_name is not None:
                existing_role = await uow.roles.get_by_name(request.new_name)
                if existing_role and existing_role.oid != role.oid:
                    raise RoleWithNameAlreadyExistsException(request.new_name)
                role.change_name(request.new_name)
            if request.new_description is not None:
                role.change_description(request.new_description)
            
            await uow.roles.update(role)
             
            return RoleUpdateResponseDTO(
                oid=role.oid,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at
            )