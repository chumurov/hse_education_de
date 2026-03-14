#!/usr/bin/env zsh
set -euo pipefail

# Ensure .env exists
if [[ ! -f .env ]]; then
  echo ".env file not found — creating default .env (local dev only)."
  cat > .env <<EOF
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
MONGO_INITDB_DATABASE=appdb
MONGO_APP_USERNAME=appuser
MONGO_APP_PASSWORD=apppassword
EOF
fi

echo "Starting MongoDB container (docker compose)..."
docker compose up -d

echo "Waiting for container to become healthy..."
# Wait for health check
i=0
until docker inspect --format='{{json .State.Health.Status}}' nosql_mongo | grep -q "healthy" || [[ $i -gt 30 ]]; do
  sleep 1
  i=$((i+1))
done

if [[ $i -gt 30 ]]; then
  echo "Timeout waiting for MongoDB healthcheck — check container logs."
else
  echo "MongoDB is healthy and running."
fi

echo "Container status:"
docker compose ps

echo "Done. You can connect with mongosh or docker exec."
