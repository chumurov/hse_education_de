#!/usr/bin/env zsh
set -euo pipefail

echo "Stopping MongoDB container (docker compose)..."
docker compose down

echo "Done."
