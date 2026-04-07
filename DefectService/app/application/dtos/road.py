from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SnapLinestringRequestDTO:
    """Запрос на привязку линии к дороге"""
    coordinates: List[List[float]]  # [[lon, lat], [lon, lat], ...]
    max_distance_meters: int = 15
    
@dataclass
class SnapLinestringResponseDTO:
    """Ответ с привязанными точками"""
    snapped_coordinates: List[List[float]]  # Привязанные координаты
    original_coordinates: List[List[float]]  # Исходные координаты
    road_info: dict  # Информация о дороге
    distance_meters: float  # Среднее расстояние до дороги
    is_on_road: bool  # Находится ли вся линия на дороге
    
@dataclass
class SnapPointRequestDTO:
    longitude: float
    latitude: float
    max_distance_meters: int = 15


@dataclass
class SnapPointResponseDTO:
    snapped_longitude: float
    snapped_latitude: float
    original_longitude: float
    original_latitude: float
    distance_meters: float
    road_info: Dict[str, Any]