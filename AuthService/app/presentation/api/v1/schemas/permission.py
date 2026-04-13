from typing import Optional

from pydantic import BaseModel

from application.dto.permission import PermissionCreateResponseDTO, PermissionUpdateResponseDTO


class PermissionCreateRequestSchema(BaseModel):
    code: str
    description: str
    
class PermissionCreateResponseSchema(BaseModel):
    oid: str
    code: str
    description: str
    
    @classmethod
    def from_dto(cls, dto: PermissionCreateResponseDTO):
        return cls(
            oid=dto.oid,
            code=dto.code,
            description=dto.description
        )

class GetPermissionResponseSchema(BaseModel):
    oid: str
    code: str
    description: str
    
    @classmethod
    def from_dto(cls, dto: PermissionCreateResponseDTO):
        return cls(
            oid=dto.oid,
            code=dto.code,
            description=dto.description
        )
        
class PermissionsGetListResponseSchema(BaseModel):
    permissions: list[GetPermissionResponseSchema]
    
    @classmethod
    def from_dto(cls, dto: list[PermissionCreateResponseDTO]):
        return cls(permissions=[GetPermissionResponseSchema.from_dto(permission) for permission in dto])
    
class PermissionUpdateRequestSchema(BaseModel):
    new_code: Optional[str] = None
    new_description: Optional[str] = None
    
class PermissionUpdateResponseSchema(BaseModel):
    oid: str
    code: str
    description: str
    
    @classmethod
    def from_dto(cls, dto: PermissionUpdateResponseDTO):
        return cls(
            oid=dto.oid,
            code=dto.code,
            description=dto.description
        )

class PermissionDeleteResponseSchema(BaseModel):
    message: str = "Permission deleted"