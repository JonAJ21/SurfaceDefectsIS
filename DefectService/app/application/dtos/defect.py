
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from domain.values.defect_types import DefectStatus, DefectType, GeometryType, SeverityLevel


class PhotoUploadDTO(BaseModel):
    filename: str
    data: bytes
    content_type: str
    
class DefectCreateRequestDTO(BaseModel):
    defect_type: DefectType
    severity: SeverityLevel
    geometry_type: GeometryType
    coordinates: List[List[float]]
    description: Optional[str] = None
    created_by: str
    photos: List[PhotoUploadDTO]

class DefectGetRequestDTO(BaseModel):
    defect_id: UUID

class DefectsGetRequestDTO(BaseModel):
    offset: int = 0
    limit: int = 100
    defect_statuses: Optional[List[DefectStatus]] = None
    defect_types: Optional[List[DefectType]] = None
    min_severity: Optional[SeverityLevel] = None
 
class DefectGetNearbyRequestDTO(BaseModel):
    longitude: float
    latitude: float
    radius_meters: float = 100
    defect_types: Optional[List[DefectType]] = None
    min_severity: Optional[SeverityLevel] = None

class DefectGetInViewPortRequestDTO(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float
    defect_types: Optional[List[DefectType]] = None
    min_severity: Optional[SeverityLevel] = None
    limit: int = 1000
    
class DefectGetByUserIdRequestDTO(BaseModel):
    user_id: str
    limit: int = 100
    offset: int = 0
    
class DefectGetPendingRequestDTO(BaseModel):
    limit: int = 100
    offset: int = 0
    
class DefectModerateRequestDTO(BaseModel):
    defect_id: UUID
    status: DefectStatus
    moderated_by: str
    rejection_reason: Optional[str] = None
    
class DefectUpdateRequestDTO(BaseModel):
    defect_id: UUID
    defect_type: Optional[DefectType] = None
    severity: Optional[SeverityLevel] = None
    description: Optional[str] = None
    fixed: Optional[bool] = None
    updated_by: str
    
class DefectDeleteRequestDTO(BaseModel):
    defect_id: UUID
    deleted_by: str
    
class RoadInfoResponseDTO(BaseModel):
    osm_way_id: Optional[int]
    road_name: Optional[str]
    road_class: Optional[str]
    distance_to_road: Optional[float]
    
class DefectCreateResponseDTO(BaseModel):
    id: UUID
    defect_type: DefectType
    severity: SeverityLevel
    geometry_type: GeometryType
    original_coordinates: List[List[float]]
    snapped_coordinates: Optional[List[List[float]]]
    description: Optional[str]
    status: DefectStatus
    road_info: Optional[RoadInfoResponseDTO]
    length_meters: Optional[float]
    photos: List[str]
    created_by: str
    created_at: datetime
    
class DefectGetResponseDTO(DefectCreateResponseDTO):
    moderated_by: Optional[str]
    moderated_at: Optional[datetime]
    rejection_reason: Optional[str]
    
class DefectGetByUserIdResponseDTO(DefectGetResponseDTO):
    ...
    
class DefectGetNearbyResponseDTO(BaseModel):
    id: UUID
    defect_type: DefectType
    severity: SeverityLevel
    snapped_coordinates: List[List[float]]
    road_name: Optional[str]
    distance_meters: float
    photos: List[str]
    
class DefectGetInViewPortResponseDTO(BaseModel):
    id: UUID
    defect_type: DefectType
    severity: SeverityLevel
    snapped_coordinates: List[List[float]]
    road_name: Optional[str]
    photos: List[str]
    
class DefectGetPendingResponseDTO(DefectGetResponseDTO):
    ...


class DefectModerateResponseDTO(DefectGetResponseDTO):
    ...


class DefectUpdateResponseDTO(DefectGetResponseDTO):
    ...


class DefectDeleteResponseDTO(BaseModel):
    success: bool
    defect_id: UUID