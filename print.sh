directory="./modern-g7-32-main"

if [ -d "$directory" ]; then
    echo "Содержимое директории $directory:"
    find "$directory" -type f | while read -r file; do
        echo ""
        echo "=== Файл: $file ==="
        echo ""
        cat "$file"
    done
else
    echo "Директория не существует: $directory"
    exit 1
fi