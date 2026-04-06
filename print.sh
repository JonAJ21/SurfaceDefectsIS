#!/bin/sh

# Укажите путь к директории
directory="AuthService/app/domain"

if [ -d "$directory" ]; then
    echo "Содержимое директории $directory:"
    find "$directory" -type f -exec cat {} \;
else
    echo "Директория не существует: $directory"
    exit 1
fi