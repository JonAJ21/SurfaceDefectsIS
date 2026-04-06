
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query

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
from presentation.api.v1.schemas.role import GetRoleResponseSchema, GetRolesResponseSchema, RoleCreateRequestSchema, RoleCreateResponseSchema, RoleDeleteResponseSchema, RoleUpdateRequestSchema, RoleUpdateResponseSchema
from presentation.api.v1.security.security import oauth2_scheme

router = APIRouter(
    prefix="/v1",
    tags=["roles"]
)

@router.post("/roles/create")
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
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = RoleCreateRequestDTO(
            name=schema.name,
            description=schema.description
        )
        result = await create_usecase.execute(request_dto)
        return RoleCreateResponseSchema.from_dto(result)   
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}

@router.get("/roles")
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
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = GetRolesRequestDTO(
            offset=offset,
            limit=limit
        )
        result = await get_usecase.execute(request_dto)
        return GetRolesResponseSchema.from_dto(result)
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
@router.get("/roles/{identifier}")
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
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = GetRoleByIdentifierRequestDTO(
            identifier=identifier,
            load_permissions=load_permissions
        )
    
        result = await get_usecase.execute(request_dto)
        return GetRoleResponseSchema.from_dto(result)
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
@router.put("/roles/{identifier}")
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
    try:
        auth_result = await auth_usecase.execute(auth_request_dto)
        request_dto = RoleUpdateRequestDTO(
            identifier=identifier,
            new_name=schema.new_name,
            new_description=schema.new_description
        )
    
        result = await update_usecase.execute(request_dto)
        return RoleUpdateResponseSchema.from_dto(result)
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
@router.delete("/roles/{identifier}")
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
    try:
        await auth_usecase.execute(auth_request_dto)
        request_dto = RoleDeleteRequestDTO(
            identifier=identifier
        )
        await delete_usecase.execute(request_dto)
        return RoleDeleteResponseSchema(
            message="Role deleted"
        )
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
@router.post("/roles/{role_identifier}/permissions/{permission_identifier}")
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
    try:
        await auth_usecase.execute(auth_request_dto)
        request_dto = RoleAssignPermissionRequestDTO(
            role_identifier=role_identifier,
            permission_identifier=permission_identifier
        )
        await assign_usecase.execute(request_dto)
        return {"message": "Permission assigned"}
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
@router.delete("/roles/{role_identifier}/permissions/{permission_identifier}")
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
    try:
        await auth_usecase.execute(auth_request_dto)
        request_dto = RoleRevokePermissionRequestDTO(
            role_identifier=role_identifier,
            permission_identifier=permission_identifier
        )

        await revoke_usecase.execute(request_dto)
        return {"message": "Permission revoked"}
    except DomainException as e:
        return {"Error": e.message}
    except Exception as e:
        return {"Error": str(e)}
    
