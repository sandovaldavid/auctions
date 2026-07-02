# Auditoría de UI/UX — Sitio de Subastas

> **Fecha:** 2026-07-02 · **Commit:** `784f51a` · **Rama:** `develop`
> **Método:** análisis estático de plantillas, CSS y JS. Sin auditoría en vivo. Ver metodología en [README.md](README.md).

## Resumen

Se identificaron **12 hallazgos** de UI/UX. Varios son "UI muerta": controles renderizados que no hacen nada porque la vista no pasa los datos o el `<form>` no tiene `action`/`name`. También hay inconsistencias sistemáticas (dos versiones de Bootstrap, seis formatos de fecha) y una acción destructiva sin confirmación. El aspecto de contraste/accesibilidad se trata aparte en [accessibility.md](accessibility.md).

| Severidad | Cantidad |
|-----------|----------|
| Crítico   | 0 |
| Alto      | 3 |
| Medio     | 5 |
| Bajo      | 4 |

## Hallazgos

| ID | Severidad | Ubicación | Resumen | Esfuerzo | PR sugerido |
|----|-----------|-----------|---------|----------|-------------|
| UX-001 | Alto | `index.html:29-60`, `auctions/views.py:20` | Formulario de filtros sin `name`/`action`; la vista `index` no pasa `categories`: el filtro no funciona | M | `chore/frontend-consistency` |
| UX-002 | Alto | `index.html:110` | `{% include "auctions/components/mini_card.html" %}` a un archivo inexistente: 500 si `recently_viewed_items` se poblara | S | `chore/frontend-consistency` |
| UX-003 | Alto | `auction.html:144-149` | Cierre de subasta (acción destructiva) sin diálogo de confirmación | S | `chore/frontend-consistency` |
| UX-004 | Medio | `layout.html:28`, `admin/base.html:19` | Bootstrap 5.3.3 (público) vs 5.3.0 (admin); Font Awesome 6.0.0 vs 6.4.0 | S | `chore/frontend-consistency` |
| UX-005 | Medio | `dashboard.html:191`, `listings.html:123`, `listing_detail.html:76` | Moneda sin `floatformat:2` en admin: decimales variables (`$1200.5` vs `$1200.50`) | S | `chore/frontend-consistency` |
| UX-006 | Medio | `card.html:34`, `auction.html:27`, `admin/listings.html:98` | Imágenes de URL sin `onerror` fallback: URL rota muestra el glifo de imagen partida | S | `chore/frontend-consistency` |
| UX-007 | Medio | `admin/base.html:114` | Mensajes admin usan `alert-{{ message.tags }}`: un `error` de Django genera `alert-error`, que no es clase Bootstrap → alerta sin estilo | S | `chore/frontend-consistency` |
| UX-008 | Medio | `card.html:5,10,15,76`, `auction.html:54,70,106,178` | Plantillas referencian atributos inexistentes (`bids_count`, `is_new`, `is_premium`, `views`, `is_ending_soon`): renderizan vacío (UI muerta) | S | `chore/frontend-consistency` |
| UX-009 | Bajo | `card.html:88` vs `auction.html:174,234` vs admin | Seis formatos de fecha distintos (`M d, Y` / `F j, Y` / `j M Y, H:i` / `d/m/Y H:i` / …) | S | `chore/frontend-consistency` |
| UX-010 | Bajo | `footer.html:14-24,89-90` | Enlaces de footer (redes, legales) son anclas `#` muertas | S | `chore/frontend-consistency` |
| UX-011 | Bajo | `layout.js:79,100,114,285` | `console.log` de depuración en JS de producción | S | `chore/frontend-consistency` |
| UX-012 | Bajo | `login.html:22-27`, `register.html:24-32` | Login/register usan una variable `message` genérica en vez del framework de mensajes: no muestran errores de validación por campo | M | `chore/frontend-consistency` |

## Detalle de hallazgos Alto

### UX-001 — Formulario de filtros que no filtra

- **Ubicación:** `index.html:29-60` (los `<select>` `#categoryFilter` y `#sortBy`), vista en `auctions/views.py:15-20`.
- **Descripción:** el `<form>` no tiene `action` ni `method`, y los `<select>` no tienen `name`, así que al enviarlo no viaja nada. Además la vista `index` solo pasa `{"listings": ...}` — no pasa `categories`, por lo que el desplegable de categorías siempre está vacío. Es un control visible que aparenta funcionalidad inexistente.
- **Escenario de fallo:** el usuario selecciona una categoría y pulsa "Apply Filters"; la página se recarga sin filtrar (o no hace nada).
- **Recomendación:** o bien conectar el formulario a la vista `categories` existente (`views.py:194-219`, que sí filtra y ya calcula las categorías), pasándole los datos y `name`/`action` correctos; o bien retirar el control de `index.html` hasta implementarlo.

### UX-002 — Include a plantilla inexistente

- **Ubicación:** `index.html:110` (`{% include "auctions/components/mini_card.html" %}`).
- **Descripción:** el archivo `mini_card.html` no existe en el árbol de plantillas. Hoy no explota solo porque la vista nunca pasa `recently_viewed_items`, así que el bloque no se ejecuta; es una bomba latente.
- **Escenario de fallo:** si alguien puebla `recently_viewed_items` en el contexto, la página lanza `TemplateDoesNotExist` (500).
- **Recomendación:** crear el componente o eliminar el bloque "Recently Viewed" de `index.html` mientras no exista la funcionalidad.

### UX-003 — Cierre de subasta sin confirmación

- **Ubicación:** `auction.html:144-149`.
- **Descripción:** la acción de cerrar subasta (irreversible: fija ganador y desactiva) es un botón POST sin `confirm()`. En cambio, acciones menos críticas sí confirman (eliminar de watchlist en `card.html:23`; toggle admin en `listings.html:240-248`).
- **Escenario de fallo:** un clic accidental cierra la subasta sin posibilidad de deshacer desde la UI.
- **Recomendación:** añadir confirmación (diálogo nativo o modal Bootstrap) antes del submit. Combinar con el cambio a POST + CSRF de [security.md](security.md) (SEC-005).

## Referencias

- El contraste de badges/botones y los problemas de accesibilidad (foco, h1, skip-link) están en [accessibility.md](accessibility.md).
- UX-003 se solapa con SEC-005 (cierre de subasta) en [security.md](security.md).
- UX-006 (imágenes de URL) también es un vector de contenido mixto en [security.md](security.md) (SEC-013).
