#!/usr/bin/env zsh
set -euo pipefail

COMPOSE_FILE="docker-compose.sharded.yml"
PROJECT_NAME="nosql-sharded"
CORE_SERVICES=(nosql_cfg1 nosql_cfg2 nosql_cfg3 nosql_shard1 nosql_shard2)

source .env 2>/dev/null || true

wait_for_health() {
  local container_name="$1"
  local retries=60
  local i=0

  until [[ "$(docker inspect --format='{{json .State.Health.Status}}' "$container_name" 2>/dev/null || true)" == "\"healthy\"" ]]; do
    sleep 2
    i=$((i + 1))
    if [[ $i -ge $retries ]]; then
      echo "Timed out waiting for $container_name to become healthy"
      exit 1
    fi
  done
}

wait_for_primary() {
  local container_name="$1"
  local port="$2"
  local retries=60
  local i=0

  until docker exec "$container_name" mongosh --quiet --port "$port" --eval 'db.hello().isWritablePrimary || false' | grep -q "true"; do
    sleep 2
    i=$((i + 1))
    if [[ $i -ge $retries ]]; then
      echo "Timed out waiting for primary on $container_name:$port"
      exit 1
    fi
  done
}

echo "Starting sharded MongoDB cluster..."
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d

for service in "${CORE_SERVICES[@]}"; do
  wait_for_health "$service"
done

echo "Initializing replica sets..."
docker exec nosql_cfg1 mongosh --quiet --port 27019 /scripts/init-cfg.js
docker exec nosql_shard1 mongosh --quiet --port 27018 /scripts/init-shard1.js
docker exec nosql_shard2 mongosh --quiet --port 27018 /scripts/init-shard2.js

wait_for_primary nosql_cfg1 27019
wait_for_primary nosql_shard1 27018
wait_for_primary nosql_shard2 27018

wait_for_health nosql_mongos

echo "Configuring shards..."
docker exec \
  -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
  nosql_mongos \
  mongosh --quiet --port 27017 /scripts/configure-cluster.js

echo "Applying schema through mongos..."
docker exec \
  -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
  -e INSERT_SAMPLE_DATA=false \
  nosql_mongos \
  mongosh --quiet --port 27017 /init-scripts/01_schema.js

if [[ "${SKIP_SEED:-false}" != "true" ]]; then
  echo "Seeding sharded cluster..."
  docker exec \
    -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
    -e TEACHERS_COUNT="${TEACHERS_COUNT:-5}" \
    -e STUDENTS_COUNT="${STUDENTS_COUNT:-50}" \
    -e COURSES_COUNT="${COURSES_COUNT:-8}" \
    -e GRADES_PER_STUDENT_MIN="${GRADES_PER_STUDENT_MIN:-2}" \
    -e GRADES_PER_STUDENT_MAX="${GRADES_PER_STUDENT_MAX:-4}" \
    nosql_mongos \
    mongosh --quiet --port 27017 /init-scripts/02_seed.js

  echo "Rebalancing grades chunks..."
  docker exec \
    -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
    nosql_mongos \
    mongosh --quiet --port 27017 /scripts/rebalance-grades.js
fi

echo "Sharded cluster is ready on mongodb://localhost:27018/${MONGO_INITDB_DATABASE:-appdb}"
