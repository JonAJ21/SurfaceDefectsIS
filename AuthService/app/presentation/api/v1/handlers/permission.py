from fastapi import APIRouter, Depends, Path, Query

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
from presentation.api.v1.security.security import oauth2_scheme

router = APIRouter(
    prefix="/v1",
    tags=["permission"]
)

@router.post("/permission/create")
async def role_create(
    schema: PermissionCreateRequestSchema,
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    create_usecase: BasePermissionCreateUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.create']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = PermissionCreateRequestDTO(
            code=schema.code,
            description=schema.description
        )
        result = await create_usecase.execute(request_dto)
        return PermissionCreateResponseSchema.from_dto(result)   
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}

@router.get("/permissions")
async def permissions_get_list(
    offset: int = Query(ge=0, default=0),
    limit: int = Query(gt=0, default=10),
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BasePermissionsGetListUseCase = Depends(),
):
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.get']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = GetPermissionsRequestDTO(
            offset=offset,
            limit=limit
        )
    
        result = await get_usecase.execute(request_dto)
        return PermissionsGetListResponseSchema.from_dto(result)
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    

@router.get("/permissions/{identifier}")
async def permission_get_by_identifier(
    identifier: str = Path(..., description="Permission code or oid"),
    access_token: str = Depends(oauth2_scheme),
    auth_usecase: BaseUserAuthUseCase = Depends(),
    get_usecase: BasePermissionGetByIdentifierUseCase = Depends(),
):  
    auth_request_dto = UserAuthRequestDTO(
        access_token=access_token,
        needed_permission_codes=['roles.get']
    )
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = GetPermissionByIdentifierRequestDTO(
            identifier=identifier
        )
    
        result = await get_usecase.execute(request_dto)
        return GetPermissionResponseSchema.from_dto(result)
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
@router.put("/permissions/{identifier}")
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
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = PermissionUpdateRequestDTO(
            identifier=identifier,
            new_code=schema.new_code,
            new_description=schema.new_description
        )
    
        result = await update_usecase.execute(request_dto)
        return PermissionUpdateResponseSchema.from_dto(result)
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
@router.delete("/permissions/{identifier}")
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
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = PermissionDeleteRequestDTO(
            identifier=identifier
        )
        
        await delete_usecase.execute(request_dto)
        return PermissionDeleteResponseSchema(
            message="Permission deleted"
        )
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
        