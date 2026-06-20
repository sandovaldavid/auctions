from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from auctions.models import Bid, Comment, Listing, Watchlist
from tests.conftest import (
    BidFactory,
    CommentFactory,
    ListingFactory,
    UserFactory,
    WatchlistFactory,
)


@pytest.mark.django_db
class TestListingModel:
    """Unit tests for the Listing model and its business logic methods."""

    def test_listing_creation(self):
        listing = ListingFactory(
            title="Vintage Watch",
            starting_bid=Decimal("50.00"),
            category="Fashion",
        )
        assert listing.pk is not None
        assert listing.title == "Vintage Watch"
        assert listing.starting_bid == Decimal("50.00")
        assert listing.category == "Fashion"
        assert listing.active is True
        assert listing.current_bid is None
        assert listing.winner is None
        assert listing.created is not None

    def test_place_bid_valid(self):
        listing = ListingFactory(starting_bid=Decimal("10.00"), current_bid=None)
        bidder = UserFactory()

        listing.place_bid(user=bidder, bid_value=Decimal("20.00"))

        listing.refresh_from_db()
        assert listing.current_bid == Decimal("20.00")
        assert Bid.objects.filter(listing=listing, user=bidder).exists()

    def test_place_bid_first_bid_sets_current(self):
        listing = ListingFactory(starting_bid=Decimal("10.00"), current_bid=None)
        bidder = UserFactory()

        listing.place_bid(user=bidder, bid_value=Decimal("10.00"))

        listing.refresh_from_db()
        assert listing.current_bid == Decimal("10.00")

    def test_place_bid_below_current_raises(self):
        listing = ListingFactory(starting_bid=Decimal("10.00"), current_bid=None)
        bidder = UserFactory()
        listing.place_bid(user=bidder, bid_value=Decimal("25.00"))

        second_bidder = UserFactory()
        with pytest.raises(ValidationError, match="higher than the current bid"):
            listing.place_bid(user=second_bidder, bid_value=Decimal("20.00"))

    def test_place_bid_equal_to_current_raises(self):
        listing = ListingFactory(starting_bid=Decimal("10.00"), current_bid=None)
        bidder = UserFactory()
        listing.place_bid(user=bidder, bid_value=Decimal("25.00"))

        with pytest.raises(ValidationError):
            listing.place_bid(user=bidder, bid_value=Decimal("25.00"))

    def test_place_bid_updates_current_bid_to_highest(self):
        listing = ListingFactory(starting_bid=Decimal("10.00"), current_bid=None)
        bidder1 = UserFactory()
        bidder2 = UserFactory()

        listing.place_bid(user=bidder1, bid_value=Decimal("20.00"))
        listing.place_bid(user=bidder2, bid_value=Decimal("35.00"))

        listing.refresh_from_db()
        assert listing.current_bid == Decimal("35.00")
        assert Bid.objects.filter(listing=listing).count() == 2

    def test_close_auction_sets_winner(self):
        listing = ListingFactory(starting_bid=Decimal("10.00"), current_bid=None)
        bidder1 = UserFactory()
        bidder2 = UserFactory()

        listing.place_bid(user=bidder1, bid_value=Decimal("20.00"))
        listing.place_bid(user=bidder2, bid_value=Decimal("50.00"))

        highest_bid = listing.bids.order_by("-amount").first()
        listing.winner = highest_bid.user
        listing.active = False
        listing.save()

        listing.refresh_from_db()
        assert listing.active is False
        assert listing.winner == bidder2

    def test_listing_str(self):
        listing = ListingFactory(title="Rare Coin", starting_bid=Decimal("100.00"))
        assert "Rare Coin" in str(listing)
        assert "100.00" in str(listing)

    def test_get_remove_url_returns_string(self):
        listing = ListingFactory()
        url = listing.get_remove_url()
        assert isinstance(url, str)
        assert str(listing.pk) in url


@pytest.mark.django_db
class TestBidModel:
    """Unit tests for the Bid model."""

    def test_bid_creation(self):
        bidder = UserFactory()
        listing = ListingFactory()
        bid = BidFactory(amount=Decimal("99.99"), user=bidder, listing=listing)

        assert bid.pk is not None
        assert bid.amount == Decimal("99.99")
        assert bid.user == bidder
        assert bid.listing == listing

    def test_bid_str(self):
        bid = BidFactory()
        assert bid.user.username in str(bid)
        assert str(bid.amount) in str(bid)


@pytest.mark.django_db
class TestCommentModel:
    """Unit tests for the Comment model."""

    def test_comment_creation(self):
        commenter = UserFactory()
        listing = ListingFactory()
        comment = CommentFactory(text="Great item!", user=commenter, listing=listing)

        assert comment.pk is not None
        assert comment.text == "Great item!"
        assert comment.user == commenter
        assert comment.listing == listing
        assert comment.created is not None

    def test_comment_str(self):
        comment = CommentFactory()
        assert comment.user.username in str(comment)
        assert comment.listing.title in str(comment)


@pytest.mark.django_db
class TestWatchlistModel:
    """Unit tests for the Watchlist model and its toggle method."""

    def test_watchlist_creation(self):
        item = WatchlistFactory(active=True)
        assert item.pk is not None
        assert item.active is True

    def test_watchlist_toggle_deactivates(self):
        item = WatchlistFactory(active=True)
        item.toggle()
        item.refresh_from_db()
        assert item.active is False

    def test_watchlist_toggle_activates(self):
        item = WatchlistFactory(active=False)
        item.toggle()
        item.refresh_from_db()
        assert item.active is True

    def test_watchlist_str(self):
        item = WatchlistFactory()
        assert item.user.username in str(item)
        assert item.listing.title in str(item)
