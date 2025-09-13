from django.test import TestCase, Client
from django.urls import reverse
from auctions.models import User, Listing
from .factories import UserFactory, ListingFactory


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/index.html")

    def test_index_view_with_listings(self):
        ListingFactory.create_batch(5)
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["listings"]), 5)


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory(username="testuser")
        self.user.set_password("testpassword")
        self.user.save()

    def test_login_view(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_invalid_credentials(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/login.html")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_view(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_register_view(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword",
                "confirmation": "newpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(User.objects.count(), 2)

    def test_register_view_password_mismatch(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "newpassword",
                "confirmation": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/register.html")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(User.objects.count(), 1)


class ListingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.listing = ListingFactory(user=self.user)

    def test_listing_view(self):
        response = self.client.get(reverse("listing", args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/auction.html")
        self.assertEqual(response.context["listing"], self.listing)


class NewAuctionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.username, password="testpassword")

    def test_new_auction_view_get(self):
        response = self.client.get(reverse("new_auction"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auctions/newAuctions.html")

    def test_new_auction_view_post(self):
        form_data = {
            "title": "New Test Listing",
            "description": "This is a new test description.",
            "starting_bid": 20.00,
            "image": "http://example.com/new_image.jpg",
            "category": "Home",
        }
        response = self.client.post(reverse("new_auction"), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(Listing.objects.filter(title="New Test Listing").exists())


from decimal import Decimal


class BidViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.listing = ListingFactory(
            starting_bid=Decimal("10.00"), current_bid=Decimal("10.00")
        )
        self.client.login(username=self.user.username, password="testpassword")

    def test_bid_view_post(self):
        response = self.client.post(
            reverse("bid", args=[self.listing.id]), {"amount": "12.00"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("listing", args=[self.listing.id]))
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.current_bid, Decimal("12.00"))


class WatchlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.listing = ListingFactory()
        self.client.login(username=self.user.username, password="testpassword")

    def test_watchlist_add(self):
        response = self.client.post(reverse("watchlist", args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("listing", args=[self.listing.id]))
        self.assertTrue(
            self.user.watchlist.filter(listing=self.listing, active=True).exists()
        )


class CloseAuctionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.listing = ListingFactory(user=self.user)
        self.client.login(username=self.user.username, password="testpassword")

    def test_close_auction(self):
        response = self.client.post(reverse("close_auction", args=[self.listing.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("listing", args=[self.listing.id]))
        self.listing.refresh_from_db()
        self.assertFalse(self.listing.active)


class CommentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.listing = ListingFactory()
        self.client.login(username=self.user.username, password="testpassword")

    def test_comment_view_post(self):
        response = self.client.post(
            reverse("comment", args=[self.listing.id]), {"text": "Test comment"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("listing", args=[self.listing.id]))
        self.assertTrue(self.listing.comments.filter(text="Test comment").exists())
