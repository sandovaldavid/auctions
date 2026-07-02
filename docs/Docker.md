# Docker — Guía del stack de contenedores

Esta guía documenta el stack Docker real del proyecto: desarrollo local con Docker Compose, la anatomía de la imagen, el despliegue de producción (Compose con nginx/certbot o Heroku container stack) y las imágenes publicadas en GHCR.

Para las convenciones generales del proyecto (ramas, commits, tests) ver [../CLAUDE.md](../CLAUDE.md).

---

## Resumen del stack

| Componente | Definición | Detalle |
|-----------|-----------|---------|
| Imagen web | `Dockerfile` | `python:3.12-slim-bookworm`, Gunicorn, `collectstatic` en build |
| Compose dev | `docker-compose.yml` | Servicios `db` (Postgres 16) + `web` (runserver) |
| Compose prod | `docker-compose.prod.yml` | `db` + `web` (imagen GHCR) + `nginx` + `certbot` |
| Heroku | `heroku.yml` | Build de la imagen `web`, `migrate` en release, Gunicorn en run |
| Registro | GHCR | `ghcr.io/sandovaldavid/auctions` (publicada por CI) |
| Estáticos | WhiteNoise | `CompressedManifestStaticFilesStorage` (ver `commerce/settings.py`) |

---

## Desarrollo local

Levantar Django + PostgreSQL:

```bash
docker compose up --build
```

El servicio `web` aplica migraciones y arranca `runserver` automáticamente (ver el `command` en `docker-compose.yml`). La app queda en http://localhost:8000.

Comandos útiles:

```bash
# Aplicar migraciones manualmente
docker compose exec web python manage.py migrate

# Crear superusuario (para el admin de Django)
docker compose exec web python manage.py createsuperuser

# Ver logs
docker compose logs -f web

# Detener y eliminar contenedores (conserva el volumen de datos)
docker compose down
```

El servicio `db` expone PostgreSQL 16 en el puerto `5432` con la base `auctions_dev` (usuario `auctions`), y monta el volumen `postgres_data` para persistir datos entre reinicios. Incluye un `healthcheck` con `pg_isready`; `web` espera a que la base esté sana (`depends_on: condition: service_healthy`).

---

## Anatomía del `Dockerfile`

```dockerfile
FROM python:3.12-slim-bookworm AS base
```

- **Base slim** (`python:3.12-slim-bookworm`) para reducir tamaño; se instalan `libpq-dev` y `build-essential` para compilar `psycopg2` y luego se limpia el cache de apt.
- **`PYTHONDONTWRITEBYTECODE=1` / `PYTHONUNBUFFERED=1`** — sin `.pyc` y logs sin buffer (mejor para contenedores).
- **`collectstatic --noinput`** en tiempo de build: los estáticos quedan servidos por WhiteNoise desde la propia imagen, sin necesidad de un servidor de archivos separado en dev.
- **Gunicorn** como servidor WSGI: `--workers 3 --timeout 120`, escuchando en `${PORT:-8000}` (Heroku inyecta `PORT`).

> Nota: las dependencias `numpy`/`pandas`/`scikit-learn` viven en `requirements-dev.txt` y **no** se instalan en esta imagen. Los módulos de analítica que las importan fallarían en producción — ver [audits/code-quality.md](audits/code-quality.md) (CODE-002).

---

## Producción con Docker Compose (Oracle VM / self-hosting)

`docker-compose.prod.yml` define el stack completo para auto-hospedaje:

- **`db`** — Postgres 16, configuración vía `.env.prod`, volumen `postgres_data_prod`.
- **`web`** — usa la imagen publicada `ghcr.io/sandovaldavid/auctions:latest` (no reconstruye), monta volúmenes de `staticfiles` y `media`, expone `8000` solo internamente.
- **`nginx`** — `nginx:1.27-alpine` como reverse proxy y terminación TLS en `80`/`443`, sirviendo estáticos/media desde volúmenes compartidos (config en `nginx/nginx.conf`).
- **`certbot`** — emisión y renovación automática de certificados Let's Encrypt (renueva cada 12 h).

```bash
# Requiere un archivo .env.prod con POSTGRES_*, DOMAIN, CERTBOT_EMAIL y las vars de Django
docker compose -f docker-compose.prod.yml up -d
```

Este stack se corresponde con la guía de [oracle-vm-stack.md](oracle-vm-stack.md) para la VM Always-Free de Oracle.

---

## Producción en Heroku (container stack)

`heroku.yml` describe el despliegue actual de producción:

```yaml
build:
  docker:
    web: Dockerfile
release:
  image: web
  command: python manage.py migrate --no-input
run:
  web: gunicorn commerce.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

- La fase **`release`** aplica migraciones automáticamente en cada deploy.
- El deploy lo dispara el workflow `cd-production.yml` en cada push a `main` (build + push a GHCR + `heroku container:push/release`).
- Cambiar la app al stack de contenedores (una sola vez): `heroku stack:set container -a <nombre-app>`.

---

## Imágenes en GHCR

El CI publica la imagen web en GitHub Container Registry:

```bash
# La imagen de producción
docker pull ghcr.io/sandovaldavid/auctions:latest

# También se etiqueta por SemVer y por SHA de commit (ver cd-production.yml)
```

`cd-develop.yml` publicaría la etiqueta `:develop` cuando el stack de staging (Oracle VM/k3s) esté activo; actualmente está deshabilitado (`workflow_dispatch`).

---

## Variables de entorno

Copiar `.env.example` a `.env` (para ejecución sin Compose) o definirlas en `.env.prod` (Compose de producción):

| Variable | Descripción | Default dev |
|---------|-------------|-------------|
| `SECRET_KEY` | Clave secreta de Django | (requerida en prod) |
| `DEBUG` | Modo debug | `False` |
| `DATABASE_URL` | URL de PostgreSQL (`postgres://user:pass@host:5432/db`) | SQLite si no está |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma | `127.0.0.1,localhost` |

> El `docker-compose.yml` de desarrollo inyecta estas variables inline (incluida una `SECRET_KEY` de desarrollo). En producción **nunca** debe usarse el valor por defecto de `SECRET_KEY` — ver [audits/security.md](audits/security.md) (SEC-008).

---

## Troubleshooting

| Síntoma | Causa probable | Acción |
|---------|----------------|--------|
| `web` no arranca, espera a `db` | La base aún no pasa el `healthcheck` | Esperar; revisar `docker compose logs db` |
| `psycopg2` falla al construir | Falta `libpq-dev`/`build-essential` | Ya incluidos en el `Dockerfile`; reconstruir con `--build` |
| Estáticos no se ven | `collectstatic` no corrió o `STATIC_ROOT` vacío | La imagen corre `collectstatic` en build; reconstruir |
| `ModuleNotFoundError: numpy` | Módulo de analítica en imagen de prod | Ver [audits/code-quality.md](audits/code-quality.md) (CODE-002) |
| CSRF/redirect loop tras nginx | Falta `SECURE_PROXY_SSL_HEADER`/`CSRF_TRUSTED_ORIGINS` | Ver [audits/security.md](audits/security.md) (SEC-010) |
