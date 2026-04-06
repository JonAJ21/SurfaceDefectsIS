from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from presentation.api.v1.schemas.permission import GetPermissionResponseSchema
from application.dto.role import GetRoleResponseDTO, RoleCreateResponseDTO


class RoleCreateRequestSchema(BaseModel):
    name: str
    description: str
    
class RoleCreateResponseSchema(BaseModel):
    oid: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dto(cls, dto: RoleCreateResponseDTO):
        return cls(
            oid=dto.oid,
            name=dto.name,
            description=dto.description,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )

class GetRoleResponseSchema(BaseModel):
    oid: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    permissions: Optional[list[GetPermissionResponseSchema]] = None
    
    @classmethod
    def from_dto(cls, dto: GetRoleResponseDTO):
        return cls(
            oid=dto.oid,
            name=dto.name,
            description=dto.description,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            permissions = [GetPermissionResponseSchema.from_dto(permission) for permission in dto.permissions] if dto.permissions is not None else None
        )
      
class GetRolesResponseSchema(BaseModel):
    roles: list[GetRoleResponseSchema]
    
    @classmethod
    def from_dto(cls, dto: list[GetRoleResponseDTO]):
        return cls(roles=[GetRoleResponseSchema.from_dto(role) for role in dto])

class RoleUpdateRequestSchema(BaseModel):
    new_name: Optional[str]
    new_description: Optional[str] 
   
class RoleUpdateResponseSchema(BaseModel):
    oid: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_dto(cls, dto: RoleCreateResponseDTO):
        return cls(
            oid=dto.oid,
            name=dto.name,
            description=dto.description,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
        
class RoleDeleteResponseSchema(BaseModel):
    message: str