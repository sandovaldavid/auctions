# Auditoría completa del proyecto — Resumen ejecutivo

> **Fecha:** 2026-07-02 · **Commit:** `784f51a` · **Rama:** `develop`

Este directorio contiene la revisión completa del sitio de subastas (Django 5.1) en seis áreas: seguridad, calidad de código, accesibilidad/contraste, rendimiento, UI/UX y tests/CI. Se documentaron **70 hallazgos** con ubicación `archivo:línea`, severidad y recomendación de remediación. Esta auditoría es **solo documentación**; las correcciones se abordarán en PRs separados según el roadmap de abajo.

## Alcance y metodología

Análisis **estático** más herramientas de línea de comandos, sin servidor en vivo ni navegador:

- **Seguridad:** lectura de código + `bandit -r auctions/ commerce/ -ll` + `safety check -r requirements.txt`.
- **Calidad de código:** lectura de código + `ruff check .` + `black --check .` + `mypy auctions/`.
- **Contraste:** cálculo matemático de ratios WCAG 2.1 con las mismas fórmulas de `tests/unit/test_theme_colors.py:12-29` (script `wcag_ratios.py` sobre 23 pares de color).
- **Rendimiento:** identificación de patrones de consulta ORM/plantillas por lectura (sin profiling).
- **Tests/CI:** `pytest --cov` + revisión de `pyproject.toml` y `.github/workflows/`.

**Qué NO se hizo** (candidato a una segunda pasada): auditoría en vivo con `axe-core`/Lighthouse (el fixture `tests/e2e/fixtures/axe.min.js` ya está preparado), profiling real de consultas con `django-debug-toolbar`, y pruebas de penetración dinámicas.

## Taxonomía de severidad

| Severidad | Criterio |
|-----------|----------|
| **Crítico** | Explotable, con pérdida de datos/dinero, o rotura garantizada en producción (XSS, condición de carrera con dinero, `ImportError` en prod, fuga de datos sin auth). |
| **Alto** | Riesgo real de seguridad o fallo funcional visible al usuario (CSRF, contraseñas sin validar, contraste ilegible, N+1 severo). |
| **Medio** | Deuda que degrada calidad, mantenibilidad o rendimiento sin fallo inmediato. |
| **Bajo** | Pulido, consistencia y limpieza. |

Esfuerzo estimado por hallazgo: **S** (pequeño), **M** (medio), **L** (grande).

## Resumen por área

| Área | Documento | Crítico | Alto | Medio | Bajo | Total |
|------|-----------|:---:|:---:|:---:|:---:|:---:|
| Seguridad | [security.md](security.md) | 4 | 6 | 5 | 3 | 18 |
| Calidad de código | [code-quality.md](code-quality.md) | 2 | 3 | 3 | 2 | 10 |
| Accesibilidad y contraste | [accessibility.md](accessibility.md) | 1 | 5 | 6 | 2 | 14 |
| Rendimiento | [performance.md](performance.md) | 0 | 3 | 3 | 2 | 8 |
| UI/UX | [ui-ux.md](ui-ux.md) | 0 | 3 | 5 | 4 | 12 |
| Tests y CI/CD | [testing-and-ci.md](testing-and-ci.md) | 0 | 3 | 3 | 2 | 8 |
| **Total** | | **7** | **23** | **25** | **15** | **70** |

## Top 10 hallazgos por severidad

1. **SEC-001** — Condición de carrera en `place_bid` (pujas concurrentes, `auctions/models.py:40-45`).
2. **SEC-002** — `place_bid` acepta pujas por debajo del precio inicial (`auctions/models.py:40-45`).
3. **CODE-001** — Analítica rota en PostgreSQL: `User` equivocado + SQL solo-SQLite (`auctions/analytics.py`).
4. **CODE-002** — `numpy`/`pandas` ausentes de `requirements.txt`: `ImportError` en producción.
5. **SEC-003** — `register` omite los validadores de contraseña y lanza 500 (`auctions/views.py:47-72`).
6. **SEC-004** — `test_admin_dashboard` filtra conteos sin autenticación (`auctions/admin_views.py:420`).
7. **A11Y-001** — 87 variables CSS rotas en el `components.css` cargado (colores intencionales no se aplican).
8. **SEC-009** — Datos de BD con `|safe` dentro de `<script>` admin: XSS almacenado potencial.
9. **SEC-005/006/007** — Mutaciones de estado vía GET (CSRF) en `close_auction`, `watchlist_remove`, `logout`.
10. **CODE-003** — `Listing.winner` con `on_delete=CASCADE` (borrar usuario elimina el listing).

## Roadmap de remediación

PRs sugeridos, alineados con la estrategia de ramas de `CLAUDE.md` (`fix/*`, `refactor/*`, `chore/*` → `develop`, con **squash merge**), en orden de prioridad. Cada hallazgo indica su PR en la columna correspondiente de su documento.

| Prioridad | Rama sugerida | Hallazgos incluidos |
|:---:|---|---|
| 1 | `fix/security-critical` | SEC-001, SEC-002, SEC-003, SEC-005, SEC-006, SEC-007, SEC-008, SEC-011, CODE-004 |
| 1 | `fix/analytics-postgres` | CODE-001, CODE-002 |
| 2 | `fix/admin-routing` | SEC-004 |
| 2 | `fix/xss-templates` | SEC-009, SEC-013, SEC-014 |
| 2 | `fix/a11y-css-variables` | A11Y-001..007, A11Y-010, TEST-006 |
| 3 | `chore/settings-hardening` | SEC-010, SEC-012, SEC-015, SEC-016, SEC-017 |
| 3 | `refactor/model-constraints` | CODE-003, CODE-005, CODE-006, PERF-006 |
| 3 | `refactor/query-performance` | PERF-001, PERF-002, PERF-003, PERF-004, PERF-005, PERF-007, PERF-008 |
| 4 | `chore/frontend-consistency` | UX-001..012, A11Y-009, A11Y-011..014, SEC-018 |
| 4 | `chore/deps-and-tests` | CODE-007, CODE-008, CODE-009, CODE-010, TEST-001..005, TEST-007, TEST-008 |

## Notas de evidencia

- `bandit`: sin hallazgos en código de aplicación (13 avisos Low, todos en la suite legacy `auctions/tests/`).
- `safety`: 0 vulnerabilidades reportadas, pero 35 ignoradas por dependencias sin fijar (ver CODE-007).
- `ruff`/`black`: limpios. `mypy`: 1 error real (CODE-010).
- `pytest`: 85 tests pasan, 81 % de cobertura (con módulos frágiles excluidos vía `omit`; ver TEST-002).
- Contraste: 23 pares evaluados, 11 fallan WCAG AA (tabla completa en [accessibility.md](accessibility.md)).
