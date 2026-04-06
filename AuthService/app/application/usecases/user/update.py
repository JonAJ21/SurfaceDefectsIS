

from typing import Optional

from domain.exceptions.role import RoleNotFoundException
from application.dto.role import GetRoleResponseDTO
from domain.services.password import BasePasswordService
from domain.exceptions.user import UserNotFoundException, UserWithEmailAlreadyExistsExcception
from domain.exceptions.identifier import InvalidIdentifierException
from domain.values.email import Email
from domain.repositories.uow import BaseUnitOfWork
from application.dto.user import GetUserResponseDTO, UserUpdateByIdentifierRequestDTO
from application.usecases.base import BaseUseCase


class BaseUserUpdateByIdentifierUseCase(BaseUseCase[UserUpdateByIdentifierRequestDTO, GetUserResponseDTO]):
    ...
    
class UserUpdateByIdentifierUseCase(BaseUserUpdateByIdentifierUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork,
        password_service: BasePasswordService
    ):
        self.uow = uow
        self.password_service = password_service
    
    async def execute(self, request: UserUpdateByIdentifierRequestDTO) -> GetUserResponseDTO:
        async with self.uow as uow:
            user = None
            
            load_roles = False
            if request.role_identifiers_to_add or request.role_identifiers_to_remove: 
                load_roles = True
            
            if request.identifier.startswith("email_"):
                email = request.identifier[6:]
                user = await uow.users.get_by_email(
                    email=Email(email),
                    load_roles=load_roles
                )
            elif request.identifier.startswith("oid_"):
                oid = request.identifier[4:]
                user = await uow.users.get_by_oid(
                    oid=oid,
                    load_roles=load_roles
                )
            else:
                raise InvalidIdentifierException(request.identifier)
                
            if not user:
                raise UserNotFoundException(request.identifier)
            
            if request.new_email is not None:
                existing_user = await uow.users.get_by_email(request.new_email)
                if existing_user and existing_user.oid != user.oid:
                    raise UserWithEmailAlreadyExistsExcception(request.new_email)
                user.change_email(request.email)
            if request.new_password is not None:
                user.change_password(request.old_password, request.new_password, self.password_service)    
            if request.new_is_active is not None:
                if request.new_is_active:
                    user.activate()
                else:
                    user.deactivate()
            if request.new_is_verified is not None:
                if request.new_is_verified:
                    user.verify()
                else:
                    user.unverify()
            if request.role_identifiers_to_add:
                for identifier in request.role_identifiers_to_add:
                    if identifier.startswith("name_"):
                        name = identifier[5:]
                        role = await uow.roles.get_by_name(name)
                    elif identifier.startswith("oid_"):
                        oid = identifier[4:]
                        role = await uow.roles.get_by_oid(oid)
                    else:
                        raise InvalidIdentifierException(identifier)
                    if not role:
                        raise RoleNotFoundException(identifier)
                    user.assign_role(role)
            if request.role_identifiers_to_remove:
                for identifier in request.role_identifiers_to_remove:
                    if identifier.startswith("name_"):
                        name = identifier[5:]
                        role = await uow.roles.get_by_name(name)
                    elif identifier.startswith("oid_"):
                        oid = identifier[4:]
                        role = await uow.roles.get_by_oid(oid)
                    else:
                        raise InvalidIdentifierException(identifier)
                    if not role:
                        raise RoleNotFoundException(identifier)
                    user.revoke_role(role)
            
            await uow.users.update(user)
            
            role_dtos: Optional[list[GetRoleResponseDTO]] = [
                GetRoleResponseDTO(
                    oid=role.oid,
                    name=role.name,
                    description=role.description,
                    created_at=role.created_at,
                    updated_at=role.updated_at,
                    permissions=None
                ) for role in user.roles
            ] if user.roles is not None else None
            
            return GetUserResponseDTO(
                oid=user.oid,
                email=user.email.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                roles=role_dtos
            )
            
           