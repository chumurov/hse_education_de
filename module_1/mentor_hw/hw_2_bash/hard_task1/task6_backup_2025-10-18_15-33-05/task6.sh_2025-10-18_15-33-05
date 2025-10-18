#!/usr/bin/env bash
set -euo pipefail

# 1) Читать данные из файла input.txt и посчитать строки
#    stdin берём из input.txt, stdout направляем в output.txt
wc -l < input.txt > output.txt

# 2) Намеренно вызвать ошибку ls для несуществующего файла
#    stderr перенаправить в error.log, stdout игнорировать или оставить при необходимости
ls "Нет такого файла$(date +%s)" 2> error.log
