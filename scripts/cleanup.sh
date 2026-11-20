#!/bin/bash
set -e

echo "=== Cleanup Script ==="
echo ""

# Stop and remove containers
echo "Stopping containers..."
docker compose down -v --remove-orphans 2>/dev/null || true

# Remove volumes
echo "Removing volumes..."
docker volume rm 51-opentelemetry-observability-home-lab_tempo-data 51-opentelemetry-observability-home-lab_grafana-data 2>/dev/null || true

# Remove images
echo "Removing images..."
docker rmi 51-opentelemetry-observability-home-lab-app 2>/dev/null || true

echo ""
echo "=== Cleanup Complete ==="
