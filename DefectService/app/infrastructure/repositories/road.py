from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.road import BaseRoadsRepository


class SQLAlchemyRoadsRepository(BaseRoadsRepository):
    """Репозиторий для работы с OSM данными"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def snap_point_to_road(
        self,
        lon: float,
        lat: float,
        max_distance_meters: float = 50
    ) -> Optional[Dict[str, Any]]:
        """Привязывает точку к ближайшей дороге"""
        
        query = text("""
            WITH point_wgs84 AS (
                SELECT ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) as geom
            ),
            point_3857 AS (
                SELECT ST_Transform(geom, 3857) as geom FROM point_wgs84
            ),
            nearest_road AS (
                SELECT 
                    osm_id,
                    name,
                    highway,
                    ST_ClosestPoint(way, (SELECT geom FROM point_3857)) as snapped_3857,
                    ST_Distance((SELECT geom FROM point_3857), way) as distance_meters
                FROM public.planet_osm_line
                WHERE highway IS NOT NULL
                AND ST_DWithin((SELECT geom FROM point_3857), way, :max_distance)
                ORDER BY (SELECT geom FROM point_3857) <-> way
                LIMIT 1
            )
            SELECT 
                osm_id,
                name as road_name,
                highway as road_class,
                distance_meters,
                ST_X(ST_Transform(snapped_3857, 4326)) as snapped_lon,
                ST_Y(ST_Transform(snapped_3857, 4326)) as snapped_lat
            FROM nearest_road
        """)
        
        result = await self.session.execute(query, {
            "lon": lon,
            "lat": lat,
            "max_distance": max_distance_meters
        })
        
        row = result.first()
        
        if row:
            return {
                "snapped_lon": row.snapped_lon,
                "snapped_lat": row.snapped_lat,
                "osm_way_id": row.osm_id,
                "road_name": row.road_name,
                "road_class": row.road_class,
                "distance_meters": row.distance_meters
            }
        return None