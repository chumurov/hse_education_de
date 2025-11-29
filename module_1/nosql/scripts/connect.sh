#!/usr/bin/env zsh
set -euo pipefail

# Connect to MongoDB using mongosh inside the container
# If you have mongosh installed locally, you can use the connection string instead.

# Use env vars if present
source .env || true

ROOT_USER=${MONGO_INITDB_ROOT_USERNAME:-root}
ROOT_PASS=${MONGO_INITDB_ROOT_PASSWORD:-example}
PORT=27017

if docker ps --filter "name=nosql_mongo" --format '{{.Names}}' | grep -q nosql_mongo; then
  echo "Opening mongosh inside container (admin user)"
  docker exec -it nosql_mongo mongosh -u "$ROOT_USER" -p "$ROOT_PASS" --authenticationDatabase admin
else
  echo "Container not running. Start it with scripts/start.sh"
fi
