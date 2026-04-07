from domain.entities.defect import RoadDefect
from domain.repositories.uow import BaseUnitOfWork
from domain.values.defect_types import DefectStatus
from application.dtos.defect import DefectModerateRequestDTO, DefectModerateResponseDTO, RoadInfoResponseDTO
from application.usecases.base import BaseUseCase


class BaseDefectModerateUseCase(BaseUseCase[DefectModerateRequestDTO, DefectModerateResponseDTO]):
    pass


class DefectModerateUseCase(BaseDefectModerateUseCase):
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def execute(self, request: DefectModerateRequestDTO) -> DefectModerateResponseDTO:
        async with self.uow as uow:
            # Получаем дефект
            defect = await uow.defects.get_by_id(request.defect_id)
            
            if not defect:
                raise ValueError(f"Defect with id {request.defect_id} not found")
            
            # Обновляем статус
            if request.status == DefectStatus.APPROVED:
                defect.approve(request.moderated_by)
            elif request.status == DefectStatus.REJECTED:
                if not request.rejection_reason:
                    raise ValueError("Rejection reason is required")
                defect.reject(request.moderated_by, request.rejection_reason)
            else:
                defect.status = request.status
            
            # Сохраняем
            updated_defect = await uow.defects.save(defect)
            
            return self._to_response(updated_defect)
    
    def _to_response(self, defect: RoadDefect) -> DefectModerateResponseDTO:
        road_info_response = None
        if defect.road_info:
            road_info_response = RoadInfoResponseDTO(
                osm_way_id=defect.road_info.osm_way_id,
                road_name=defect.road_info.road_name,
                road_class=defect.road_info.road_class,
                distance_to_road=defect.road_info.distance_to_road
            )
        
        return DefectModerateResponseDTO(
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