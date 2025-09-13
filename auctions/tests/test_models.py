from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from auctions.models import Listing, Bid, Comment, Watchlist
from .factories import (
    UserFactory,
    ListingFactory,
    BidFactory,
    CommentFactory,
    WatchlistFactory,
)


class ListingModelTest(TestCase):
    def test_string_representation(self):
        listing = ListingFactory(title="My Test Listing", starting_bid=Decimal("10.00"))
        self.assertEqual(str(listing), "My Test Listing - 10.00")

    def test_place_bid_successfully(self):
        listing = ListingFactory(
            starting_bid=Decimal("10.00"), current_bid=Decimal("10.00")
        )
        user = UserFactory()
        listing.place_bid(user, Decimal("12.00"))
        self.assertEqual(listing.current_bid, Decimal("12.00"))
        self.assertEqual(listing.bids.count(), 1)
        self.assertEqual(listing.bids.first().user, user)
        self.assertEqual(listing.bids.first().amount, Decimal("12.00"))

    def test_place_bid_with_lower_amount(self):
        listing = ListingFactory(
            starting_bid=Decimal("10.00"), current_bid=Decimal("12.00")
        )
        user = UserFactory()
        with self.assertRaises(ValidationError):
            listing.place_bid(user, Decimal("11.00"))

    def test_place_bid_with_equal_amount(self):
        listing = ListingFactory(
            starting_bid=Decimal("10.00"), current_bid=Decimal("12.00")
        )
        user = UserFactory()
        with self.assertRaises(ValidationError):
            listing.place_bid(user, Decimal("12.00"))


class BidModelTest(TestCase):
    def test_string_representation(self):
        user = UserFactory(username="testuser")
        listing = ListingFactory(title="Test Listing")
        bid = BidFactory(user=user, listing=listing, amount=Decimal("15.00"))
        self.assertEqual(str(bid), "testuser bid 15.00 on Test Listing")


class CommentModelTest(TestCase):
    def test_string_representation(self):
        user = UserFactory(username="commenter")
        listing = ListingFactory(title="Another Listing")
        comment = CommentFactory(user=user, listing=listing)
        self.assertEqual(str(comment), "commenter commented on Another Listing")


class WatchlistModelTest(TestCase):
    def test_string_representation(self):
        user = UserFactory(username="watcher")
        listing = ListingFactory(title="Watchlist Item")
        watchlist_item = WatchlistFactory(user=user, listing=listing)
        self.assertEqual(
            str(watchlist_item), "watcher added Watchlist Item to watchlist"
        )

    def test_toggle_watchlist(self):
        watchlist_item = WatchlistFactory(active=True)
        self.assertTrue(watchlist_item.active)
        watchlist_item.toggle()
        self.assertFalse(watchlist_item.active)
        watchlist_item.toggle()
        self.assertTrue(watchlist_item.active)
