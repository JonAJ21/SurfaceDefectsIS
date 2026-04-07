#!/bin/bash

PATTERNS=(".postgres" ".redis" ".auth-postgres" ".auth-redis" ".defects-minio" ".defects-postgres" ".defects-redis" "__pycache__")
DRY_RUN=false

# Парсим аргументы
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|-n)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            echo "Использование: $0 [--dry-run|-n] [-h|--help]"
            echo "  --dry-run, -n  Показать что будет удалено, но не удалять"
            exit 0
            ;;
        *)
            echo "Неизвестный аргумент: $1"
            exit 1
            ;;
    esac
done

echo "🔍 Поиск..."
echo ""

FOUND_ITEMS=()
for pattern in "${PATTERNS[@]}"; do
    while IFS= read -r item; do
        [ -n "$item" ] && FOUND_ITEMS+=("$item")
    done < <(find . -name "$pattern" 2>/dev/null)
done

if [ ${#FOUND_ITEMS[@]} -eq 0 ]; then
    echo "✅ Ничего не найдено"
    exit 0
fi

echo "Найдено ${#FOUND_ITEMS[@]} объектов:"
for item in "${FOUND_ITEMS[@]}"; do
    echo "  - $item"
done
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "📋 Dry-run режим. Ничего не удалено."
    exit 0
fi

read -p "Удалить эти объекты? (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Отменено"
    exit 1
fi

for item in "${FOUND_ITEMS[@]}"; do
    rm -rf "$item" 2>/dev/null && echo "✅ Удалено: $item"
done

echo ""
echo "✅ Готово!"