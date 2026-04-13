#!/bin/bash

# Загрузка переменных окружения
source .env

# Переменные
OSM_FILE="moscow_oblast.osm.pbf"
PMTILES_FILE="moscow_oblast.pmtiles"

echo "Генерация PMTiles из OSM файла..."

# Шаг 1: Генерация тайлов
docker compose run --rm tilemaker \
  /data/osmpbf/${OSM_FILE} \
  --output /data/pmtiles/${PMTILES_FILE} \
  --config /data/config/config.json \
  --process /data/config/process.lua \
  --store /data/temp_store

if [ $? -ne 0 ]; then
  echo "Ошибка при генерации тайлов"
  exit 1
fi

echo "Тайлы сгенерированы: pmtiles/${PMTILES_FILE}"

