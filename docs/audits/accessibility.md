# Auditoría de Accesibilidad y Contraste — Sitio de Subastas

> **Fecha:** 2026-07-02 · **Commit:** `784f51a` · **Rama:** `develop`
> **Método:** análisis estático de plantillas/CSS + cálculo matemático de ratios de contraste WCAG 2.1 (mismas fórmulas que `tests/unit/test_theme_colors.py:12-29`). Sin auditoría en vivo (axe/Lighthouse). Ver metodología en [README.md](README.md).

## Resumen

Se identificaron **14 hallazgos** de accesibilidad. El más estructural es que el `components.css` cargado referencia **22 variables CSS distintas que no existen** (87 referencias `var()` rotas), mientras el sistema de variables correcto vive en archivos CSS huérfanos que ningún template enlaza. Sobre contraste, de **23 pares** de color evaluados matemáticamente, **11 fallan** el mínimo WCAG AA, concentrados en badges e íconos de Bootstrap con texto blanco sobre fondos claros y en botones outline que usan colores semánticos crudos como texto.

| Severidad | Cantidad |
|-----------|----------|
| Crítico   | 1 |
| Alto      | 5 |
| Medio     | 6 |
| Bajo      | 2 |

## Hallazgos

| ID | Severidad | Ubicación | Resumen | Esfuerzo | PR sugerido |
|----|-----------|-----------|---------|----------|-------------|
| A11Y-001 | Crítico | `auctions/static/css/components.css` (87 refs) | 22 variables CSS indefinidas en el archivo cargado; los colores correctos están en `static/css/components/{card,alert,footer,pagination}.css` huérfanos (sin enlazar) | L | `fix/a11y-css-variables` |
| A11Y-002 | Alto | `admin/users.html:87`, `reports.html:206,294`, `listings.html:145` … | Badges `bg-warning`/`bg-info` con texto blanco: 1.63:1 y 1.96:1 (fallo severo) | M | `fix/a11y-css-variables` |
| A11Y-003 | Alto | `dashboard.html:153`, `listing_detail.html:182`, admin | `text-warning`/`text-info` sobre blanco: 1.63:1 y 1.96:1 | M | `fix/a11y-css-variables` |
| A11Y-004 | Alto | `pages/error-pages.css:237-240`, `auction.css:429-431`, `index.css:132` | Botones outline con color semántico crudo como texto: 2.15–3.76:1 | M | `fix/a11y-css-variables` |
| A11Y-005 | Alto | `layout.css:27-45`, `layout.js:172-184` | Skip-link con CSS + JS pero **sin elemento `<a class="skip-link">` en el DOM**: usuarios de teclado sin salto al contenido | S | `fix/a11y-css-variables` |
| A11Y-006 | Alto | `index.html`, `watchList.html`, `login.html`, `register.html`, `newAuctions.html` | Sin `<h1>`: las páginas empiezan en `h2`/`h3` | S | `fix/a11y-css-variables` |
| A11Y-007 | Medio | `auctions/static/css/pages/auction.css:153-157` | `.bids-count` (`#d97706` sobre `#eff6ff`): 2.93:1, texto pequeño | S | `fix/a11y-css-variables` |
| A11Y-008 | Medio | `errors/404.html:4` (y 400/403/500), `layout.html:4` | `lang="en"` en el layout pero contenido de páginas de error en español | S | `fix/a11y-css-variables` |
| A11Y-009 | Medio | `components/card.html:91-94` | Enlace "View" con texto oculto bajo breakpoint `sm`: en móvil queda solo un ícono sin nombre accesible | S | `chore/frontend-consistency` |
| A11Y-010 | Medio | `pages/login.css:76-80`, `pages/auction.css:201-205` | Anillo de foco eliminado (`box-shadow:none; border:none`): sin indicador de foco visible (WCAG 2.4.7) | S | `fix/a11y-css-variables` |
| A11Y-011 | Medio | `admin/listings.html:161-171`, `users.html:134-144`, `listing_detail.html:114` | Controles solo-ícono en admin sin `aria-label` (solo `title`) | S | `chore/frontend-consistency` |
| A11Y-012 | Medio | `index.html:16,35,45,57`, `card.html:7,12,17`, `auction.html:39,52` | Íconos Font Awesome decorativos sin `aria-hidden="true"` de forma consistente | S | `chore/frontend-consistency` |
| A11Y-013 | Bajo | `components/alert.html:6` | `aria-live="assertive"` para todos los mensajes (incluidos success/info); debería ser `polite` salvo errores críticos | S | `chore/frontend-consistency` |
| A11Y-014 | Bajo | `layout.html:9`, `admin/base.html:7` | `maximum-scale=5.0` en viewport: restringe el zoom del usuario | S | `chore/frontend-consistency` |

## Tabla de contraste (WCAG 2.1, calculada)

Ratios calculados con el script `wcag_ratios.py` (reutiliza `relative_luminance`/`contrast_ratio` de `tests/unit/test_theme_colors.py`). Umbral AA: 4.5:1 texto normal, 3.0:1 texto grande / componentes UI.

| Par (fg sobre bg) | Ubicación | Ratio | Umbral | Resultado |
|---|---|---|---|---|
| Badge `bg-warning` + blanco (`#ffffff`/`#ffc107`) | `admin/users.html:87` +6 | 1.63:1 | 4.5:1 | **FALLA** |
| Badge `bg-info` + blanco (`#ffffff`/`#0dcaf0`) | `admin/users.html:109` +6 | 1.96:1 | 4.5:1 | **FALLA** |
| Badge `bg-success` + blanco (`#ffffff`/`#198754`) | `card.html:65`, `auction.html:51` | 4.53:1 | 4.5:1 | Pasa |
| `text-warning` sobre blanco (`#ffc107`/`#ffffff`) | `dashboard.html:153` (8 usos) | 1.63:1 | 4.5:1 | **FALLA** |
| `text-info` sobre blanco (`#0dcaf0`/`#ffffff`) | admin (9 usos) | 1.96:1 | 4.5:1 | **FALLA** |
| `text-success` sobre blanco (`#198754`/`#ffffff`) | `listings.html:127-131` (20 usos) | 4.53:1 | 4.5:1 | Pasa |
| `btn-outline-heart` (`#ef4444`/`#ffffff`) | `auction.css:429-431` | 3.76:1 | 4.5:1 | **FALLA** |
| `btn-outline-custom` 404 (`#3b82f6`/`#ffffff`) | `error-pages.css:237` | 3.68:1 | 4.5:1 | **FALLA** |
| `btn-outline-custom` 400 (`#f59e0b`/`#ffffff`) | `error-pages.css:238` | 2.15:1 | 4.5:1 | **FALLA** |
| `btn-outline-custom` 403 (`#d97706`/`#ffffff`) | `error-pages.css:239` | 3.19:1 | 4.5:1 | **FALLA** |
| `btn-outline-custom` 500 (`#ef4444`/`#ffffff`) | `error-pages.css:240` | 3.76:1 | 4.5:1 | **FALLA** |
| `.filter-card .btn-outline-primary` (`#3b82f6`/`#ffffff`) | `index.css:132` | 3.68:1 | 4.5:1 | **FALLA** |
| `.bids-count` (`#d97706`/`#eff6ff`) | `auction.css:153-157` | 2.93:1 | 4.5:1 | **FALLA** |
| `.price-amount` (`#059669`/`#ffffff`) | `auction.css:140-143` (texto grande) | 3.77:1 | 3.0:1 | Pasa |
| `--error-text` sobre blanco (`#dc2626`/`#ffffff`) | `variables.css:281` | 4.83:1 | 4.5:1 | Pasa |
| `text-muted` (`#6b7280`/`#ffffff`) | 47 usos | 4.83:1 | 4.5:1 | Pasa |
| `text-muted` sobre `#f9fafb` | fondo de página | 4.63:1 | 4.5:1 | Pasa |
| Texto principal (`#111827`/`#ffffff`) | body | 17.74:1 | 4.5:1 | Pasa |
| Badge categoría (`#1d4ed8`/`#dbeafe`) | `test_theme_colors.py` | 5.49:1 | 4.5:1 | Pasa |
| Nav: blanco/`#2563eb` | `navigation.css:189` | 5.17:1 | 4.5:1 | Pasa |
| Nav: blanco/`#1e40af` | extremo del gradiente | 8.72:1 | 4.5:1 | Pasa |
| Ícono dorado sobre nav (`#fbbf24`/`#2563eb`) | `navigation.css:102` (decorativo) | 3.10:1 | 3.0:1 | Pasa |
| Debug info (`#e5e7eb`/`#1f2937`) | `error-pages.css:209-210` | 11.86:1 | 4.5:1 | Pasa |

**Total: 23 pares, 11 fallan WCAG AA.**

## Detalle de hallazgos Crítico y Alto

### A11Y-001 — Dos sistemas de variables CSS en conflicto

- **Ubicación:** `auctions/static/css/components.css` (87 referencias rotas). Valores correctos en `static/css/components/{card,alert,footer,pagination}.css` (huérfanos, ningún template los enlaza).
- **Descripción:** `variables.css` define el esquema `--primary-500`, `--success`, `--text-primary`, etc. Pero el `components.css` **cargado** usa un esquema legacy distinto (`--primary-color`, `--success-color`, `--card-bg`, `--price-color`, `--bid-color`, `--text-light`, `--gradient-primary`, …). Verificado por script: **87** referencias `var()` a **22** variables que no están definidas en ninguna parte. Esas declaraciones son inválidas y caen al valor heredado/inicial.
- **Escenario de fallo:** los colores de acento de cards, footer, paginación y las barras de alerta no se aplican; el texto que debería ser azul de marca se renderiza como gris de cuerpo heredado (`--text-primary #111827`). Cualquier medición "de diseño" del contraste es engañosa porque el color intencional no llega a pintarse.
- **Recomendación:** unificar en el sistema de `variables.css`. O bien enlazar los 4 archivos `components/*.css` (que ya contienen los colores correctos y con contraste corregido) y retirar los bloques legacy de `components.css`, o bien reescribir `components.css` para usar los nombres de `variables.css`. Resolver esto **antes** de tocar contraste, porque cambia qué colores están realmente en pantalla.

### A11Y-002 / A11Y-003 — Badges y texto Bootstrap con contraste severo

- **Ubicación:** badges en `admin/users.html:87,109`, `reports.html:206,243,288,294`, `listings.html:139,145`, `listing_detail.html:49,103,107`, `analytics.html:120,127`; utilidades `text-warning`/`text-info` en `dashboard.html:153`, `listing_detail.html:182`, y otros.
- **Descripción:** Bootstrap 5.3 fija `color:#fff` en `.badge`. Usar `bg-warning` (`#ffc107`) o `bg-info` (`#0dcaf0`) sin `text-dark` produce texto blanco sobre amarillo/cian: **1.63:1** y **1.96:1**. Lo mismo con las utilidades de texto `text-warning`/`text-info` sobre fondo blanco.
- **Escenario de fallo:** una etiqueta de estado "Pendiente" en amarillo con texto blanco es prácticamente ilegible; usuarios con baja visión no pueden leerla.
- **Recomendación:** añadir `text-dark` a los badges `bg-warning`/`bg-info` (patrón ya usado correctamente en `auction.html:64`), y para las utilidades de texto usar tonos oscurecidos (p. ej. las variables `--*-text` de `variables.css`). Extender `tests/unit/test_theme_colors.py` para cubrir estos pares (ver [testing-and-ci.md](testing-and-ci.md), TEST-006).

### A11Y-004 — Botones outline con colores semánticos crudos

- **Ubicación:** `pages/error-pages.css:237-240` (`.btn-outline-custom` de las 4 páginas de error), `auction.css:429-431` (`.btn-outline-heart`, botón "Add to Watchlist"), `index.css:132` (`.filter-card .btn-outline-primary`).
- **Descripción:** el texto del botón usa el color semántico puro (`--warning #f59e0b`, `--info #3b82f6`, `--error #ef4444`) sobre blanco, con ratios de **2.15:1 a 3.76:1**, todos por debajo de 4.5:1.
- **Escenario de fallo:** el botón "Volver" de la página 400 (amarillo, 2.15:1) es casi ilegible en reposo.
- **Recomendación:** usar las variantes oscurecidas (`--*-dark`/`--*-text`) para el texto en reposo, manteniendo el color vivo solo para el fondo en `:hover` (donde el texto pasa a blanco y sí contrasta).

### A11Y-005 — Skip-link sin elemento en el DOM

- **Ubicación:** CSS en `layout.css:27-45` y `auctions/styles.css:116-130`; JS en `layout.js:172-184`; pero ningún template renderiza `<a class="skip-link">`.
- **Descripción:** existen los estilos `.skip-link` y un handler de click que hace foco en `.skip-link`, pero el elemento no está en el DOM (grep: cero coincidencias en templates). Además `<main id="main-content">` (`layout.html:70`) no tiene `tabindex="-1"`, así que no es enfocable aunque el enlace existiera.
- **Escenario de fallo:** un usuario de teclado no tiene forma de saltar la navegación e ir directo al contenido en cada página.
- **Recomendación:** añadir `<a href="#main-content" class="skip-link">Saltar al contenido</a>` como primer elemento del `<body>` en `layout.html`, y `tabindex="-1"` en `<main>`.

### A11Y-006 — Páginas sin `<h1>`

- **Ubicación:** `index.html` (empieza en `h2.display-5`, `:15`), `watchList.html` (`h2`, `:16`), `newAuctions.html` (`h2`, `:17`), `login.html` (`h2`, `:18`), `register.html` (`h2`, `:18`).
- **Descripción:** estas páginas no tienen un `<h1>`; la jerarquía arranca en `h2`/`h3`. Los lectores de pantalla usan el `h1` como ancla del contenido principal.
- **Escenario de fallo:** un usuario que navega por encabezados no encuentra el título principal de la página de inicio.
- **Recomendación:** promover el encabezado principal de cada página a `<h1>` (manteniendo las clases visuales `display-*` para el tamaño). Revisar también el salto h1→h4 en `auction.html:79,189`.

## Evidencia

Conteo de variables CSS indefinidas en el archivo cargado (`components.css`):

```text
referencias var() en components.css: 132
referencias a variables INDEFINIDAS: 87
variables indefinidas distintas: 22
['--badge-ending', '--bg-accent', '--bg-hover', '--bg-main', '--bg-user',
 '--bid-color', '--border-color', '--card-bg', '--danger-color',
 '--gradient-primary', '--hover-shadow', '--info-color', '--price-color',
 '--primary-color', '--primary-light', '--secondary-color', '--secondary-dark',
 '--secondary-light', '--success-color', '--text-light', '--toggle-icon',
 '--warning-color']
```

Ratios de contraste: ver la tabla arriba (23 pares, 11 fallos), generada con `wcag_ratios.py` sobre las mismas fórmulas WCAG 2.1 del test existente.

## Referencias

- La suite `tests/unit/test_theme_colors.py` ya valida contraste de forma estática; ampliarla para cubrir los 11 pares que fallan se detalla en [testing-and-ci.md](testing-and-ci.md) (TEST-006).
- El `axe.min.js` presente en `tests/e2e/fixtures/` habilita una auditoría en vivo futura (fuera del alcance de este análisis estático) — ver [testing-and-ci.md](testing-and-ci.md) (TEST-004).
- Los problemas de UI muerta y consistencia visual relacionados (formulario de filtros sin funcionar, versiones de Bootstrap divergentes) están en [ui-ux.md](ui-ux.md).
