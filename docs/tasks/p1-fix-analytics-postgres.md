# Tarea: `fix/analytics-postgres` — Analítica funcional en PostgreSQL

> **Prioridad:** 1 (Crítico) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** En progreso
> **Detalle de hallazgos:** [../audits/code-quality.md](../audits/code-quality.md)

## Objetivo

La cadena de analítica está rota en producción: importa el modelo `User` equivocado y usa SQL exclusivo de SQLite (falla en la BD PostgreSQL de producción), y varios módulos importan `numpy`/`pandas` que no están en `requirements.txt` (fallo de importación en la imagen de producción). Es prioridad 1 porque son roturas garantizadas fuera de dev, hoy enmascaradas por un `try/except` amplio.

## Rama

```bash
git checkout develop && git pull
git checkout -b fix/analytics-postgres
```

## Hallazgos a resolver

- [x] **CODE-001** — `analytics.py` importa `django.contrib.auth.models.User` + `.extra()` solo-SQLite (`auctions/analytics.py:19,84,93,102,283,296`)
- [x] **CODE-002** — `numpy`/`pandas` ausentes de `requirements.txt` (`auctions/data_utils.py:8`, `management/commands/generate_reports.py:86`)

## Instrucciones / recomendaciones

1. **CODE-001 (User swapped).** Cambiar `from django.contrib.auth.models import User` por `get_user_model()`:

   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   ```

2. **CODE-001 (SQL agnóstico).** Sustituir `.extra(select={...})` con `date(...)`/`strftime(...)` por funciones de BD portables:

   ```python
   from django.db.models.functions import TruncDate, TruncMonth
   # ej.: .annotate(day=TruncDate("created")).values("day").annotate(n=Count("id"))
   ```

   `.extra()` está deprecado; `Trunc*` funciona igual en SQLite y PostgreSQL.

3. **CODE-002 (dependencias).** Decidir si la analítica es funcionalidad de producción:
   - **Si lo es:** mover `numpy`, `pandas`, `scikit-learn`, `plotly` de `requirements-dev.txt` a `requirements.txt`.
   - **Si no:** proteger los imports (`try/except ImportError` con degradación, como ya hace `analytics.py:8-17`) y documentar que el panel BI requiere las deps de dev. Alinear con la decisión de arquitectura de [CLAUDE.md](../../CLAUDE.md) (analítica como fase futura).

4. Quitar el `except Exception` amplio de `admin_dashboard` (`auctions/admin_views.py:58`) que hoy oculta estos fallos, o al menos loguearlos (ver `chore/settings-hardening`, SEC-012).

## Tests requeridos

- Retirar `analytics.py`/`data_utils.py`/`admin_views.py` de la lista `omit` de cobertura (**TEST-002**) y añadir tests que ejerciten `get_time_series_data`/`get_market_trends` **contra PostgreSQL** (el workflow `_reusable-tests.yml` ya levanta Postgres 16). Estos tests habrían detectado CODE-001.

## Verificación

```bash
# Contra PostgreSQL (no SQLite) para reproducir el entorno de prod
DATABASE_URL=postgres://... pytest tests/ -q -k analytics
ruff check . && mypy auctions/
```

## Commits sugeridos

```
fix(auctions): use get_user_model in analytics
fix(auctions): replace SQLite-only extra() with Trunc functions
build(deps): move pandas and numpy to runtime requirements
```

## Criterios de done

- [x] Analítica funciona en PostgreSQL sin excepciones (verificado contra PostgreSQL 16 real)
- [x] Imports de `numpy`/`pandas` resueltos en la imagen de producción (movidos a `requirements.txt`)
- [x] Tests de analítica en la suite (fuera del `omit`); cobertura ≥ 70% (86.04%)
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
