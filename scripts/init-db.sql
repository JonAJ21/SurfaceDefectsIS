
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS hstore; 

CREATE SCHEMA IF NOT EXISTS osm;
COMMENT ON SCHEMA osm IS 'Schema for OpenStreetMap data imported via osm2pgsql';




GRANT ALL ON SCHEMA osm TO "user";
GRANT ALL ON SCHEMA public TO "user";


ALTER DEFAULT PRIVILEGES IN SCHEMA osm GRANT ALL ON TABLES TO "user";
ALTER DEFAULT PRIVILEGES IN SCHEMA osm GRANT ALL ON SEQUENCES TO "user";


CREATE OR REPLACE FUNCTION osm.length_m(geom geometry)
RETURNS double precision AS $$
BEGIN
    RETURN ST_Length(geom::geography);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE OR REPLACE FUNCTION osm.merge_road_segments(
    road_name text, 
    road_type text DEFAULT NULL
)
RETURNS TABLE(osm_id bigint, merged_geom geometry) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        MIN(p.osm_id) AS osm_id,
        ST_LineMerge(ST_Collect(p.geom)) AS merged_geom
    FROM planet_osm_line p
    WHERE p.name = road_name
      AND (road_type IS NULL OR p.highway = road_type)
      AND p.geom IS NOT NULL
    GROUP BY p.name, p.highway;
END;
$$ LANGUAGE plpgsql;


CREATE INDEX IF NOT EXISTS idx_planet_osm_line_name ON planet_osm_line USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_planet_osm_line_highway ON planet_osm_line(highway) WHERE highway IS NOT NULL;


DO $$
BEGIN
    RAISE NOTICE '\nDatabase initialized: postgis, hstore, osm schema ready for user %', current_setting('user', true);
END $$;