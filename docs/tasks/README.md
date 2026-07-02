# Tablero de tareas — Sitio de Subastas

Backlog accionable derivado de la [auditoría del proyecto](../audits/README.md) (70 hallazgos). Cada fila es una rama de trabajo = un PR. Trabaja de arriba hacia abajo por prioridad.

## Cómo trabajar una tarea

1. Elige la ficha con la prioridad más alta que esté `Pendiente`.
2. Crea la rama desde `develop` (comandos en cada ficha):
   ```bash
   git checkout develop && git pull
   git checkout -b <rama-de-la-ficha>
   ```
3. Resuelve los hallazgos marcando el checklist de la ficha; sigue sus instrucciones y añade los tests indicados.
4. Pasa los **quality gates** antes de abrir el PR:
   ```bash
   ruff check .
   black --check .
   mypy auctions/
   bandit -r auctions/ -ll
   pytest            # cobertura mínima 70%
   ```
5. Commits con [Conventional Commits](../../CLAUDE.md#commits--conventional-commits-obligatorio) (scope obligatorio).
6. Abre PR a `develop` y mergea con **"Squash and merge"** (ver [reglas de ramas](../../CLAUDE.md#ramas)).
7. Actualiza el **Estado** de la fila en este tablero.

Convenciones completas: [CLAUDE.md](../../CLAUDE.md) · Guía operativa para agentes: [AGENTS.md](../../AGENTS.md).

## Leyenda de estado

`Pendiente` · `En progreso` · `Hecho`

## Prioridad 1 — Crítico

| Rama | Área | Hallazgos | Esfuerzo | Estado | Ficha |
|------|------|-----------|:--------:|--------|-------|
| `fix/security-critical` | Seguridad | SEC-001,002,003,005,006,007,008,011 · CODE-004 | M | Pendiente | [p1-fix-security-critical.md](p1-fix-security-critical.md) |
| `fix/analytics-postgres` | Correctitud | CODE-001, CODE-002 | L | Pendiente | [p1-fix-analytics-postgres.md](p1-fix-analytics-postgres.md) |

## Prioridad 2 — Alto

| Rama | Área | Hallazgos | Esfuerzo | Estado | Ficha |
|------|------|-----------|:--------:|--------|-------|
| `fix/admin-routing` | Seguridad | SEC-004 | S | Pendiente | [p2-fix-admin-routing.md](p2-fix-admin-routing.md) |
| `fix/xss-templates` | Seguridad | SEC-009, SEC-013, SEC-014 | M | Pendiente | [p2-fix-xss-templates.md](p2-fix-xss-templates.md) |
| `fix/a11y-css-variables` | Accesibilidad | A11Y-001..007, A11Y-010, TEST-006 | L | Pendiente | [p2-fix-a11y-css-variables.md](p2-fix-a11y-css-variables.md) |

## Prioridad 3 — Medio

| Rama | Área | Hallazgos | Esfuerzo | Estado | Ficha |
|------|------|-----------|:--------:|--------|-------|
| `chore/settings-hardening` | Seguridad | SEC-010,012,015,016,017 | M | Pendiente | [p3-chore-settings-hardening.md](p3-chore-settings-hardening.md) |
| `refactor/model-constraints` | Modelos | CODE-003,005,006 · PERF-006 | M | Pendiente | [p3-refactor-model-constraints.md](p3-refactor-model-constraints.md) |
| `refactor/query-performance` | Rendimiento | PERF-001..005,007,008 | M | Pendiente | [p3-refactor-query-performance.md](p3-refactor-query-performance.md) |

## Prioridad 4 — Bajo

| Rama | Área | Hallazgos | Esfuerzo | Estado | Ficha |
|------|------|-----------|:--------:|--------|-------|
| `chore/frontend-consistency` | UI/UX | UX-001..012 · A11Y-009,011..014 · SEC-018 | M | Pendiente | [p4-chore-frontend-consistency.md](p4-chore-frontend-consistency.md) |
| `chore/deps-and-tests` | Tooling/Tests | CODE-007..010 · TEST-001..005,007,008 | M | Pendiente | [p4-chore-deps-and-tests.md](p4-chore-deps-and-tests.md) |

## Orden recomendado

Prioridad 1 primero (seguridad crítica y rotura en producción). Dentro de P2, `fix/admin-routing` es el más rápido (un solo hallazgo). `refactor/model-constraints` conviene antes que `refactor/query-performance` porque los índices de PERF-006 viven en la misma migración de constraints. `chore/deps-and-tests` puede ir en paralelo en cualquier momento (no toca código de la app salvo tests).
