from typing import Tuple, List

from domain.repositories.uow import BaseUnitOfWork
from domain.services.road import BaseRoadSnappingService
from domain.values.location import Coordinate
from domain.values.defect_types import RoadInfo


class OSMRoadSnappingService(BaseRoadSnappingService):
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def snap_point(
        self,
        point: Coordinate,
        max_distance_meters: float = 15
    ) -> Tuple[Coordinate, RoadInfo, float]:
        """Привязать точку к дороге"""
        
        result = await self.uow.roads.snap_point_to_road(
            point.longitude, point.latitude, max_distance_meters
        )
        
        if not result:
            raise ValueError(f"No road found within {max_distance_meters}m")
        
        snapped_point = Coordinate(result["snapped_lon"], result["snapped_lat"])
        road_info = RoadInfo(
            osm_way_id=result["osm_way_id"],
            road_name=result["road_name"],
            road_class=result["road_class"],
            distance_to_road=result["distance_meters"]
        )
        
        return snapped_point, road_info, result["distance_meters"]
    
    async def snap_linestring(
        self,
        points: List[Coordinate],
        max_distance_meters: float = 50
    ) -> Tuple[List[Coordinate], RoadInfo, float]:
        """Привязать линию к дороге"""
        
        if not points:
            raise ValueError("Points list cannot be empty")
        
        # Привязываем первую точку
        first_point, road_info, first_distance = await self.snap_point(
            points[0], max_distance_meters
        )
        
        snapped_points = [first_point]
        total_distance = first_distance
        
        # Остальные точки привязываем к той же дороге
        for point in points[1:]:
            result = await self.uow.roads.snap_point_to_road(
                point.longitude, point.latitude, max_distance_meters
            )
            
            if result and result["osm_way_id"] == road_info.osm_way_id:
                snapped_points.append(Coordinate(result["snapped_lon"], result["snapped_lat"]))
                total_distance += result["distance_meters"]
            else:
                # Если точка далеко от дороги, оставляем как есть
                snapped_points.append(point)
                total_distance += max_distance_meters
        
        avg_distance = total_distance / len(points)
        
        return snapped_points, road_info, avg_distance