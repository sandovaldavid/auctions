.PHONY: help up down migrate seed shell logs \
        test test-e2e test-a11y test-contrast test-responsive \
        download-axe build-playwright

# ── Local dev workflow ────────────────────────────────────────────────────────

help:
	@echo "Development targets:"
	@echo "  make up            Start Django + PostgreSQL (detached)"
	@echo "  make down          Stop all services"
	@echo "  make migrate       Run pending migrations"
	@echo "  make seed          Load sample data for all models"
	@echo "  make shell         Django interactive shell"
	@echo "  make logs          Follow web service logs"
	@echo ""
	@echo "Test targets:"
	@echo "  make test          Unit + integration tests (inside web container)"
	@echo "  make test-e2e      All E2E tests (Playwright in Docker)"
	@echo "  make test-a11y     Accessibility tests only (axe-core, WCAG 2.1 AA)"
	@echo "  make test-contrast Color contrast tests only"
	@echo "  make test-responsive Responsive layout tests only"
	@echo ""
	@echo "Setup:"
	@echo "  make download-axe  Download axe.min.js for local E2E runs"

up:
	docker compose up --build -d

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

seed:
	docker compose exec web python manage.py seed_data

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f web

# ── Testing ───────────────────────────────────────────────────────────────────

test:
	docker compose exec web pytest tests/unit/ tests/integration/ -v

# Requires: make up && make seed (run once before E2E tests)
# --no-cov: E2E tests connect via HTTP so Django code coverage is meaningless here
test-e2e:
	docker compose -f docker-compose.yml -f docker-compose.e2e.yml \
		run --rm playwright \
		pytest tests/e2e/ -v --browser chromium --base-url http://web:8000 \
		--no-cov --html=reports/e2e-report.html --self-contained-html

test-a11y:
	docker compose -f docker-compose.yml -f docker-compose.e2e.yml \
		run --rm playwright \
		pytest tests/e2e/test_accessibility.py -v --browser chromium --base-url http://web:8000 \
		-m a11y --no-cov --html=reports/e2e-a11y.html --self-contained-html

test-contrast:
	docker compose -f docker-compose.yml -f docker-compose.e2e.yml \
		run --rm playwright \
		pytest tests/e2e/test_contrast.py -v --browser chromium --base-url http://web:8000 \
		-m contrast --no-cov --html=reports/e2e-contrast.html --self-contained-html

test-responsive:
	docker compose -f docker-compose.yml -f docker-compose.e2e.yml \
		run --rm playwright \
		pytest tests/e2e/test_responsive.py -v --browser chromium --base-url http://web:8000 \
		-m responsive --no-cov --html=reports/e2e-responsive.html --self-contained-html

# ── Tooling ───────────────────────────────────────────────────────────────────

download-axe:
	mkdir -p tests/e2e/fixtures
	curl -fsSL -o tests/e2e/fixtures/axe.min.js \
		https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js
	@echo "axe.min.js downloaded to tests/e2e/fixtures/"

build-playwright:
	docker compose -f docker-compose.yml -f docker-compose.e2e.yml build playwright
