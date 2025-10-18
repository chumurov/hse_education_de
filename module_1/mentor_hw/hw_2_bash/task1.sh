#!/bin/sh
# usage: ./task1.sh path/to/file

# 1) Список всех объектов в текущей директории с указанием типа
# Используем find с -maxdepth 1 и -printf для получения типа и имени.
# Типы в %y: f=обычный файл, d=каталог, l=символическая ссылка, s=сокет, p=именованный канал, b=блочное, c=символьное.
echo "Типы объектов в текущей директории:"
find . -maxdepth 1 -mindepth 1 -printf '%y %p\n' | while read t name; do
  case "$t" in
    f) kind="файл" ;;
    d) kind="каталог" ;;
    l) kind="симв. ссылка" ;;
    s) kind="сокет" ;;
    p) kind="канал (FIFO)" ;;
    b) kind="блочное устройство" ;;
    c) kind="символьное устройство" ;;
    *) kind="неизвестный тип" ;;
  esac
  # Удалим ведущие ./ для аккуратного вывода
  clean_name="${name#./}"
  printf '%-16s %s\n' "$kind:" "$clean_name"
done

echo

# 2) Проверка наличия файла, переданного как аргумент
TARGET="$1"
if [ -z "$TARGET" ]; then
  echo "Не указан путь к файлу для проверки. Использование: $0 path/to/file" >&2
else
  if [ -e "$TARGET" ]; then
    if [ -f "$TARGET" ]; then
      echo "Найден: обычный файл: $TARGET"
    elif [ -d "$TARGET" ]; then
      echo "Найден: каталог: $TARGET"
    elif [ -L "$TARGET" ]; then
      echo "Найдена: символическая ссылка: $TARGET"
    else
      echo "Найден объект (не файл/каталог): $TARGET"
    fi
  else
    echo "Объект не найден: $TARGET"
  fi
fi

echo

# 3) Цикл for: имя и права доступа каждого объекта (как строка вида rwxr-xr-x)
# Возьмём краткий список через ls -A и для каждого вызовем stat, чтобы получить права.
# На Linux обычно доступно stat -c '%A %n'; на BSD/macOS можно заменить на 'stat -f "%Sp %N"'.
echo "Имя и права доступа:"
for item in * .*; do
  # пропустим . и ..
  [ "$item" = "." ] && continue
  [ "$item" = ".." ] && continue
  # Если файл/ссылка/каталог реально существует (включая скрытые), выводим
  if [ -e "$item" ] || [ -L "$item" ]; then
    # Права в символьном виде и имя
    perms="$(stat -c '%A' -- "$item" 2>/dev/null || stat -f '%Sp' -- "$item" 2>/dev/null)"
    printf '%s  %s\n' "$perms" "$item"
  fi
done
