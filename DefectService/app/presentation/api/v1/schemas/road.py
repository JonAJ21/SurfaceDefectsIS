from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SnapPointRequestSchema(BaseModel):
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    max_distance_meters: int = Field(15, ge=1, le=100)


class SnapPointResponseSchema(BaseModel):
    snapped_longitude: float
    snapped_latitude: float
    original_longitude: float
    original_latitude: float
    distance_meters: float
    road_info: Dict[str, Any]
    
    class Config:
        from_attributes = True
        
class SnapLinestringRequestSchema(BaseModel):
    coordinates: List[List[float]] = Field(..., min_length=1)
    max_distance_meters: int = Field(15, ge=1, le=100)


class SnapLinestringResponseSchema(BaseModel):
    snapped_coordinates: List[List[float]]
    original_coordinates: List[List[float]]
    road_info: Dict[str, Any]
    distance_meters: float
    is_on_road: bool
    
    class Config:
        from_attributes = True


class ErrorResponseSchema(BaseModel):
    error: str
    detail: Optional[str] = None