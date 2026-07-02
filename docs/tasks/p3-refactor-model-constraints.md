# Tarea: `refactor/model-constraints` — Constraints e índices de modelo

> **Prioridad:** 3 (Medio) · **Rama base:** `develop` · **Merge:** Squash and merge · **Estado:** Pendiente
> **Detalle de hallazgos:** [../audits/code-quality.md](../audits/code-quality.md) · [../audits/performance.md](../audits/performance.md)

## Objetivo

Llevar a la base de datos las garantías que hoy solo viven (o no viven) en código: `on_delete` correcto en `winner`, constraints de integridad, unicidad de watchlist, unicidad de título, y los índices de las columnas de filtro/orden calientes. Una sola migración cubre constraints e índices.

## Rama

```bash
git checkout develop && git pull
git checkout -b refactor/model-constraints
```

## Hallazgos a resolver

- [ ] **CODE-003** — `Listing.winner` con `on_delete=CASCADE` (`auctions/models.py:23-29`)
- [ ] **CODE-005** — Modelos sin `Meta`: sin índices, constraints, `unique_together`
- [ ] **CODE-006** — Unicidad de `title` solo en el form (TOCTOU, `auctions/forms.py:30-36`)
- [ ] **PERF-006** — Sin índices en `active`, `category`, `created`, `amount`

## Instrucciones / recomendaciones

1. **CODE-003.** Cambiar `winner` a `on_delete=models.SET_NULL` (ya es `null=True, blank=True`).

2. **CODE-005 + PERF-006.** Añadir `class Meta` a los modelos:
   ```python
   class Meta:
       indexes = [
           models.Index(fields=["active"]),
           models.Index(fields=["category"]),
           models.Index(fields=["-created"]),
       ]
       constraints = [
           models.CheckConstraint(check=Q(starting_bid__gte=0), name="starting_bid_gte_0"),
       ]
   ```
   Para `Watchlist`: `UniqueConstraint(fields=["user", "listing"], name="uniq_watchlist_user_listing")`. Para `Bid`: `CheckConstraint(amount__gt=0)`.

3. **CODE-006.** Añadir `unique=True` a `Listing.title` en el modelo (respaldo de BD para la validación del form, que deja de ser un TOCTOU). Valorar si la unicidad de título es realmente deseable de negocio antes de imponerla; si lo es, la constraint de BD es la fuente de verdad y el form solo da el mensaje amigable.

4. Generar la migración: `python manage.py makemigrations auctions`. Revisar que no rompa datos existentes (p. ej. títulos duplicados previos si se impone `unique`).

## Tests requeridos

- Test de que un `Bid`/`starting_bid` inválido es rechazado por la BD (`IntegrityError`).
- Test de que no se pueden crear dos `Watchlist` con el mismo `(user, listing)`.
- Test de que borrar un usuario ganador **no** borra el listing (queda `winner=NULL`).

## Verificación

```bash
python manage.py makemigrations --check --dry-run   # debe existir la migración
pytest tests/unit/test_models.py -q
mypy auctions/
```

## Commits sugeridos

```
refactor(auctions): set winner on_delete to SET_NULL
refactor(auctions): add model indexes and check constraints
refactor(auctions): enforce unique watchlist and listing title at DB
```

## Criterios de done

- [ ] Migración creada y aplicada sin pérdida de datos
- [ ] Constraints/índices/unicidad verificados por test
- [ ] `pr-validate` en verde; PR a `develop`; fila actualizada en el [tablero](README.md)
