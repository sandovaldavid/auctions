# 🛒 Sitio de Subastas

[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Mobile Responsive](https://img.shields.io/badge/Mobile-Responsive-orange.svg)](https://getbootstrap.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📋 Descripción General

**Sitio de Subastas** es una aplicación web completa que permite a los usuarios participar en subastas en línea. Construida con Django, la plataforma ofrece una experiencia fluida para crear listas de subastas, realizar ofertas competitivas e interactuar con otros usuarios a través de comentarios y listas de seguimiento. La aplicación cuenta con un diseño responsivo que funciona en dispositivos de escritorio y móviles, con componentes de interfaz de usuario cuidadosamente diseñados y una experiencia de usuario moderna.

## ✨ Demo en Vivo

🔗 [Ver Demo en Vivo](https://auction-site-demo.herokuapp.com) (Reemplazar con la URL de despliegue real)

---

## 🚀 Características Principales

### 🔐 Autenticación de Usuarios

-   **Registro, inicio de sesión y cierre de sesión seguros.**
-   **Navegación dinámica** basada en el estado de autenticación.
-   Gestión de perfiles de usuario.
-   Protección de contraseñas y medidas de seguridad.

### 📝 Gestión de Anuncios

-   Crea anuncios de subasta detallados con:
    -   Título y descripción.
    -   Monto de la oferta inicial.
    -   URL de imagen opcional.
    -   Selección de categoría opcional.
-   Control del estado de los anuncios (activos/inactivos).
-   Formularios intuitivos con validación.

### 🏠 Página de Anuncios Activos

-   Navega por todas las subastas actualmente activas.
-   Visualiza los detalles esenciales de los anuncios de un vistazo.
-   Filtra los anuncios por categorías.
-   Diseño de tarjetas responsivo para todos los tamaños de dispositivo.

### 📊 Páginas de Anuncios Detallados

-   Visualización de información completa del anuncio.
-   Oferta actual e historial de ofertas.
-   Sección de comentarios de los usuarios.
-   Botones de gestión de la lista de seguimiento.
-   Funcionalidad de puja con validación.
-   Mecanismo de cierre de subasta para los propietarios de los anuncios.
-   Notificaciones al ganador.

### ⭐ Lista de Seguimiento

-   Colección personalizada de artículos de interés.
-   Funcionalidad de añadir/eliminar con un solo clic.
-   Acceso rápido a los artículos seguidos.
-   Indicadores visuales para los artículos seguidos.

### 🏷️ Categorías

-   Categorías de anuncios organizadas.
-   Filtra los anuncios por categorías específicas.
-   Navega por todas las categorías disponibles.
-   Páginas específicas por categoría.

### 💬 Comentarios

-   Deja comentarios en cualquier anuncio.
-   Visualiza todos los comentarios de los anuncios.
-   Interacción con la comunidad.
-   Información de autor y marca de tiempo.

### ⚙️ Interfaz de Administración

-   Panel de control de gestión integral.
-   Control sobre todos los anuncios, ofertas y comentarios.
-   Capacidades de gestión de usuarios.
-   Funcionalidad de filtrado y búsqueda de datos.

---

## 🛠️ Tecnologías Utilizadas

-   **Backend**: [Django](https://www.djangoproject.com/) (Python) - Framework web robusto.
-   **Frontend**: HTML, CSS, [Bootstrap](https://getbootstrap.com/) - Diseño responsivo.
-   **Base de Datos**: SQLite (desarrollo), PostgreSQL (listo para producción).
-   **Autenticación**: Sistema de autenticación incorporado de Django.
-   **Estilos**: CSS personalizado con diseño responsivo, iconos de Font Awesome.
-   **Despliegue**: Soporte para contenedores Docker.
-   **Control de Versiones**: Git.
-   **Diseño Responsivo**: Media queries y sistema de rejilla de Bootstrap.
-   **Componentes de UI**: Tarjetas, navegación, formularios y alertas personalizadas.

---

## 🔧 Instalación y Configuración

### Prerrequisitos

-   Python 3.10 o superior.
-   Django 5.1.2 o superior.
-   Paquetes de sistema requeridos (Ubuntu):
    ```bash
    sudo apt update
    sudo apt install build-essential libpq-dev python3-dev
    ```

### Configuración Local

1.  **Clona el Repositorio**
    ```bash
    git clone https://github.com/sandovaldavid/project-02-auctions.git
    cd auction-site
    ```

2.  **Instala las Dependencias**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Aplica las Migraciones de la Base de Datos**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4.  **Crea un Superusuario**
    ```bash
    python manage.py createsuperuser
    ```

5.  **Ejecuta el Servidor de Desarrollo**
    ```bash
    python manage.py runserver
    ```

6.  **Accede a la Aplicación**
    Abre [http://localhost:8000](http://localhost:8000) en tu navegador.

### Configuración con Docker

1.  **Construye y Ejecuta con Docker Compose**
    ```bash
    docker compose up --build
    ```

2.  **Accede a la Aplicación**
    Abre [http://localhost:8000](http://localhost:8000) en tu navegador.

---

## 📂 Estructura del Proyecto

```plaintext
auctions/
├── migrations/         # Archivos de migración de la base de datos
├── templates/          # Plantillas HTML para la aplicación
│   ├── auctions/
│   │   ├── layout.html         # Diseño base
│   │   ├── index.html          # Página de anuncios activos
│   │   ├── create.html         # Página para crear anuncios
│   │   ├── listing.html        # Página de detalles del anuncio
│   │   ├── categories.html     # Página de categorías
│   │   └── watchlist.html      # Página de la lista de seguimiento
│   └── auctions/components/    # Componentes de UI reutilizables
│       ├── footer.html         # Pie de página del sitio
│       └── ...                 # Otros componentes
├── static/             # Archivos CSS y JavaScript
│   ├── css/
│   │   ├── auctions/           # Estilos específicos de la página
│   │   ├── components/         # Estilos de los componentes
│   │   └── styles.css          # Estilos base
│   └── js/                     # Archivos JavaScript
├── models.py           # Modelos de datos para la aplicación
├── views.py            # Lógica de la aplicación y vistas
├── urls.py             # Configuración de URLs
├── forms.py            # Formularios de Django
├── context_processors.py # Procesadores de contexto personalizados
└── admin.py            # Configuración de la interfaz de administración
```

---

## 📱 Guía de Uso

1.  **Regístrate e Inicia Sesión**
    -   Crea una nueva cuenta o inicia sesión para acceder a toda la funcionalidad.
    -   Navega a través de la interfaz responsiva.

2.  **Explora los Anuncios**
    -   Explora la página de inicio para ver todas las subastas activas.
    -   Usa los filtros de categoría para encontrar artículos específicos.

3.  **Crea tu Propio Anuncio**
    -   Haz clic en "Crear Anuncio" en el menú de navegación.
    -   Completa el formulario con los detalles de tu artículo.
    -   Publica tu subasta.

4.  **Realiza una Oferta**
    -   Realiza ofertas en los anuncios activos.
    -   Monitorea tus ofertas activas.
    -   Recibe notificaciones si ganas una subasta.

5.  **Gestiona tu Lista de Seguimiento**
    -   Añade artículos interesantes a tu lista de seguimiento.
    -   Elimina artículos según sea necesario.
    -   Accede rápidamente a tus artículos seguidos.

6.  **Interactúa con la Comunidad**
    -   Deja comentarios en los anuncios.
    -   Interactúa con vendedores y otros postores.

---

## 🎨 Características de UI/UX

-   **Diseño Responsivo**: Optimizado para todos los tamaños de pantalla, desde móviles hasta ordenadores de escritorio.
-   **Modo Oscuro/Claro**: Soporte para las preferencias de tema del sistema.
-   **Accesibilidad**: Estados de foco y HTML semántico.
-   **Interfaz Moderna**: Diseño limpio con espaciado y tipografía consistentes.
-   **Navegación Intuitiva**: Rutas de usuario claras a través de la aplicación.
-   **Microinteracciones**: Retroalimentación visual para las acciones del usuario.

---

## 🔄 Endpoints de API

Actualmente, la aplicación no expone APIs públicas, pero utiliza el enrutamiento de URLs de Django para toda la funcionalidad.

---

## 🔒 Características de Seguridad

-   Protección CSRF para todos los formularios.
-   Hashing de contraseñas y autenticación segura.
-   Validación de formularios para prevenir entradas maliciosas.
-   Configuración del middleware de seguridad de Django.

---

## 🚧 Mejoras Futuras

-   [ ] **Actualizaciones en tiempo real** con WebSockets para experiencias de puja en vivo.
-   [ ] Opciones avanzadas de **filtrado de anuncios** (rango de precios, fecha de publicación).
-   [ ] Sistema de **notificaciones por correo electrónico** para actualizaciones de ofertas y cierres de subastas.
-   [ ] Mejoras en la **responsividad móvil y UI/UX**.
-   [ ] Integración de **pasarelas de pago** para subastas finalizadas.
-   [ ] Sistema de **calificaciones y reseñas** de usuarios.
-   [ ] Funcionalidad de **búsqueda mejorada** con autocompletado.
-   [ ] Integración para **compartir en redes sociales**.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! No dudes en enviar un Pull Request.

1.  **Haz un Fork** del repositorio.
2.  Crea tu rama de características (`git checkout -b feature/amazing-feature`).
3.  **Haz Commit** de tus cambios (`git commit -m 'Añade una característica increíble'`).
4.  **Haz Push** a la rama (`git push origin feature/amazing-feature`).
5.  Abre un **Pull Request**.

---

## 🧪 Pruebas

Ejecuta la suite de pruebas para asegurarte de que todo funciona correctamente:

```bash
python manage.py test
```

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto

David Sandoval - [@sandovaldavid](https://github.com/sandovaldavid)

Enlace del Proyecto: [https://github.com/sandovaldavid/project-02-auctions.git](https://github.com/sandovaldavid/project-02-auctions.git)
