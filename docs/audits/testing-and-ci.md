# Auditoría de Tests y CI/CD — Sitio de Subastas

> **Fecha:** 2026-07-02 · **Commit:** `784f51a` · **Rama:** `develop`
> **Método:** inventario de la suite, ejecución de `pytest --cov`, revisión de `pyproject.toml` y los workflows de `.github/`. Ver metodología en [README.md](README.md).

## Resumen

Se identificaron **8 hallazgos**. La suite activa está sana (85 tests pasan, 81 % de cobertura sobre `auctions/`), pero la configuración de cobertura **excluye** los módulos más frágiles (analítica, admin), existe una suite legacy duplicada que no se ejecuta, y faltan tests para las clases de bug más peligrosas: concurrencia de pujas y cabeceras de seguridad. En CI, `safety` no bloquea y no hay comprobaciones de accesibilidad, rendimiento ni escaneo de contenedores.

| Severidad | Cantidad |
|-----------|----------|
| Crítico   | 0 |
| Alto      | 3 |
| Medio     | 3 |
| Bajo      | 2 |

## Hallazgos

| ID | Severidad | Ubicación | Resumen | Esfuerzo | PR sugerido |
|----|-----------|-----------|---------|----------|-------------|
| TEST-001 | Alto | `tests/unit/test_models.py` | Sin test de concurrencia para `place_bid` (la condición de carrera SEC-001 no está cubierta) | M | `chore/deps-and-tests` |
| TEST-002 | Alto | `pyproject.toml` `[tool.coverage.run] omit` | Cobertura omite `admin_views.py`, `analytics.py`, `data_utils.py`: los módulos con los bugs críticos CODE-001/002 no se testean | M | `chore/deps-and-tests` |
| TEST-003 | Alto | `auctions/tests/` | Suite legacy duplicada fuera de `testpaths=["tests"]`: no se ejecuta, confunde y arrastra avisos de bandit | S | `chore/deps-and-tests` |
| TEST-004 | Medio | `tests/e2e/` | Directorio e2e vacío (solo `__init__.py`); `fixtures/axe.min.js` sin trackear y propiedad de root; cero tests Playwright pese a estar provisionado en CI | M | `chore/deps-and-tests` |
| TEST-005 | Medio | `tests/` (global) | Sin tests de cabeceras de seguridad (HSTS, X-Frame-Options, cookies seguras) | S | `chore/deps-and-tests` |
| TEST-006 | Medio | `tests/unit/test_theme_colors.py` | Los tests de contraste no cubren los 11 pares que fallan (badges/botones Bootstrap); solo validan `variables.css` | S | `fix/a11y-css-variables` |
| TEST-007 | Bajo | `tests/integration/` | Sin `assertNumQueries` para detectar regresiones N+1 (PERF-004/008) | S | `chore/deps-and-tests` |
| TEST-008 | Bajo | `.github/workflows/pr-validate.yml` | `safety` corre con `continue-on-error: true` (no bloquea); sin a11y/perf/escaneo de contenedor/CodeQL en CI | M | `chore/deps-and-tests` |

## Detalle de hallazgos Alto

### TEST-001 — Sin cobertura de concurrencia

- **Ubicación:** `tests/unit/test_models.py` (cubre `place_bid` en el camino feliz, pero no la carrera).
- **Descripción:** el bug de mayor severidad de la auditoría (SEC-001, condición de carrera con dinero) no tiene test que lo reproduzca ni que verifique la corrección con transacción/`select_for_update`.
- **Recomendación:** añadir un test que simule pujas concurrentes (p. ej. con `TransactionTestCase` y hilos, o verificando que dos `place_bid` con el mismo `current_bid` de partida no ambos tengan éxito). Debe acompañar al fix de SEC-001.

### TEST-002 — Cobertura ciega en los módulos frágiles

- **Ubicación:** `pyproject.toml`, sección `[tool.coverage.run] omit` (excluye `admin_views.py`, `analytics.py`, `data_utils.py`, `admin_config.py`, `management/commands/generate_reports.py`).
- **Descripción:** el 81 % de cobertura reportado se calcula **excluyendo** justamente los módulos donde viven los bugs críticos CODE-001 (analytics rota en Postgres) y CODE-002 (imports ausentes). Esos módulos suman ~37 KB de código sin ninguna prueba.
- **Recomendación:** retirar `analytics.py`/`data_utils.py`/`admin_views.py` de la lista `omit` y añadir tests que ejerciten sus rutas contra una BD PostgreSQL (el workflow `_reusable-tests.yml` ya levanta un servicio Postgres 16). Esto habría detectado CODE-001 automáticamente.

### TEST-003 — Suite legacy duplicada

- **Ubicación:** `auctions/tests/` (`factories.py`, `test_forms.py`, `test_integration.py`, `test_models.py`, `test_templates.py`, `test_views.py`).
- **Descripción:** `testpaths = ["tests"]` en `pyproject.toml` solo recoge la suite de nivel superior. La suite dentro de `auctions/tests/` está trackeada en git pero **no se ejecuta** en local ni en CI, y es la fuente de los 13 avisos Low de bandit (contraseñas de prueba hardcodeadas). Es un layout Django antiguo abandonado.
- **Recomendación:** decidir cuál es la suite canónica (`tests/` según `CLAUDE.md`) y eliminar `auctions/tests/`, o migrar lo que aún aporte. Documentar la convención en la guía de tests.

## Estado de la suite (contexto)

- **85 tests** pasan; **81 %** de cobertura sobre `auctions/` (umbral configurado: **70 %**).
- Factories con `factory-boy` en `tests/conftest.py`: `UserFactory`, `ListingFactory`, `BidFactory`, `CommentFactory`, `WatchlistFactory`.
- Módulos con baja cobertura visible: `error_views.py` (32 %), `middleware.py` (49 %), `templatetags/auctions_filters.py` (59 %).

## Estado de CI/CD (contexto)

- `pr-validate.yml`: lint + tests + `bandit -r auctions/ -ll` + `safety check` (no bloqueante) + publicación de reporte en gh-pages.
- `_reusable-tests.yml`: levanta Postgres 16, instala `requirements-dev.txt`, `playwright install chromium`, migra y corre pytest.
- `cd-develop.yml`: **deshabilitado** (`workflow_dispatch`), pendiente del stack Oracle VM/k3s.
- `cd-production.yml`: build + push GHCR + deploy Heroku (container stack).
- **Sin** comprobaciones de accesibilidad (axe/pa11y/Lighthouse), rendimiento, escaneo de imágenes (Trivy/Grype) ni SAST más allá de bandit.

## Evidencia

`pytest --cov=auctions --cov-report=term-missing -q` (resumen):

```text
auctions/error_views.py                        63     43    32%
auctions/middleware.py                         35     18    49%
auctions/models.py                             52      1    98%
auctions/forms.py                              59      2    97%
auctions/views.py                             146      5    97%
auctions/templatetags/auctions_filters.py      17      7    59%
-------------------------------------------------------------------------
TOTAL                                         417     78    81%
85 passed, 35 warnings in 23.00s
```

Nota: `admin_views.py`, `analytics.py` y `data_utils.py` no aparecen en el informe porque están en la lista `omit` (TEST-002).

## Referencias

- TEST-001 acompaña a la corrección de la condición de carrera en [security.md](security.md) (SEC-001).
- TEST-002 cubre los módulos de los bugs de [code-quality.md](code-quality.md) (CODE-001, CODE-002).
- TEST-006 amplía los tests de contraste de [accessibility.md](accessibility.md) (A11Y-002/003/004).
