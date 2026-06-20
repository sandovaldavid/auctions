import pytest
from django.urls import reverse

from auctions.models import Watchlist
from tests.conftest import WatchlistFactory


@pytest.mark.django_db
class TestWatchlistViews:
    def test_watchlist_requires_login(self, client, listing):
        response = client.get(reverse("watchlist", args=[listing.id]))
        assert response.status_code == 302
        assert "/login" in response.url

    def test_watchlist_add(self, client, user, listing):
        client.force_login(user)
        response = client.post(reverse("watchlist", args=[listing.id]))
        assert response.status_code == 302
        assert Watchlist.objects.filter(
            user=user, listing=listing, active=True
        ).exists()

    def test_watchlist_toggle_off(self, client, user, listing):
        WatchlistFactory(user=user, listing=listing, active=True)
        client.force_login(user)
        # POST again toggles it off
        client.post(reverse("watchlist", args=[listing.id]))
        item = Watchlist.objects.get(user=user, listing=listing)
        assert item.active is False

    def test_watchlist_toggle_back_on(self, client, user, listing):
        WatchlistFactory(user=user, listing=listing, active=False)
        client.force_login(user)
        client.post(reverse("watchlist", args=[listing.id]))
        item = Watchlist.objects.get(user=user, listing=listing)
        assert item.active is True

    def test_watchlist_remove(self, client, user, listing):
        WatchlistFactory(user=user, listing=listing, active=True)
        client.force_login(user)
        response = client.get(reverse("watchlist_remove", args=[listing.id]))
        assert response.status_code == 302
        item = Watchlist.objects.get(user=user, listing=listing)
        assert item.active is False

    def test_watchlist_page_shows_active_items(self, client, user, listing):
        WatchlistFactory(user=user, listing=listing, active=True)
        client.force_login(user)
        # GET /watchlist/<user_id> shows the user's watchlist
        response = client.get(reverse("watchlist", args=[user.id]))
        assert response.status_code == 200
        assert listing.title.encode() in response.content

    def test_watchlist_page_excludes_inactive(self, client, user, listing):
        WatchlistFactory(user=user, listing=listing, active=False)
        client.force_login(user)
        response = client.get(reverse("watchlist", args=[user.id]))
        assert response.status_code == 200
        assert listing.title.encode() not in response.content
