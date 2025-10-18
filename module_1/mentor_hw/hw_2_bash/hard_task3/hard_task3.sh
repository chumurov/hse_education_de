#!/usr/bin/env bash
set -Eeuo pipefail

# Настройки
SRC_DIR="${1:-$HOME/Downloads}"
IMAGES_DIR="${SRC_DIR}/Images"
DOCS_DIR="${SRC_DIR}/Documents"
LOG_FILE="${SRC_DIR}/organize_downloads.log"

# Создать папки, если их нет
mkdir -p "$IMAGES_DIR" "$DOCS_DIR"

log() {
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE"
}

move_with_logging() {
  local pattern="$1"
  local target_dir="$2"
  # find по шаблону в верхнем уровне каталога, безопасные имена, нулевой разделитель
  while IFS= read -r -d '' f; do
    base="$(basename "$f")"
    dest="$target_dir/$base"

    # Если существует одноимённый файл — добавляем суффикс времени, чтобы не перезаписать
    if [[ -e "$dest" ]]; then
      ext=""
      name="$base"
      if [[ "$base" == *.* ]]; then
        ext=".${base##*.}"
        name="${base%.*}"
      fi
      dest="$target_dir/${name}_$(date '+%Y%m%d_%H%M%S')${ext}"
    fi

    mv -v -- "$f" "$dest" \
      && log "Перенесен: $f -> $dest" \
      || log "Ошибка переноса: $f"
  done < <(find "$SRC_DIR" -maxdepth 1 -type f \( $pattern \) -print0)
}

log "==== Запуск в $SRC_DIR ===="

# Картинки: .jpg, .png, .gif
move_with_logging \
  "-iname *.jpg -o -iname *.jpeg -o -iname *.png -o -iname *.gif" \
  "$IMAGES_DIR"

# Документы: .txt, .pdf, .docx
move_with_logging \
  "-iname *.txt -o -iname *.pdf -o -iname *.docx" \
  "$DOCS_DIR"

log "==== Завершение ===="
