from django.urls import path

from . import views
from . import admin_views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_auction", views.new_auctions, name="new_auction"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    # skipcq: FLK-E501
    path(
        "Watchlist_remove/<int:listing_id>",
        views.watchlist_remove,
        name="watchlist_remove",
    ),
    path("listing/<int:listing_id>/close", views.close_auction, name="close_auction"),
    path("categories", views.categories, name="categories"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    # Admin Panel URLs
    path("admin/dashboard", admin_views.admin_dashboard, name="admin_dashboard"),
    path("admin/analytics", admin_views.admin_analytics, name="admin_analytics"),
    path("admin/listings", admin_views.admin_listings, name="admin_listings"),
    path("admin/users", admin_views.admin_users, name="admin_users"),
    path("admin/reports", admin_views.admin_reports, name="admin_reports"),
    path(
        "admin/listing/<int:listing_id>",
        admin_views.admin_listing_detail,
        name="admin_listing_detail",
    ),
    path(
        "admin/listing/<int:listing_id>/toggle",
        admin_views.admin_toggle_listing_status,
        name="admin_toggle_listing_status",
    ),
    path("admin/export", admin_views.admin_export_data, name="admin_export_data"),
    # API endpoints for AJAX
    path("admin/api/metrics", admin_views.admin_api_metrics, name="admin_api_metrics"),
    path("admin/api/charts", admin_views.admin_api_charts, name="admin_api_charts"),
    # URLs de prueba para errores (solo en desarrollo)
    path("test/404/", admin_views.test_404_view, name="test_404"),
    path("test/500/", admin_views.test_500_view, name="test_500"),
    path("test/403/", admin_views.test_403_view, name="test_403"),
    path("test/admin/", admin_views.test_admin_dashboard, name="test_admin"),
    # Capturar todas las URLs no encontradas (debe estar al final)
    path("<path:path>", admin_views.catch_all_404_view, name="catch_all_404"),
]
