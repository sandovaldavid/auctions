# CLAUDE.md — Auctions Project

Guía de referencia para Claude Code y colaboradores. Define la arquitectura objetivo, convenciones y reglas del proyecto.

---

## Stack técnico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 5.1+ / Python 3.10 |
| Base de datos dev | SQLite (local) |
| Base de datos prod | PostgreSQL 16 |
| Frontend | Django Templates + Bootstrap 5.3 |
| Servidor WSGI | Gunicorn |
| Archivos estáticos | WhiteNoise |
| Contenedores | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Releases | release-please (Conventional Commits) |

---

## Arquitectura objetivo

```
Django Monolith (actual)
  └── auctions/          ← única app Django
       ├── models.py     ← User, Listing, Bid, Comment, Watchlist
       ├── views.py      ← 11 vistas SSR
       ├── forms.py      ← ListingForm, BidForm, CommentForm
       └── templates/    ← Bootstrap 5.3

Evolución planificada (en fases):
  Fase 2 → djangorestframework: API endpoints para Listing/Bid/Watchlist
  Fase 3 → django-channels + Redis: WebSockets para pujas en tiempo real
  Fase 4 → Celery: tareas asíncronas (notificaciones, expiración de subastas)
```

**Decisión de arquitectura:** Mantener Django monolito. No migrar a FastAPI, Node.js ni microservicios hasta que haya evidencia de necesidad de escala. Django ORM + admin justifica seguir con él para este dominio.

---

## Entornos de despliegue

| Entorno | Plataforma | Trigger |
|---------|-----------|---------|
| Local | `docker compose up` | Manual |
| Staging | Oracle VM (k3s + Argo CD) | Push a `develop` |
| Producción | Heroku (Docker stack) | Push a `main` via GitHub Actions |
| Producción futura | Oracle VM | Cuando se agoten créditos Heroku |

**Oracle VM:** ARM Ampere A1, 24 GB RAM, 200 GB SSD — Always Free. Ver `docs/oracle-vm-stack.md`.

---

## Ramas

| Rama | Propósito | Merge hacia |
|------|-----------|-------------|
| `main` | Producción | — |
| `develop` | Staging / integración | `main` (via PR) |
| `feature/*` | Nuevas features | `develop` |
| `fix/*` | Bug fixes | `develop` |
| `chore/*` | Mantenimiento | `develop` |
| `refactor/*` | Refactors | `develop` |
| `gh-pages` | Reportes de tests | — (rama independiente) |

**Reglas:**
- **Squash merge** para feature/fix/chore/refactor → `develop` — condensa los commits WIP del desarrollo en un commit limpio
- **Merge commit (--no-ff)** para `develop` → `main` — preserva los commits individuales de develop en main para que release-please calcule versiones correctamente desde los tipos reales (`fix`, `feat`)
- **Merge commit** para el backsync `main` → `develop` — preserva la ancestría de git y permite que release-please ancle su baseline desde los tags de main
- `main` solo acepta PRs desde `develop`
- Las ramas se eliminan automáticamente al hacer merge
- `main`, `develop` y `v2` están protegidas contra eliminación

**Tipo de merge según operación — elegir en el botón desplegable de GitHub:**

| Operación | Botón en GitHub UI |
|---|---|
| `feature/*` / `fix/*` → `develop` | **"Squash and merge"** |
| `develop` → `main` | **"Create a merge commit"** |
| `main` → `develop` (backsync) | **"Create a merge commit"** |

**Backsync main → develop (después de cada release estable):**
1. Crear rama `chore/sync-vX.Y.Z` desde `main`
2. Abrir PR a `develop` con título `chore(develop): sync main vX.Y.Z into develop`
3. Mergear con **"Create a merge commit"** (no squash)
4. Release-please en develop detectará automáticamente el nuevo baseline desde el tag de main

---

## Commits — Conventional Commits (obligatorio)

Formato: `type(scope): descripción imperativa en minúsculas`

```
feat(auctions): add real-time bid updates via WebSockets
fix(commerce): correct database URL parsing for SSL mode
ci(ci): add path filter to devcontainer workflow
```

### Tipos válidos

| Tipo | SemVer | Cuándo usarlo |
|------|--------|---------------|
| `feat` | MINOR | Nueva funcionalidad |
| `fix` | PATCH | Corrección de bug |
| `docs` | — | Solo documentación |
| `style` | — | Formato, whitespace (sin cambio de lógica) |
| `refactor` | — | Reestructura sin cambiar comportamiento |
| `perf` | — | Mejora de rendimiento |
| `test` | — | Agregar o actualizar tests |
| `build` | — | Sistema de build o dependencias |
| `ci` | — | Cambios en pipelines de CI/CD |
| `chore` | — | Mantenimiento, tooling |
| `revert` | — | Revertir commit anterior |
| `config` | — | Archivos de configuración |

### Scopes válidos

| Scope | Qué cubre |
|-------|-----------|
| `auctions` | App Django — modelos, vistas, forms, templates, admin, migrations |
| `commerce` | Config Django — settings.py, urls.py, wsgi.py, asgi.py |
| `ci` | GitHub Actions workflows, pre-commit |
| `docker` | Dockerfile, docker-compose.yml, docker-compose.prod.yml, nginx/ |
| `deps` | requirements.txt, requirements-dev.txt, pyproject.toml |
| `devcontainer` | .devcontainer/ |
| `docs` | docs/, README.md, CLAUDE.md |
| `infra` | Oracle VM, k3s, Argo CD, Heroku, scripts de infraestructura |
| `gh-pages` | Rama gh-pages, reportes de tests, index.html |
| `release` | release-please-config.json, .release-please-manifest.json, CHANGELOG |
| `tests` | tests/ (si el cambio es solo en tests, sin tocar código de app) |

**Prohibido:**
- Sin scope: `fix: update` ❌
- Emojis en el header: `✨ feat(auctions): add...` ❌
- Mayúsculas: `Fix(Auctions): Update` ❌
- Punto al final: `feat(auctions): add feature.` ❌

---

## Calidad de código

### Herramientas configuradas en `pyproject.toml`

| Herramienta | Propósito | Comando |
|------------|-----------|---------|
| `ruff` | Linter Python (reemplaza flake8, isort) | `ruff check .` |
| `black` | Formatter Python | `black .` |
| `mypy` | Type checking | `mypy auctions/` |
| `bandit` | Seguridad estática | `bandit -r auctions/ -ll` |
| `safety` | Vulnerabilidades en deps | `safety check -r requirements.txt` |

### Pre-commit

```bash
pip install pre-commit
pre-commit install
```

Los hooks en `.pre-commit-config.yaml` corren automáticamente en cada commit: ruff, black, bandit, trailing whitespace, merge conflicts.

### Línea de código

- Longitud máxima: **88 caracteres** (Black default)
- Target Python: **3.10**
- Sin `print()` en código de producción
- Sin comentarios que expliquen QUÉ hace el código — solo el PORQUÉ cuando no es obvio

---

## Tests

### Stack

```
tests/
├── conftest.py          # Factories (factory-boy) + fixtures pytest
├── unit/
│   ├── test_models.py   # Listing.place_bid(), Watchlist, Bid, Comment
│   └── test_forms.py    # Validación de ListingForm, BidForm, CommentForm
├── integration/
│   ├── test_views_auth.py
│   ├── test_views_auction.py
│   ├── test_views_watchlist.py
│   └── test_views_categories.py
└── e2e/                 # Playwright — flujos completos en browser
```

### Correr tests

```bash
# Todos los tests con cobertura
pytest

# Solo unit tests (sin E2E)
pytest tests/unit/ tests/integration/

# Con paralelismo
pytest -n auto

# Reporte de cobertura en terminal
pytest --cov=auctions --cov-report=term-missing --no-header -q
```

### Requisitos
- Cobertura mínima: **70%** (`--cov-fail-under=70` en pyproject.toml)
- Todo código nuevo en `auctions/` debe tener test correspondiente
- Usar factories (`UserFactory`, `ListingFactory`, etc.) — no crear objetos directamente

---

## Docker

### Desarrollo local

```bash
# Levantar Django + PostgreSQL
docker compose up --build

# Correr migrations
docker compose exec web python manage.py migrate

# Acceder en: http://localhost:8000
```

### Producción (simulado localmente)

```bash
docker compose -f docker-compose.prod.yml up --build
```

### Variables de entorno requeridas

Copiar `.env.example` a `.env`:

```bash
cp .env.example .env
```

| Variable | Descripción | Default dev |
|---------|-------------|-------------|
| `SECRET_KEY` | Clave secreta Django | (requerida) |
| `DEBUG` | Modo debug | `False` |
| `DATABASE_URL` | URL PostgreSQL | SQLite si no está |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos | `127.0.0.1,localhost` |

---

## GitHub Actions — Resumen de workflows

| Workflow | Trigger | Hace qué |
|---------|---------|---------|
| `pr-validate` | PR → develop o main | Lint + tests + security scan + publica reporte en gh-pages |
| `cd-develop` | Push a develop | Tests + build Docker + push GHCR + actualiza reporte develop |
| `cd-production` | Push a main | Tests + build Docker + deploy Heroku + actualiza reporte main |
| `release-please` | Push a main | Crea PR de release con CHANGELOG automático |
| `devcontainer` | Push (paths: `.devcontainer/**`) | Build + push imagen a GHCR |
| `branch-cleanup` | PR closed | Elimina rama + elimina reporte de gh-pages |
| `_reusable-lint` | `workflow_call` | ruff + black + mypy + bandit |
| `_reusable-tests` | `workflow_call` | pytest + cobertura + pytest-html |

**Secrets de GitHub requeridos:**

| Secret | Descripción |
|--------|-------------|
| `HEROKU_API_KEY` | API Key de Heroku (Settings → Account) |
| `HEROKU_APP_NAME` | Nombre de la app en Heroku |
| `HEROKU_EMAIL` | Email de tu cuenta Heroku |

---

## Reportes de tests (GitHub Pages)

URL: `https://sandovaldavid.github.io/auctions/`

Estructura en rama `gh-pages`:
```
reports/
├── main/          # Último reporte de producción
├── develop/       # Último reporte de staging
└── pr/
    ├── 30/        # Reporte del PR #30 (se elimina al cerrar PR)
    └── 31/
```

---

## Heroku — Notas de migración a Docker stack

Si el proyecto estaba usando buildpacks, cambiar a Docker stack:

```bash
heroku stack:set container -a <nombre-app>
```

El archivo `heroku.yml` en la raíz define el build. Desconectar el auto-deploy nativo de Heroku (Dashboard → Deploy → Disconnect) para que solo GitHub Actions controle los deploys.
