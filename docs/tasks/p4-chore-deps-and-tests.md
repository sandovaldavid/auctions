# Tarea: `chore/deps-and-tests` — Dependencias, tooling y cobertura de tests

> **Prioridad:** 4 (Bajo) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/code-quality.md](../audits/code-quality.md) · [../audits/testing-and-ci.md](../audits/testing-and-ci.md)

## Objetivo

Sanear el tooling y cerrar los huecos de la suite de tests y del CI: fijar dependencias, retirar código muerto y deps sin uso, eliminar la suite legacy duplicada, ampliar la cobertura a los módulos frágiles y reforzar el pipeline. No toca código de la app salvo tests, así que puede ir en paralelo con otras ramas.

## Rama

```bash
git checkout develop && git pull
git checkout -b chore/deps-and-tests
```

## Hallazgos a resolver

- [ ] **CODE-007** — Dependencias con `>=` sin lockfile (`requirements.txt`)
- [ ] **CODE-008** — `Custom404Middleware` código muerto (`auctions/middleware.py:64-86`, guard sobre setting inexistente)
- [ ] **CODE-009** — `django-import-export` instalado sin uso (`commerce/settings.py:30`)
- [ ] **CODE-010** — `mypy`: asignación incompatible en config de BD (`commerce/settings.py:84`)
- [ ] **TEST-001** — Sin test de concurrencia para `place_bid`
- [ ] **TEST-002** — Cobertura omite `admin_views.py`/`analytics.py`/`data_utils.py`
- [ ] **TEST-003** — Suite legacy duplicada `auctions/tests/` fuera de `testpaths`
- [ ] **TEST-004** — `tests/e2e/` vacío; `fixtures/axe.min.js` sin trackear
- [ ] **TEST-005** — Sin tests de cabeceras de seguridad
- [ ] **TEST-007** — Sin `assertNumQueries` para regresiones N+1
- [ ] **TEST-008** — `safety` no bloqueante; sin a11y/perf/escaneo de contenedor/CodeQL en CI

## Instrucciones / recomendaciones

1. **CODE-007.** Fijar versiones (`==`) o adoptar un lockfile (`pip-tools`/`uv`). Como mínimo, poner topes superiores.
2. **CODE-008.** Eliminar `Custom404Middleware` (o el guard muerto) y quitarlo de `MIDDLEWARE` en `settings.py:45`.
3. **CODE-009.** Retirar `import_export` de `INSTALLED_APPS` si no se usa, o implementarlo en `admin.py`.
4. **CODE-010.** Corregir la anotación de tipos / uso de `dj_database_url` para que `mypy` pase limpio.
5. **TEST-003.** Eliminar `auctions/tests/` (suite legacy no recolectada) tras confirmar que `tests/` cubre lo mismo. Esto también elimina los 13 avisos Low de bandit.
6. **TEST-002.** Retirar `admin_views.py`/`analytics.py`/`data_utils.py` del `omit` de cobertura y añadir tests (coordinar con `fix/analytics-postgres`).
7. **TEST-001/005/007.** Añadir los tests de concurrencia, cabeceras de seguridad y `assertNumQueries` (algunos se entregan junto a sus ramas de fix; aquí se consolida lo que quede).
8. **TEST-004.** Escribir al menos un flujo e2e con Playwright + `axe-core` (el fixture ya está en `tests/e2e/fixtures/`), y trackearlo correctamente (hoy es propiedad de root y sin trackear).
9. **TEST-008.** Hacer `safety` bloqueante en `pr-validate.yml` y valorar añadir escaneo de imagen (Trivy) y/o CodeQL.

## Verificación

```bash
pytest -q                      # incluye los módulos antes omitidos
ruff check . && black --check . && mypy auctions/   # mypy limpio (CODE-010)
bandit -r auctions/ -ll        # sin avisos de la suite legacy eliminada
```

## Commits sugeridos

```
build(deps): pin dependency versions
chore(auctions): remove dead Custom404Middleware
chore(commerce): drop unused import_export app
chore(commerce): fix database config type for mypy
test(tests): remove legacy duplicate test suite
test(tests): cover admin, analytics and security headers
ci(ci): make safety blocking and add container scan
```

## Criterios de done

- [ ] Dependencias fijadas; código muerto y deps sin uso retirados; `mypy` limpio
- [ ] Suite legacy eliminada; cobertura amplía a los módulos frágiles
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
