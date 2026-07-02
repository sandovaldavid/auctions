# AGENTS.md — Guía operativa para agentes

Punto de entrada para agentes de IA que trabajan en este repositorio. Define **cómo trabajar** aquí; las convenciones detalladas (tablas de tipos/scopes de commit, estrategia de merge, workflows) están en [CLAUDE.md](CLAUDE.md) — este archivo remite a ellas, no las duplica.

## Snapshot del proyecto

Monolito Django 5.1 (sitio de subastas, SSR con Bootstrap 5.3). Una sola app `auctions/`; configuración en `commerce/`. BD SQLite en dev, PostgreSQL 16 en prod. Despliegue en Heroku (container stack); staging futuro en Oracle VM. Ver el stack completo y la arquitectura objetivo en [CLAUDE.md](CLAUDE.md).

**Decisión de arquitectura:** se mantiene Django monolito. No migrar a otro framework ni a microservicios sin evidencia de necesidad de escala.

## Setup rápido

```bash
# Dependencias
pip install -r requirements.txt -r requirements-dev.txt

# App + PostgreSQL con Docker
docker compose up --build          # http://localhost:8000
docker compose exec web python manage.py migrate

# Tests
pytest                             # con cobertura (mínimo 70%)
```

Variables de entorno: copiar `.env.example` a `.env`. Guía Docker: [docs/Docker.md](docs/Docker.md).

## Reglas de trabajo

1. **Conventional Commits obligatorio**, con **scope** siempre presente: `type(scope): descripción imperativa en minúsculas`. Tipos y scopes válidos: tablas en [CLAUDE.md](CLAUDE.md#commits--conventional-commits-obligatorio). Sin emojis, sin mayúsculas iniciales, sin punto final.
2. **Ramas:** trabaja en `feature/*`, `fix/*`, `chore/*` o `refactor/*` partiendo de `develop`. **Nunca** commitees directo a `main` ni a `develop`. Merge a `develop` con **"Squash and merge"**. Reglas completas: [CLAUDE.md](CLAUDE.md#ramas).
3. **Quality gates antes de abrir un PR** (todos deben pasar):
   ```bash
   ruff check .
   black --check .
   mypy auctions/
   bandit -r auctions/ -ll
   pytest                 # cobertura ≥ 70%
   ```
   El workflow `pr-validate` corre estos mismos checks; no dependas de él, pásalos localmente.
4. **Tests:** todo código nuevo en `auctions/` requiere test. Usa las factories de `tests/conftest.py` (`UserFactory`, `ListingFactory`, …); no crees objetos a mano. La suite canónica es `tests/` (no `auctions/tests/`, que es legacy).
5. **Estilo de código:** líneas ≤ 88 (Black); sin `print()` en código de producción; los comentarios explican el PORQUÉ, no el QUÉ.

## Mapa del código

| Ruta | Contenido |
|------|-----------|
| `auctions/models.py` | `User`, `Listing`, `Bid`, `Comment`, `Watchlist` (lógica de pujas en `Listing.place_bid`) |
| `auctions/views.py` | 12 vistas SSR públicas |
| `auctions/forms.py` | `ListingForm`, `BidForm`, `CommentForm` |
| `auctions/admin_views.py` | Panel admin/BI (solo superusuario) |
| `auctions/analytics.py`, `data_utils.py` | Reportes y series (dependen de pandas/plotly) |
| `auctions/middleware.py`, `error_views.py` | Middleware y páginas de error |
| `auctions/templates/auctions/` | Plantillas (base pública `layout.html`; admin en `admin/`) |
| `auctions/static/css/` | `variables.css` es la fuente de verdad de color |
| `commerce/` | `settings.py`, `urls.py`, `wsgi.py`, `asgi.py` |
| `tests/` | Suite pytest (unit/integration/e2e) |

## Backlog y hallazgos conocidos

Antes de proponer trabajo, consulta:

- **[docs/tasks/](docs/tasks/README.md)** — tablero de tareas priorizadas; una ficha por rama con checklist, instrucciones, verificación y mensajes de commit sugeridos. Empieza por la prioridad más alta que esté `Pendiente`.
- **[docs/audits/](docs/audits/README.md)** — auditoría completa (70 hallazgos con `archivo:línea`, severidad y remediación).

Si trabajas un hallazgo, usa la rama indicada en su ficha y marca su checkbox al terminar.

## Qué NO hacer

- No migrar de Django a otro stack ni introducir microservicios.
- No reescribir ni renombrar migraciones históricas de `auctions/migrations/`.
- No exponer secretos: `SECRET_KEY` y credenciales vienen de variables de entorno, nunca hardcodeadas.
- No commitear directo a `main`/`develop` ni saltarte los quality gates.
- No romper la convención de Conventional Commits (scope obligatorio).
- No añadir dependencias de runtime a `requirements-dev.txt` (los módulos de prod solo pueden importar lo que está en `requirements.txt`).
