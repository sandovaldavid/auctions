from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from auctions.models import User, Listing
from .factories import UserFactory


class AuctionFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = UserFactory(username="user1")
        self.user1.set_password("testpassword")
        self.user1.save()
        self.user2 = UserFactory(username="user2")
        self.user2.set_password("testpassword")
        self.user2.save()

    def test_full_auction_flow(self):
        # 1. user1 creates a listing
        self.client.login(username="user1", password="testpassword")
        response = self.client.post(
            reverse("new_auction"),
            {
                "title": "Integration Test Listing",
                "description": "A listing for integration testing.",
                "starting_bid": "10.00",
                "category": "Other",
            },
        )
        self.assertEqual(response.status_code, 302)
        listing = Listing.objects.get(title="Integration Test Listing")
        self.assertEqual(listing.user, self.user1)

        # 2. user2 places a bid
        self.client.login(username="user2", password="testpassword")
        response = self.client.post(
            reverse("bid", args=[listing.id]), {"amount": "15.00"}
        )
        self.assertEqual(response.status_code, 302)
        listing.refresh_from_db()
        self.assertEqual(listing.current_bid, Decimal("15.00"))

        # 3. user1 closes the auction
        self.client.login(username="user1", password="testpassword")
        response = self.client.post(reverse("close_auction", args=[listing.id]))
        self.assertEqual(response.status_code, 302)
        listing.refresh_from_db()
        self.assertFalse(listing.active)
        self.assertEqual(listing.winner, self.user2)
