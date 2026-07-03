from decimal import Decimal

import pytest

from auctions.data_utils import AlertSystem, DataProcessor, ReportGenerator
from tests.conftest import BidFactory, ListingFactory, UserFactory


class TestDataProcessor:
    def test_calculate_growth_rate(self):
        assert DataProcessor.calculate_growth_rate(150, 100) == 50
        assert DataProcessor.calculate_growth_rate(50, 100) == -50

    def test_calculate_growth_rate_zero_previous(self):
        assert DataProcessor.calculate_growth_rate(100, 0) == 0

    def test_get_time_periods(self):
        periods = DataProcessor.get_time_periods(days=10)
        assert periods["days"] == 10
        assert periods["end"] > periods["start"]

    @pytest.mark.django_db
    def test_calculate_engagement_score(self):
        user = UserFactory()
        listing = ListingFactory(user=user)
        BidFactory(user=user, listing=listing)
        score = DataProcessor.calculate_engagement_score(user)
        # 1 listing (weight 3) + 1 bid (weight 2)
        assert score == 5

    def test_detect_anomalies_too_few_points(self):
        assert DataProcessor.detect_anomalies([1, 2]) == []

    def test_detect_anomalies_finds_outlier(self):
        data = [10, 11, 9, 10, 100]
        anomalies = DataProcessor.detect_anomalies(data, threshold=1)
        assert any(a["value"] == 100 for a in anomalies)

    def test_calculate_market_volatility_empty(self):
        assert DataProcessor.calculate_market_volatility([]) == 0

    def test_calculate_market_volatility_single_price(self):
        assert DataProcessor.calculate_market_volatility([{"current_bid": 10}]) == 0

    def test_calculate_market_volatility_computes_value(self):
        listings_data = [
            {"current_bid": 100, "starting_bid": 100},
            {"current_bid": 110, "starting_bid": 100},
            {"current_bid": 90, "starting_bid": 100},
        ]
        volatility = DataProcessor.calculate_market_volatility(listings_data)
        assert volatility > 0


@pytest.mark.django_db
class TestReportGenerator:
    def test_generate_user_activity_report_all_users(self):
        user = UserFactory()
        listing = ListingFactory(user=user)
        BidFactory(user=user, listing=listing)

        report = ReportGenerator.generate_user_activity_report(days=30)

        entry = next(item for item in report if item["username"] == user.username)
        assert entry["listings_created"] == 1
        assert entry["bids_made"] == 1

    def test_generate_user_activity_report_single_user(self):
        user = UserFactory()
        report = ReportGenerator.generate_user_activity_report(user_id=user.id, days=30)
        assert len(report) == 1
        assert report[0]["user_id"] == user.id

    def test_generate_market_analysis_with_listings(self):
        listing = ListingFactory(
            starting_bid=Decimal("10.00"), current_bid=Decimal("20.00")
        )
        BidFactory(listing=listing)

        analysis = ReportGenerator.generate_market_analysis(days=30)

        assert analysis["total_listings"] >= 1
        assert analysis["avg_starting_price"] >= 0
        assert "category_breakdown" in analysis

    def test_generate_market_analysis_no_listings(self):
        analysis = ReportGenerator.generate_market_analysis(days=30)
        assert analysis["avg_starting_price"] == 0
        assert analysis["price_increase_percent"] == 0

    def test_generate_performance_metrics(self):
        user = UserFactory()
        listing = ListingFactory(user=user)
        BidFactory(user=user, listing=listing)

        metrics = ReportGenerator.generate_performance_metrics(days=30)

        assert metrics["total_listings"] >= 1
        assert 0 <= metrics["conversion_rate"] <= 100


@pytest.mark.django_db
class TestAlertSystem:
    def test_check_low_activity_alert_triggers_when_quiet(self):
        alert = AlertSystem.check_low_activity_alert()
        assert alert is not None
        assert alert["type"] == "warning"

    def test_check_low_activity_alert_none_when_active(self):
        for _ in range(6):
            listing = ListingFactory()
            for _ in range(2):
                BidFactory(listing=listing)
        assert AlertSystem.check_low_activity_alert() is None

    def test_check_high_value_alert_none_by_default(self):
        assert AlertSystem.check_high_value_alert() is None

    def test_check_high_value_alert_triggers(self):
        BidFactory(amount=Decimal("15000.00"))
        alert = AlertSystem.check_high_value_alert()
        assert alert is not None
        assert alert["type"] == "info"

    def test_get_all_alerts_aggregates(self):
        BidFactory(amount=Decimal("15000.00"))
        alerts = AlertSystem.get_all_alerts()
        assert any(a["type"] == "info" for a in alerts)
