#!/bin/bash

read -r -p "Введите целое число: " n

# Проверка знака числа
if [ "$n" -gt 0 ]; then
  echo "Число $n положительное."
  i=1
  while [ "$i" -le "$n" ]; do
    echo "$i"
    ((i++))
  done
elif [ "$n" -lt 0 ]; then
  echo "Число $n отрицательное."
else
  echo "Число равно нулю."
fi



