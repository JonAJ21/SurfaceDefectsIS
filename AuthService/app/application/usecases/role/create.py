from domain.exceptions.role import RoleWithNameAlreadyExistsException
from domain.entities.role import Role
from domain.repositories.uow import BaseUnitOfWork
from application.dto.role import RoleCreateRequestDTO, RoleCreateResponseDTO
from application.usecases.base import BaseUseCase


class BaseRoleCreateUseCase(BaseUseCase[RoleCreateRequestDTO, RoleCreateResponseDTO]):
    ...
    
class RoleCreateUseCase(BaseRoleCreateUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: RoleCreateRequestDTO) -> RoleCreateResponseDTO:
        async with self.uow as uow:
            existing_role = await uow.roles.get_by_name(request.name)
            if existing_role:
                raise RoleWithNameAlreadyExistsException(request.name)
            
            role = Role(
                name=request.name,
                description=request.description
            )    
            await uow.roles.create(role)
            
            return RoleCreateResponseDTO(
                oid=role.oid,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at
            )