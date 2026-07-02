# Auditoría de Seguridad — Sitio de Subastas

> **Fecha:** 2026-07-02 · **Commit:** `784f51a` · **Rama:** `develop`
> **Método:** análisis estático (lectura de código + `bandit` + `safety`), sin servidor en vivo. Ver metodología en [README.md](README.md).

## Resumen

Se identificaron **18 hallazgos** de seguridad. Los más graves no dependen de vulnerabilidades en dependencias (bandit y safety salen limpios), sino de la lógica de la aplicación: una condición de carrera con dinero en `place_bid`, mutaciones de estado vía GET (bypaseables por CSRF), un endpoint de datos sin autenticación, y el registro de usuarios que evita por completo los validadores de contraseña de Django.

| Severidad | Cantidad |
|-----------|----------|
| Crítico   | 4 |
| Alto      | 6 |
| Medio     | 5 |
| Bajo      | 3 |

## Hallazgos

| ID | Severidad | Ubicación | Resumen | Esfuerzo | PR sugerido |
|----|-----------|-----------|---------|----------|-------------|
| SEC-001 | Crítico | `auctions/models.py:40-45` | `place_bid` sin transacción ni `select_for_update`: condición de carrera en pujas concurrentes | M | `fix/security-critical` |
| SEC-002 | Crítico | `auctions/models.py:40-45` | `place_bid` no valida contra `starting_bid` cuando `current_bid is None`: se aceptan pujas por debajo del precio inicial | S | `fix/security-critical` |
| SEC-003 | Crítico | `auctions/views.py:47-72` | `register` usa `create_user` con `request.POST` crudo: omite `AUTH_PASSWORD_VALIDATORS` (contraseñas débiles) y lanza `KeyError`→500 si falta un campo | M | `fix/security-critical` |
| SEC-004 | Crítico | `auctions/admin_views.py:420`, `auctions/urls.py:47` | `test_admin_dashboard` sin `@login_required`/`@user_passes_test` ni guard de `DEBUG`: fuga de conteos (usuarios, pujas, listings) a anónimos | S | `fix/admin-routing` |
| SEC-005 | Alto | `auctions/views.py:176-191` | `close_auction` cambia estado en GET: CSRF vía `<img src>` con víctima autenticada | M | `fix/security-critical` |
| SEC-006 | Alto | `auctions/views.py:166-173` | `watchlist_remove` muta estado en GET (invocado por `card.html:23`) | S | `fix/security-critical` |
| SEC-007 | Alto | `auctions/views.py:42-44` | `logout` acepta GET: cierre de sesión forzable vía CSRF | S | `fix/security-critical` |
| SEC-008 | Alto | `commerce/settings.py:14` | `SECRET_KEY` con fallback hardcodeado; sin validación de que exista en producción | S | `fix/security-critical` |
| SEC-009 | Alto | `auctions/templates/auctions/admin/analytics.html:275,328`, `reports.html:340` | Datos de BD renderizados con `\|safe` dentro de `<script>`: XSS almacenado si un label deriva de entrada de usuario | M | `fix/xss-templates` |
| SEC-010 | Alto | `commerce/settings.py:118-128` | Faltan `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS` (detrás de proxy Heroku/nginx) | M | `chore/settings-hardening` |
| SEC-011 | Medio | `auctions/views.py:26-27,49-54` | `login`/`register` leen `request.POST["campo"]` sin `.get()`: `KeyError`→500 con peticiones manipuladas | S | `fix/security-critical` |
| SEC-012 | Medio | `commerce/settings.py` (global) | Sin configuración `LOGGING`: sin captura de errores ni auditoría en producción | M | `chore/settings-hardening` |
| SEC-013 | Medio | `auctions/forms.py:52-61`, `auction.html:27`, `card.html:34` | `image` es URL de usuario permitiendo `http://`: contenido mixto + vector de tracking/phishing en `<img src>` | M | `fix/xss-templates` |
| SEC-014 | Medio | `auctions/templates/auctions/layout.html:28-37`, `admin/base.html:19-25,132` | Recursos de CDN sin `integrity` (SRI); `plotly-latest.min.js` sin versión fija | M | `fix/xss-templates` |
| SEC-015 | Medio | `commerce/settings.py:120` | `SECURE_BROWSER_XSS_FILTER` está obsoleto (header `X-XSS-Protection` desaconsejado) | S | `chore/settings-hardening` |
| SEC-016 | Bajo | `commerce/settings.py:126-127` | `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` solo bajo `not DEBUG`; sin `SESSION_COOKIE_HTTPONLY` explícito ni `SESSION_COOKIE_AGE` | S | `chore/settings-hardening` |
| SEC-017 | Bajo | `auctions/admin_views.py:58`, `error_views` | `except Exception as e` con `str(e)` al contexto de plantilla: potencial fuga de detalles internos | S | `chore/settings-hardening` |
| SEC-018 | Bajo | `auctions/templates/auctions/errors/404.html:43` (y 400/500) | Las páginas de error enlazan a `admin_dashboard`, revelando la URL del panel a anónimos | S | `chore/frontend-consistency` |

## Detalle de hallazgos Crítico y Alto

### SEC-001 — Condición de carrera en `place_bid`

- **Ubicación:** `auctions/models.py:40-45` (la vista `auctions/views.py:112-140` tampoco abre transacción).
- **Descripción:** `place_bid` lee `self.current_bid`, compara, asigna y guarda sin `select_for_update()` ni `transaction.atomic()`. Dos pujas concurrentes leen el mismo `current_bid`, ambas pasan la comprobación y una sobrescribe silenciosamente a la otra.
- **Escenario de fallo:** dos usuarios pujan \$110 y \$120 casi a la vez sobre un `current_bid` de \$100. Ambas transacciones leen \$100, ambas pasan la validación, la última en escribir gana; el importe intermedio y su `Bid` pueden quedar inconsistentes respecto a `current_bid`.
- **Recomendación:** envolver la lectura-modificación-escritura en `transaction.atomic()` y recargar la fila con `Listing.objects.select_for_update().get(pk=...)` antes de comparar. Añadir un test de concurrencia (ver [testing-and-ci.md](testing-and-ci.md), TEST-001).

```python
from django.db import transaction

def place_bid(self, user, bid_value):
    with transaction.atomic():
        listing = Listing.objects.select_for_update().get(pk=self.pk)
        floor = listing.current_bid or listing.starting_bid
        if bid_value <= floor:
            raise ValidationError("The bid must be higher than the current bid.")
        listing.current_bid = bid_value
        listing.save(update_fields=["current_bid"])
        Bid.objects.create(user=user, listing=listing, amount=bid_value)
```

### SEC-002 — `place_bid` no valida contra `starting_bid`

- **Ubicación:** `auctions/models.py:40-45`.
- **Descripción:** la única comprobación es `if self.current_bid is not None and bid_value <= self.current_bid`. Cuando aún no hay pujas (`current_bid is None`), la condición se salta por completo y se acepta cualquier valor positivo, incluso por debajo del precio inicial.
- **Escenario de fallo:** un listing con `starting_bid=1000` y sin pujas acepta una primera puja de \$0.01; `BidForm.clean_amount` (`forms.py:69-75`) solo rechaza `<= 0`, no tiene acceso al listing para comparar contra el precio inicial.
- **Recomendación:** usar `floor = current_bid or starting_bid` como en el snippet de SEC-001. Considerar además una `CheckConstraint` a nivel de BD (ver [code-quality.md](code-quality.md), CODE-005).

### SEC-003 — `register` omite los validadores de contraseña y lanza 500

- **Ubicación:** `auctions/views.py:47-72`.
- **Descripción:** el registro no usa un `Form`/`UserCreationForm`; lee `request.POST["username"|"email"|"password"|"confirmation"]` directamente y llama `User.objects.create_user(...)`. Esto **evita** por completo `AUTH_PASSWORD_VALIDATORS` (definidos en `settings.py:92-99`), por lo que se aceptan contraseñas como `123`. Además, cualquier campo ausente produce `KeyError`→HTTP 500, y el email no se valida.
- **Escenario de fallo:** un POST sin el campo `email` devuelve 500; un POST con `password=a` crea un usuario con contraseña de un carácter.
- **Recomendación:** migrar el registro a `UserCreationForm` (o un `ModelForm` propio) que ejecute `validate_password()` y valide el email. Con ello se resuelve también SEC-011 para esta vista.

### SEC-004 — Endpoint de datos sin autenticación

- **Ubicación:** `auctions/admin_views.py:420` (`test_admin_dashboard`), ruta en `auctions/urls.py:47` (`test/admin/`).
- **Descripción:** a diferencia del resto de vistas admin (decoradas con `@user_passes_test(is_superuser)`, verificado en `admin_views.py:15-23`) y de las otras vistas `test/*` que sí están protegidas por `DEBUG` en `error_views.py`, esta vista **no tiene decorador de auth ni guard de `DEBUG`** y renderiza `total_listings`, `active_listings`, `total_users` y `total_bids`.
- **Escenario de fallo:** un anónimo visita `/test/admin/` en producción y obtiene los conteos del negocio.
- **Recomendación:** eliminar la vista y su ruta, o al menos protegerla con `@user_passes_test(is_superuser)` y un guard `if not settings.DEBUG: raise Http404`.

### SEC-005 / SEC-006 / SEC-007 — Mutaciones de estado vía GET (CSRF)

- **Ubicación:** `close_auction` (`views.py:176-191`), `watchlist_remove` (`views.py:166-173`, invocado por `window.location.href` en `card.html:23`), `logout` (`views.py:42-44`).
- **Descripción:** el middleware CSRF de Django solo protege métodos "unsafe" (POST/PUT/DELETE). Estas tres vistas cambian estado en GET, por lo que **no** están protegidas contra CSRF. `close_auction` sí verifica propiedad (`request.user == listing.user`, `views.py:180` — correcto contra IDOR), pero el cambio de estado sigue siendo forzable.
- **Escenario de fallo:** una página maliciosa incrusta `<img src="https://sitio/listing/42/close">`; si la víctima (dueña del listing) está autenticada, la subasta se cierra sin su intención. Lo mismo aplica a `logout` y a eliminar de la watchlist.
- **Recomendación:** requerir POST (`@require_POST`) y `{% csrf_token %}` en formularios; convertir los enlaces GET de `card.html:23` y las acciones de admin (`listings.html:166`, `listing_detail.html:114`) en formularios POST.

### SEC-008 — `SECRET_KEY` con fallback inseguro

- **Ubicación:** `commerce/settings.py:14`.
- **Descripción:** `SECRET_KEY = os.getenv("SECRET_KEY", "a-default-secret-key-for-testing-only")`. Si la variable de entorno no está definida en producción, se usa silenciosamente un valor conocido, comprometiendo firmas de sesión, tokens CSRF y `PasswordResetTokenGenerator`.
- **Escenario de fallo:** un despliegue sin `SECRET_KEY` configurada arranca sin error usando la clave pública del repositorio.
- **Recomendación:** exigir la variable en producción: `SECRET_KEY = os.environ["SECRET_KEY"]` cuando `not DEBUG` (dejar el fallback solo para dev/tests). `docker-compose.yml` ya inyecta un valor de desarrollo.

### SEC-009 — `|safe` con datos de BD dentro de `<script>`

- **Ubicación:** `auctions/templates/auctions/admin/analytics.html:242,275,328`, `reports.html:340`, y los divs Plotly de `dashboard.html:130,142,157`.
- **Descripción:** valores derivados de la BD (`market_trends`, `time_analysis`, `bid_analysis`) se interpolan con `|safe` como literales JavaScript. Al ser `repr()`/estructuras Python, no son JSON válido ni están escapados; cualquier string influido por el usuario (p. ej. una categoría o título usados como label) queda sin escapar dentro del `<script>`.
- **Escenario de fallo:** un título/categoría de listing con `</script><script>...` que llegue a un label de gráfico produce ejecución de JS en el navegador del admin.
- **Recomendación:** usar `{{ data|json_script:"id-datos" }}` y leer el JSON desde JS con `JSON.parse(document.getElementById(...).textContent)`, en lugar de `|safe`.

### SEC-010 — Configuración de proxy/HTTPS incompleta

- **Ubicación:** `commerce/settings.py:118-128`.
- **Descripción:** el bloque `if not DEBUG` activa HSTS y cookies seguras, pero faltan `SECURE_SSL_REDIRECT` (forzar HTTPS), `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` (detrás de Heroku/nginx Django no detecta HTTPS y puede caer en bucles de redirección o cookies inseguras) y `CSRF_TRUSTED_ORIGINS` (requerido en Django 4+ para POST HTTPS con dominios personalizados).
- **Escenario de fallo:** con `SESSION_COOKIE_SECURE=True` pero sin `SECURE_PROXY_SSL_HEADER`, Django ve la petición como HTTP y puede no emitir la cookie de sesión; los POST desde un dominio personalizado fallan con "CSRF verification failed".
- **Recomendación:** añadir los tres settings dentro del bloque `if not DEBUG`, tomando `CSRF_TRUSTED_ORIGINS` de una variable de entorno.

## Evidencia

`bandit -r auctions/ commerce/ -ll` — sin hallazgos en código de aplicación (los 13 avisos Low son `B105/B106` en `auctions/tests/` legacy, contraseñas de prueba):

```text
Test results:
	No issues identified.

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 13   (todos en auctions/tests/*, hardcoded test passwords)
		Medium: 0
		High: 0
Total lines of code: 2587
```

`safety check -r requirements.txt` — sin vulnerabilidades conocidas, pero advierte que **todas las dependencias están sin fijar** (rangos `>=`), por lo que safety no analiza versiones flotantes (ver [code-quality.md](code-quality.md), CODE-007):

```text
Found and scanned 10 packages
0 vulnerabilities reported
35 vulnerabilities ignored   (paquetes sin pin: django, gunicorn, psycopg2-binary, ...)
```

## Referencias

- La condición de carrera (SEC-001) y la falta de validación (SEC-002) se complementan con las constraints de BD propuestas en [code-quality.md](code-quality.md) (CODE-005).
- El vector de `<img src>` con URL de usuario (SEC-013) también aparece como problema de UX de imágenes rotas en [ui-ux.md](ui-ux.md) (UX-006).
- La ausencia de tests de concurrencia y de headers de seguridad se detalla en [testing-and-ci.md](testing-and-ci.md) (TEST-001, TEST-005).
