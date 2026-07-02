# Tarea: `fix/admin-routing` — Endpoint admin sin autenticación

> **Prioridad:** 2 (Alto) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/security.md](../audits/security.md)

## Objetivo

Cerrar la fuga de datos de negocio a usuarios anónimos a través de `test_admin_dashboard`, una vista de prueba que quedó expuesta sin autenticación ni guard de `DEBUG`. Rápida de resolver (un solo hallazgo).

## Rama

```bash
git checkout develop && git pull
git checkout -b fix/admin-routing
```

## Hallazgos a resolver

- [ ] **SEC-004** — `test_admin_dashboard` sin auth ni guard `DEBUG` (`auctions/admin_views.py:420`, ruta en `auctions/urls.py:47`)

## Instrucciones / recomendaciones

Opción recomendada: **eliminar** la vista `test_admin_dashboard` (`admin_views.py:420`) y su ruta `test/admin/` (`urls.py:47`), ya que es una vista de prueba que no debería existir en producción.

Si se quiere conservar para desarrollo, protegerla con el mismo patrón que el resto del panel más un guard de `DEBUG`:

```python
from django.conf import settings
from django.http import Http404
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(is_superuser)
def test_admin_dashboard(request):
    if not settings.DEBUG:
        raise Http404
    ...
```

Nota relacionada (no bloqueante, va en `chore/frontend-consistency`, SEC-018): las páginas de error enlazan a `admin_dashboard`, revelando la URL del panel a anónimos.

## Verificación

```bash
pytest tests/integration/ -q
# Comprobar manualmente que GET /test/admin/ devuelve 404 (o requiere superusuario)
```

Añadir un test de integración: GET `/test/admin/` como anónimo → 404/403.

## Commits sugeridos

```
fix(auctions): remove unauthenticated test admin dashboard view
```

## Criterios de done

- [ ] SEC-004 resuelto; `/test/admin/` ya no expone datos a anónimos
- [ ] Test que lo verifica; cobertura ≥ 70%
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
