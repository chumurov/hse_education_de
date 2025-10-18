#!/bin/bash
# --- Функция 1: выводит строку с префиксом "Hello, " ---
hello() {
    local name="$1"
    echo "Hello, $name"
}

# --- Функция 2: принимает два числа и возвращает их сумму ---
sum_numbers() {
    local a="$1"
    local b="$2"
    echo $((a + b))
}

# --- Вызовы функций ---
hello "World"

result=$(sum_numbers 5 7)
echo "Сумма чисел 5 и 7: $result"



