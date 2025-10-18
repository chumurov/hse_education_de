#!/bin/bash

# Проверяем аргумент
if [ -z "$1" ]; then
    echo "Использование: $0 <путь_к_директории>"
    exit 1
fi

SOURCE_DIR="$1"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="$(pwd)/$(basename "$SOURCE_DIR")_backup_${DATE}"
LOG_FILE="${BACKUP_DIR}/backup.log"

# Создаём папку для бэкапа
mkdir -p "$BACKUP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Начало резервного копирования..." | tee -a "$LOG_FILE"

count=0
for file in "$SOURCE_DIR"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "${BACKUP_DIR}/${filename}_${DATE}"
        echo "[$(date '+%H:%M:%S')] Скопирован файл: $filename" >> "$LOG_FILE"
        ((count++))
    fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Завершено: скопировано файлов — $count" | tee -a "$LOG_FILE"

echo "✅ Резервное копирование завершено. Создано $count файлов."
echo "📄 Лог сохранён в: $LOG_FILE"
