from domain.repositories.uow import BaseUnitOfWork
from application.dtos.defect import DefectDeleteRequestDTO, DefectDeleteResponseDTO
from application.usecases.base import BaseUseCase


class BaseDefectDeleteUseCase(BaseUseCase[DefectDeleteRequestDTO, DefectDeleteResponseDTO]):
    pass


class DefectDeleteUseCase(BaseDefectDeleteUseCase):
    def __init__(self, uow: BaseUnitOfWork):
        self.uow = uow
    
    async def execute(self, request: DefectDeleteRequestDTO) -> DefectDeleteResponseDTO:
        async with self.uow as uow:
            # Получаем дефект
            defect = await uow.defects.get_by_id(request.defect_id)
            
            if not defect:
                return DefectDeleteResponseDTO(
                    success=False,
                    defect_id=request.defect_id,
                    message="Defect not found"
                )
            
            # Проверка прав (только создатель)
            if defect.created_by != request.deleted_by:
                return DefectDeleteResponseDTO(
                    success=False,
                    defect_id=request.defect_id,
                    message="You can only delete your own defects"
                )
            
            # Удаляем фото из MinIO
            # await uow.photos.delete_all(str(request.defect_id))
            
            # Мягкое удаление дефекта
            result = await uow.defects.delete(request.defect_id)
            await uow.commit()
            
            return DefectDeleteResponseDTO(
                success=result,
                defect_id=request.defect_id,
                message="Defect deleted successfully" if result else "Failed to delete defect"
            )