#!/bin/bash
set -e

echo "=== Verify Telemetry Data ==="
echo ""

# Check if services are running
echo "Checking if services are running..."

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Verify Prometheus is scrapeable
echo ""
echo "Checking Prometheus scrape target..."
if curl -sf http://localhost:9090/api/v1/targets | python3 -c "import sys, json; data=json.load(sys.stdin); targets=[t['labels']['instance'] for t in data['data']['activeTargets'] if t['health']=='up']; print(f'Healthy targets: {len(targets)}'); sys.exit(0 if targets else 1)" 2>/dev/null; then
    echo "✓ Prometheus: scrape targets healthy"
else
    echo "✗ Prometheus: unable to verify scrape targets"
fi

# Verify Tempo is accepting traces
echo ""
echo "Checking Tempo health..."
if curl -sf http://localhost:3200/status 2>/dev/null | grep -q "ready"; then
    echo "✓ Tempo: service ready"
else
    echo "✗ Tempo: service not responding"
fi

# Verify Grafana is running
echo ""
echo "Checking Grafana..."
if curl -sf http://localhost:3000/api/health 2>/dev/null | grep -q "ready"; then
    echo "✓ Grafana: service ready"
else
    echo "✗ Grafana: service not responding"
fi

echo ""
echo "=== Telemetry Verification Complete ==="
