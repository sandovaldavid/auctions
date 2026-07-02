# Auditoría de Calidad de Código — Sitio de Subastas

> **Fecha:** 2026-07-02 · **Commit:** `784f51a` · **Rama:** `develop`
> **Método:** análisis estático (lectura de código + `ruff` + `black` + `mypy`), sin servidor en vivo. Ver metodología en [README.md](README.md).

## Resumen

Se identificaron **10 hallazgos** de calidad de código. `ruff` y `black` salen limpios y `mypy` reporta un único error real; los problemas graves son de correctitud en tiempo de ejecución que las herramientas estáticas no detectan: el módulo de analítica importa el modelo `User` equivocado y usa SQL exclusivo de SQLite (rompe en la BD PostgreSQL de producción), y varios módulos importan `numpy`/`pandas` que no están en `requirements.txt` (fallo de importación en la imagen de producción).

| Severidad | Cantidad |
|-----------|----------|
| Crítico   | 2 |
| Alto      | 3 |
| Medio     | 3 |
| Bajo      | 2 |

## Hallazgos

| ID | Severidad | Ubicación | Resumen | Esfuerzo | PR sugerido |
|----|-----------|-----------|---------|----------|-------------|
| CODE-001 | Crítico | `auctions/analytics.py:19,84,93,102,283,296` | Importa `django.contrib.auth.models.User` (no el swapped) y usa `.extra()` con SQL solo-SQLite (`date()`, `strftime()`): rompe en PostgreSQL | L | `fix/analytics-postgres` |
| CODE-002 | Crítico | `auctions/data_utils.py:8`, `management/commands/generate_reports.py:86` | Importan `numpy`/`pandas`, ausentes de `requirements.txt` (solo en `requirements-dev.txt`): `ImportError` en imagen de producción | M | `fix/analytics-postgres` |
| CODE-003 | Alto | `auctions/models.py:23-29` | `Listing.winner` con `on_delete=CASCADE`: borrar un usuario ganador elimina en cascada el listing | S | `refactor/model-constraints` |
| CODE-004 | Alto | `auctions/views.py:147,169-170` | `.get()` desnudos (`Listing`, `Watchlist`) sin `get_object_or_404`: `DoesNotExist`→500 con IDs inválidos | S | `fix/security-critical` |
| CODE-005 | Alto | `auctions/models.py` (todos los modelos) | Sin `class Meta`: sin índices, sin `constraints`, sin `ordering`, sin `unique_together` en `Watchlist(user, listing)` | M | `refactor/model-constraints` |
| CODE-006 | Medio | `auctions/forms.py:30-36` | Unicidad de `title` solo en el form (`filter(...).exists()`): TOCTOU y sustituye a un `unique=True` de BD ausente | S | `refactor/model-constraints` |
| CODE-007 | Medio | `requirements.txt` (global) | Todas las dependencias con `>=` y sin lockfile: builds no reproducibles | S | `chore/deps-and-tests` |
| CODE-008 | Medio | `auctions/middleware.py:64-86`, `commerce/settings.py:45` | `Custom404Middleware` guarda sobre `settings.USE_CUSTOM_ERROR_HANDLERS`, que no existe: código muerto | S | `chore/deps-and-tests` |
| CODE-009 | Bajo | `commerce/settings.py:30`, `auctions/admin.py` | `django-import-export` instalado pero sin uso (los `ModelAdmin` son planos) | S | `chore/deps-and-tests` |
| CODE-010 | Bajo | `commerce/settings.py:84` | `mypy`: asignación incompatible `DBConfig` a `dict[str, str]` en la config de base de datos | S | `chore/deps-and-tests` |

## Detalle de hallazgos Crítico y Alto

### CODE-001 — Analítica rota en PostgreSQL

- **Ubicación:** `auctions/analytics.py:19` (import) y `:84,93,102,283,296` (`.extra()`).
- **Descripción:** dos problemas combinados. (1) `from django.contrib.auth.models import User` importa el modelo de auth estándar en vez del swapped `auctions.User` (`AUTH_USER_MODEL`, `settings.py:90`); las anotaciones `User.objects.annotate(Count("bids"|"listings"|"comments"))` (`analytics.py:137-152`) apuntan a relaciones que no existen en ese modelo → `FieldError`/`OperationalError`. (2) `.extra(select={...})` usa `date(created)` y `strftime(...)`, funciones **exclusivas de SQLite** que no existen en PostgreSQL; además `.extra()` está deprecado.
- **Escenario de fallo:** en producción (PostgreSQL, `settings.py:82-88`) `get_time_series_data`/`get_market_trends` lanzan excepción. El dashboard "sobrevive" solo porque `admin_dashboard` envuelve todo en `try/except` (`admin_views.py:58`), lo que enmascara el fallo y deja las gráficas vacías.
- **Recomendación:** importar `from django.contrib.auth import get_user_model` y sustituir `.extra()` por `TruncDate`/`TruncMonth` (`django.db.models.functions`), que son agnósticos de motor. Cubrir con tests (este módulo está en la lista `omit` de coverage — ver [testing-and-ci.md](testing-and-ci.md), TEST-002).

### CODE-002 — `numpy`/`pandas` ausentes en producción

- **Ubicación:** `auctions/data_utils.py:8` (`import numpy` incondicional), `management/commands/generate_reports.py:86` (`import pandas`).
- **Descripción:** el stack de datos/ML (`pandas`, `numpy`, `scikit-learn`, `plotly`) está en `requirements-dev.txt`, **no** en `requirements.txt`. `analytics.py:8-17` protege sus imports con `try/except` y degrada, pero `data_utils.py` importa `numpy` sin guardia y el comando de gestión importa `pandas`. La imagen de producción se construye solo desde `requirements.txt`.
- **Escenario de fallo:** en la imagen de producción, importar `data_utils` o ejecutar `manage.py generate_reports` produce `ModuleNotFoundError: No module named 'numpy'`/`'pandas'`.
- **Recomendación:** decidir si la analítica es funcionalidad de producción. Si lo es, mover esas dependencias a `requirements.txt`; si no, aislar el módulo de comandos y proteger los imports. Alinear con la decisión de arquitectura de `CLAUDE.md` (analítica como fase futura).

### CODE-003 — `Listing.winner` con borrado en cascada

- **Ubicación:** `auctions/models.py:23-29`.
- **Descripción:** `winner = models.ForeignKey(User, on_delete=models.CASCADE, ...)`. Borrar al usuario que ganó una subasta elimina en cascada el propio `Listing` (registro histórico de la venta).
- **Escenario de fallo:** se borra una cuenta que ganó 5 subastas → desaparecen los 5 listings y su historial de pujas.
- **Recomendación:** cambiar a `on_delete=models.SET_NULL` (el campo ya es `null=True, blank=True`). Requiere una migración.

### CODE-004 — `.get()` desnudos producen 500

- **Ubicación:** `auctions/views.py:147` (`Listing.objects.get(pk=...)` en `watchlist`), `:169-170` (`Listing`/`Watchlist` en `watchlist_remove`).
- **Descripción:** mientras otras vistas usan `get_object_or_404` (`views.py:102,114,178,224`), estas dos usan `.get()` directo, que lanza `DoesNotExist` (HTTP 500) ante un ID inexistente en vez de un 404 limpio.
- **Escenario de fallo:** `POST /watchlist/999999` con un ID inexistente devuelve 500 en lugar de 404.
- **Recomendación:** sustituir por `get_object_or_404`. Se solapa con SEC-006 (esas mismas vistas también deben pasar a POST).

### CODE-005 — Modelos sin `Meta`, índices ni constraints

- **Ubicación:** `auctions/models.py` (los cinco modelos).
- **Descripción:** ningún modelo declara `class Meta`. Consecuencias: (1) sin índices de BD en columnas de filtro/orden calientes (`Listing.active`, `category`, `created`; ver [performance.md](performance.md), PERF-006); (2) sin `CheckConstraint` para `starting_bid >= 0`, `amount > 0` o `current_bid >= starting_bid` (toda la validación es a nivel de app); (3) sin `UniqueConstraint`/`unique_together` en `Watchlist(user, listing)`, por lo que son posibles filas duplicadas (solo evitadas de casualidad por `get_or_create` en `views.py:148`); (4) sin `ordering` por defecto.
- **Escenario de fallo:** una segunda ruta que cree `Watchlist` sin `get_or_create` genera duplicados; una puja negativa insertada por el ORM/admin no es rechazada por la BD.
- **Recomendación:** añadir `Meta` con `indexes`, `constraints` (`CheckConstraint`) y `UniqueConstraint` en `Watchlist`. Agrupar con PERF-006 en `refactor/model-constraints`.

## Evidencia

`ruff check . --statistics` y `black --check .` — limpios:

```text
=== ruff check . --statistics ===
(sin hallazgos)

=== black --check . ===
All done! ✨ 🍰 ✨
45 files would be left unchanged.
```

`mypy auctions/` — un único error (CODE-010):

```text
commerce/settings.py:84: error: Incompatible types in assignment
  (expression has type "DBConfig", target has type "dict[str, str]")  [assignment]
Found 1 error in 1 file (checked 26 source files)
```

## Referencias

- CODE-001 y CODE-002 comparten el PR sugerido `fix/analytics-postgres` porque ambos atañen a la cadena de analítica.
- CODE-005 (índices/constraints) se detalla desde la perspectiva de rendimiento en [performance.md](performance.md) (PERF-006).
- CODE-004 se solapa con las mutaciones-vía-GET de [security.md](security.md) (SEC-006).
