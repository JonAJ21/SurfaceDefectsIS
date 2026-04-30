#!/usr/bin/env python3
"""
gen_data.py — Генерация 100 тестовых записей для road_defects
Запуск: python gen_data.py > defects_100.sql
"""

import uuid
import random
import json

# ─────────────────────────────────────────────────────────────────────────────
# КОНФИГУРАЦИЯ
# ─────────────────────────────────────────────────────────────────────────────
NUM_RECORDS = 100

# Границы Москвы
LAT_MIN, LAT_MAX = 55.5, 55.9
LON_MIN, LON_MAX = 37.4, 37.9

# ENUM-значения (в верхнем регистре, как в БД)
DEFECT_TYPES = [
    'POTHOLE', 'LONGITUDINAL_CRACK', 'TRANSVERSE_CRACK', 'ALLIGATOR_CRACK',
    'REPAIRED_CRACK', 'CROSSWALK_BLUR', 'LANE_LINE_BLUR', 'MANHOLE_COVER',
    'PATCH', 'RUTTING', 'OTHER'
]
SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
STATUSES = ['PENDING', 'APPROVED', 'REJECTED', 'FIXED']
GEOM_TYPES = ['POINT', 'LINESTRING']

# Тестовые данные
ROADS = [
    'Тверская улица', 'улица Арбат', 'Ленинский проспект', 'Кутузовский проспект',
    'Садовое кольцо', 'Бульварное кольцо', 'Мясницкая улица', 'Покровка',
    'Большая Дмитровка', 'улица Петровка', 'Цветной бульвар', 'Страстной бульвар',
    'улица 1905 года', 'Профсоюзная улица', 'Новый Арбат'
]
ROAD_CLASSES = ['primary', 'secondary', 'tertiary', 'residential', 'service', 'footway']
USER_IDS = [
    '044c7697-3405-4039-881f-138e339419ed',
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
    'b2c3d4e5-f6a7-8901-bcde-f12345678901',
    'c3d4e5f6-a7b8-9012-cdef-123456789012'
]
REJECTION_REASONS = [
    'NULL',
    "'Не соответствует ГОСТ Р 50597-2017'",
    "'Дубликат'",
    "'Низкое качество фото'",
    "'Неверные координаты'"
]


def rand_coord():
    """Случайные координаты в пределах Москвы"""
    return (
        round(random.uniform(LON_MIN, LON_MAX), 7),
        round(random.uniform(LAT_MIN, LAT_MAX), 7)
    )


def rand_geom():
    """Генерирует геометрию и возвращает (тип, WKT)"""
    gtype = random.choice(GEOM_TYPES)
    if gtype == 'POINT':
        lon, lat = rand_coord()
        return gtype, f'POINT ({lon} {lat})'
    else:
        # LINESTRING с 2-4 точками
        points = [rand_coord() for _ in range(random.randint(2, 4))]
        coords = ', '.join(f'{lon} {lat}' for lon, lat in points)
        return gtype, f'LINESTRING ({coords})'


def rand_timestamp():
    """Случайная дата в апреле 2026"""
    day = random.randint(1, 30)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    micro = random.randint(100000, 999999)
    return f'2026-04-{day:02d} {hour:02d}:{minute:02d}:{second:02d}.{micro}'


def generate_row(idx):
    """Генерирует одну строку VALUES для INSERT"""
    # UUID
    uid = str(uuid.uuid4())
    
    # Геометрия
    gtype, geom_wkt = rand_geom()
    
    # Snapped geometry: 85% привязаны, 15% NULL
    if random.random() < 0.85:
        snapped_wkt = geom_wkt
        distance = round(random.uniform(0, 15), 10)
    else:
        snapped_wkt = None
        distance = round(random.uniform(10, 20), 10)
    
    # Основные поля
    defect_type = random.choice(DEFECT_TYPES)
    severity = random.choice(SEVERITIES)
    status = random.choice(STATUSES)
    
    # Описание (простое, без сложных кавычек)
    descriptions = [
        'test', 'defect', 'road damage', 'pothole', 'crack',
        'manhole', 'blur', 'patch', 'rut', 'needs repair'
    ]
    description = random.choice(descriptions)
    
    # Rejection reason (только для REJECTED)
    if status == 'REJECTED':
        rejection_reason = random.choice(REJECTION_REASONS)
    else:
        rejection_reason = 'NULL'
    
    # Дорога
    osm_way_id = random.randint(100000000, 999999999)
    if random.random() < 0.85:
        road_name = "'" + random.choice(ROADS) + "'"
        road_class = "'" + random.choice(ROAD_CLASSES) + "'"
    else:
        road_name = 'NULL'
        road_class = 'NULL'
    
    # Фото (1-3 шт.)
    num_photos = random.randint(1, 3)
    photo_urls = [
        f'"http://localhost:9000/defects/defects/{uid}/p{i}.jpg"'
        for i in range(1, num_photos + 1)
    ]
    photos_json = '[' + ', '.join(photo_urls) + ']'
    
    # Пользователи и время
    created_by = random.choice(USER_IDS)
    created_at = rand_timestamp()
    
    # Модерация (только для утверждённых/отклонённых/исправленных)
    if status in ('APPROVED', 'REJECTED', 'FIXED') and random.random() < 0.7:
        moderated_by = "'" + random.choice(USER_IDS) + "'"
        moderated_at = "'" + rand_timestamp() + "'"
    else:
        moderated_by = 'NULL'
        moderated_at = 'NULL'
    
    # Формируем строку (без f-строк для сложных частей)
    snapped_sql = 'NULL' if snapped_wkt is None else f"'SRID=4326;{snapped_wkt}'::public.geometry"
    
    parts = [
        f"'{uid}'::uuid",
        f"'SRID=4326;{geom_wkt}'::public.geometry",
        f"'{gtype}'::public.geometrytype",
        snapped_sql,
        str(distance),
        f"'{defect_type}'::public.defecttype",
        f"'{severity}'::public.severitylevel",
        f"'{description}'",
        f"'{status}'::public.defectstatus",
        rejection_reason,
        str(osm_way_id),
        road_name,
        road_class,
        f"'{photos_json}'::json",
        f"'{created_by}'",
        f"'{created_at}'",
        moderated_by,
        moderated_at
    ]
    
    return '\t (' + ', '.join(parts) + ')'


def main():
    # Заголовок INSERT
    header = (
        "INSERT INTO public.road_defects "
        "(id,original_geometry,geometry_type,snapped_geometry,distance_to_road,"
        "defect_type,severity,description,status,rejection_reason,"
        "osm_way_id,road_name,road_class,photos,created_by,created_at,"
        "moderated_by,moderated_at) VALUES"
    )
    print(header)
    
    # Генерируем записи
    rows = []
    for i in range(NUM_RECORDS):
        rows.append(generate_row(i))
    
    # Вывод с запятыми между строками
    for i, row in enumerate(rows):
        if i < len(rows) - 1:
            print(row + ',')
        else:
            print(row + ';')


if __name__ == '__main__':
    main()