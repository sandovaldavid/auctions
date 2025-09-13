import factory
from factory.django import DjangoModelFactory
from auctions.models import User, Listing, Bid, Comment, Watchlist

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')

class ListingFactory(DjangoModelFactory):
    class Meta:
        model = Listing

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text')
    starting_bid = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    user = factory.SubFactory(UserFactory)

class BidFactory(DjangoModelFactory):
    class Meta:
        model = Bid

    amount = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)

class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    text = factory.Faker('text')
    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)

class WatchlistFactory(DjangoModelFactory):
    class Meta:
        model = Watchlist

    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)
    active = True
