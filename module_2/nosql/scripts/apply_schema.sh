#!/usr/bin/env zsh
set -euo pipefail

APP_DB=${MONGO_INITDB_DATABASE:-appdb}
ROOT_USER=${MONGO_INITDB_ROOT_USERNAME:-root}
ROOT_PASS=${MONGO_INITDB_ROOT_PASSWORD:-example}

SCRIPT_PATH="/docker-entrypoint-initdb.d/01_schema.js"

# Copy the script into the container

docker cp mongo-init/01_schema.js nosql_mongo:/tmp/01_schema.js

# Run it with root user (admin auth)
docker exec -i nosql_mongo mongosh -u "$ROOT_USER" -p "$ROOT_PASS" --authenticationDatabase admin /tmp/01_schema.js

echo "Schema applied to database $APP_DB"
