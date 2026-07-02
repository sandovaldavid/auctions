# Tarea: `chore/settings-hardening` — Endurecer configuración de producción

> **Prioridad:** 3 (Medio) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/security.md](../audits/security.md)

## Objetivo

Completar la configuración de seguridad de Django para producción: forzado de HTTPS y detección correcta tras proxy, orígenes CSRF confiables, logging, y ajustes de cookies/headers. Ninguno es explotable por sí solo, pero juntos cierran la superficie de despliegue.

## Rama

```bash
git checkout develop && git pull
git checkout -b chore/settings-hardening
```

## Hallazgos a resolver

- [ ] **SEC-010** — Faltan `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS` (`commerce/settings.py:118-128`)
- [ ] **SEC-012** — Sin configuración `LOGGING`
- [ ] **SEC-015** — `SECURE_BROWSER_XSS_FILTER` obsoleto (`commerce/settings.py:120`)
- [ ] **SEC-016** — Cookies: sin `SESSION_COOKIE_HTTPONLY` explícito ni `SESSION_COOKIE_AGE`
- [ ] **SEC-017** — `except Exception` con `str(e)` al contexto de plantilla (fuga de detalles)

## Instrucciones / recomendaciones

1. **SEC-010.** Dentro del bloque `if not DEBUG` de `settings.py`, añadir:
   ```python
   SECURE_SSL_REDIRECT = True
   SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
   CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
   ```
   `SECURE_PROXY_SSL_HEADER` es imprescindible tras Heroku/nginx para que Django detecte HTTPS y no entre en bucles de redirección ni emita cookies inseguras.

2. **SEC-012.** Añadir un `LOGGING` dict con handler a consola (Heroku captura stdout) y nivel configurable por env. Sirve también para dejar de silenciar los fallos de analítica (ver `fix/analytics-postgres`).

3. **SEC-015.** Eliminar `SECURE_BROWSER_XSS_FILTER` (el header `X-XSS-Protection` está desaconsejado por los navegadores modernos).

4. **SEC-016.** `SESSION_COOKIE_HTTPONLY = True` explícito y un `SESSION_COOKIE_AGE` razonable.

5. **SEC-017.** No pasar `str(e)` a la plantilla; loguear la excepción y mostrar un mensaje genérico.

## Tests requeridos

- **TEST-005:** test de cabeceras de seguridad con `DEBUG=False` (HSTS, `X-Frame-Options`, `Secure` en cookies, redirección SSL).

## Verificación

```bash
python manage.py check --deploy   # no debe reportar los warnings corregidos
pytest tests/integration/ -q
```

## Commits sugeridos

```
chore(commerce): add SSL redirect, proxy header and trusted origins
chore(commerce): add production logging configuration
chore(commerce): tighten session cookie settings
```

## Criterios de done

- [ ] `manage.py check --deploy` sin los warnings relevantes
- [ ] Test de cabeceras de seguridad verde
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
