from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from domain.values.defect_types import DefectStatus, DefectType, GeometryType, SeverityLevel


# Request Schemas
class PhotoUploadSchema(BaseModel):
    filename: str
    data: bytes
    content_type: str = "image/jpeg"


class DefectCreateRequest(BaseModel):
    defect_type: DefectType = Field(..., description="Тип дефекта")
    severity: SeverityLevel = Field(..., description="Уровень опасности")
    geometry_type: GeometryType = Field(..., description="Тип геометрии (point или linestring)")
    coordinates: List[List[float]] = Field(..., description="Координаты [[lon, lat], ...]")
    description: Optional[str] = Field(None, max_length=500, description="Описание дефекта")
    max_distance_meters: int = Field(15, ge=5, le=100, description="Максимальное расстояние до дороги для привязки")
    # photos передаются отдельно через UploadFile


class DefectUpdateRequest(BaseModel):
    defect_type: Optional[DefectType] = Field(None, description="Тип дефекта")
    severity: Optional[SeverityLevel] = Field(None, description="Уровень опасности")
    description: Optional[str] = Field(None, max_length=500, description="Описание дефекта")


class DefectModerateRequest(BaseModel):
    status: DefectStatus = Field(..., description="Новый статус")
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Причина отклонения (обязательно для rejected)")


class DefectsNearbyQuery(BaseModel):
    longitude: float = Field(..., ge=-180, le=180, description="Долгота")
    latitude: float = Field(..., ge=-90, le=90, description="Широта")
    radius_meters: float = Field(100, ge=10, le=5000, description="Радиус поиска в метрах")
    defect_types: Optional[List[DefectType]] = Field(None, description="Фильтр по типам дефектов")
    min_severity: Optional[SeverityLevel] = Field(None, description="Минимальный уровень опасности")


class DefectPendingQuery(BaseModel):
    limit: int = Field(100, ge=1, le=500, description="Количество записей")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")


# Response Schemas
class RoadInfoResponse(BaseModel):
    osm_way_id: Optional[int]
    road_name: Optional[str]
    road_class: Optional[str]
    distance_to_road: Optional[float]


class DefectResponse(BaseModel):
    id: UUID
    defect_type: DefectType
    severity: SeverityLevel
    geometry_type: GeometryType
    original_coordinates: List[List[float]]
    snapped_coordinates: Optional[List[List[float]]]
    description: Optional[str]
    status: DefectStatus
    road_info: Optional[RoadInfoResponse]
    photos: List[str]
    length_meters: Optional[float]
    created_by: str
    created_at: datetime
    moderated_by: Optional[str]
    moderated_at: Optional[datetime]
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True
        


class DefectNearbyResponse(BaseModel):
    id: UUID
    defect_type: DefectType
    severity: SeverityLevel
    geometry_type: GeometryType
    snapped_coordinates: List[List[float]]
    road_name: Optional[str]
    distance_meters: float
    photos: List[str]
    length_meters: Optional[float]


class DefectDeleteResponse(BaseModel):
    success: bool
    defect_id: UUID
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None