# Oracle Cloud VM — Self-Hosting Stack

> Oracle Cloud Always Free: 4 vCPU ARM Ampere A1, 24 GB RAM, 200 GB SSD  
> OS: Ubuntu 22.04 LTS (aarch64)

Esta guía describe cómo instalar y configurar el stack completo de herramientas para auto-hospedar múltiples proyectos de portfolio (Django, Node, etc.) en tu VM de Oracle de forma gratuita y permanente.

---

## Arquitectura General

```
Internet → IP Pública → Traefik v3 (Reverse Proxy + SSL)
                           │
              ┌────────────┼────────────┐
              │            │            │
          Auctions    GlitchTip     Grafana
          (Django)   (Error Track)  (Metrics)
              │
           PostgreSQL + Redis
```

**Opciones de orchestration:**
- **Opción A (Recomendada):** k3s + Helm charts — para múltiples proyectos y GitOps con Argo CD
- **Opción B (Más simple):** Docker Compose + Portainer CE — si prefieres menos complejidad

---

## Prerrequisitos

```bash
# Conectarse a la VM
ssh ubuntu@<IP_PUBLICA>

# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Herramientas base
sudo apt install -y curl wget git htop jq unzip
```

### Abrir puertos en Oracle Cloud
En Oracle Console → Networking → VCN → Security Lists, agregar reglas de entrada para:
- TCP 80 (HTTP)
- TCP 443 (HTTPS)
- TCP 6443 (k3s API — solo si necesitas kubectl remoto)

También en el firewall de Ubuntu:
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

---

## Opción A: k3s + Argo CD (GitOps)

### 1. Instalar k3s

```bash
# Instalar k3s (ARM64 compatible)
curl -sfL https://get.k3s.io | sh -s - \
  --disable traefik \
  --write-kubeconfig-mode 644

# Verificar
kubectl get nodes

# Configurar kubectl local (opcional)
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER ~/.kube/config
```

### 2. Instalar Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 3. Instalar Traefik v3 (Ingress + SSL)

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update

# Crear namespace
kubectl create namespace traefik

# values-traefik.yaml
cat > values-traefik.yaml <<EOF
deployment:
  replicas: 1
ingressRoute:
  dashboard:
    enabled: false
ports:
  web:
    redirectTo:
      port: websecure
  websecure:
    tls:
      enabled: true
      certResolver: letsencrypt
additionalArguments:
  - --certificatesresolvers.letsencrypt.acme.email=tu@email.com
  - --certificatesresolvers.letsencrypt.acme.storage=/data/acme.json
  - --certificatesresolvers.letsencrypt.acme.tlschallenge=true
persistence:
  enabled: true
  storageClass: local-path
  size: 256Mi
EOF

helm install traefik traefik/traefik \
  --namespace traefik \
  --values values-traefik.yaml
```

### 4. Instalar cert-manager (alternativa a ACME integrado)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# Verificar
kubectl get pods -n cert-manager

# ClusterIssuer para Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: tu@email.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: traefik
EOF
```

### 5. Instalar Argo CD (GitOps)

```bash
kubectl create namespace argocd

kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Exponer UI via Ingress (crear IngressRoute de Traefik)
kubectl apply -f - <<EOF
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: argocd
  namespace: argocd
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(\`argocd.tudominio.com\`)
      kind: Rule
      services:
        - name: argocd-server
          port: 443
  tls:
    certResolver: letsencrypt
EOF

# Password inicial
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
```

**Conectar Argo CD con GitHub:**
En la UI de Argo CD → Settings → Repositories → Connect Repo
- URL: `https://github.com/sandovaldavid/auctions`
- Tipo: HTTPS con GitHub App Token o Personal Access Token

**Crear Application para staging:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: auctions-staging
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/sandovaldavid/auctions
    targetRevision: develop
    path: k8s/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## Opción B: Docker Compose + Portainer (Más simple)

```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Instalar Portainer CE
docker volume create portainer_data
docker run -d \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

# Acceder en: https://<IP>:9443
```

---

## Stack de Herramientas

### GlitchTip — Error Tracking (Alternativa Open Source a Sentry)

```bash
# docker-compose.glitchtip.yml
mkdir -p ~/glitchtip && cd ~/glitchtip
cat > docker-compose.yml <<'EOF'
version: "3"
x-environment: &default-environment
  DATABASE_URL: postgres://glitchtip:glitchtip@postgres:5432/glitchtip
  SECRET_KEY: cambia-esto-por-algo-seguro
  EMAIL_URL: consolemail://
  GLITCHTIP_DOMAIN: https://glitchtip.tudominio.com
  DEFAULT_FROM_EMAIL: glitchtip@tudominio.com
  CELERY_WORKER_CONCURRENCY: 2

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: glitchtip
      POSTGRES_USER: glitchtip
      POSTGRES_PASSWORD: glitchtip
    volumes:
      - glitchtip_pg:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    image: glitchtip/glitchtip:latest
    environment: *default-environment
    depends_on: [postgres, redis]
    restart: unless-stopped

  worker:
    image: glitchtip/glitchtip:latest
    command: celery -A glitchtip worker -B -l INFO
    environment: *default-environment
    depends_on: [postgres, redis]
    restart: unless-stopped

volumes:
  glitchtip_pg:
EOF

docker compose up -d
```

**Integrar con Django:**
```bash
pip install sentry-sdk
```
```python
# En settings.py
import sentry_sdk
sentry_sdk.init(
    dsn="https://<key>@glitchtip.tudominio.com/<project-id>",
    traces_sample_rate=0.1,
)
```

### Grafana + Prometheus + Loki — Observabilidad

```bash
mkdir -p ~/monitoring && cd ~/monitoring
cat > docker-compose.yml <<'EOF'
version: "3"
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: cambia-esto
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

  loki:
    image: grafana/loki:latest
    restart: unless-stopped

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail.yml:/etc/promtail/config.yml
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
EOF

# prometheus.yml básico
cat > prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
EOF

docker compose up -d
```

**Dashboards recomendados en Grafana (importar por ID):**
- `1860` — Node Exporter Full (métricas del sistema)
- `9628` — PostgreSQL Database
- `7639` — Django Prometheus

### Uptime Kuma — Monitoreo de Disponibilidad

```bash
docker run -d \
  --restart=always \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  --name uptime-kuma \
  louislam/uptime-kuma:latest

# Acceder en http://<IP>:3001
```

Configurar monitores para:
- `https://tudominio.com` — Django prod
- `https://staging.tudominio.com` — Staging
- `https://argocd.tudominio.com` — Argo CD
- PostgreSQL TCP monitor

Alertas via: Telegram, Discord, Email, Webhook

### MinIO — Object Storage S3-Compatible

```bash
docker run -d \
  --name minio \
  --restart unless-stopped \
  -p 9000:9000 \
  -p 9001:9001 \
  -v minio_data:/data \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=cambia-esto-min-8-chars \
  quay.io/minio/minio server /data --console-address ":9001"
```

**Integrar con Django (media files en producción):**
```bash
pip install django-storages boto3
```
```python
# settings.py (prod)
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = os.getenv("MINIO_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = "auctions-media"
AWS_S3_ENDPOINT_URL = "https://minio.tudominio.com"
```

### Infisical — Gestión de Secretos

```bash
# Instalar Infisical CLI
curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo bash
sudo apt install -y infisical

# Inicializar en el proyecto
infisical init
# Seleccionar el workspace y environment

# Correr Django con secretos de Infisical
infisical run -- python manage.py runserver
```

**O usar self-hosted Infisical:**
```bash
# Ver: https://infisical.com/docs/self-hosting/deployment-options/standalone-infisical
```

### Adminer — UI para PostgreSQL

```bash
docker run -d \
  --name adminer \
  --restart unless-stopped \
  -p 8080:8080 \
  adminer:latest
```

---

## Agregar Proyectos de Portfolio

Cada proyecto adicional sigue este patrón:

1. **Crear namespace** en k3s: `kubectl create namespace mi-proyecto`
2. **Crear manifiestos** en `k8s/<proyecto>/` con Deployment + Service + IngressRoute
3. **Registrar en Argo CD** como nueva Application apuntando a la rama y path
4. **Configurar secrets** con Infisical o Kubernetes Secrets
5. **Agregar dominio** al certificado TLS o crear nuevo IngressRoute

**Recursos estimados por proyecto Django típico:**
- CPU: ~100-200m (milicores)
- RAM: ~256-512 MB
- Con 24 GB RAM disponibles: ~20-40 proyectos pequeños sin problemas

---

## Resumen de Recursos

| Servicio | RAM | CPU (milicores) |
|---------|-----|-----------------|
| k3s sistema | ~512 MB | 200m |
| Traefik | ~64 MB | 50m |
| Argo CD | ~512 MB | 200m |
| GlitchTip | ~512 MB | 200m |
| Grafana | ~256 MB | 100m |
| Prometheus | ~256 MB | 100m |
| Loki | ~256 MB | 100m |
| Uptime Kuma | ~128 MB | 50m |
| PostgreSQL | ~1 GB | 500m |
| Redis | ~128 MB | 50m |
| MinIO | ~256 MB | 100m |
| Apps (x4) | ~1-2 GB | 400m |
| **Total** | **~5-7 GB** | **~2 vCPU** |

Queda 17+ GB RAM libre para más proyectos o picos de tráfico.

---

## Próximos Pasos

1. [ ] Registrar un dominio (Namecheap, Cloudflare — ~$10/año)
2. [ ] Configurar DNS apuntando a la IP pública de la VM
3. [ ] Instalar k3s y Traefik
4. [ ] Instalar Argo CD y conectar con el repo
5. [ ] Desplegar GlitchTip y conectar con Django (sentry-sdk)
6. [ ] Instalar Grafana + Prometheus
7. [ ] Configurar Uptime Kuma con alertas
8. [ ] Migrar de Heroku cuando se agoten los créditos
