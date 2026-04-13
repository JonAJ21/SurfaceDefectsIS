from typing import Optional

from fastapi import APIRouter, Depends, Form,  Path, Query, Request

from application.usecases.user.get import BaseUsersGetUseCase
from core.config.settings import settings
from application.usecases.user.verification_by_email import BaseEmailVerificationByEmailUseCase
from application.usecases.user.update import BaseUserUpdateByIdentifierUseCase
from application.usecases.user.logout_all import BaseUserLogoutAllUseCase
from application.usecases.user.logout import BaseUserLogoutUseCase
from application.usecases.user.refresh_token import BaseUserRefreshTokenUseCase
from application.usecases.user.auth import BaseUserAuthUseCase
from application.usecases.user.get_by_identifier import BaseUserGetByIdentifierUseCase
from application.dto.user import EmailVerificationByEmailRequestDTO, GetUserByIdentifierRequestDTO, GetUsersRequestDTO, UserAuthRequestDTO, UserAuthResponseDTO, UserLoginRequestDTO, UserLogoutRequestDTO, UserRefreshTokenRequestDTO, UserRegisterRequestDTO, UserUpdateByIdentifierRequestDTO
from application.usecases.user.login import BaseUserLoginUseCase
from presentation.api.v1.schemas.user import GetUserResponseSchema, GetUserSessionOidsResponseSchema, GetUserSessionResponseSchema, GetUsersResponseSchema, UserLoggedOutResponseSchema, UserLoginResponseSchema, UserRefreshTokenResponseSchema, UserRegisterRequestSchema, UserRegisterResponseSchema, UserVerifyByEmailResponseSchema
from application.usecases.user.register import BaseUserRegisterUseCase
from presentation.api.v1.utils.security import oauth2_scheme
from presentation.api.v1.utils.exception import handle_exceptions

router = APIRouter(
    prefix="/v1",
    tags=["user"]
)

@router.post(
    "/users/register",
    responses={
        200: {"description": "User registered successfully", "model": UserRegisterResponseSchema},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def register_user(
    schema: UserRegisterRequestSchema,
    register_usecase: BaseUserRegisterUseCase = Depends(),
):
    request_dto = UserRegisterRequestDTO(
        email=schema.email,
        password=schema.password,
        password_confirm=schema.password_confirm
    )
    result = await register_usecase.execute(request_dto)
    return UserRegisterResponseSchema.from_dto(result)


@router.post(
    "/users/login",
    responses={
        200: {"description": "User logged in successfully", "model": UserLoginResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    login_usecase: BaseUserLoginUseCase = Depends(),
):
    request_dto = UserLoginRequestDTO(
        email=username,
        password=password,
        ip_address=request.client.host,
        user_agent=request.headers["user-agent"],
    )
    
    result = await login_usecase.execute(request_dto)
    return UserLoginResponseSchema.from_dto(result)

@router.post(
    "/users/me/refresh",
    responses={
        200: {"description": "Session refreshed successfully", "model": UserRefreshTokenResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def refresh_token(
    request: Request,
    refresh_token: str = Form(...),
    refresh_usecase: BaseUserRefreshTokenUseCase = Depends(),
    _: str = Depends(oauth2_scheme),
):
    request_dto = UserRefreshTokenRequestDTO(
        refresh_token=refresh_token,
        user_agent=request.headers["user-agent"],
        provider="local"
    )
    
    result = await refresh_usecase.execute(request_dto)
    return UserRefreshTokenResponseSchema.from_dto(result)   

    
@router.delete(
    "/users/me/logout",
    responses={
        200: {"description": "User logged out and session deleted successfully", "model": UserLoggedOutResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def logout_user(
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    logout_usecase: BaseUserLogoutUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.logout']
    )
    auth_result = await auth_usecase.execute(auth_request_dto)
    request_dto = UserLogoutRequestDTO(
        user_oid=auth_result.user_oid,
        session_oid=auth_result.session_oid
    )
    await logout_usecase.execute(request_dto)
    return UserLoggedOutResponseSchema()
    
        
@router.delete(
    "/users/me/logout-all",
    responses={
        200: {"description": "User logged out and session deleted successfully", "model": UserLoggedOutResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def logout_all_user(
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    logout_usecase: BaseUserLogoutAllUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.logout']
    )
    auth_result = await auth_usecase.execute(auth_request_dto)
    request_dto = UserLogoutRequestDTO(
        user_oid=auth_result.user_oid,
        session_oid=auth_result.session_oid
    )
    await logout_usecase.execute(request_dto)
    return UserLoggedOutResponseSchema()


@router.get(
    "/users",
    responses={
        200: {"description": "Users got successfully", "model": GetUsersResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def get_users(
    access_token: str = Depends(oauth2_scheme),
    offset: int = Query(ge=0, default=0),
    limit: int = Query(ge=0, default=10),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BaseUsersGetUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.get']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = GetUsersRequestDTO(
        offset=offset,
        limit=limit
    )
    result = await get_usecase.execute(request_dto)
    return GetUsersResponseSchema.from_dto(result)


@router.get(
    "/users/me",
    responses={
        200: {"description": "User got successfully", "model": GetUserResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    load_sessions: Optional[bool] = Query(default=None),
    load_roles: Optional[bool] = Query(default=None),
    load_permissions: Optional[bool] = Query(default=None),
    load_login_history: Optional[bool] = Query(default=None),
    login_history_offset: Optional[int] = Query(default=None),
    login_history_limit: Optional[int] = Query(default=None),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BaseUserGetByIdentifierUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.get-me']
    )
    
    auth_result = await auth_usecase.execute(auth_request_dto)
    request_dto = GetUserByIdentifierRequestDTO(
        identifier=f"oid_{auth_result.user_oid}",
        load_sessions=load_sessions,
        load_roles=load_roles,
        load_permissions=load_permissions,
        load_login_history=load_login_history,
        login_history_offset=login_history_offset,
        login_history_limit=login_history_limit
    )
    result = await get_usecase.execute(request_dto)
    return GetUserResponseSchema.from_dto(result)


@router.get(
    "/users/me/session",
    responses={
        200: {"description": "User session got successfully", "model": GetUserSessionOidsResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_current_user_session_oids(
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.get-me']
    )
    
    auth_result = await auth_usecase.execute(auth_request_dto)
    
    return GetUserSessionOidsResponseSchema.from_dto(auth_result)


@router.get(
    "/users/{identifier}",
    responses={
        200: {"description": "User got successfully", "model": GetUserResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def get_user_by_identifier(
    identifier: str = Path(..., description="User name or oid"),
    load_sessions: Optional[bool] = Query(default=None),
    load_roles: Optional[bool] = Query(default=None),
    load_permissions: Optional[bool] = Query(default=None),
    load_login_history: Optional[bool] = Query(default=None),
    login_history_offset: Optional[int] = Query(default=None),
    login_history_limit: Optional[int] = Query(default=None),
    access_token: str = Depends(oauth2_scheme), 
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BaseUserGetByIdentifierUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.get']
    )
    await auth_usecase.execute(auth_request_dto)
    
    request_dto = GetUserByIdentifierRequestDTO(
        identifier=identifier,
        load_sessions=load_sessions,
        load_roles=load_roles,
        load_permissions=load_permissions,
        load_login_history=load_login_history,
        login_history_offset=login_history_offset,
        login_history_limit=login_history_limit
    )
    result = await get_usecase.execute(request_dto)
    return GetUserResponseSchema.from_dto(result)

    
@router.post(
    "/users/{user_identifier}/roles/{role_identifier}",
    responses={
        200: {"description": "Role assigned successfully", "model": GetUserResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def assign_role_to_user(
    access_token : str = Depends(oauth2_scheme),
    user_identifier: str = Path(..., description="User email or oid"),
    role_identifier: str = Path(..., description="Role name or oid"),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BaseUserUpdateByIdentifierUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.assign-role']
    )
    
    await auth_usecase.execute(auth_request_dto)
    request_dto = UserUpdateByIdentifierRequestDTO(
        identifier=user_identifier,
        role_identifiers_to_add=[role_identifier],
    )
    result = await update_usecase.execute(request_dto)
    return GetUserResponseSchema.from_dto(result)

@router.delete(
    "/users/{user_identifier}/roles/{role_identifier}",
    responses={
        200: {"description": "Role revoked successfully", "model": GetUserResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def revoke_role_from_user(
    access_token : str = Depends(oauth2_scheme),
    user_identifier: str = Path(..., description="User email or oid"),
    role_identifier: str = Path(..., description="Role name or oid"),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BaseUserUpdateByIdentifierUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.revoke-role']
    )
    
    await auth_usecase.execute(auth_request_dto)
    request_dto = UserUpdateByIdentifierRequestDTO(
        identifier=user_identifier,
        role_identifiers_to_remove=[role_identifier],
    )
    result = await update_usecase.execute(request_dto)
    return GetUserResponseSchema.from_dto(result)

    
@router.post(
    "/users/me/verify-by-email",
    responses={
        200: {"description": "Verification email sent successfully", "model": UserVerifyByEmailResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def email_verify_by_email(
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BaseEmailVerificationByEmailUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.verify']
    )

    auth_result = await auth_usecase.execute(auth_request_dto)
    request_dto = EmailVerificationByEmailRequestDTO(
        user_oid=auth_result.user_oid
    )
    await update_usecase.execute(request_dto)
    return UserVerifyByEmailResponseSchema()

        
@router.get(
    "/users/me/verify",
    responses={
        200: {"description": "User email verified successfully", "model": GetUserResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def verify_user(
    access_token : str = Query(default=None),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BaseUserUpdateByIdentifierUseCase = Depends(),
    _: str = Depends(oauth2_scheme),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
    )
    auth_result = await auth_usecase.execute(auth_request_dto)
    request_dto = UserUpdateByIdentifierRequestDTO(
        identifier=f"oid_{auth_result.user_oid}",
        new_is_verified=True
    )
    result = await update_usecase.execute(request_dto)
    return GetUserResponseSchema.from_dto(result)
        
        
@router.patch(
    "/users/{identifier}/activate",
    responses={
        200: {"description": "User activated successfully", "model": GetUserResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def activate_user(
    identifier: str = Path(..., description="User email or oid"),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BaseUserUpdateByIdentifierUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.activate']
    )
    
    await auth_usecase.execute(auth_request_dto)
    request_dto = UserUpdateByIdentifierRequestDTO(
        identifier=identifier,
        new_is_active=True
    )
    result = await update_usecase.execute(request_dto)
    return GetUserResponseSchema.from_dto(result)

        
@router.patch(
    "/users/{identifier}/deactivate",
    responses={
        200: {"description": "User deactivated successfully", "model": GetUserResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def deactivate_user(
    identifier: str = Path(..., description="User email or oid"),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BaseUserUpdateByIdentifierUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['users.deactivate']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = UserUpdateByIdentifierRequestDTO(
        identifier=identifier,
        new_is_active=False
    )
    result = await update_usecase.execute(request_dto)
    return GetUserResponseSchema.from_dto(result)