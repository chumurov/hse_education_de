#!/usr/bin/env zsh
set -euo pipefail

echo "Resetting MongoDB data (docker compose down, remove ./data)"
docker compose down

if [[ -d ./data ]]; then
  echo "Removing data folder ./data..."
  rm -rf ./data
fi

echo "Starting a fresh MongoDB container..."
docker compose up -d

echo "Done."
