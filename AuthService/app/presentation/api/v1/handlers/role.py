
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query

from presentation.api.v1.utils.exception import handle_exceptions
from application.dto.user import UserAuthRequestDTO
from application.usecases.user.auth import BaseUserAuthUseCase
from application.usecases.role.revoke_permission import BaseRoleRevokePermissionUseCase
from application.usecases.role.assign_permission import BaseRoleAssignPermissionUseCase
from application.usecases.role.delete import BaseRoleDeleteUseCase
from application.usecases.role.update import BaseRoleUpdateUseCase
from application.usecases.role.get_by_identifier import BaseRoleGetByIdentifierUseCase
from application.usecases.role.get_list import BaseRolesGetListUseCase
from domain.exceptions.base import DomainException
from application.dto.role import GetRoleByIdentifierRequestDTO, GetRolesRequestDTO, RoleAssignPermissionRequestDTO, RoleCreateRequestDTO, RoleDeleteRequestDTO, RoleRevokePermissionRequestDTO, RoleUpdateRequestDTO
from application.usecases.role.create import BaseRoleCreateUseCase
from presentation.api.v1.schemas.role import GetRoleResponseSchema, GetRolesResponseSchema, RoleAssignPermissionResponseSchema, RoleCreateRequestSchema, RoleCreateResponseSchema, RoleDeleteResponseSchema, RoleRevokePermissionResponseSchema, RoleUpdateRequestSchema, RoleUpdateResponseSchema
from presentation.api.v1.utils.security import oauth2_scheme

router = APIRouter(
    prefix="/v1",
    tags=["roles"]
)

@router.post(
    "/roles/create",
    responses={
        200: {"description": "Role created successfully", "model": RoleCreateResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def role_create(
    schema: RoleCreateRequestSchema,
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    create_usecase: BaseRoleCreateUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.create']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = RoleCreateRequestDTO(
        name=schema.name,
        description=schema.description
    )
    result = await create_usecase.execute(request_dto)
    return RoleCreateResponseSchema.from_dto(result)   

@router.get(
    "/roles",
    responses={
        200: {"description": "Role created successfully", "model": GetRolesResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def roles_get_list(
    offset: int = Query(ge=0, default=0),
    limit: int = Query(gt=0, default=10),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BaseRolesGetListUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.get']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = GetRolesRequestDTO(
        offset=offset,
        limit=limit
    )
    result = await get_usecase.execute(request_dto)
    return GetRolesResponseSchema.from_dto(result)

    
@router.get(
    "/roles/{identifier}",
    responses={
        200: {"description": "Role got successfully", "model": GetRoleResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def role_get_by_identifier(
    identifier: str = Path(..., description="Role name or oid"),
    load_permissions: Optional[bool] = Query(default=None),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BaseRoleGetByIdentifierUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.get']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = GetRoleByIdentifierRequestDTO(
        identifier=identifier,
        load_permissions=load_permissions
    )
    
    result = await get_usecase.execute(request_dto)
    return GetRoleResponseSchema.from_dto(result)

    
@router.put(
    "/roles/{identifier}",
    responses={
        200: {"description": "Role updated successfully", "model": RoleUpdateResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def role_update(
    schema: RoleUpdateRequestSchema,
    identifier: str = Path(..., description="Role name or oid"),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BaseRoleUpdateUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.update']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = RoleUpdateRequestDTO(
        identifier=identifier,
        new_name=schema.new_name,
        new_description=schema.new_description
    )
    
    result = await update_usecase.execute(request_dto)
    return RoleUpdateResponseSchema.from_dto(result)

    
@router.delete(
    "/roles/{identifier}",
    responses={
        200: {"description": "Role deleted successfully", "model": RoleDeleteResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def role_delete(
    identifier: str = Path(..., description="Role name or oid. oid_<oid>, name_<name>"),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    delete_usecase: BaseRoleDeleteUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.delete']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = RoleDeleteRequestDTO(
        identifier=identifier
    )
    await delete_usecase.execute(request_dto)
    return RoleDeleteResponseSchema()
    
@router.post(
    "/roles/{role_identifier}/permissions/{permission_identifier}",
    responses={
        200: {"description": "Permission assigned successfully", "model": RoleAssignPermissionResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def role_assign_permission(
    role_identifier: str = Path(..., description="Role name or oid"),
    permission_identifier: str = Path(..., description="Permission code or oid"),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    assign_usecase: BaseRoleAssignPermissionUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.assign-permission']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = RoleAssignPermissionRequestDTO(
        role_identifier=role_identifier,
        permission_identifier=permission_identifier
    )
    await assign_usecase.execute(request_dto)
    return RoleAssignPermissionResponseSchema()

    
@router.delete(
    "/roles/{role_identifier}/permissions/{permission_identifier}",
    responses={
        200: {"description": "Permission revoked successfully", "model": RoleRevokePermissionResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def role_assign_permission(
    role_identifier: str = Path(..., description="Role name or oid"),
    permission_identifier: str = Path(..., description="Permission code or oid"),
    access_token : str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    revoke_usecase: BaseRoleRevokePermissionUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.revoke-permission']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = RoleRevokePermissionRequestDTO(
        role_identifier=role_identifier,
        permission_identifier=permission_identifier
    )

    await revoke_usecase.execute(request_dto)
    return RoleRevokePermissionResponseSchema()

    
