import pytest

from auctions.forms import BidForm, CommentForm, ListingForm
from tests.conftest import ListingFactory

VALID_LISTING_DATA = {
    "title": "Unique Listing Title",
    "description": "A detailed description of this auction item.",
    "starting_bid": "25.00",
    "image": "https://example.com/image.jpg",
    "category": "Electronics",
}


@pytest.mark.django_db
class TestListingForm:
    """Unit tests for ListingForm validation logic."""

    def test_valid_form(self):
        form = ListingForm(data=VALID_LISTING_DATA)
        assert form.is_valid(), form.errors

    def test_empty_title_invalid(self):
        data = {**VALID_LISTING_DATA, "title": ""}
        form = ListingForm(data=data)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_duplicate_title_invalid(self):
        ListingFactory(title="Already Taken")
        data = {**VALID_LISTING_DATA, "title": "Already Taken"}
        form = ListingForm(data=data)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_empty_description_invalid(self):
        data = {**VALID_LISTING_DATA, "description": ""}
        form = ListingForm(data=data)
        assert not form.is_valid()
        assert "description" in form.errors

    def test_negative_starting_bid_invalid(self):
        data = {**VALID_LISTING_DATA, "starting_bid": "-1.00"}
        form = ListingForm(data=data)
        assert not form.is_valid()
        assert "starting_bid" in form.errors

    def test_zero_starting_bid_valid(self):
        # The form validator rejects < 0, but 0 itself is accepted per current logic.
        data = {**VALID_LISTING_DATA, "starting_bid": "0.00"}
        form = ListingForm(data=data)
        assert form.is_valid(), form.errors

    def test_invalid_image_url_rejected(self):
        data = {**VALID_LISTING_DATA, "image": "not-a-url"}
        form = ListingForm(data=data)
        assert not form.is_valid()
        assert "image" in form.errors

    def test_valid_https_image_url_accepted(self):
        data = {**VALID_LISTING_DATA, "image": "https://cdn.example.com/photo.png"}
        form = ListingForm(data=data)
        assert form.is_valid(), form.errors

    def test_valid_http_image_url_accepted(self):
        data = {**VALID_LISTING_DATA, "image": "http://example.com/image.jpg"}
        form = ListingForm(data=data)
        assert form.is_valid(), form.errors

    def test_blank_image_is_allowed(self):
        data = {**VALID_LISTING_DATA, "image": ""}
        form = ListingForm(data=data)
        assert form.is_valid(), form.errors

    def test_all_category_choices_accepted(self):
        for category, _ in ListingForm.CATEGORY_CHOICES:
            data = {
                **VALID_LISTING_DATA,
                "title": f"Listing {category}",
                "category": category,
            }
            form = ListingForm(data=data)
            assert form.is_valid(), f"Category '{category}' failed: {form.errors}"


@pytest.mark.django_db
class TestBidForm:
    """Unit tests for BidForm validation logic."""

    def test_valid_bid(self):
        form = BidForm(data={"amount": "50.00"})
        assert form.is_valid(), form.errors

    def test_zero_bid_invalid(self):
        form = BidForm(data={"amount": "0.00"})
        assert not form.is_valid()
        assert "amount" in form.errors

    def test_negative_bid_invalid(self):
        form = BidForm(data={"amount": "-5.00"})
        assert not form.is_valid()
        assert "amount" in form.errors

    def test_empty_bid_invalid(self):
        form = BidForm(data={"amount": ""})
        assert not form.is_valid()
        assert "amount" in form.errors

    def test_large_valid_bid(self):
        form = BidForm(data={"amount": "9999999.99"})
        assert form.is_valid(), form.errors


class TestCommentForm:
    """Unit tests for CommentForm validation logic."""

    def test_valid_comment(self):
        form = CommentForm(data={"text": "This is a great auction!"})
        assert form.is_valid(), form.errors

    def test_empty_comment_invalid(self):
        form = CommentForm(data={"text": ""})
        assert not form.is_valid()
        assert "text" in form.errors

    def test_long_comment_valid(self):
        form = CommentForm(data={"text": "x" * 499})
        assert form.is_valid(), form.errors
