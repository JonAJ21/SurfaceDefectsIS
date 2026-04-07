

from typing import Tuple

from domain.values.defect_types import RoadInfo
from domain.values.location import Coordinate
from domain.repositories.uow import BaseUnitOfWork
from application.dtos.road import SnapLinestringRequestDTO, SnapLinestringResponseDTO
from application.usecases.base import BaseUseCase


class BaseSnapLinestringUseCase(BaseUseCase[SnapLinestringRequestDTO, SnapLinestringResponseDTO]):
    pass


class SnapLinestringUseCase(BaseSnapLinestringUseCase):
    """Use case для привязки линии к дороге (без создания дефекта)"""
    
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def _snap_point(
        self,
        point: Coordinate,
        max_distance_meters: int
    ) -> Tuple[Coordinate, RoadInfo, float]:
        """Привязывает одну точку к дороге"""
        snap_result = await self.uow.roads.snap_point_to_road(
            point.longitude, point.latitude, max_distance_meters
        )
        
        if not snap_result:
            raise ValueError(f"No road found near point ({point.longitude}, {point.latitude})")
        
        snapped_point = Coordinate(snap_result["snapped_lon"], snap_result["snapped_lat"])
        road_info = RoadInfo(
            osm_way_id=snap_result["osm_way_id"],
            road_name=snap_result["road_name"],
            road_class=snap_result["road_class"],
            distance_to_road=snap_result["distance_meters"]
        )
        
        return snapped_point, road_info, snap_result["distance_meters"]
    
    async def execute(self, request: SnapLinestringRequestDTO) -> SnapLinestringResponseDTO:
        """
        Привязывает линию к дороге.
        Возвращает привязанные координаты для каждой точки.
        """
        async with self.uow as uow:
            
            # Преобразуем в Coordinate объекты
            points = [Coordinate(lon, lat) for lon, lat in request.coordinates]
            
            # Привязываем первую точку
            first_point = points[0]
            first_snapped, road_info, first_distance = await self._snap_point(
                first_point, request.max_distance_meters
            )
            
            snapped_points = [[first_snapped.longitude, first_snapped.latitude]]
            total_distance = first_distance
            all_on_road = first_distance <= request.max_distance_meters
            
            
            # Привязываем остальные точки к той же дороге
            for point in points[1:]:
                result = await uow.roads.snap_point_to_road(
                    point.longitude, point.latitude, request.max_distance_meters
                )
                
                if result:
                    snapped_point = Coordinate(result["snapped_lon"], result["snapped_lat"])
                    snapped_points.append([snapped_point.longitude, snapped_point.latitude])
                    total_distance += result["distance_meters"]
                    
                    # Проверяем, что точка на той же дороге
                    if result["osm_way_id"] != road_info.osm_way_id:
                        all_on_road = False
                    
                    if result["distance_meters"] > request.max_distance_meters:
                        all_on_road = False
                else:
                    # Если точка не привязалась, оставляем исходную
                    snapped_points.append([point.longitude, point.latitude])
                    total_distance += request.max_distance_meters
                    all_on_road = False
            
            avg_distance = total_distance / len(points)
            
            return SnapLinestringResponseDTO(
                snapped_coordinates=snapped_points,
                original_coordinates=request.coordinates,
                road_info={
                    "osm_way_id": road_info.osm_way_id,
                    "road_name": road_info.road_name,
                    "road_class": road_info.road_class,
                    "distance_to_road": road_info.distance_to_road
                },
                distance_meters=avg_distance,
                is_on_road=all_on_road
            )