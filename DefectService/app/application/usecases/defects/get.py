from domain.entities.defect import RoadDefect
from domain.repositories.uow import BaseUnitOfWork
from application.dtos.defect import DefectGetRequestDTO, DefectGetResponseDTO, RoadInfoResponseDTO
from application.usecases.base import BaseUseCase


class BaseDefectGetUseCase(BaseUseCase[DefectGetRequestDTO, DefectGetResponseDTO]):
    pass


class DefectGetUseCase(BaseDefectGetUseCase):
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def execute(self, request: DefectGetRequestDTO) -> DefectGetResponseDTO:
        async with self.uow as uow:
            defect = await uow.defects.get_by_id(request.defect_id)
            
            if not defect:
                raise ValueError(f"Defect with id {request.defect_id} not found")
            
            return self._to_response(defect)
    
    def _to_response(self, defect: RoadDefect) -> DefectGetResponseDTO:
        road_info_response = None
        if defect.road_info:
            road_info_response = RoadInfoResponseDTO(
                osm_way_id=defect.road_info.osm_way_id,
                road_name=defect.road_info.road_name,
                road_class=defect.road_info.road_class,
                distance_to_road=defect.road_info.distance_to_road
            )
        
        return DefectGetResponseDTO(
            id=defect.id,
            defect_type=defect.defect_type,
            severity=defect.severity,
            geometry_type=defect.geometry_type,
            original_coordinates=defect.original_coordinates,
            snapped_coordinates=defect.snapped_coordinates,
            description=defect.description,
            status=defect.status,
            road_info=road_info_response,
            photos=defect.photos,
            created_by=defect.created_by,
            created_at=defect.created_at,
            length_meters=defect.length,
            moderated_by=defect.moderated_by,
            moderated_at=defect.moderated_at,
            rejection_reason=defect.rejection_reason
        )