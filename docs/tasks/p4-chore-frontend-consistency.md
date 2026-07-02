# Tarea: `chore/frontend-consistency` — Consistencia y limpieza de frontend

> **Prioridad:** 4 (Bajo) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/ui-ux.md](../audits/ui-ux.md) · [../audits/accessibility.md](../audits/accessibility.md) · [../audits/security.md](../audits/security.md)

## Objetivo

Pulir la UI: retirar la UI muerta (controles que no hacen nada), unificar versiones y formatos, dar consistencia a fechas/moneda, y limpiar restos de depuración. Cambios de bajo riesgo y alto impacto en percepción de calidad.

## Rama

```bash
git checkout develop && git pull
git checkout -b chore/frontend-consistency
```

## Hallazgos a resolver

- [ ] **UX-001** — Formulario de filtros del index sin `name`/`action` (`index.html:29-60`)
- [ ] **UX-002** — Include a `mini_card.html` inexistente (`index.html:110`)
- [ ] **UX-003** — Cierre de subasta sin confirmación (`auction.html:144-149`)
- [ ] **UX-004** — Bootstrap 5.3.3 vs 5.3.0; FA 6.0.0 vs 6.4.0
- [ ] **UX-005** — Moneda sin `floatformat:2` en admin
- [ ] **UX-006** — Imágenes de URL sin `onerror` fallback
- [ ] **UX-007** — Mensajes admin con `alert-{{ tags }}` → `alert-error` sin estilo (`admin/base.html:114`)
- [ ] **UX-008** — Plantillas referencian atributos inexistentes (`bids_count`, `is_new`, …)
- [ ] **UX-009** — Seis formatos de fecha distintos
- [ ] **UX-010** — Enlaces de footer son anclas `#` muertas
- [ ] **UX-011** — `console.log` en `layout.js:79,100,114,285`
- [ ] **UX-012** — Login/register usan `message` genérico, no el framework de mensajes
- [ ] **A11Y-009** — Enlace "View" sin nombre accesible en móvil (`card.html:91-94`)
- [ ] **A11Y-011** — Controles solo-ícono en admin sin `aria-label`
- [ ] **A11Y-012** — Íconos FA decorativos sin `aria-hidden` consistente
- [ ] **A11Y-013** — `aria-live="assertive"` para todos los mensajes (`alert.html:6`)
- [ ] **A11Y-014** — `maximum-scale=5.0` restringe el zoom
- [ ] **SEC-018** — Páginas de error enlazan a `admin_dashboard` (revela URL admin)

## Instrucciones / recomendaciones

- **UX-001:** conectar el formulario a la vista `categories` existente (`views.py:194-219`, que ya filtra y calcula categorías) con `name`/`action`/`method`, o retirar el control hasta implementarlo.
- **UX-002:** crear `mini_card.html` o eliminar el bloque "Recently Viewed".
- **UX-003:** añadir `confirm()` o modal antes del submit de cierre (combinar con el cambio a POST de SEC-005 si aún no se hizo).
- **UX-004:** unificar a una sola versión de Bootstrap y FA en `layout.html` y `admin/base.html`.
- **UX-005/UX-009:** definir un formato único de moneda (`|floatformat:2`) y de fecha; aplicarlo en todos los templates. Considerar un template filter o `DATE_FORMAT` global.
- **UX-006:** `onerror` que muestre el placeholder ya existente.
- **UX-007:** mapear `error`→`danger` en `admin/base.html` como hace `components/alert.html:9`.
- **UX-008:** retirar las referencias a atributos inexistentes o anotarlos en la vista.
- **UX-011:** quitar los `console.log`.
- **A11Y-009/011/012:** añadir `aria-label` a controles solo-ícono y `aria-hidden="true"` a los íconos decorativos.
- **A11Y-013:** `aria-live="polite"` salvo para errores críticos.
- **A11Y-014:** quitar `maximum-scale` del viewport.
- **SEC-018:** quitar el enlace a `admin_dashboard` de las páginas de error públicas.

## Verificación

```bash
pytest tests/integration/ -q
ruff check . && black --check .
# Revisar manualmente: filtros del index, cierre con confirmación, alertas admin con estilo
```

## Commits sugeridos

```
fix(auctions): wire index filters to categories view
chore(auctions): unify bootstrap and font-awesome versions
style(auctions): consistent currency and date formatting
fix(auctions): map admin error messages to bootstrap danger class
chore(auctions): remove debug console.log and dead UI references
fix(auctions): add aria labels and fix decorative icon semantics
```

## Criterios de done

- [ ] Sin UI muerta ni `console.log`; versiones y formatos unificados
- [ ] Controles accesibles (aria) y alertas admin con estilo
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
