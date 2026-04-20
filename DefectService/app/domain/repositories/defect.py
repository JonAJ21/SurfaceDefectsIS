from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.defect import RoadDefect
from domain.values.location import Coordinate, Distance
from domain.values.defect_types import DefectType, SeverityLevel, DefectStatus


class BaseDefectsRepository(ABC):
    """Интерфейс репозитория дефектов"""
    
    @abstractmethod
    async def save(self, defect: RoadDefect) -> RoadDefect:
        """Сохранить дефект"""
        ...
    
    @abstractmethod
    async def get(
        self,
        offset: int = 0,
        limit: int = 10,
        defect_statuses: Optional[List[DefectStatus]] = None,
        defect_types: Optional[List[DefectType]] = None,
        min_severity: Optional[SeverityLevel] = None
    ) -> List[RoadDefect]:
        """Получить дефекты"""
        ...
    
    @abstractmethod
    async def get_by_id(self, defect_id: UUID) -> Optional[RoadDefect]:
        """Получить по ID"""
        ...
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[RoadDefect]:
        """Получить по ID пользователя"""
        ...
    
    @abstractmethod
    async def find_nearby(
        self,
        center: Coordinate,
        radius: Distance,
        defect_types: List[DefectType] | None = None,
        min_severity: SeverityLevel | None = None
    ) -> List[RoadDefect]:
        """Найти дефекты рядом"""
        ...
    
    @abstractmethod
    async def find_in_viewport(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        defect_types: Optional[List[DefectType]] = None,
        min_severity: Optional[SeverityLevel] = None,
        limit: int = 1000,
    ) -> List[RoadDefect]:
        """Находит дефекты внутри прямоугольника (viewport/bounding box)."""
        ...
        
    @abstractmethod
    async def get_pending(self, offset: int = 0, limit: int = 10) -> List[RoadDefect]:
        """Получить дефекты на модерацию"""
        ...
    
    @abstractmethod
    async def update_status(
        self,
        defect_id: UUID,
        status: DefectStatus,
        moderated_by: str,
        reason: str | None = None
    ) -> Optional[RoadDefect]:
        """Обновить статус"""
        ...
        
    @abstractmethod
    async def delete(self, defect_id: UUID):
        """Мягкое удаление - меняем статус на deleted"""
        ...