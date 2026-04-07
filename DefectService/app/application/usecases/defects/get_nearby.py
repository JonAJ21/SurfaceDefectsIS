from typing import List

from domain.entities.defect import RoadDefect
from domain.repositories.uow import BaseUnitOfWork
from domain.values.location import Coordinate, Distance
from domain.values.defect_types import GeometryType
from application.dtos.defect import DefectGetNearbyRequestDTO, DefectGetNearbyResponseDTO
from application.usecases.base import BaseUseCase


class BaseDefectGetNearbyUseCase(BaseUseCase[DefectGetNearbyRequestDTO, List[DefectGetNearbyResponseDTO]]):
    pass


class DefectGetNearbyUseCase(BaseDefectGetNearbyUseCase):
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def execute(self, request: DefectGetNearbyRequestDTO) -> List[DefectGetNearbyResponseDTO]:
        async with self.uow as uow:
            center = Coordinate(request.longitude, request.latitude)
            radius = Distance(request.radius_meters)
            
            defects = await uow.defects.find_nearby(
                center=center,
                radius=radius,
                defect_types=request.defect_types,
                min_severity=request.min_severity
            )
            
            return [self._to_response(defect, center) for defect in defects]
    
    def _to_response(self, defect: RoadDefect, center: Coordinate) -> DefectGetNearbyResponseDTO:
        # Вычисляем расстояние до дефекта
        coords = defect.snapped_coordinates or defect.original_coordinates
        
        if defect.geometry_type == GeometryType.POINT:
            defect_point = Coordinate(coords[0][0], coords[0][1])
            distance = center.distance_to(defect_point)
        else:
            # Для линии - минимальное расстояние до любой точки
            distance = min(
                center.distance_to(Coordinate(lon, lat)) for lon, lat in coords
            )
        
        return DefectGetNearbyResponseDTO(
            id=defect.id,
            defect_type=defect.defect_type,
            severity=defect.severity,
            geometry_type=defect.geometry_type,
            snapped_coordinates=coords,
            road_name=defect.road_info.road_name if defect.road_info else None,
            distance_meters=distance,
            photos=defect.photos[:1] if defect.photos else [],
            length_meters=defect.length
        )