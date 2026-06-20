import factory
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model

from auctions.models import Bid, Comment, Listing, Watchlist

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for the custom User model."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "testpassword123")


class ListingFactory(factory.django.DjangoModelFactory):
    """Factory for auction Listing objects."""

    class Meta:
        model = Listing

    title = factory.Sequence(lambda n: f"Test Listing {n}")
    description = "A test auction listing description."
    starting_bid = Decimal("10.00")
    current_bid = None
    image = "https://example.com/img.jpg"
    category = "Electronics"
    active = True
    user = factory.SubFactory(UserFactory)


class BidFactory(factory.django.DjangoModelFactory):
    """Factory for Bid objects."""

    class Meta:
        model = Bid

    amount = Decimal("15.00")
    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    """Factory for Comment objects."""

    class Meta:
        model = Comment

    text = "Test comment text."
    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)


class WatchlistFactory(factory.django.DjangoModelFactory):
    """Factory for Watchlist objects."""

    class Meta:
        model = Watchlist

    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)
    active = True


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def another_user(db):
    return UserFactory(username="other_user", email="other@test.com")


@pytest.fixture
def listing(db):
    return ListingFactory()
