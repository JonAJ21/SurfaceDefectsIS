#!/usr/bin/env bash

DIRECTORY="./DefectService/app"

# === НАСТРОЙКИ ИГНОРИРОВАНИЯ ===
# 📁 Директории (рекурсивно пропускаются целиком)
IGNORE_DIRS=("__pycache__" "node_modules" ".git" ".idea" "dist" "build" ".next")

# 📄 Файлы и расширения (пропускаются по имени или маске)
IGNORE_PATTERNS=("package-lock.json" "yarn.lock" ".DS_Store" "*.md" "*.png" "*.jpg" "*.log" "*.pyc" "*.svg")
# ===============================

# Убираем слэш в конце, если он есть, для корректной работы подстановки
DIRECTORY="${DIRECTORY%/}"

if [[ ! -d "$DIRECTORY" ]]; then
    echo "❌ Директория не существует: $DIRECTORY" >&2
    exit 1
fi

# Собираем аргументы для find
find_args=()

# 1️⃣ Игнор директорий (прерываем рекурсию через -prune)
if (( ${#IGNORE_DIRS[@]} > 0 )); then
    find_args+=( "(" )
    for i in "${!IGNORE_DIRS[@]}"; do
        find_args+=( -name "${IGNORE_DIRS[$i]}" )
        (( i < ${#IGNORE_DIRS[@]} - 1 )) && find_args+=( -o )
    done
    find_args+=( ")" -prune -o )
fi

# 2️⃣ Игнор файлов и расширений
for pat in "${IGNORE_PATTERNS[@]}"; do
    find_args+=( ! -name "$pat" )
done

# 3️⃣ Ищем только файлы, выводим через null-байт (безопасно для пробелов/спецсимволов)
find_args+=( -type f -print0 )

# Выполняем поиск
find "$DIRECTORY" "${find_args[@]}" | while IFS= read -r -d '' file; do
    # 🔑 Вычисляем относительный путь (отбрасываем префикс DIRECTORY/)
    rel_path="${file#"$DIRECTORY"/}"

    printf "\n=== Файл: %s ===\n" "$rel_path"
    cat "$file" 2>/dev/null || printf "[⚠️ Нет прав на чтение]\n"
    printf "\n%s\n" "────────────────────────────────────────"
done