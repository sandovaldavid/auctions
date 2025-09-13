"""
Vistas del panel de administración para superusuarios
Dashboard de Business Intelligence para gestión de subastas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Listing, Bid, Comment, User, Watchlist
from .analytics import AuctionAnalytics
from .error_views import test_404_view, test_500_view, test_403_view
import json


def is_superuser(user):
    """Verificar si el usuario es superusuario"""
    return user.is_superuser


@user_passes_test(is_superuser)
def admin_dashboard(request):
    """
    Dashboard principal de administración con métricas y gráficos
    """
    try:
        analytics = AuctionAnalytics()
        dashboard_data = analytics.get_kpi_dashboard_data()

        # Obtener subastas recientes
        recent_listings = Listing.objects.select_related("user").order_by("-created")[
            :10
        ]

        # Obtener pujas recientes
        recent_bids = Bid.objects.select_related("user", "listing").order_by("-id")[:10]

        # Obtener usuarios más activos
        top_users = (
            User.objects.annotate(
                total_activity=Count("bids") + Count("listings") + Count("comments")
            )
            .filter(total_activity__gt=0)
            .order_by("-total_activity")[:5]
        )

        context = {
            "dashboard_data": dashboard_data,
            "recent_listings": recent_listings,
            "recent_bids": recent_bids,
            "top_users": top_users,
            "page_title": "Dashboard de Administración",
        }

        return render(request, "auctions/admin/dashboard.html", context)
    except Exception as e:
        # En caso de error, mostrar una página simple de administración
        context = {
            "page_title": "Dashboard de Administración",
            "error": str(e),
            "dashboard_data": {
                "metrics": {
                    "total_listings": Listing.objects.count(),
                    "active_listings": Listing.objects.filter(active=True).count(),
                    "total_users": User.objects.count(),
                    "total_bids": Bid.objects.count(),
                }
            },
            "recent_listings": [],
            "recent_bids": [],
            "top_users": [],
        }
        return render(request, "auctions/admin/dashboard.html", context)


@user_passes_test(is_superuser)
def admin_analytics(request):
    """
    Página de análisis avanzados y reportes
    """
    analytics = AuctionAnalytics()

    # Análisis por categorías
    category_analysis = analytics.get_category_analysis()

    # Análisis de comportamiento de usuarios
    user_behavior = analytics.get_user_behavior_analysis()

    # Análisis de pujas
    bid_analysis = analytics.get_bid_analysis()

    # Tendencias del mercado
    market_trends = analytics.get_market_trends()

    context = {
        "category_analysis": category_analysis,
        "user_behavior": user_behavior,
        "bid_analysis": bid_analysis,
        "market_trends": market_trends,
        "page_title": "Análisis Avanzados",
    }

    return render(request, "auctions/admin/analytics.html", context)


@user_passes_test(is_superuser)
def admin_listings(request):
    """
    Gestión de subastas con filtros y búsqueda
    """
    listings = Listing.objects.select_related("user").prefetch_related("bids")

    # Filtros
    search_query = request.GET.get("search", "")
    category_filter = request.GET.get("category", "")
    status_filter = request.GET.get("status", "")
    sort_by = request.GET.get("sort", "-created")

    if search_query:
        listings = listings.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(user__username__icontains=search_query)
        )

    if category_filter:
        listings = listings.filter(category=category_filter)

    if status_filter == "active":
        listings = listings.filter(active=True)
    elif status_filter == "inactive":
        listings = listings.filter(active=False)
    elif status_filter == "with_bids":
        listings = listings.filter(bids__isnull=False).distinct()

    listings = listings.order_by(sort_by)

    # Paginación
    paginator = Paginator(listings, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Obtener categorías únicas para el filtro
    categories = (
        Listing.objects.values_list("category", flat=True)
        .distinct()
        .exclude(category="")
    )

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "category_filter": category_filter,
        "status_filter": status_filter,
        "sort_by": sort_by,
        "categories": categories,
        "page_title": "Gestión de Subastas",
    }

    return render(request, "auctions/admin/listings.html", context)


@user_passes_test(is_superuser)
def admin_users(request):
    """
    Gestión de usuarios con estadísticas
    """
    users = User.objects.annotate(
        listings_count=Count("listings"),
        bids_count=Count("bids"),
        comments_count=Count("comments"),
        watchlist_count=Count("watchlist", filter=Q(watchlist__active=True)),
    ).order_by("-date_joined")

    # Filtros
    search_query = request.GET.get("search", "")
    sort_by = request.GET.get("sort", "-date_joined")

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )

    users = users.order_by(sort_by)

    # Paginación
    paginator = Paginator(users, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "sort_by": sort_by,
        "page_title": "Gestión de Usuarios",
    }

    return render(request, "auctions/admin/users.html", context)


@user_passes_test(is_superuser)
def admin_listing_detail(request, listing_id):
    """
    Detalle de una subasta con análisis predictivo
    """
    listing = get_object_or_404(Listing, id=listing_id)
    analytics = AuctionAnalytics()

    # Obtener pujas de la subasta
    bids = listing.bids.select_related("user").order_by("-amount")

    # Obtener comentarios
    comments = listing.comments.select_related("user").order_by("-created")

    # Análisis predictivo
    prediction = analytics.predict_auction_success(listing_id)

    # Estadísticas de la subasta
    listing_stats = {
        "total_bids": bids.count(),
        "unique_bidders": bids.values("user").distinct().count(),
        "price_increase": 0,
        "days_active": (timezone.now() - listing.created).days,
    }

    if listing.current_bid and listing.starting_bid:
        listing_stats["price_increase"] = (
            (listing.current_bid - listing.starting_bid) / listing.starting_bid * 100
        )

    context = {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "prediction": prediction,
        "listing_stats": listing_stats,
        "page_title": f"Detalle: {listing.title}",
    }

    return render(request, "auctions/admin/listing_detail.html", context)


@user_passes_test(is_superuser)
def admin_reports(request):
    """
    Generación de reportes y exportación de datos
    """
    analytics = AuctionAnalytics()

    # Métricas básicas
    basic_metrics = analytics.get_basic_metrics()

    # Análisis temporal
    time_analysis = analytics.get_time_series_data(90)  # Últimos 90 días

    # Análisis de categorías
    category_analysis = analytics.get_category_analysis()

    # Análisis de usuarios
    user_analysis = analytics.get_user_behavior_analysis()

    context = {
        "basic_metrics": basic_metrics,
        "time_analysis": time_analysis,
        "category_analysis": category_analysis,
        "user_analysis": user_analysis,
        "page_title": "Reportes y Exportación",
    }

    return render(request, "auctions/admin/reports.html", context)


@user_passes_test(is_superuser)
def admin_api_metrics(request):
    """
    API endpoint para métricas en tiempo real (AJAX)
    """
    analytics = AuctionAnalytics()
    metrics = analytics.get_basic_metrics()

    return JsonResponse(metrics)


@user_passes_test(is_superuser)
def admin_api_charts(request):
    """
    API endpoint para datos de gráficos (AJAX)
    """
    analytics = AuctionAnalytics()
    chart_type = request.GET.get("type", "trends")

    if chart_type == "trends":
        data = analytics.get_time_series_data(30)
    elif chart_type == "categories":
        data = analytics.get_category_analysis()
    elif chart_type == "bids":
        data = analytics.get_bid_analysis()
    else:
        data = {}

    return JsonResponse(data, safe=False)


@user_passes_test(is_superuser)
def admin_toggle_listing_status(request, listing_id):
    """
    Activar/desactivar una subasta
    """
    if request.method == "POST":
        listing = get_object_or_404(Listing, id=listing_id)
        listing.active = not listing.active
        listing.save()

        status = "activada" if listing.active else "desactivada"
        messages.success(request, f"Subasta {status} exitosamente.")

    return redirect("admin_listing_detail", listing_id=listing_id)


@user_passes_test(is_superuser)
def admin_export_data(request):
    """
    Exportar datos del sistema
    """
    import csv
    from django.http import HttpResponse

    export_type = request.GET.get("type", "listings")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{export_type}_export.csv"'

    writer = csv.writer(response)

    if export_type == "listings":
        writer.writerow(
            [
                "ID",
                "Título",
                "Usuario",
                "Precio Inicial",
                "Precio Actual",
                "Categoría",
                "Activa",
                "Fecha Creación",
            ]
        )
        for listing in Listing.objects.select_related("user"):
            writer.writerow(
                [
                    listing.id,
                    listing.title,
                    listing.user.username,
                    listing.starting_bid,
                    listing.current_bid,
                    listing.category,
                    listing.active,
                    listing.created.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

    elif export_type == "bids":
        writer.writerow(["ID", "Usuario", "Subasta", "Monto", "Fecha"])
        for bid in Bid.objects.select_related("user", "listing"):
            writer.writerow(
                [
                    bid.id,
                    bid.user.username,
                    bid.listing.title,
                    bid.amount,
                    bid.listing.created.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

    elif export_type == "users":
        writer.writerow(
            [
                "ID",
                "Usuario",
                "Email",
                "Nombre",
                "Apellido",
                "Fecha Registro",
                "Es Staff",
                "Es Superusuario",
            ]
        )
        for user in User.objects.all():
            writer.writerow(
                [
                    user.id,
                    user.username,
                    user.email,
                    user.first_name,
                    user.last_name,
                    user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                    user.is_staff,
                    user.is_superuser,
                ]
            )

    return response


def catch_all_404_view(request, path):
    """
    Vista que captura todas las URLs no encontradas y muestra nuestra página 404 personalizada
    """
    from .error_views import custom_404_view

    return custom_404_view(request, None)


def test_admin_dashboard(request):
    """
    Vista de prueba para el dashboard de administración (sin autenticación)
    """
    try:
        context = {
            "page_title": "Dashboard de Administración - Prueba",
            "dashboard_data": {
                "metrics": {
                    "total_listings": Listing.objects.count(),
                    "active_listings": Listing.objects.filter(active=True).count(),
                    "total_users": User.objects.count(),
                    "total_bids": Bid.objects.count(),
                }
            },
            "recent_listings": [],
            "recent_bids": [],
            "top_users": [],
        }
        return render(request, "auctions/admin/dashboard.html", context)
    except Exception as e:
        return render(request, "auctions/errors/500.html", {"error": str(e)})
