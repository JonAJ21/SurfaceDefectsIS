from abc import ABC, abstractmethod
from typing import Tuple, List

from domain.values.location import Coordinate
from domain.values.defect_types import RoadInfo


class BaseRoadSnappingService(ABC):
    """Сервис для привязки точек к дорогам"""
    
    @abstractmethod
    async def snap_point(
        self,
        point: Coordinate,
        max_distance_meters: float = 15
    ) -> Tuple[Coordinate, RoadInfo, float]:
        """
        Привязать точку к дороге
        Returns: (snapped_point, road_info, distance)
        """
        pass
    
    @abstractmethod
    async def snap_linestring(
        self,
        points: List[Coordinate],
        max_distance_meters: float = 15
    ) -> Tuple[List[Coordinate], RoadInfo, float]:
        """
        Привязать линию к дороге
        Returns: (snapped_points, road_info, avg_distance)
        """
        pass