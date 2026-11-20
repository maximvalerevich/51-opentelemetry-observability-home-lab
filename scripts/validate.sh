#!/bin/bash
set -e

echo "=== Validate Docker Compose Configuration ==="
echo ""

# Check docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "ERROR: docker-compose.yml not found"
    exit 1
fi

# Validate YAML syntax
echo "Checking YAML syntax..."
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" && echo "✓ docker-compose.yml: valid YAML"

# Validate otel-collector.yaml
if [ -f "otel-collector.yaml" ]; then
    python3 -c "import yaml; yaml.safe_load(open('otel-collector.yaml'))" && echo "✓ otel-collector.yaml: valid YAML"
fi

# Validate prometheus.yml
if [ -f "prometheus.yml" ]; then
    python3 -c "import yaml; yaml.safe_load(open('prometheus.yml'))" && echo "✓ prometheus.yml: valid YAML"
fi

# Validate tempo.yaml
if [ -f "tempo.yaml" ]; then
    python3 -c "import yaml; yaml.safe_load(open('tempo.yaml'))" && echo "✓ tempo.yaml: valid YAML"
fi

# Validate grafana provisioning files
if [ -f "grafana/provisioning/datasources/datasources.yaml" ]; then
    python3 -c "import yaml; yaml.safe_load(open('grafana/provisioning/datasources/datasources.yaml'))" && echo "✓ datasources.yaml: valid YAML"
fi

if [ -f "grafana/provisioning/dashboards/dashboards.yaml" ]; then
    python3 -c "import yaml; yaml.safe_load(open('grafana/provisioning/dashboards/dashboards.yaml'))" && echo "✓ dashboards.yaml: valid YAML"
fi

echo ""
echo "=== Validate Docker Build ==="
if [ -f "app/Dockerfile" ]; then
    echo "Checking Dockerfile syntax..."
    # Check for basic Dockerfile instructions
    if grep -q "^FROM" app/Dockerfile && grep -q "^RUN" app/Dockerfile && grep -q "^COPY" app/Dockerfile; then
        echo "✓ Dockerfile: basic syntax OK"
    else
        echo "✗ Dockerfile: missing required instructions"
        exit 1
    fi
fi

echo ""
echo "=== Validate Python Application ==="
if [ -f "app/app.py" ]; then
    echo "Checking Python syntax..."
    python3 -m py_compile app/app.py && echo "✓ app/app.py: valid Python"
fi

echo ""
echo "=== Validate Configuration Files ==="
echo "Checking required files exist..."

required_files=(
    ".gitignore"
    "app/requirements.txt"
    "app/Dockerfile"
    "app/app.py"
    "otel-collector.yaml"
    "prometheus.yml"
    "prometheus-rules.yml"
    "tempo.yaml"
    "docker-compose.yml"
    "Makefile"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file: MISSING"
        exit 1
    fi
done

echo ""
echo "=== Validate Grafana Provisioning ==="
grafana_files=(
    "grafana/provisioning/datasources/datasources.yaml"
    "grafana/provisioning/dashboards/dashboards.yaml"
    "grafana/provisioning/dashboards/red-slo-dashboard.json"
)

for file in "${grafana_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file: MISSING"
        exit 1
    fi
done

echo ""
echo "=== Validation Complete ==="
echo "All checks passed!"
