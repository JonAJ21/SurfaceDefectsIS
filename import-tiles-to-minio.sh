source .env

mc alias set defects-minio http://localhost:${DEFECTS_MINIO_API_PORT:-9000} \
  "${DEFECTS_MINIO_ROOT_USER}" "${DEFECTS_MINIO_ROOT_PASSWORD}"

mc mb defects-minio/pmtiles

mc cp ./TileMaker/pmtiles/small.pmtiles defects-minio/pmtiles/small.pmtiles

mc anonymous set download defects-minio/pmtiles

mc ls defects-minio/pmtiles/