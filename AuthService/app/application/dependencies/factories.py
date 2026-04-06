from functools import cache

from fastapi import Depends

from application.usecases.user.get import BaseUsersGetUseCase, UsersGetUseCase
from application.usecases.user.verification_by_email import BaseEmailVerificationByEmailUseCase, EmailVerificationByEmailUseCase
from core.config.settings import settings
from domain.services.email import BaseEmailService
from infrastructure.services.email import SMTPEmailService
from application.usecases.user.update import BaseUserUpdateByIdentifierUseCase, UserUpdateByIdentifierUseCase
from application.usecases.user.logout_all import BaseUserLogoutAllUseCase, UserLogoutAllUseCase
from application.usecases.user.logout import BaseUserLogoutUseCase, UserLogoutUseCase
from application.usecases.user.refresh_token import BaseUserRefreshTokenUseCase, UserRefreshUseCase
from application.usecases.user.auth import BaseUserAuthUseCase, UserAuthUseCase
from application.usecases.user.get_by_identifier import BaseUserGetByIdentifierUseCase, UserGetByIdentifierUseCase
from domain.services.token import BaseTokenService
from infrastructure.services.token import JSONWebTokenService
from application.usecases.role.revoke_permission import BaseRoleRevokePermissionUseCase, RoleRevokePermissionUseCase
from application.usecases.role.assign_permission import BaseRoleAssignPermissionUseCase, RoleAssignPermissionUseCase
from application.usecases.role.delete import BaseRoleDeleteUseCase, RoleDeleteUseCase
from application.usecases.role.update import BaseRoleUpdateUseCase, RoleUpdateUseCase
from application.usecases.role.get_by_identifier import BaseRoleGetByIdentifierUseCase, RoleGetByIdentifierUseCase
from application.usecases.permission.get_by_identifier import BasePermissionGetByIdentifierUseCase, PermissionGetByIdentifierUseCase
from application.usecases.permission.delete import BasePermissionDeleteUseCase, PermissionDeleteUseCase
from application.usecases.permission.update import BasePermissionUpdateUseCase, PermissionUpdateUseCase
from application.usecases.permission.get_list import BasePermissionsGetListUseCase, PermissionsGetListUseCase
from application.usecases.permission.create import BasePermissionCreateUseCase, PermissionCreateUseCase
from application.usecases.role.get_list import BaseRolesGetListUseCase, RolesGetListUseCase
from application.usecases.role.create import BaseRoleCreateUseCase, RoleCreateUseCase
from domain.services.password import BasePasswordService
from infrastructure.database.session import async_session_maker
from infrastructure.repositories.uow import SQLAlchemyUnitOfWork
from domain.repositories.uow import BaseUnitOfWork
from infrastructure.services.password import BcryptPasswordService
from infrastructure.database.redis import get_redis
from application.usecases.user.register import BaseUserRegisterUseCase, UserRegisterUseCase
from application.dependencies.registrator import add_factory_to_mapper
from application.usecases.user.login import BaseUserLoginUseCase, UserLoginUseCase

# Base

def uow_factory() -> BaseUnitOfWork:
    return SQLAlchemyUnitOfWork(session_factory=async_session_maker, redis=get_redis())
          
@cache
def password_service_factory() -> BasePasswordService:
    return BcryptPasswordService()

@cache 
def token_service_factory() -> BaseTokenService:
    return JSONWebTokenService()

@cache
def email_service_factory() -> BaseEmailService:
    return SMTPEmailService(
        smtp_server=settings.smtp_server,
        smtp_port=settings.smtp_port,
        smtp_address=settings.email_address,
        smtp_password=settings.email_password
    )


# User


@add_factory_to_mapper(BaseUserRegisterUseCase)
@cache
def register_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory),
    password_service: BasePasswordService = Depends(password_service_factory)
) -> BaseUserRegisterUseCase:
    return UserRegisterUseCase(uow, password_service)


@add_factory_to_mapper(BaseUserLoginUseCase)
@cache
def login_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory),
    password_service: BasePasswordService = Depends(password_service_factory),
    jwt_service: BaseTokenService = Depends(token_service_factory),
) -> BaseUserLoginUseCase:
    return UserLoginUseCase(
        uow=uow,
        password_service=password_service,
        jwt_service=jwt_service
    )

@add_factory_to_mapper(BaseUserRefreshTokenUseCase)
@cache
def user_refresh_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory),
    jwt_service: BaseTokenService = Depends(token_service_factory)
) -> BaseUserRefreshTokenUseCase:
    return UserRefreshUseCase(uow, jwt_service)

@add_factory_to_mapper(BaseUserLogoutUseCase)
@cache
def user_logout_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseUserLogoutUseCase:
    return UserLogoutUseCase(uow)

@add_factory_to_mapper(BaseUserLogoutAllUseCase)
@cache
def user_logout_all_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseUserLogoutAllUseCase:
    return UserLogoutAllUseCase(uow)

@add_factory_to_mapper(BaseUserGetByIdentifierUseCase)
@cache
def user_get_by_identifier_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseUserGetByIdentifierUseCase:
    return UserGetByIdentifierUseCase(uow)

@add_factory_to_mapper(BaseUsersGetUseCase)
@cache
def users_get_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseUsersGetUseCase:
    return UsersGetUseCase(uow)

@add_factory_to_mapper(BaseUserAuthUseCase)
@cache
def user_auth_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory),
    jwt_service: BaseTokenService = Depends(token_service_factory)
) -> BaseUserAuthUseCase:
    return UserAuthUseCase(uow, jwt_service)

@add_factory_to_mapper(BaseUserUpdateByIdentifierUseCase)
@cache
def user_update_by_identifier_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory),
    password_service: BasePasswordService = Depends(password_service_factory)
) -> BaseUserUpdateByIdentifierUseCase:
    return UserUpdateByIdentifierUseCase(uow, password_service)

@add_factory_to_mapper(BaseEmailVerificationByEmailUseCase)
@cache
def email_verification_by_email_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory),
    email_service: BaseEmailService = Depends(email_service_factory),
    jwt_service: BaseTokenService = Depends(token_service_factory)
) -> BaseEmailVerificationByEmailUseCase:
    return EmailVerificationByEmailUseCase(
        uow=uow,
        email_service=email_service,
        jwt_service=jwt_service
)

# Role

@add_factory_to_mapper(BaseRoleCreateUseCase)
@cache
def role_create_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseRoleCreateUseCase:
    return RoleCreateUseCase(uow)

@add_factory_to_mapper(BaseRolesGetListUseCase)
@cache
def roles_get_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseRolesGetListUseCase:
    return RolesGetListUseCase(uow)

@add_factory_to_mapper(BaseRoleGetByIdentifierUseCase)
@cache
def role_get_by_code_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseRoleGetByIdentifierUseCase:
    return RoleGetByIdentifierUseCase(uow)

@add_factory_to_mapper(BaseRoleUpdateUseCase)
@cache
def role_update_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseRoleUpdateUseCase:
    return RoleUpdateUseCase(uow)

@add_factory_to_mapper(BaseRoleDeleteUseCase)
@cache
def role_delete_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseRoleDeleteUseCase:
    return RoleDeleteUseCase(uow)

@add_factory_to_mapper(BaseRoleAssignPermissionUseCase)
@cache
def role_assign_permission_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseRoleAssignPermissionUseCase:
    return RoleAssignPermissionUseCase(uow)

@add_factory_to_mapper(BaseRoleRevokePermissionUseCase)
@cache
def role_revoke_permission_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BaseRoleRevokePermissionUseCase:
    return RoleRevokePermissionUseCase(uow)


# Permission

@add_factory_to_mapper(BasePermissionCreateUseCase)
@cache
def permission_create_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BasePermissionCreateUseCase:
    return PermissionCreateUseCase(uow)

@add_factory_to_mapper(BasePermissionGetByIdentifierUseCase)
@cache
def permission_get_by_code_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BasePermissionGetByIdentifierUseCase:
    return PermissionGetByIdentifierUseCase(uow)

@add_factory_to_mapper(BasePermissionsGetListUseCase)
@cache
def permissions_get_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BasePermissionsGetListUseCase:
    return PermissionsGetListUseCase(uow)

@add_factory_to_mapper(BasePermissionUpdateUseCase)
@cache
def permission_update_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BasePermissionUpdateUseCase:
    return PermissionUpdateUseCase(uow)

@add_factory_to_mapper(BasePermissionDeleteUseCase)
@cache
def permission_delete_usecase_factory(
    uow: BaseUnitOfWork = Depends(uow_factory)
) -> BasePermissionDeleteUseCase:
    return PermissionDeleteUseCase(uow)