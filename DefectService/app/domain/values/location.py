from dataclasses import dataclass
import math
from typing import Tuple


@dataclass(frozen=True)
class Coordinate:
    """Value Object для координат"""
    longitude: float
    latitude: float
    
    def __post_init__(self):
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
    
    def distance_to(self, other: 'Coordinate') -> float:
        """Расстояние в метрах (формула гаверсинуса)"""
        R = 6371000
        
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(other.latitude)
        delta_lat = math.radians(other.latitude - self.latitude)
        delta_lon = math.radians(other.longitude - self.longitude)
        
        a = math.sin(delta_lat/2)**2 + \
            math.cos(lat1) * math.cos(lat2) * \
            math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.longitude, self.latitude)
    
    @classmethod
    def from_tuple(cls, coords: Tuple[float, float]) -> 'Coordinate':
        return cls(longitude=coords[0], latitude=coords[1])


@dataclass(frozen=True)
class Distance:
    """Value Object для расстояния"""
    value_meters: float
    
    def __post_init__(self):
        if self.value_meters < 0:
            raise ValueError("Distance cannot be negative")
    
    @property
    def km(self) -> float:
        return self.value_meters / 1000
    
    def __lt__(self, other: 'Distance') -> bool:
        return self.value_meters < other.value_meters