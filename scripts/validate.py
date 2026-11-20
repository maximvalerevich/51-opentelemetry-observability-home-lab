#!/usr/bin/env python3
"""Validate the observability stack configuration."""

import sys
import yaml
import json
from pathlib import Path

def validate_yaml(filepath):
    """Validate YAML file syntax."""
    try:
        with open(filepath, 'r') as f:
            yaml.safe_load(f)
        return True, None
    except Exception as e:
        return False, str(e)

def validate_python(filepath):
    """Validate Python syntax."""
    try:
        import py_compile
        py_compile.compile(filepath, doraise=True)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    base = Path(__file__).parent.parent
    print("=== Validate Docker Compose Configuration ===")
    print()
    
    errors = []
    
    # Check docker-compose.yml
    print("Checking docker-compose.yml...")
    filepath = base / "docker-compose.yml"
    if filepath.exists():
        valid, err = validate_yaml(filepath)
        if valid:
            print("✓ docker-compose.yml: valid YAML")
        else:
            print(f"✗ docker-compose.yml: {err}")
            errors.append(f"docker-compose.yml: {err}")
    else:
        print("✗ docker-compose.yml: MISSING")
        errors.append("docker-compose.yml: MISSING")
    
    # Validate otel-collector.yaml
    print("Checking otel-collector.yaml...")
    filepath = base / "otel-collector.yaml"
    if filepath.exists():
        valid, err = validate_yaml(filepath)
        if valid:
            print("✓ otel-collector.yaml: valid YAML")
        else:
            print(f"✗ otel-collector.yaml: {err}")
            errors.append(f"otel-collector.yaml: {err}")
    else:
        print("✗ otel-collector.yaml: MISSING")
        errors.append("otel-collector.yaml: MISSING")
    
    # Validate prometheus.yml
    print("Checking prometheus.yml...")
    filepath = base / "prometheus.yml"
    if filepath.exists():
        valid, err = validate_yaml(filepath)
        if valid:
            print("✓ prometheus.yml: valid YAML")
        else:
            print(f"✗ prometheus.yml: {err}")
            errors.append(f"prometheus.yml: {err}")
    else:
        print("✗ prometheus.yml: MISSING")
        errors.append("prometheus.yml: MISSING")
    
    # Validate prometheus-rules.yml
    print("Checking prometheus-rules.yml...")
    filepath = base / "prometheus-rules.yml"
    if filepath.exists():
        valid, err = validate_yaml(filepath)
        if valid:
            print("✓ prometheus-rules.yml: valid YAML")
        else:
            print(f"✗ prometheus-rules.yml: {err}")
            errors.append(f"prometheus-rules.yml: {err}")
    else:
        print("✗ prometheus-rules.yml: MISSING")
        errors.append("prometheus-rules.yml: MISSING")
    
    # Validate tempo.yaml
    print("Checking tempo.yaml...")
    filepath = base / "tempo.yaml"
    if filepath.exists():
        valid, err = validate_yaml(filepath)
        if valid:
            print("✓ tempo.yaml: valid YAML")
        else:
            print(f"✗ tempo.yaml: {err}")
            errors.append(f"tempo.yaml: {err}")
    else:
        print("✗ tempo.yaml: MISSING")
        errors.append("tempo.yaml: MISSING")
    
    # Validate grafana provisioning files
    print("Checking grafana provisioning files...")
    for fname in ["datasources.yaml", "dashboards.yaml", "red-slo-dashboard.json"]:
        # Try datasources path first, then dashboards
        paths_to_check = [
            base / "grafana" / "provisioning" / "datasources" / fname,
            base / "grafana" / "provisioning" / "dashboards" / fname
        ]
        found = False
        for filepath in paths_to_check:
            if filepath.exists():
                found = True
                if fname.endswith('.json'):
                    try:
                        json.load(open(filepath))
                        print(f"✓ {fname}: valid JSON")
                    except Exception as e:
                        print(f"✗ {fname}: {e}")
                        errors.append(f"{fname}: {e}")
                else:
                    valid, err = validate_yaml(filepath)
                    if valid:
                        print(f"✓ {fname}: valid YAML")
                    else:
                        print(f"✗ {fname}: {err}")
                        errors.append(f"{fname}: {err}")
                break
        if not found:
            print(f"✗ {fname}: MISSING")
            errors.append(f"{fname}: MISSING")
    
    print()
    print("=== Validate Docker Build ===")
    if (base / "app" / "Dockerfile").exists():
        print("Checking Dockerfile syntax...")
        with open(base / "app" / "Dockerfile") as f:
            content = f.read()
            if "FROM" in content and "RUN" in content and "COPY" in content:
                print("✓ Dockerfile: basic syntax OK")
            else:
                print("✗ Dockerfile: missing required instructions")
                errors.append("Dockerfile: missing instructions")
    else:
        print("✗ Dockerfile: MISSING")
        errors.append("Dockerfile: MISSING")
    
    print()
    print("=== Validate Python Application ===")
    if (base / "app" / "app.py").exists():
        print("Checking Python syntax...")
        valid, err = validate_python(base / "app" / "app.py")
        if valid:
            print("✓ app/app.py: valid Python")
        else:
            print(f"✗ app/app.py: {err}")
            errors.append(f"app/app.py: {err}")
    else:
        print("✗ app/app.py: MISSING")
        errors.append("app/app.py: MISSING")
    
    print()
    print("=== Validate Configuration Files ===")
    print("Checking required files exist...")
    
    required_files = [
        ".gitignore",
        "app/requirements.txt",
        "app/Dockerfile",
        "app/app.py",
        "otel-collector.yaml",
        "prometheus.yml",
        "prometheus-rules.yml",
        "tempo.yaml",
        "docker-compose.yml",
        "Makefile",
    ]
    
    for relpath in required_files:
        filepath = base / relpath
        if filepath.exists():
            print(f"✓ {relpath}")
        else:
            print(f"✗ {relpath}: MISSING")
            errors.append(f"{relpath}: MISSING")
    
    print()
    print("=== Validate Grafana Provisioning ===")
    grafana_files = [
        "grafana/provisioning/datasources/datasources.yaml",
        "grafana/provisioning/dashboards/dashboards.yaml",
        "grafana/provisioning/dashboards/red-slo-dashboard.json",
    ]
    
    for relpath in grafana_files:
        filepath = base / relpath
        if filepath.exists():
            print(f"✓ {relpath}")
        else:
            print(f"✗ {relpath}: MISSING")
            errors.append(f"{relpath}: MISSING")
    
    print()
    print("=== Validation Complete ===")
    
    if errors:
        print()
        print("ERRORS FOUND:")
        for e in errors:
            print(f"  - {e}")
        print()
        print("Validation FAILED")
        return 1
    else:
        print()
        print("All checks passed!")
        print("Validation PASSED")
        return 0

if __name__ == "__main__":
    sys.exit(main())
