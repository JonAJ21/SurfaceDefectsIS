from fastapi import APIRouter, Depends, Path, Query

from presentation.api.v1.utils.exception import handle_exceptions
from application.dto.user import UserAuthRequestDTO
from application.usecases.user.auth import BaseUserAuthUseCase
from application.usecases.permission.delete import BasePermissionDeleteUseCase
from application.usecases.permission.get_by_identifier import BasePermissionGetByIdentifierUseCase
from application.usecases.permission.update import BasePermissionUpdateUseCase
from application.usecases.permission.get_list import BasePermissionsGetListUseCase
from domain.exceptions.base import DomainException
from application.dto.permission import GetPermissionByIdentifierRequestDTO, GetPermissionsRequestDTO, PermissionCreateRequestDTO, PermissionDeleteRequestDTO, PermissionUpdateRequestDTO
from application.usecases.permission.create import BasePermissionCreateUseCase
from presentation.api.v1.schemas.permission import GetPermissionResponseSchema, PermissionCreateRequestSchema, PermissionCreateResponseSchema, PermissionDeleteResponseSchema, PermissionUpdateRequestSchema, PermissionUpdateResponseSchema, PermissionsGetListResponseSchema
from presentation.api.v1.utils.security import oauth2_scheme

router = APIRouter(
    prefix="/v1",
    tags=["permission"]
)

@router.post(
    "/permission/create",
    responses={
        200: {"description": "Permission created successfully", "model": PermissionCreateResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def role_create(
    schema: PermissionCreateRequestSchema,
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    create_usecase: BasePermissionCreateUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['permissions.create']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = PermissionCreateRequestDTO(
        code=schema.code,
        description=schema.description
    )
    result = await create_usecase.execute(request_dto)
    return PermissionCreateResponseSchema.from_dto(result)   


@router.get(
    "/permissions",
    responses={
        200: {"description": "Permissions got successfully", "model": PermissionsGetListResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def permissions_get_list(
    offset: int = Query(ge=0, default=0),
    limit: int = Query(gt=0, default=10),
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BasePermissionsGetListUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['permissions.get']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = GetPermissionsRequestDTO(
        offset=offset,
        limit=limit
    )
    
    result = await get_usecase.execute(request_dto)
    return PermissionsGetListResponseSchema.from_dto(result)

    

@router.get(
    "/permissions/{identifier}",
    responses={
        200: {"description": "Permission got successfully", "model": GetPermissionResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def permission_get_by_identifier(
    identifier: str = Path(..., description="Permission code or oid"),
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BasePermissionGetByIdentifierUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['permissions.get']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = GetPermissionByIdentifierRequestDTO(
        identifier=identifier
    )
    
    result = await get_usecase.execute(request_dto)
    return GetPermissionResponseSchema.from_dto(result)

    
@router.put(
    "/permissions/{identifier}",
    responses={
        200: {"description": "Permission updated successfully", "model": PermissionUpdateResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def permission_update(
    schema: PermissionUpdateRequestSchema,
    identifier: str = Path(..., description="Permission code or oid"),
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    update_usecase: BasePermissionUpdateUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.update']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = PermissionUpdateRequestDTO(
        identifier=identifier,
        new_code=schema.new_code,
        new_description=schema.new_description
    )
    
    result = await update_usecase.execute(request_dto)
    return PermissionUpdateResponseSchema.from_dto(result)

    
@router.delete(
    "/permissions/{identifier}",
    responses={
        200: {"description": "Permission deleted successfully", "model": PermissionDeleteResponseSchema},
        400: {"description": "Bad request"},
        401: {"description": "Not authorized"},
        500: {"description": "Internal server error"}
    }
)
@handle_exceptions
async def permission_delete(
    identifier: str = Path(..., description="Permission code or oid"),
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    delete_usecase: BasePermissionDeleteUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.delete']
    )
    await auth_usecase.execute(auth_request_dto)
    request_dto = PermissionDeleteRequestDTO(
        identifier=identifier
    )
        
    await delete_usecase.execute(request_dto)
    return PermissionDeleteResponseSchema()
        