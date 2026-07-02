# Tarea: `fix/a11y-css-variables` — Sistema de variables CSS y contraste WCAG

> **Prioridad:** 2 (Alto) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/accessibility.md](../audits/accessibility.md) · [../audits/testing-and-ci.md](../audits/testing-and-ci.md)

## Objetivo

Reparar la accesibilidad de la capa visual: unificar el sistema de variables CSS roto (los colores intencionales no se pintan), corregir los 11 pares de color que fallan WCAG AA, restaurar el indicador de foco, añadir el skip-link y los `<h1>` ausentes. El orden importa: **primero** las variables CSS, porque cambian qué colores están realmente en pantalla.

## Rama

```bash
git checkout develop && git pull
git checkout -b fix/a11y-css-variables
```

## Hallazgos a resolver

- [ ] **A11Y-001** — 87 `var()` indefinidas en el `components.css` cargado (colores correctos en `static/css/components/*.css` huérfanos)
- [ ] **A11Y-002** — Badges `bg-warning`/`bg-info` con texto blanco (1.63:1 / 1.96:1)
- [ ] **A11Y-003** — `text-warning`/`text-info` sobre blanco
- [ ] **A11Y-004** — Botones outline con color semántico crudo (2.15–3.76:1)
- [ ] **A11Y-005** — Skip-link con CSS+JS pero sin elemento en el DOM
- [ ] **A11Y-006** — Sin `<h1>` en index/watchlist/login/register
- [ ] **A11Y-007** — `.bids-count` (`#d97706` sobre `#eff6ff`, 2.93:1)
- [ ] **A11Y-010** — Anillo de foco eliminado (`login.css:76-80`, `auction.css:201-205`)
- [ ] **TEST-006** — Ampliar `tests/unit/test_theme_colors.py` a los pares que fallan

## Instrucciones / recomendaciones

1. **A11Y-001 primero.** Unificar en el sistema de `variables.css`. Dos caminos:
   - **Recomendado:** enlazar los 4 archivos `static/css/components/{card,alert,footer,pagination}.css` (que ya usan las variables correctas y con contraste corregido) y retirar los bloques legacy equivalentes de `components.css`.
   - Alternativa: reescribir `components.css` para usar los nombres de `variables.css` (`--primary-500` en vez de `--primary-color`, etc.).

   Verifica que no queden `var(--*)` sin definir (ver comando abajo).

2. **A11Y-002/003 (badges/utilidades).** Añadir `text-dark` a los badges `bg-warning`/`bg-info` (patrón ya correcto en `auction.html:64`). Para texto, usar las variantes oscurecidas `--*-text`/`--*-dark` de `variables.css`.

3. **A11Y-004/007 (botones y contadores).** Usar `--*-dark`/`--*-text` para el texto en reposo; mantener el color vivo solo para el fondo en `:hover` (donde el texto es blanco y sí contrasta).

4. **A11Y-005 (skip-link).** Añadir como primer elemento del `<body>` en `layout.html`:
   ```html
   <a href="#main-content" class="skip-link">Saltar al contenido</a>
   ```
   y `tabindex="-1"` en `<main id="main-content">`. El CSS (`layout.css:27-45`) y el JS (`layout.js:172-184`) ya existen.

5. **A11Y-006 (`<h1>`).** Promover el encabezado principal de cada página a `<h1>` conservando las clases visuales `display-*`. Revisar el salto h1→h4 en `auction.html`.

6. **A11Y-010 (foco).** Restaurar un indicador de foco visible (outline o box-shadow con contraste) en `login.css:76-80` y `auction.css:201-205`.

## Tests requeridos

- **TEST-006:** ampliar `tests/unit/test_theme_colors.py` para cubrir los 11 pares que fallan (badges/botones Bootstrap), reutilizando `contrast_ratio`. Los tests deben fallar con el estado actual y pasar tras el fix.

## Verificación

```bash
pytest tests/unit/test_theme_colors.py -q
# No deben quedar variables CSS indefinidas en components.css:
python3 - <<'EOF'
import re
defined=set()
for f in ["auctions/static/css/variables.css","auctions/static/css/components.css"]:
    defined|=set(re.findall(r'(--[\w-]+)\s*:',open(f).read()))
used=re.findall(r'var\((--[\w-]+)',open("auctions/static/css/components.css").read())
undef=[u for u in used if u not in defined]
print("indefinidas:",len(undef))
EOF
```

## Commits sugeridos

```
fix(auctions): unify CSS variable system and drop legacy components.css
fix(auctions): meet WCAG AA contrast for badges and outline buttons
fix(auctions): add skip link and restore focus indicators
fix(auctions): add missing h1 headings on public pages
test(tests): extend contrast tests to Bootstrap badge and button pairs
```

## Criterios de done

- [ ] Cero `var()` indefinidas en `components.css`
- [ ] Los 11 pares de contraste pasan WCAG AA (verificado por test)
- [ ] Skip-link funcional; foco visible; `<h1>` en todas las páginas públicas
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
