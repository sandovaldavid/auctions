# Tarea: `fix/xss-templates` — XSS en plantillas y saneo de contenido externo

> **Prioridad:** 2 (Alto) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/security.md](../audits/security.md)

## Objetivo

Eliminar el vector de XSS almacenado de los datos de BD inyectados con `|safe` dentro de `<script>` en el panel admin, y endurecer el contenido externo: URLs de imagen de usuario que permiten `http://` y recursos de CDN sin verificación de integridad.

## Rama

```bash
git checkout develop && git pull
git checkout -b fix/xss-templates
```

## Hallazgos a resolver

- [ ] **SEC-009** — Datos de BD con `|safe` dentro de `<script>` (`auctions/templates/auctions/admin/analytics.html:242,275,328`, `reports.html:340`)
- [ ] **SEC-013** — `image` de usuario permite `http://` (`auctions/forms.py:52-61`, render en `auction.html:27`, `card.html:34`)
- [ ] **SEC-014** — CDN sin SRI; `plotly-latest.min.js` sin versión fija (`layout.html:28-37`, `admin/base.html:19-25,132`)

## Instrucciones / recomendaciones

1. **SEC-009 (`json_script`).** Reemplazar `{{ data|safe }}` dentro de `<script>` por el filtro seguro `json_script`, que escapa correctamente y produce JSON válido:

   ```django
   {{ market_trends.monthly_trends|json_script:"market-trends-data" }}
   ```
   ```js
   const marketTrendsData = JSON.parse(
       document.getElementById("market-trends-data").textContent
   );
   ```

   Aplicar a los tres archivos. Los divs Plotly de `dashboard.html:130,142,157` son HTML generado por Plotly (menor riesgo), pero conviene verificar que ningún label proviene de entrada de usuario sin escapar.

2. **SEC-013 (URL de imagen).** En `forms.clean_image`, restringir el esquema a `https://` (evita contenido mixto en el sitio HTTPS) y validar el host si se quiere. Considerar un `onerror` de fallback en las plantillas (se solapa con UX-006 en `chore/frontend-consistency`).

3. **SEC-014 (SRI + pinning).** Añadir `integrity="sha384-..."` y `crossorigin="anonymous"` a los `<link>`/`<script>` de CDN, y fijar `plotly-latest.min.js` a una versión concreta. Alternativa más robusta: vendorizar Bootstrap/FA localmente y servirlos con WhiteNoise.

## Tests requeridos

- Test de que un título/categoría con `</script>` no rompe ni ejecuta en las plantillas admin (render sin `|safe`).
- Test de que `clean_image` rechaza URLs `http://`.

## Verificación

```bash
pytest tests/unit/test_forms.py tests/integration/ -q
bandit -r auctions/ -ll
# Revisar manualmente el HTML renderizado del panel admin: no debe haber datos sin escapar en <script>
```

## Commits sugeridos

```
fix(auctions): use json_script for admin chart data
fix(auctions): require https scheme for listing image urls
fix(auctions): add SRI hashes and pin CDN assets
```

## Criterios de done

- [ ] Sin `|safe` sobre datos de BD dentro de `<script>`
- [ ] URLs de imagen restringidas a `https`
- [ ] Recursos de CDN con SRI y versión fija
- [ ] Tests verdes; `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
