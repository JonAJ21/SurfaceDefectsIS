from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from application.dto.permission import GetPermissionResponseDTO


@dataclass
class RoleCreateRequestDTO:
    name: str
    description: str
    
@dataclass
class RoleCreateResponseDTO:
    oid: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

@dataclass 
class GetRolesRequestDTO:
    offset: int
    limit: int

@dataclass
class GetRoleByIdentifierRequestDTO:
    identifier: str
    load_permissions: Optional[bool] = None
    
@dataclass
class GetRoleResponseDTO:
    oid: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    permissions: Optional[list[GetPermissionResponseDTO]] = None
    
@dataclass
class RoleUpdateRequestDTO:
    identifier: str
    new_name: str
    new_description: str
    
@dataclass
class RoleUpdateResponseDTO:
    oid: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    
@dataclass
class RoleDeleteRequestDTO:
    identifier: str
    
@dataclass
class RoleAssignPermissionRequestDTO:
    role_identifier: str
    permission_identifier: str
    
    
@dataclass
class RoleRevokePermissionRequestDTO:
    role_identifier: str
    permission_identifier: str
