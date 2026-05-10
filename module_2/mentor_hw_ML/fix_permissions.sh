#!/usr/bin/env sh
set -eu

mkdir -p dags logs logs/dag_processor plugins config ddl data

docker run --rm \
  -v "$(pwd)/dags:/mnt/dags" \
  -v "$(pwd)/logs:/mnt/logs" \
  alpine:latest \
  sh -c '
    chmod -R 777 /mnt/dags /mnt/logs
    mkdir -p /mnt/logs/dag_processor
    chmod -R 777 /mnt/logs
  '

echo "Permissions for dags/ and logs/ have been fixed."
