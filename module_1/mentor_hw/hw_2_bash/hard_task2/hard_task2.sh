#!/bin/bash

LOG_FILE="./monitor.log"
MEMORY_THRESHOLD=80

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Мониторинг системы запущен ==="

# --- CPU ---
CPU_LOAD=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
log "Загрузка CPU: ${CPU_LOAD}%"

# --- Memory (через /proc/meminfo) ---
MEM_TOTAL=$(grep MemTotal /proc/meminfo | awk '{print $2}')  # в килобайтах
MEM_AVAILABLE=$(grep MemAvailable /proc/meminfo | awk '{print $2}')

if [[ -z "$MEM_TOTAL" || -z "$MEM_AVAILABLE" || "$MEM_TOTAL" -eq 0 ]]; then
    log "⚠️ Ошибка: не удалось определить использование памяти."
    exit 1
fi

MEM_USED=$((MEM_TOTAL - MEM_AVAILABLE))
MEM_USAGE=$(( 100 * MEM_USED / MEM_TOTAL ))
log "Использование памяти: ${MEM_USAGE}%"

# --- Disk ---
DISK_USAGE=$(df -h --total | awk '/total/ {print $5}')
log "Использование диска: ${DISK_USAGE}"

# --- Проверка порога памяти ---
if [ "$MEM_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
    log "⚠️ Память превышает ${MEMORY_THRESHOLD}%!"
    ps -eo pid,comm,%mem,%cpu --sort=-%mem | head -n 10 | tee -a "$LOG_FILE"
else
    log "✅ Использование памяти в норме."
fi

log "=== Мониторинг завершён ==="
