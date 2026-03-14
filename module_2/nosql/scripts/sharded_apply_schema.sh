#!/usr/bin/env zsh
set -euo pipefail

source .env 2>/dev/null || true

docker exec \
  -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
  nosql_mongos \
  mongosh --quiet --port 27017 /scripts/configure-cluster.js

docker exec \
  -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
  -e INSERT_SAMPLE_DATA=false \
  nosql_mongos \
  mongosh --quiet --port 27017 /init-scripts/01_schema.js
