from decimal import Decimal

import pytest
from django.urls import reverse

from tests.conftest import BidFactory, ListingFactory


@pytest.mark.django_db
class TestAdminAccessControl:
    def test_admin_dashboard_requires_login(self, client):
        response = client.get(reverse("admin_dashboard"))
        assert response.status_code == 302
        assert "/login" in response.url

    def test_admin_dashboard_requires_superuser(self, client, user):
        client.force_login(user)
        response = client.get(reverse("admin_dashboard"))
        assert response.status_code == 302
        assert "/login" in response.url


@pytest.mark.django_db
class TestAdminDashboardAndAnalytics:
    def test_admin_dashboard_renders_for_superuser(self, client, superuser, listing):
        BidFactory(listing=listing)
        client.force_login(superuser)
        response = client.get(reverse("admin_dashboard"))
        assert response.status_code == 200

    def test_admin_analytics_renders(self, client, superuser, listing):
        BidFactory(listing=listing, amount=Decimal("15.00"))
        client.force_login(superuser)
        response = client.get(reverse("admin_analytics"))
        assert response.status_code == 200

    def test_admin_reports_renders(self, client, superuser, listing):
        client.force_login(superuser)
        response = client.get(reverse("admin_reports"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminListings:
    def test_admin_listings_renders(self, client, superuser, listing):
        client.force_login(superuser)
        response = client.get(reverse("admin_listings"))
        assert response.status_code == 200
        assert listing.title.encode() in response.content

    def test_admin_listings_search_filter(self, client, superuser, listing):
        client.force_login(superuser)
        response = client.get(reverse("admin_listings"), {"search": listing.title})
        assert response.status_code == 200
        assert listing.title.encode() in response.content

    def test_admin_listings_category_and_status_filters(self, client, superuser):
        ListingFactory(category="Books", active=True)
        ListingFactory(category="Toys", active=False)
        client.force_login(superuser)

        response = client.get(
            reverse("admin_listings"), {"category": "Books", "status": "active"}
        )
        assert response.status_code == 200

        response = client.get(reverse("admin_listings"), {"status": "inactive"})
        assert response.status_code == 200

        response = client.get(reverse("admin_listings"), {"status": "with_bids"})
        assert response.status_code == 200

    def test_admin_listing_detail_renders(self, client, superuser, listing):
        BidFactory(listing=listing)
        client.force_login(superuser)
        response = client.get(reverse("admin_listing_detail", args=[listing.id]))
        assert response.status_code == 200

    def test_admin_toggle_listing_status(self, client, superuser, listing):
        client.force_login(superuser)
        was_active = listing.active
        response = client.post(
            reverse("admin_toggle_listing_status", args=[listing.id])
        )
        assert response.status_code == 302
        listing.refresh_from_db()
        assert listing.active is not was_active


@pytest.mark.django_db
class TestAdminUsers:
    def test_admin_users_renders(self, client, superuser, user):
        client.force_login(superuser)
        response = client.get(reverse("admin_users"))
        assert response.status_code == 200
        assert user.username.encode() in response.content

    def test_admin_users_search_filter(self, client, superuser, user):
        client.force_login(superuser)
        response = client.get(reverse("admin_users"), {"search": user.username})
        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminApiEndpoints:
    def test_admin_api_metrics(self, client, superuser, listing):
        client.force_login(superuser)
        response = client.get(reverse("admin_api_metrics"))
        assert response.status_code == 200
        assert response.json()["total_listings"] >= 1

    @pytest.mark.parametrize("chart_type", ["trends", "categories", "bids", "unknown"])
    def test_admin_api_charts(self, client, superuser, listing, chart_type):
        client.force_login(superuser)
        response = client.get(reverse("admin_api_charts"), {"type": chart_type})
        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminExportData:
    @pytest.mark.parametrize("export_type", ["listings", "bids", "users"])
    def test_admin_export_data(self, client, superuser, listing, export_type):
        BidFactory(listing=listing)
        client.force_login(superuser)
        response = client.get(reverse("admin_export_data"), {"type": export_type})
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"


@pytest.mark.django_db
def test_test_admin_dashboard_view_renders(client):
    response = client.get(reverse("test_admin"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_catch_all_404_view(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
