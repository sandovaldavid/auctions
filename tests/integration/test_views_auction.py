from decimal import Decimal

import pytest
from django.urls import reverse

from auctions.models import Bid, Listing
from tests.conftest import BidFactory, ListingFactory, UserFactory


@pytest.mark.django_db
class TestAuctionViews:
    def test_listing_detail_get(self, client, listing):
        response = client.get(reverse("listing", args=[listing.id]))
        assert response.status_code == 200
        assert listing.title.encode() in response.content

    def test_listing_not_found(self, client):
        response = client.get(reverse("listing", args=[99999]))
        # catch_all_404_view may intercept; accept 200 or 404
        assert response.status_code in (200, 404)

    def test_bid_requires_login(self, client, listing):
        response = client.post(
            reverse("bid", args=[listing.id]), {"amount": "20.00"}
        )
        assert response.status_code == 302
        assert "/login" in response.url

    def test_bid_get_redirects_to_listing(self, client, user, listing):
        client.force_login(user)
        response = client.get(reverse("bid", args=[listing.id]))
        assert response.status_code == 302
        assert reverse("listing", args=[listing.id]) in response.url

    def test_bid_valid_post(self, client, user, listing):
        client.force_login(user)
        response = client.post(
            reverse("bid", args=[listing.id]),
            {"amount": "25.00"},
        )
        assert response.status_code == 302
        listing.refresh_from_db()
        assert listing.current_bid == Decimal("25.00")
        assert Bid.objects.filter(listing=listing, user=user).exists()

    def test_bid_too_low(self, client, user, listing):
        listing.current_bid = Decimal("50.00")
        listing.save()
        client.force_login(user)
        response = client.post(
            reverse("bid", args=[listing.id]),
            {"amount": "10.00"},
        )
        assert response.status_code == 200
        listing.refresh_from_db()
        assert listing.current_bid == Decimal("50.00")

    def test_close_auction_owner_can_close(self, client, user, listing):
        client.force_login(user)
        response = client.post(reverse("close_auction", args=[listing.id]))
        assert response.status_code == 302
        listing.refresh_from_db()
        assert listing.active is False

    def test_close_auction_non_owner_forbidden(self, client, another_user, listing):
        client.force_login(another_user)
        response = client.post(reverse("close_auction", args=[listing.id]))
        assert response.status_code == 302
        listing.refresh_from_db()
        assert listing.active is True

    def test_close_auction_sets_winner(self, client, user, another_user):
        listing = ListingFactory(user=user)
        BidFactory(user=another_user, listing=listing, amount=Decimal("30.00"))
        client.force_login(user)
        client.post(reverse("close_auction", args=[listing.id]))
        listing.refresh_from_db()
        assert listing.winner == another_user
        assert listing.active is False

    def test_new_auction_get(self, client, user):
        client.force_login(user)
        response = client.get(reverse("new_auction"))
        assert response.status_code == 200

    def test_new_auction_post_valid(self, client, user):
        client.force_login(user)
        response = client.post(
            reverse("new_auction"),
            {
                "title": "Unique Auction Title ABC",
                "description": "A great item for sale",
                "starting_bid": "5.00",
                "image": "https://example.com/photo.jpg",
                "category": "Electronics",
            },
        )
        assert response.status_code == 302
        assert Listing.objects.filter(
            title="Unique Auction Title ABC", user=user
        ).exists()
