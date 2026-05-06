import json
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import List, Tuple

from domain.values.defect_types import GeometryType, RoadInfo
from domain.values.location import Coordinate, Distance
from domain.entities.defect import RoadDefect
from application.dtos.defect import DefectCreateRequestDTO, DefectCreateResponseDTO, RoadInfoResponseDTO
from domain.repositories.uow import BaseUnitOfWork
from application.usecases.base import BaseUseCase
from core.config.settings import settings


class BaseDefectCreateUseCase(BaseUseCase[DefectCreateRequestDTO, DefectCreateResponseDTO]):
    ...
    

class DefectCreateUseCase(BaseDefectCreateUseCase):
    def __init__(
        self,
        uow: BaseUnitOfWork
    ):
        self.uow = uow
        self._redis_client = None
    
    async def _get_redis_client(self) -> redis.Redis:
        if self._redis_client is None:
            self._redis_client = await redis.from_url(
                f"redis://{settings.redis_host}:{settings.redis_port}",
                decode_responses=True
            )
        return self._redis_client
    
    async def _publish_to_detection_stream(self, defect_id: str, photo_path: str) -> None:
        """Публикация сообщения в Redis Streams для сервиса детекции"""
        try:
            redis_client = await self._get_redis_client()
            stream_name = "defect:detection"
            
            message_id = await redis_client.xadd(
                stream_name,
                {
                    "defect_id": defect_id,
                    "photo_path": photo_path,
                }
            )
            print(f"Published defect {defect_id} to stream {stream_name}, message_id: {message_id}")
        except Exception as e:
            print(f"Failed to publish to stream: {e}")
    
    async def _check_duplicate(
        self,
        coordinates: List[List[float]],
        geometry_type: GeometryType,
        distance_tolerance_meters: float = 10
    ) -> bool:
        """Проверяет, существует ли похожий дефект в том же месте"""
        
        if geometry_type == GeometryType.POINT:
            center_lon = coordinates[0][0]
            center_lat = coordinates[0][1]
        else:
            mid = len(coordinates) // 2
            center_lon = coordinates[mid][0]
            center_lat = coordinates[mid][1]
        
        center = Coordinate(center_lon, center_lat)
        radius = Distance(distance_tolerance_meters)
        
        nearby_defects = await self.uow.defects.find_nearby(
            center=center,
            radius=radius
        )
        
        for defect in nearby_defects:
            if geometry_type == GeometryType.POINT:
                defect_center = defect.center
                distance = center.distance_to(defect_center)
                if distance <= distance_tolerance_meters:
                    return True
        
        return False
    
    async def _snap_point(
        self, 
        coordinates: List[List[float]],
        max_distance_meters: int = 15
    ) -> Tuple[List[List[float]], RoadInfo, float]:
        """Привязка точечного дефекта"""
        center = Coordinate(coordinates[0][0], coordinates[0][1])
        snap_result = await self.uow.roads.snap_point_to_road(
            center.longitude, center.latitude, max_distance_meters
        )
        
        if not snap_result:
            raise ValueError(f"No road found near point ({center.longitude}, {center.latitude})")
        
        snapped_point = [[snap_result["snapped_lon"], snap_result["snapped_lat"]]]
        road_info = RoadInfo(
            osm_way_id=snap_result["osm_way_id"],
            road_name=snap_result["road_name"],
            road_class=snap_result["road_class"],
            distance_to_road=snap_result["distance_meters"]
        )
        
        return snapped_point, road_info, snap_result["distance_meters"]
    
    async def _snap_linestring(
        self, 
        coordinates: List[List[float]],
        max_distance_meters: int = 15
    ) -> Tuple[List[List[float]], RoadInfo, float]:
        """Привязка линейного дефекта"""
        if len(coordinates) < 2:
            raise ValueError("Linestring must have at least 2 points")
        
        points = [Coordinate(lon, lat) for lon, lat in coordinates]
        
        first_point = points[0]
        first_result = await self.uow.roads.snap_point_to_road(
            first_point.longitude, first_point.latitude, max_distance_meters
        )
        
        if not first_result:
            raise ValueError(f"No road found near first point ({first_point.longitude}, {first_point.latitude})")
        
        snapped_points = [[first_result["snapped_lon"], first_result["snapped_lat"]]]
        total_distance = first_result["distance_meters"]
        
        road_info = RoadInfo(
            osm_way_id=first_result["osm_way_id"],
            road_name=first_result["road_name"],
            road_class=first_result["road_class"],
            distance_to_road=first_result["distance_meters"]
        )
        
        for point in points[1:]:
            result = await self.uow.roads.snap_point_to_road(
                point.longitude, point.latitude, max_distance_meters
            )
            
            if result and result["osm_way_id"] == road_info.osm_way_id:
                snapped_points.append([result["snapped_lon"], result["snapped_lat"]])
                total_distance += result["distance_meters"]
            else:
                snapped_points.append([point.longitude, point.latitude])
                total_distance += max_distance_meters
        
        avg_distance = total_distance / len(points)
        
        return snapped_points, road_info, avg_distance
    
    async def execute(self, request: DefectCreateRequestDTO) -> DefectCreateResponseDTO:
        async with self.uow as uow:
            is_duplicate = await self._check_duplicate(
                coordinates=request.coordinates,
                geometry_type=request.geometry_type,
                distance_tolerance_meters=settings.duplicate_distance_tolerance_meters
            )
            
            if is_duplicate:
                raise ValueError(
                    "Similar defect already exists nearby. "
                    "Please check existing defects before creating a new one."
                )
            
            defect = RoadDefect(
                defect_type=request.defect_type,
                severity=request.severity,
                geometry_type=request.geometry_type,
                original_coordinates=request.coordinates,
                created_by=request.created_by,
                description=request.description,
            )
            max_distance = request.max_distance_meters
            
            if request.geometry_type == GeometryType.POINT:
                snapped_coords, road_info, distance = await self._snap_point(
                    request.coordinates, max_distance
                )
            else:
                snapped_coords, road_info, distance = await self._snap_linestring(
                    request.coordinates, max_distance    
                )
            
            defect.snap_to_road(
                snapped_coords=snapped_coords,
                road_info=road_info,
                distance=distance
            )
            
            photo_urls = []
            for photo in request.photos:
                url = await uow.photos.upload(
                    defect_id=str(defect.id),
                    filename=photo.filename,
                    data=photo.data,
                    content_type=photo.content_type
                )
                photo_urls.append(url)
            
            defect.photos = photo_urls
            defect.validate_for_submission()
            
            length_meters = None
            if defect.geometry_type == GeometryType.LINESTRING:
                length_meters = defect.length
            
            saved_defect = await uow.defects.save(defect)
            await uow.commit()
            
            for photo_url in photo_urls:
                await self._publish_to_detection_stream(str(saved_defect.id), photo_url)
            
            road_info_response = None
            if saved_defect.road_info:
                road_info_response = RoadInfoResponseDTO(
                    osm_way_id=saved_defect.road_info.osm_way_id,
                    road_name=saved_defect.road_info.road_name,
                    road_class=saved_defect.road_info.road_class,
                    distance_to_road=saved_defect.road_info.distance_to_road
                )
            
            return DefectCreateResponseDTO(
                id=saved_defect.id,
                defect_type=saved_defect.defect_type,
                severity=saved_defect.severity,
                geometry_type=saved_defect.geometry_type,
                original_coordinates=saved_defect.original_coordinates,
                snapped_coordinates=saved_defect.snapped_coordinates,
                description=saved_defect.description,
                status=saved_defect.status,
                road_info=road_info_response,
                photos=saved_defect.photos,
                created_by=saved_defect.created_by,
                created_at=saved_defect.created_at,
                length_meters=length_meters
            )