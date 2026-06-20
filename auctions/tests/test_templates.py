from django.test import Client, TestCase
from django.urls import reverse

from .factories import ListingFactory, UserFactory


class TemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()

    def test_index_template_displays_listings(self):
        ListingFactory.create_batch(3, title="Test Listing")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Listing", count=6)

    def test_auction_template_displays_listing_details(self):
        listing = ListingFactory(
            title="Detailed Listing", description="Detailed description."
        )
        response = self.client.get(reverse("listing", args=[listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detailed Listing")
        self.assertContains(response, "Detailed description.")
