#!/usr/bin/env zsh
set -euo pipefail

docker exec -it nosql_mongos mongosh --port 27017
