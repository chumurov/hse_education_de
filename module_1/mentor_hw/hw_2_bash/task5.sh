#!/bin/bash
set -m  # включаем управление заданиями
# Запускаем два sleep в фоне и сохраняем PID
sleep 25 & pid1=$!
sleep 25 & pid2=$!

jobs -l
fg %1
jobs -l
bg %1
jobs -l
