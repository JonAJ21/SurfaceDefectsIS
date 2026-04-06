from typing import Optional

from domain.values.email import Email
from application.dto.permission import GetPermissionResponseDTO
from application.dto.role import GetRoleResponseDTO
from domain.exceptions.user import UserNotFoundException
from domain.exceptions.identifier import InvalidIdentifierException
from domain.repositories.uow import BaseUnitOfWork
from application.dto.user import   GetUserByIdentifierRequestDTO, GetUserLoginHistoryResponseDTO, GetUserResponseDTO, GetUserSessionResponseDTO
from application.usecases.base import BaseUseCase


class BaseUserGetByIdentifierUseCase(BaseUseCase[GetUserByIdentifierRequestDTO, GetUserResponseDTO]):
    ...
    
class UserGetByIdentifierUseCase(BaseUserGetByIdentifierUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
    
    async def execute(self, request: GetUserByIdentifierRequestDTO) -> GetUserResponseDTO:
        async with self.uow as uow:
            user = None
            if request.identifier.startswith("email_"):
                email = request.identifier[6:]
                user = await uow.users.get_by_email(
                    email=Email(email),
                    load_sessions=request.load_sessions,
                    load_roles=request.load_roles,
                    load_permissions=request.load_permissions,
                    load_login_history=request.load_login_history,
                    login_history_limit=request.login_history_limit,
                    login_history_offset=request.login_history_offset
                )
            elif request.identifier.startswith("oid_"):
                oid = request.identifier[4:]
                user = await uow.users.get_by_oid(
                    oid=oid,
                    load_sessions=request.load_sessions,
                    load_roles=request.load_roles,
                    load_permissions=request.load_permissions,
                    load_login_history=request.load_login_history,
                    login_history_limit=request.login_history_limit,
                    login_history_offset=request.login_history_offset
                )
            else:
                raise InvalidIdentifierException(request.identifier)
            
            if not user:
                raise UserNotFoundException(request.identifier)
            
            role_dtos: Optional[list[GetRoleResponseDTO]] = [
                GetRoleResponseDTO(
                    oid=role.oid,
                    name=role.name,
                    description=role.description,
                    created_at=role.created_at,
                    updated_at=role.updated_at,
                    permissions=[GetPermissionResponseDTO(
                        oid=permission.oid,
                        code=permission.code,
                        description=permission.description
                    ) for permission in role.permissions] if role.permissions is not None else None
                ) for role in user.roles
            ] if user.roles is not None else None
                    
            login_history_dtos: Optional[list[GetUserLoginHistoryResponseDTO]] = [
                GetUserLoginHistoryResponseDTO(
                    oid=login_history.oid,
                    user_oid=login_history.user_oid,
                    login_at=login_history.login_at,
                    ip_address=login_history.ip_address,
                    user_agent=login_history.user_agent,
                    provider=login_history.provider,
                    success=login_history.success,
                    failure_reason=login_history.failure_reason
                ) for login_history in user.login_history
            ] if user.login_history is not None else None
            
            session_dtos: Optional[list[GetUserSessionResponseDTO]] = [
                GetUserSessionResponseDTO(
                    oid=session.oid,
                    user_oid=session.user_oid,
                    user_agent=session.user_agent,
                    provider=session.provider,
                    refresh_token_oid=session.refresh_token_oid,
                    refreshed_at=session.refreshed_at,
                    created_at=session.created_at
                ) for session in user.sessions
            ] if user.sessions is not None else None
            

            return GetUserResponseDTO(
                oid=user.oid,
                email=user.email.value,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                roles=role_dtos,
                sessions=session_dtos,
                login_history=login_history_dtos
            )