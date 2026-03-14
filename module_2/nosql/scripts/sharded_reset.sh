#!/usr/bin/env zsh
set -euo pipefail

docker compose -p nosql-sharded -f docker-compose.sharded.yml down -v
