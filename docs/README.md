# Documentación — Sitio de Subastas

Índice de la documentación del proyecto. Para las convenciones de desarrollo (stack, ramas, commits, calidad, tests) ver [../CLAUDE.md](../CLAUDE.md); para la visión general y la instalación ver [../README.md](../README.md).

## Guías

| Documento | Descripción | Audiencia |
|-----------|-------------|-----------|
| [Docker.md](Docker.md) | Stack de contenedores: desarrollo local, imagen, producción (Compose + nginx/certbot y Heroku), GHCR | Desarrollo / DevOps |
| [oracle-vm-stack.md](oracle-vm-stack.md) | Auto-hospedaje en la VM Always-Free de Oracle (k3s + Argo CD o Docker Compose + Portainer) y stack de observabilidad | DevOps / Infra |

## Auditoría del proyecto

Revisión estática completa (2026-07-02, commit `784f51a`): 70 hallazgos con `archivo:línea`, severidad y roadmap de remediación.

| Documento | Descripción |
|-----------|-------------|
| [audits/README.md](audits/README.md) | Resumen ejecutivo: metodología, taxonomía, conteos por área, top 10 y roadmap de PRs |
| [audits/security.md](audits/security.md) | Seguridad (18): condición de carrera en pujas, CSRF vía GET, registro sin validadores, XSS |
| [audits/code-quality.md](audits/code-quality.md) | Calidad de código (10): analítica rota en Postgres, dependencias ausentes, modelos sin constraints |
| [audits/accessibility.md](audits/accessibility.md) | Accesibilidad y contraste (14): variables CSS rotas, 11 pares que fallan WCAG AA, skip-link ausente |
| [audits/performance.md](audits/performance.md) | Rendimiento (8): N+1, conteos multiplicados, agregaciones en Python, índices ausentes |
| [audits/ui-ux.md](audits/ui-ux.md) | UI/UX (12): UI muerta, inconsistencias de versión/formato, acción destructiva sin confirmación |
| [audits/testing-and-ci.md](audits/testing-and-ci.md) | Tests y CI/CD (8): cobertura ciega en módulos frágiles, suite legacy duplicada, gaps de CI |
