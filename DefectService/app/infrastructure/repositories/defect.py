from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin, ST_Intersects, ST_MakeEnvelope, ST_SetSRID, ST_MakePoint
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point, LineString

from domain.entities.defect import RoadDefect
from domain.repositories.defect import BaseDefectsRepository
from domain.values.location import Coordinate, Distance
from domain.values.defect_types import (
    DefectType, SeverityLevel, DefectStatus, GeometryType, RoadInfo
)
from infrastructure.database.models import RoadDefectModel, DefectType, SeverityLevel, DefectStatus, GeometryType


class SQLAlchemyDefectsRepository(BaseDefectsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save(self, defect: RoadDefect) -> RoadDefect:
        """Сохранить дефект (создать или обновить)"""
        
        # Проверяем, существует ли дефект с таким ID
        stmt = select(RoadDefectModel).where(RoadDefectModel.id == defect.id)
        result = await self.session.execute(stmt)
        existing_model = result.scalar_one_or_none()
        
        if existing_model:
            # Обновляем существующий дефект
            updated_model = await self._update_model(existing_model, defect)
            await self.session.flush()
            return await self._to_entity(updated_model)
        else:
            # Создаём новый дефект
            model = await self._to_model(defect)
            self.session.add(model)
            await self.session.flush()
            return await self._to_entity(model)
    
    async def _update_model(self, model: RoadDefectModel, defect: RoadDefect) -> RoadDefectModel:
        """Обновляет существующую модель новыми данными"""
        
        # Обновляем геометрию
        if defect.geometry_type == GeometryType.POINT:
            point = Point(defect.original_coordinates[0][0], defect.original_coordinates[0][1])
            model.original_geometry = from_shape(point, srid=4326)
        else:
            line = LineString(defect.original_coordinates)
            model.original_geometry = from_shape(line, srid=4326)
        
        model.geometry_type = defect.geometry_type
        
        # Обновляем привязанную геометрию
        if defect.snapped_coordinates:
            if len(defect.snapped_coordinates) == 1:
                point = Point(defect.snapped_coordinates[0][0], defect.snapped_coordinates[0][1])
                model.snapped_geometry = from_shape(point, srid=4326)
            else:
                line = LineString(defect.snapped_coordinates)
                model.snapped_geometry = from_shape(line, srid=4326)
        else:
            model.snapped_geometry = None
        
        model.distance_to_road = defect.distance_to_road_meters
        model.defect_type = defect.defect_type
        model.severity = defect.severity
        model.description = defect.description
        model.status = defect.status
        model.rejection_reason = defect.rejection_reason
        
        # Обновляем информацию о дороге
        if defect.road_info:
            model.osm_way_id = defect.road_info.osm_way_id
            model.road_name = defect.road_info.road_name
            model.road_class = defect.road_info.road_class
        else:
            model.osm_way_id = None
            model.road_name = None
            model.road_class = None
        
        model.photos = defect.photos
        model.created_by = defect.created_by
        model.created_at = defect.created_at
        model.moderated_by = defect.moderated_by
        model.moderated_at = defect.moderated_at
        
        return model
    
    async def get_by_id(self, defect_id: UUID) -> Optional[RoadDefect]:
        """Получить по ID"""
        stmt = select(RoadDefectModel).where(RoadDefectModel.id == defect_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return await self._to_entity(model) if model else None
    
    
    async def get_by_user_id(self, user_id: str) -> List[RoadDefect]:
        """Получить по ID пользователя"""
        stmt = select(RoadDefectModel).where(RoadDefectModel.created_by == user_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [await self._to_entity(m) for m in models]
    
    async def find_nearby(
        self,
        center: Coordinate,
        radius: Distance,
        defect_types: List[DefectType] | None = None,
        min_severity: SeverityLevel | None = None
    ) -> List[RoadDefect]:
        """Найти дефекты рядом"""
        point = ST_SetSRID(ST_MakePoint(center.longitude, center.latitude), 4326)
        
        stmt = select(RoadDefectModel).where(
            RoadDefectModel.status == DefectStatus.APPROVED,
            RoadDefectModel.snapped_geometry.is_not(None),
            ST_DWithin(RoadDefectModel.snapped_geometry, point, radius.value_meters)
        )
        
        if defect_types:
            stmt = stmt.where(RoadDefectModel.defect_type.in_(defect_types))
        
        if min_severity:
            stmt = stmt.where(RoadDefectModel.severity >= min_severity)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [await self._to_entity(m) for m in models]
    
    async def find_in_viewport(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        defect_types: Optional[List[DefectType]] = None,
        min_severity: Optional[SeverityLevel] = None,
        limit: int = 1000
    ) -> List[RoadDefect]:
        """
        Находит дефекты внутри прямоугольника (viewport/bounding box).
        Оптимизировано для карты: загружает только то, что видно на экране.
        """
        # 1. Создаем прямоугольник (Bounding Box)
        bbox = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
        
        # 2. Формируем запрос
        stmt = select(RoadDefectModel).where(
            RoadDefectModel.status == DefectStatus.APPROVED,
            RoadDefectModel.snapped_geometry.is_not(None),
            ST_Intersects(RoadDefectModel.snapped_geometry, bbox)
        )
        
        # Фильтры
        if defect_types:
            stmt = stmt.where(RoadDefectModel.defect_type.in_(defect_types))
            
        if min_severity:
            stmt = stmt.where(RoadDefectModel.severity >= min_severity)
        
        if limit < 500:
            stmt = stmt.order_by(func.random())
        
        stmt = stmt.limit(limit)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [await self._to_entity(m) for m in models]
    
    
    async def get_pending(self, offset: int = 0, limit: int = 10) -> List[RoadDefect]:
        """Получить дефекты на модерацию"""
        stmt = select(RoadDefectModel).where(
            RoadDefectModel.status == DefectStatus.PENDING
        ).order_by(RoadDefectModel.created_at).offset(offset).limit(limit)
        
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [await self._to_entity(m) for m in models]
    
    async def update_status(
        self,
        defect_id: UUID,
        status: DefectStatus,
        moderated_by: str,
        reason: str | None = None
    ) -> Optional[RoadDefect]:
        """Обновить статус"""
        stmt = update(RoadDefectModel).where(
            RoadDefectModel.id == defect_id
        ).values(
            status=status,
            moderated_by=moderated_by,
            moderated_at=datetime.now(),
            rejection_reason=reason
        ).returning(RoadDefectModel)
        
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        return await self._to_entity(model) if model else None
    
    async def delete(self, defect_id: UUID) -> bool:
        """Мягкое удаление - меняем статус на deleted"""
        stmt = update(RoadDefectModel).where(
            RoadDefectModel.id == defect_id
        ).values(status=DefectStatus.REJECTED, rejection_reason="deleted_by_user")
        
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def _to_entity(self, model: RoadDefectModel) -> RoadDefect:
        """Конвертировать ORM модель в доменную сущность"""
        # Извлекаем координаты
        geom = to_shape(model.original_geometry)
        if isinstance(geom, Point):
            geometry_type = GeometryType.POINT
            coordinates = [(geom.x, geom.y)]
        else:
            geometry_type = GeometryType.LINESTRING
            coordinates = [(c[0], c[1]) for c in geom.coords]
        
        # Привязанные координаты
        snapped_coords = None
        if model.snapped_geometry:
            snapped_geom = to_shape(model.snapped_geometry)
            if isinstance(snapped_geom, Point):
                snapped_coords = [(snapped_geom.x, snapped_geom.y)]
            else:
                snapped_coords = [(c[0], c[1]) for c in snapped_geom.coords]
        
        # Информация о дороге
        road_info = None
        if model.osm_way_id:
            road_info = RoadInfo(
                osm_way_id=model.osm_way_id,
                road_name=model.road_name,
                road_class=model.road_class,
                distance_to_road=model.distance_to_road
            )
        
        return RoadDefect(
            id=model.id,
            defect_type=model.defect_type,
            severity=model.severity,
            geometry_type=geometry_type,
            original_coordinates=coordinates,
            created_by=model.created_by,
            description=model.description,
            status=model.status,
            snapped_coordinates=snapped_coords,
            road_info=road_info,
            distance_to_road_meters=model.distance_to_road,
            photos=model.photos,
            created_at=model.created_at,
            moderated_by=model.moderated_by,
            moderated_at=model.moderated_at,
            rejection_reason=model.rejection_reason
        )
    
    async def _to_model(self, defect: RoadDefect) -> RoadDefectModel:
        """Конвертировать доменную сущность в ORM модель"""
        # Создаём геометрию
        if defect.geometry_type == GeometryType.POINT:
            point = Point(defect.original_coordinates[0][0], defect.original_coordinates[0][1])
            geometry = from_shape(point, srid=4326)
        else:
            line = LineString(defect.original_coordinates)
            geometry = from_shape(line, srid=4326)
        
        # Привязанная геометрия
        snapped_geometry = None
        if defect.snapped_coordinates:
            if len(defect.snapped_coordinates) == 1:
                point = Point(defect.snapped_coordinates[0][0], defect.snapped_coordinates[0][1])
                snapped_geometry = from_shape(point, srid=4326)
            else:
                line = LineString(defect.snapped_coordinates)
                snapped_geometry = from_shape(line, srid=4326)
        
        return RoadDefectModel(
            id=defect.id,
            original_geometry=geometry,
            geometry_type=defect.geometry_type,
            snapped_geometry=snapped_geometry,
            distance_to_road=defect.distance_to_road_meters,
            defect_type=defect.defect_type,
            severity=defect.severity,
            description=defect.description,
            status=defect.status,
            rejection_reason=defect.rejection_reason,
            osm_way_id=defect.road_info.osm_way_id if defect.road_info else None,
            road_name=defect.road_info.road_name if defect.road_info else None,
            road_class=defect.road_info.road_class if defect.road_info else None,
            photos=defect.photos,
            created_by=defect.created_by,
            created_at=defect.created_at,
            moderated_by=defect.moderated_by,
            moderated_at=defect.moderated_at
        )