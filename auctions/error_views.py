"""
Vistas personalizadas para manejo de errores
Incluye funcionalidad de debug en desarrollo y páginas personalizadas en producción
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
import traceback
import sys


def custom_404_view(request, exception=None):
    """
    Vista personalizada para error 404
    Muestra información de debug en desarrollo y página personalizada en producción
    """
    context = {
        "debug": settings.DEBUG,
        "request_path": request.path,
        "request_method": request.method,
    }

    # En modo desarrollo, agregar información técnica
    if settings.DEBUG:
        debug_info = f"""
Request Method: {request.method}
Request URL: {request.build_absolute_uri()}
Raised by: {getattr(exception, "__class__", "Unknown")}

Using the URLconf defined in {settings.ROOT_URLCONF}, Django tried these URL patterns:

{_get_url_patterns_info()}

The current path, {request.path}, matched the last one.

You're seeing this error because you have DEBUG = True in your Django settings file. 
Change that to False, and Django will display a standard 404 page.
        """
        context["debug_info"] = debug_info.strip()

    return render(request, "auctions/errors/404.html", context, status=404)


def custom_500_view(request):
    """
    Vista personalizada para error 500
    Muestra información de debug en desarrollo y página personalizada en producción
    """
    context = {
        "debug": settings.DEBUG,
        "request_path": request.path,
        "request_method": request.method,
    }

    # En modo desarrollo, agregar información técnica
    if settings.DEBUG:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            debug_info = f"""
Request Method: {request.method}
Request URL: {request.build_absolute_uri()}
Exception Type: {exc_type.__name__ if exc_type else "Unknown"}
Exception Value: {str(exc_value) if exc_value else "Unknown"}

Traceback:
{traceback.format_exc()}

You're seeing this error because you have DEBUG = True in your Django settings file.
        """
            context["debug_info"] = debug_info.strip()

    return render(request, "auctions/errors/500.html", context, status=500)


def custom_403_view(request, exception=None):
    """
    Vista personalizada para error 403 (Forbidden)
    """
    context = {
        "debug": settings.DEBUG,
        "request_path": request.path,
        "request_method": request.method,
    }

    if settings.DEBUG:
        debug_info = f"""
Request Method: {request.method}
Request URL: {request.build_absolute_uri()}
Exception: {getattr(exception, "__class__", "Unknown")}

You don't have permission to access this resource.
        """
        context["debug_info"] = debug_info.strip()

    return render(request, "auctions/errors/403.html", context, status=403)


def custom_400_view(request, exception=None):
    """
    Vista personalizada para error 400 (Bad Request)
    """
    context = {
        "debug": settings.DEBUG,
        "request_path": request.path,
        "request_method": request.method,
    }

    if settings.DEBUG:
        debug_info = f"""
Request Method: {request.method}
Request URL: {request.build_absolute_uri()}
Exception: {getattr(exception, "__class__", "Unknown")}

Bad Request - The request could not be understood by the server.
        """
        context["debug_info"] = debug_info.strip()

    return render(request, "auctions/errors/400.html", context, status=400)


def _get_url_patterns_info():
    """
    Obtener información sobre los patrones de URL disponibles
    """
    try:
        from django.urls import get_resolver

        resolver = get_resolver()
        patterns = []

        def extract_patterns(url_patterns, prefix=""):
            for pattern in url_patterns:
                if hasattr(pattern, "url_patterns"):
                    # Es un include
                    extract_patterns(
                        pattern.url_patterns, prefix + str(pattern.pattern)
                    )
                else:
                    # Es un patrón de URL
                    patterns.append(
                        f"{prefix}{pattern.pattern} [{getattr(pattern, 'name', 'No name')}]"
                    )

        extract_patterns(resolver.url_patterns)
        return "\n".join(patterns)
    except Exception:
        return "No se pudieron obtener los patrones de URL"


@require_http_methods(["GET"])
def test_404_view(request):
    """
    Vista para probar el error 404 (solo en desarrollo)
    """
    if not settings.DEBUG:
        return HttpResponse(
            "Esta vista solo está disponible en modo desarrollo", status=404
        )

    from django.http import Http404

    raise Http404("Esta es una página de prueba para el error 404")


@require_http_methods(["GET"])
def test_500_view(request):
    """
    Vista para probar el error 500 (solo en desarrollo)
    """
    if not settings.DEBUG:
        return HttpResponse(
            "Esta vista solo está disponible en modo desarrollo", status=404
        )

    raise Exception("Esta es una excepción de prueba para el error 500")


@require_http_methods(["GET"])
def test_403_view(request):
    """
    Vista para probar el error 403 (solo en desarrollo)
    """
    if not settings.DEBUG:
        return HttpResponse(
            "Esta vista solo está disponible en modo desarrollo", status=404
        )

    from django.core.exceptions import PermissionDenied

    raise PermissionDenied("Esta es una excepción de prueba para el error 403")
