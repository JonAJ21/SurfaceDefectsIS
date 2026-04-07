from datetime import datetime
from typing import Any, Optional, List
from uuid import UUID, uuid4
from sqlalchemy import (
    String, Float, DateTime, Text, JSON,
    Enum as SQLEnum, BigInteger, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry


from domain.values.defect_types import DefectStatus, DefectType, GeometryType, SeverityLevel
from infrastructure.database.session import Base



class RoadDefectModel(Base):
    __tablename__ = "road_defects"
    __table_args__ = (
        Index("idx_defect_geometry", "snapped_geometry", postgresql_using="gist"),
        Index("idx_defect_status", "status"),
    )
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    
    # Геометрия
    original_geometry: Mapped[Any] = mapped_column(Geometry('GEOMETRY', srid=4326), nullable=False)
    geometry_type: Mapped[GeometryType] = mapped_column(SQLEnum(GeometryType), nullable=False)
    snapped_geometry: Mapped[Optional[Any]] = mapped_column(Geometry('GEOMETRY', srid=4326), nullable=True)
    distance_to_road: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Данные дефекта
    defect_type: Mapped[DefectType] = mapped_column(SQLEnum(DefectType), nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(SQLEnum(SeverityLevel), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Статус
    status: Mapped[DefectStatus] = mapped_column(SQLEnum(DefectStatus), nullable=False, default=DefectStatus.PENDING)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Привязка к дороге
    osm_way_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    road_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    road_class: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Фото
    photos: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    # Кто создал
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Модерация
    moderated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    moderated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)