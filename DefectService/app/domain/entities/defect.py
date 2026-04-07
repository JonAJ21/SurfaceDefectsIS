from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4

from domain.values.location import Coordinate
from domain.values.defect_types import (
    DefectType, SeverityLevel, DefectStatus, GeometryType, RoadInfo
)


@dataclass
class RoadDefect:
    """Доменная сущность дефекта дороги"""
    
    # Обязательные поля
    defect_type: DefectType
    severity: SeverityLevel
    geometry_type: GeometryType
    original_coordinates: List[Tuple[float, float]]
    created_by: str
    
    # Опциональные поля
    id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    status: DefectStatus = DefectStatus.PENDING
    
    # Привязанная геометрия
    snapped_coordinates: Optional[List[Tuple[float, float]]] = None
    road_info: Optional[RoadInfo] = None
    distance_to_road_meters: Optional[float] = None
    
    # Фото
    photos: List[str] = field(default_factory=list)
    
    # Метаданные
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Модерация
    moderated_by: Optional[str] = None
    moderated_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    def __post_init__(self):
        """Валидация при создании"""
        self._validate_coordinates()
        self._validate_description()
    
    def _validate_coordinates(self):
        """Валидация координат"""
        if not self.original_coordinates:
            raise ValueError("Coordinates cannot be empty")
        
        for coord in self.original_coordinates:
            if len(coord) < 2:
                raise ValueError("Each coordinate must have longitude and latitude")
            
            lon, lat = coord[0], coord[1]
            if not (-180 <= lon <= 180):
                raise ValueError(f"Invalid longitude: {lon}")
            if not (-90 <= lat <= 90):
                raise ValueError(f"Invalid latitude: {lat}")
    
    def _validate_description(self):
        """Валидация описания"""
        if self.description and len(self.description) > 500:
            raise ValueError("Description too long (max 500 characters)")
    
    def validate_for_submission(self):
        """Валидация перед отправкой на модерацию"""
        if not self.photos:
            raise ValueError("At least one photo is required")
    
    @property
    def center(self) -> Coordinate:
        """Центр геометрии"""
        if self.geometry_type == GeometryType.POINT:
            return Coordinate.from_tuple(self.original_coordinates[0])
        # Для линии - средняя точка
        mid = len(self.original_coordinates) // 2
        return Coordinate.from_tuple(self.original_coordinates[mid])
    
    @property
    def length(self) -> Optional[float]:
        """Вычисляет длину линейного дефекта"""
        if self.geometry_type != GeometryType.LINESTRING:
            return None
        
        coords = self.snapped_coordinates or self.original_coordinates
        if not coords or len(coords) < 2:
            return None
        
        length = 0.0
        for i in range(1, len(coords)):
            p1 = Coordinate(coords[i-1][0], coords[i-1][1])
            p2 = Coordinate(coords[i][0], coords[i][1])
            length += p1.distance_to(p2)
        
        self.length_meters = length
        return length
    
    def snap_to_road(self, snapped_coords: List[Tuple[float, float]], 
                     road_info: RoadInfo, distance: float):
        """Привязывает дефект к дороге"""
        self.snapped_coordinates = snapped_coords
        self.road_info = road_info
        self.distance_to_road_meters = distance
    
    def approve(self, moderated_by: str):
        """Подтверждает дефект"""
        self.status = DefectStatus.APPROVED
        self.moderated_by = moderated_by
        self.moderated_at = datetime.utcnow()
    
    def reject(self, moderated_by: str, reason: str):
        """Отклоняет дефект"""
        if not reason:
            raise ValueError("Rejection reason is required")
        self.status = DefectStatus.REJECTED
        self.moderated_by = moderated_by
        self.moderated_at = datetime.utcnow()
        self.rejection_reason = reason
    
    def mark_fixed(self, fixed_by: str):
        """Отмечает как исправленный"""
        self.status = DefectStatus.FIXED
    
    def update(self, defect_type: Optional[DefectType] = None,
               severity: Optional[SeverityLevel] = None,
               description: Optional[str] = None):
        """Обновляет дефект с валидацией"""
        if defect_type is not None:
            self.defect_type = defect_type
        if severity is not None:
            self.severity = severity
        if description is not None:
            if len(description) > 500:
                raise ValueError("Description too long (max 500 characters)")
            self.description = description