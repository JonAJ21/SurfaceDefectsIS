from typing import List

from domain.entities.defect import RoadDefect
from domain.repositories.uow import BaseUnitOfWork
from application.dtos.defect import DefectGetInViewPortRequestDTO, DefectGetInViewPortResponseDTO
from application.usecases.base import BaseUseCase



class BaseDefectGetInViewPortUseCase(BaseUseCase[DefectGetInViewPortRequestDTO, List[DefectGetInViewPortResponseDTO]]):
    ...


class DefectGetInViewPortUseCase(BaseDefectGetInViewPortUseCase):
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def execute(self, request: DefectGetInViewPortRequestDTO) -> List[DefectGetInViewPortResponseDTO]:
        async with self.uow as uow:
            
            defects = await uow.defects.find_in_viewport(
                min_lon=request.min_lon,
                min_lat=request.min_lat,
                max_lon=request.max_lon,
                max_lat=request.max_lat,
                defect_types=request.defect_types,
                min_severity=request.min_severity,
                limit=request.limit
            )
            
            return [self._to_response(defect) for defect in defects]
    
    def _to_response(self, defect: RoadDefect) -> DefectGetInViewPortResponseDTO:
        coords = defect.snapped_coordinates or defect.original_coordinates
        
        return DefectGetInViewPortResponseDTO(
            id=defect.id,
            defect_type=defect.defect_type,
            severity=defect.severity,
            geometry_type=defect.geometry_type,
            snapped_coordinates=coords,
            road_name=defect.road_info.road_name if defect.road_info else None,
            photos=defect.photos[:1] if defect.photos else [],
            length_meters=defect.length
        )