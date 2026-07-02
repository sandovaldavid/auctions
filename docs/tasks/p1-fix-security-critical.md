# Tarea: `fix/security-critical` — Correcciones críticas de seguridad

> **Prioridad:** 1 (Crítico) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/security.md](../audits/security.md) · [../audits/code-quality.md](../audits/code-quality.md)

## Objetivo

Cerrar los defectos de seguridad explotables de la app: la condición de carrera con dinero en las pujas, las mutaciones de estado vía GET (CSRF), el registro que evita los validadores de contraseña, la `SECRET_KEY` con fallback inseguro y los 500 por acceso crudo a `request.POST`. Es prioridad 1 porque son explotables por un tercero y algunos afectan a la integridad del dinero.

## Rama

```bash
git checkout develop && git pull
git checkout -b fix/security-critical
```

## Hallazgos a resolver

- [ ] **SEC-001** — Condición de carrera en `place_bid` (`auctions/models.py:40-45`)
- [ ] **SEC-002** — `place_bid` acepta pujas por debajo de `starting_bid`
- [ ] **SEC-003** — `register` omite `AUTH_PASSWORD_VALIDATORS` (`auctions/views.py:47-72`)
- [ ] **SEC-005** — `close_auction` cambia estado en GET (`auctions/views.py:176-191`)
- [ ] **SEC-006** — `watchlist_remove` muta estado en GET (`auctions/views.py:166-173`)
- [ ] **SEC-007** — `logout` acepta GET (`auctions/views.py:42-44`)
- [ ] **SEC-008** — `SECRET_KEY` con fallback hardcodeado (`commerce/settings.py:14`)
- [ ] **SEC-011** — `login`/`register` leen `request.POST["campo"]` sin `.get()` → 500
- [ ] **CODE-004** — `.get()` desnudos en `watchlist`/`watchlist_remove` → 500

## Instrucciones / recomendaciones

Orden sugerido (de mayor a menor riesgo):

1. **SEC-001 + SEC-002 (juntos).** Envolver la lectura-modificación-escritura de `place_bid` en `transaction.atomic()` con `select_for_update()`, y usar `floor = current_bid or starting_bid` como piso de validación:

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

2. **SEC-003 + SEC-011 (registro).** Reemplazar el `request.POST` crudo por `UserCreationForm` (o un `ModelForm` propio) que ejecute `validate_password()` y valide el email. Esto elimina de golpe el bypass de validadores y los `KeyError`→500 de esa vista.

3. **SEC-005/006/007 (GET→POST).** Decorar `close_auction`, `watchlist_remove` y `logout` con `@require_POST`; convertir los disparadores en el frontend a formularios POST con `{% csrf_token %}` (el enlace GET de `card.html:23` y las acciones admin). `close_auction` ya valida propiedad (`views.py:180`) — mantener esa comprobación.

4. **SEC-008.** Exigir `SECRET_KEY` cuando `not DEBUG`: `os.environ["SECRET_KEY"]` en producción, dejando el fallback solo para dev/tests.

5. **CODE-004 + SEC-011 restante.** Sustituir los `.get()` por `get_object_or_404` y `request.POST.get("campo")`.

Gotcha: `@require_POST` en `logout` implica que cualquier enlace/botón de logout del template debe ser un `<form method="post">`.

## Tests requeridos

- Test de concurrencia para `place_bid` (**TEST-001**): dos pujas partiendo del mismo `current_bid` no pueden ambas tener éxito. Usar `TransactionTestCase`.
- Test de que una primera puja por debajo de `starting_bid` es rechazada (SEC-002).
- Test de que `register` rechaza contraseñas débiles (SEC-003).
- Test de que GET a `close_auction`/`watchlist_remove`/`logout` no muta estado (405).

## Verificación

```bash
pytest tests/unit/test_models.py tests/integration/ -q
bandit -r auctions/ -ll
ruff check . && black --check . && mypy auctions/
```

## Commits sugeridos

```
fix(auctions): guard place_bid with transaction and select_for_update
fix(auctions): reject bids below starting price
fix(auctions): validate registration with UserCreationForm
fix(auctions): require POST for close_auction, watchlist_remove and logout
fix(commerce): require SECRET_KEY in production
fix(auctions): use get_object_or_404 and POST.get in views
```

## Criterios de done

- [ ] Todos los checkboxes de hallazgos marcados
- [ ] Tests nuevos verdes; cobertura ≥ 70%
- [ ] `pr-validate` en verde
- [ ] PR a `develop` con "Squash and merge"; fila actualizada en el [tablero](README.md)
