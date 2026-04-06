
from dataclasses import dataclass
from typing import Optional


@dataclass
class PermissionCreateRequestDTO:
    code: str
    description: str
    
@dataclass
class PermissionCreateResponseDTO:
    oid: str
    code: str
    description: str
    
@dataclass
class GetPermissionsRequestDTO:
    offset: int
    limit: int
    
@dataclass
class GetPermissionByIdentifierRequestDTO:
    identifier: str

@dataclass
class GetPermissionResponseDTO:
    oid: str
    code: str
    description: str
    
@dataclass
class PermissionDeleteRequestDTO:
    identifier: str
    
@dataclass
class PermissionUpdateRequestDTO:
    identifier: str
    new_code: Optional[str]
    new_description: Optional[str]

@dataclass
class PermissionUpdateResponseDTO:
    oid: str
    code: str
    description: str