from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseRoadsRepository(ABC):
    """Репозиторий для работы с OSM данными"""
    
    @abstractmethod
    async def snap_point_to_road(
        self,
        lon: float,
        lat: float,
        max_distance_meters: float = 15
    ) -> Optional[Dict[str, Any]]:
        """Привязывает точку к ближайшей дороге"""
        ...