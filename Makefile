.PHONY: validate up traffic verify down

validate:
	@echo "=== Validating docker-compose configuration ==="
	bash scripts/validate.sh

up:
	@echo "=== Starting observability stack ==="
	docker compose up -d

traffic:
	@echo "=== Generating sample traffic ==="
	docker compose exec -T app python -c "\
import urllib.request; \
[urllib.request.urlopen(f'http://localhost:8080/slow') for _ in range(3)]; \
[urllib.request.urlopen(f'http://localhost:8080/error') for _ in range(2)]; \
[urllib.request.urlopen(f'http://localhost:8080/') for _ in range(10)]; \
[urllib.request.urlopen(f'http://localhost:8080/chain') for _ in range(5)]; \
[urllib.request.urlopen(f'http://localhost:8080/healthz') for _ in range(5)]; \
print('Traffic generated')"

verify:
	@echo "=== Verifying telemetry data ==="
	bash scripts/verify-telemetry.sh

down:
	@echo "=== Stopping observability stack ==="
	docker compose down --volumes

clean: down
	@echo "=== Cleaning up volumes ==="
	bash scripts/cleanup.sh

help:
	@echo "Available targets:"
	@echo "  validate  - Validate docker-compose configuration"
	@echo "  up        - Start the observability stack"
	@echo "  traffic   - Generate sample traffic"
	@echo "  verify    - Verify telemetry data"
	@echo "  down      - Stop the observability stack"
	@echo "  clean     - Stop and remove volumes"
	@echo "  help      - Show this help"
