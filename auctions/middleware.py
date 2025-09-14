"""
Middleware personalizado para manejo de errores
Intercepta errores 404 y usa nuestros handlers personalizados
"""

from django.http import HttpResponseNotFound
from django.conf import settings
from django.urls import resolve, Resolver404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
import traceback
import sys


class CustomErrorHandlerMiddleware:
    """
    Middleware que intercepta errores y usa nuestros handlers personalizados
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Procesar excepciones y usar nuestros handlers personalizados
        """
        if (
            hasattr(settings, "USE_CUSTOM_ERROR_HANDLERS")
            and settings.USE_CUSTOM_ERROR_HANDLERS
        ):
            if isinstance(exception, Resolver404):
                return self._handle_404(request, exception)
            elif isinstance(exception, PermissionDenied):
                return self._handle_403(request, exception)
            else:
                return self._handle_500(request, exception)
        return None

    def _handle_404(self, request, exception):
        """
        Manejar error 404 con nuestro handler personalizado
        """
        from .error_views import custom_404_view

        return custom_404_view(request, exception)

    def _handle_403(self, request, exception):
        """
        Manejar error 403 con nuestro handler personalizado
        """
        from .error_views import custom_403_view

        return custom_403_view(request, exception)

    def _handle_500(self, request, exception):
        """
        Manejar error 500 con nuestro handler personalizado
        """
        from .error_views import custom_500_view

        return custom_500_view(request, exception)


class Custom404Middleware:
    """
    Middleware específico para interceptar errores 404
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Si la respuesta es 404 y tenemos handlers personalizados habilitados
        if (
            response.status_code == 404
            and hasattr(settings, "USE_CUSTOM_ERROR_HANDLERS")
            and settings.USE_CUSTOM_ERROR_HANDLERS
        ):
            # Usar nuestro handler personalizado
            from .error_views import custom_404_view

            return custom_404_view(request, None)

        return response
