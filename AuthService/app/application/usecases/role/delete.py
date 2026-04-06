from domain.exceptions.role import RoleNotFoundException
from domain.exceptions.identifier import InvalidIdentifierException
from domain.repositories.uow import BaseUnitOfWork
from application.dto.role import RoleDeleteRequestDTO
from application.usecases.base import BaseUseCase


class BaseRoleDeleteUseCase(BaseUseCase[RoleDeleteRequestDTO, None]):
    ...
    
class RoleDeleteUseCase(BaseRoleDeleteUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: RoleDeleteRequestDTO) -> None:
        async with self.uow as uow:
            role = None
            if request.identifier.startswith("name_"):
                name = request.identifier[5:]
                role = await uow.roles.get_by_name(name)
            elif request.identifier.startswith("oid_"):
                oid = request.identifier[4:]
                role = await uow.roles.get_by_oid(oid)
            else:
                raise InvalidIdentifierException(identifier=request.identifier)
                
            if not role:
                raise RoleNotFoundException(request.identifier)
            
            await uow.roles.delete(role)