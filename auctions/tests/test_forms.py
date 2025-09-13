from django.test import TestCase
from auctions.forms import ListingForm, BidForm, CommentForm
from .factories import UserFactory


class ListingFormTest(TestCase):
    def test_valid_form(self):
        user = UserFactory()
        form_data = {
            "title": "Test Listing",
            "description": "This is a test description.",
            "starting_bid": 10.00,
            "image": "http://example.com/image.jpg",
            "category": "Other",
        }
        form = ListingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_title(self):
        form_data = {"title": ""}
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_duplicate_title(self):
        user = UserFactory()
        from auctions.models import Listing

        Listing.objects.create(title="Test Listing", user=user, starting_bid=10.00)
        form_data = {"title": "Test Listing"}
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_empty_description(self):
        form_data = {"description": ""}
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_empty_starting_bid(self):
        form_data = {"starting_bid": None}
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("starting_bid", form.errors)

    def test_negative_starting_bid(self):
        form_data = {"starting_bid": -10.00}
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("starting_bid", form.errors)

    def test_invalid_image_url(self):
        form_data = {"image": "not a url"}
        form = ListingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)


class BidFormTest(TestCase):
    def test_valid_form(self):
        form_data = {"amount": 10.00}
        form = BidForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_amount(self):
        form_data = {"amount": None}
        form = BidForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_zero_amount(self):
        form_data = {"amount": 0}
        form = BidForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_negative_amount(self):
        form_data = {"amount": -10.00}
        form = BidForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)


class CommentFormTest(TestCase):
    def test_valid_form(self):
        form_data = {"text": "This is a test comment."}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_text(self):
        form_data = {"text": ""}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())  # empty comment is allowed
