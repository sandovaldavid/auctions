from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from auctions.analytics import AuctionAnalytics
from auctions.models import Listing
from tests.conftest import BidFactory, ListingFactory, UserFactory


@pytest.mark.django_db
class TestGetTimeSeriesData:
    """These queries used to run SQLite-only .extra() SQL (CODE-001);
    they must produce the same grouped output on PostgreSQL."""

    def test_groups_listings_by_day(self):
        today = timezone.now()
        listing1 = ListingFactory()
        listing2 = ListingFactory()
        Listing.objects.filter(pk__in=[listing1.pk, listing2.pk]).update(created=today)

        data = AuctionAnalytics().get_time_series_data(days=7)

        today_str = today.date().isoformat()
        matching = [item for item in data["listings"] if item["day"] == today_str]
        assert len(matching) == 1
        assert matching[0]["count"] == 2

    def test_uses_correct_day_bucket_for_older_listing(self):
        listing = ListingFactory()
        target_date = timezone.now() - timedelta(days=2)
        Listing.objects.filter(pk=listing.pk).update(created=target_date)

        data = AuctionAnalytics().get_time_series_data(days=7)

        target_str = target_date.date().isoformat()
        matching = [item for item in data["listings"] if item["day"] == target_str]
        assert len(matching) == 1
        assert matching[0]["count"] == 1

    def test_counts_bids_and_total_amount_by_listing_day(self):
        listing = ListingFactory()
        bidder = UserFactory()
        BidFactory(listing=listing, user=bidder, amount=Decimal("15.00"))
        BidFactory(listing=listing, user=bidder, amount=Decimal("25.00"))

        data = AuctionAnalytics().get_time_series_data(days=7)

        today_str = timezone.now().date().isoformat()
        bids_today = next(item for item in data["bids"] if item["day"] == today_str)
        assert bids_today["count"] == 2
        assert bids_today["total_amount"] == Decimal("40.00")

    def test_counts_users_joined_today(self):
        UserFactory()

        data = AuctionAnalytics().get_time_series_data(days=7)

        today_str = timezone.now().date().isoformat()
        users_today = next(item for item in data["users"] if item["day"] == today_str)
        assert users_today["count"] >= 1


@pytest.mark.django_db
class TestGetMarketTrends:
    """monthly_trends/seasonal_patterns used the SQLite-only strftime() SQL
    (CODE-001); values must stay JSON/JS-safe strings after the fix."""

    def test_monthly_trends_grouped_and_stringified(self):
        ListingFactory(starting_bid=Decimal("10.00"), current_bid=Decimal("20.00"))

        trends = AuctionAnalytics().get_market_trends()

        assert trends["monthly_trends"]
        entry = trends["monthly_trends"][0]
        assert isinstance(entry["month"], str)
        assert entry["month"] == timezone.now().strftime("%Y-%m")
        assert entry["listings_count"] >= 1

    def test_seasonal_patterns_grouped_and_zero_padded(self):
        ListingFactory()

        trends = AuctionAnalytics().get_market_trends()

        assert trends["seasonal_patterns"]
        entry = trends["seasonal_patterns"][0]
        assert isinstance(entry["month"], str)
        assert len(entry["month"]) == 2
        assert entry["month"] == timezone.now().strftime("%m")
