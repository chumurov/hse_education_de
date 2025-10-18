#!/bin/bash

# Проверяем, что пользователь передал аргумент
if [ -z "$1" ]; then
  echo "Использование: $0 <путь_к_директории>"
  exit 1
fi

# Выводим текущее значение PATH
echo "Текущее значение PATH:"
echo "$PATH"

# Добавляем новую директорию в PATH
export PATH="$PATH:$1"

echo
echo "Обновлённый PATH:"
echo "$PATH"

