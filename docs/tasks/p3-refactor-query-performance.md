# Tarea: `refactor/query-performance` — Optimización de consultas

> **Prioridad:** 3 (Medio) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/performance.md](../audits/performance.md)

## Objetivo

Eliminar los patrones N+1 y las agregaciones hechas en Python, y corregir los conteos multiplicados del panel admin. Conviene hacerla **después** de `refactor/model-constraints` (los índices de PERF-006 amplifican estas mejoras).

## Rama

```bash
git checkout develop && git pull
git checkout -b refactor/query-performance
```

## Hallazgos a resolver

- [ ] **PERF-001** — `Count()` múltiple sin `distinct=True` → conteos multiplicados (`auctions/admin_views.py:42-47,170-174`)
- [ ] **PERF-002** — `generate_user_activity_report` O(N·5) queries (`auctions/data_utils.py:125-147`)
- [ ] **PERF-003** — `admin_export_data` sin límite/streaming (`auctions/admin_views.py:326-408`)
- [ ] **PERF-004** — N+1 en comentarios (`auctions/views.py:103`, `auction.html:230`)
- [ ] **PERF-005** — Query de categorías por request sin caché (`auctions/views.py:210-216`)
- [ ] **PERF-007** — `generate_market_analysis` suma en Python en vez de `Avg` (`auctions/data_utils.py:171-176`)
- [ ] **PERF-008** — Listados sin `select_related("user")` (`auctions/views.py:16,157,197`)

## Instrucciones / recomendaciones

1. **PERF-001 (crítico funcional).** Añadir `distinct=True` a cada `Count`:
   ```python
   User.objects.annotate(
       total_activity=Count("bids", distinct=True)
                    + Count("listings", distinct=True)
                    + Count("comments", distinct=True)
   )
   ```
   Sin esto los conteos del dashboard/`admin_users` son incorrectos por fan-out de JOINs.

2. **PERF-004 + PERF-008.** Añadir `select_related("user")` en `auction.comments.select_related("user").all()` (`views.py:103`) y en los listados que la plantilla vaya a recorrer por FK.

3. **PERF-002 + PERF-007.** Reemplazar los bucles con `.count()`/`sum()` por una única query con `annotate(Count(..., distinct=True))` / `aggregate(Avg(...))`.

4. **PERF-003.** Usar `QuerySet.iterator()` + `StreamingHttpResponse` en la exportación, o paginar.

5. **PERF-005.** Cachear la lista de categorías (framework de caché de Django) o resolverla con el índice de `category` (creado en `refactor/model-constraints`).

## Tests requeridos

- **TEST-007:** `assertNumQueries` en la vista de detalle de listing con N comentarios (debe ser constante, no crecer con N).
- Test de que los conteos de actividad del admin son correctos con datos conocidos (PERF-001).

## Verificación

```bash
pytest tests/integration/ -q
# Opcional: django-debug-toolbar (ya en requirements-dev.txt) para inspeccionar queries reales
```

## Commits sugeridos

```
perf(auctions): use distinct counts in admin annotations
perf(auctions): select_related user in comment and listing queries
perf(auctions): aggregate reports in the database
perf(auctions): stream admin data export
```

## Criterios de done

- [ ] Conteos del admin correctos; N+1 de comentarios eliminado (verificado con `assertNumQueries`)
- [ ] Exportación acotada en memoria
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
