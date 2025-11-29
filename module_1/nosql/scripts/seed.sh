#!/usr/bin/env zsh
set -euo pipefail

# By default seed only if empty; to force reseed set FORCE_SEED=true
FORCE=${FORCE_SEED:-false}
ROOT_USER=${MONGO_INITDB_ROOT_USERNAME:-root}
ROOT_PASS=${MONGO_INITDB_ROOT_PASSWORD:-example}

if [[ "$FORCE" == "true" ]]; then
  echo "FORCE seed enabled: clearing and reseeding collections"
fi

# Copy and run the script in the container

docker cp mongo-init/02_seed.js nosql_mongo:/tmp/02_seed.js

docker exec -i \
  -e FORCE_SEED=${FORCE} \
  nosql_mongo mongosh -u "$ROOT_USER" -p "$ROOT_PASS" --authenticationDatabase admin /tmp/02_seed.js

echo "Seeding completed"
