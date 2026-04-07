from domain.values.location import Coordinate
from domain.repositories.uow import BaseUnitOfWork
from application.dtos.road import SnapPointRequestDTO, SnapPointResponseDTO
from application.usecases.base import BaseUseCase


class BaseSnapPointUseCase(BaseUseCase[SnapPointRequestDTO, SnapPointResponseDTO]):
    pass


class SnapPointUseCase(BaseSnapPointUseCase):
    
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def execute(self, request: SnapPointRequestDTO) -> SnapPointResponseDTO:
        async with self.uow as uow:
            point = Coordinate(request.longitude, request.latitude)
            
            snap_result = await uow.roads.snap_point_to_road(
                point.longitude, point.latitude, request.max_distance_meters
            )
            
            if not snap_result:
                raise ValueError(f"No road found near point ({point.longitude}, {point.latitude})")
            
            snapped_point = Coordinate(snap_result["snapped_lon"], snap_result["snapped_lat"])
            
            return SnapPointResponseDTO(
                snapped_longitude=snapped_point.longitude,
                snapped_latitude=snapped_point.latitude,
                original_longitude=point.longitude,
                original_latitude=point.latitude,
                distance_meters=snap_result["distance_meters"],
                road_info={
                    "osm_way_id": snap_result["osm_way_id"],
                    "road_name": snap_result["road_name"],
                    "road_class": snap_result["road_class"],
                    "distance_to_road": snap_result["distance_meters"]
                }
            )