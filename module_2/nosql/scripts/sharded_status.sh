#!/usr/bin/env zsh
set -euo pipefail

source .env 2>/dev/null || true

docker exec nosql_mongos mongosh --quiet --port 27017 --eval "sh.status()"
docker exec nosql_mongos mongosh --quiet --port 27017 --eval "db.getSiblingDB('${MONGO_INITDB_DATABASE:-appdb}').grades.getShardDistribution()"
