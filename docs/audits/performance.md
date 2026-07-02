# Auditoría de Rendimiento — Sitio de Subastas

> **Fecha:** 2026-07-02 · **Commit:** `784f51a` · **Rama:** `develop`
> **Método:** análisis estático de patrones de consulta ORM y plantillas (sin profiling en vivo ni `django-debug-toolbar` con datos reales). Ver metodología en [README.md](README.md).

## Resumen

Se identificaron **8 hallazgos** de rendimiento. Los patrones dominantes son consultas N+1 sin `select_related`/`prefetch_related` y agregaciones hechas en Python en vez de en la base de datos. Dos de ellos afectan al panel de administración con un coste que crece linealmente con el número de usuarios. La ausencia de índices en las columnas de filtro/orden calientes amplifica todo lo anterior.

| Severidad | Cantidad |
|-----------|----------|
| Crítico   | 0 |
| Alto      | 3 |
| Medio     | 3 |
| Bajo      | 2 |

## Hallazgos

| ID | Severidad | Ubicación | Resumen | Esfuerzo | PR sugerido |
|----|-----------|-----------|---------|----------|-------------|
| PERF-001 | Alto | `auctions/admin_views.py:42-47,170-174` | `Count("bids") + Count("listings") + Count("comments")` sin `distinct=True`: conteos multiplicados por fan-out de JOINs | S | `refactor/query-performance` |
| PERF-002 | Alto | `auctions/data_utils.py:125-147` | `generate_user_activity_report` itera todos los usuarios con ~5 `.count()` cada uno: O(N·5) consultas | M | `refactor/query-performance` |
| PERF-003 | Alto | `auctions/admin_views.py:326-408` | `admin_export_data` exporta todos los listings/bids/users sin límite ni paginación: memoria no acotada | M | `refactor/query-performance` |
| PERF-004 | Medio | `auctions/views.py:103`, `auction.html:230` | N+1 en comentarios: `auction.comments.all()` sin `select_related("user")` | S | `refactor/query-performance` |
| PERF-005 | Medio | `auctions/views.py:210-216` | Query `distinct()` de categorías en cada request, sin caché ni índice en `category` | S | `refactor/query-performance` |
| PERF-006 | Medio | `auctions/models.py` (todos) | Sin índices de BD en `active`, `category`, `created`, `amount` (columnas de filtro/orden) | M | `refactor/model-constraints` |
| PERF-007 | Bajo | `auctions/data_utils.py:171-176` | `generate_market_analysis` trae precios a Python y suma con `sum()/len()` en vez de `Avg` en BD | S | `refactor/query-performance` |
| PERF-008 | Bajo | `auctions/views.py:16,157,197` | Listados sin `select_related("user")`: N+1 latente si la plantilla accede a `auction.user` | S | `refactor/query-performance` |

## Detalle de hallazgos Alto

### PERF-001 — Conteos multiplicados por fan-out de JOINs

- **Ubicación:** `auctions/admin_views.py:42-47` (`top_users` en el dashboard) y `:170-174` (`admin_users`).
- **Descripción:** `User.objects.annotate(total_activity=Count("bids") + Count("listings") + Count("comments"))` combina varios `Count` sobre relaciones distintas en una sola query. Sin `distinct=True`, cada JOIN multiplica las filas de los otros (producto cartesiano), inflando los conteos. Igual patrón en `admin_users` (`listings_count`, `bids_count`, `comments_count`).
- **Escenario de fallo:** un usuario con 3 listings y 4 pujas puede reportar `listings_count = 12` en vez de 3, porque el JOIN con pujas duplica las filas de listings.
- **Recomendación:** usar `Count("bids", distinct=True)` en cada anotación, o separar las anotaciones con subconsultas (`Subquery`/`Count` independientes). Añadir un test que verifique los conteos con datos conocidos.

### PERF-002 — Reporte de actividad O(N·5)

- **Ubicación:** `auctions/data_utils.py:125-147` (más `calculate_engagement_score` en `:44-47`).
- **Descripción:** el método itera sobre **cada** usuario y ejecuta ~5 `.count()`/`.filter().count()` por iteración. El total de consultas crece como O(N·5) sin paginación ni anotación.
- **Escenario de fallo:** con 1.000 usuarios se ejecutan ~5.000 consultas para un solo reporte.
- **Recomendación:** reemplazar el bucle por una única query con `annotate(Count(..., distinct=True))` y paginar. Nota: este módulo también tiene el import `numpy` no disponible en producción (ver [code-quality.md](code-quality.md), CODE-002).

### PERF-003 — Exportación sin límite

- **Ubicación:** `auctions/admin_views.py:326-408` (`admin_export_data`).
- **Descripción:** construye la exportación cargando en memoria todos los listings, pujas y usuarios sin `iterator()`, límite ni streaming.
- **Escenario de fallo:** con tablas grandes, la petición consume memoria proporcional al dataset completo y puede agotar el dyno de Heroku.
- **Recomendación:** usar `QuerySet.iterator()` y `StreamingHttpResponse`, o paginar/segmentar la exportación.

## Detalle de hallazgos Medio (destacado)

### PERF-004 — N+1 en comentarios

- **Ubicación:** `auctions/views.py:103` (`auction.comments.all()`), consumido en `auction.html:230` (`comment.user.username` por cada comentario).
- **Descripción:** sin `select_related("user")`, cada comentario dispara una consulta adicional para su usuario. El mismo camino se recorre al re-renderizar tras `bid` (`views.py:138`).
- **Escenario de fallo:** un listing con 50 comentarios genera 1 + 50 consultas.
- **Recomendación:** `auction.comments.select_related("user").all()`.

## Metodología y limitaciones

Este análisis es estático: se identificaron los patrones por lectura del código ORM y de las plantillas, no midiendo tiempos ni número de queries en ejecución. Para cuantificarlos conviene una pasada futura con `django-debug-toolbar` (ya en `requirements-dev.txt`) o `assertNumQueries` en tests, sobre datos representativos. Los índices propuestos (PERF-006) deberían priorizarse tras confirmar los planes de consulta reales en PostgreSQL.

## Referencias

- PERF-006 (índices) se agrupa con las constraints de modelo en [code-quality.md](code-quality.md) (CODE-005), bajo el PR `refactor/model-constraints`.
- PERF-002 comparte módulo con el problema de dependencias de [code-quality.md](code-quality.md) (CODE-002).
- La falta de tests de rendimiento (`assertNumQueries`) se anota en [testing-and-ci.md](testing-and-ci.md) (TEST-007).
