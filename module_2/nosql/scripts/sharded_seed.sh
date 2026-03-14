#!/usr/bin/env zsh
set -euo pipefail

source .env 2>/dev/null || true

docker exec \
  -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
  -e TEACHERS_COUNT="${TEACHERS_COUNT:-5}" \
  -e STUDENTS_COUNT="${STUDENTS_COUNT:-50}" \
  -e COURSES_COUNT="${COURSES_COUNT:-8}" \
  -e GRADES_PER_STUDENT_MIN="${GRADES_PER_STUDENT_MIN:-2}" \
  -e GRADES_PER_STUDENT_MAX="${GRADES_PER_STUDENT_MAX:-4}" \
  nosql_mongos \
  mongosh --quiet --port 27017 /init-scripts/02_seed.js

docker exec \
  -e MONGO_INITDB_DATABASE="${MONGO_INITDB_DATABASE:-appdb}" \
  nosql_mongos \
  mongosh --quiet --port 27017 /scripts/rebalance-grades.js
