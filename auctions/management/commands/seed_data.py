"""
Populate the database with realistic sample data for local development and E2E tests.

Usage:
    python manage.py seed_data           # Create data if not present (idempotent)
    python manage.py seed_data --reset   # Drop existing seed data first
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from auctions.models import Bid, Comment, Listing, Watchlist

User = get_user_model()

SEED_PASSWORD = "TestPass123!"

SEED_USERS = [
    {"username": "seed_admin", "email": "admin@seed.dev", "is_staff": True, "is_superuser": True},
    {"username": "seed_seller1", "email": "seller1@seed.dev"},
    {"username": "seed_seller2", "email": "seller2@seed.dev"},
    {"username": "seed_buyer1", "email": "buyer1@seed.dev"},
    {"username": "seed_buyer2", "email": "buyer2@seed.dev"},
    {"username": "seed_buyer3", "email": "buyer3@seed.dev"},
]

SEED_LISTINGS = [
    # Electronics (2)
    {
        "title": "Apple MacBook Pro 14-inch M3",
        "description": "Brand new MacBook Pro with M3 chip. 16GB RAM, 512GB SSD. "
        "Perfect for developers and creatives. Comes in original packaging.",
        "starting_bid": Decimal("1200.00"),
        "image": "https://picsum.photos/seed/macbook/400/300",
        "category": "Electronics",
        "seller": "seed_seller1",
    },
    {
        "title": "Sony WH-1000XM5 Headphones",
        "description": "Industry-leading noise cancellation wireless headphones. "
        "30-hour battery life. Only used for 2 months.",
        "starting_bid": Decimal("250.00"),
        "image": "https://picsum.photos/seed/headphones/400/300",
        "category": "Electronics",
        "seller": "seed_seller2",
    },
    # Fashion (2)
    {
        "title": "Vintage Levi's 501 Jeans (32x32)",
        "description": "Authentic 1990s Levi's 501 jeans in excellent condition. "
        "Classic straight fit, true vintage piece.",
        "starting_bid": Decimal("45.00"),
        "image": "https://picsum.photos/seed/jeans/400/300",
        "category": "Fashion",
        "seller": "seed_seller1",
    },
    {
        "title": "Louis Vuitton Monogram Tote Bag",
        "description": "Authentic LV Neverfull MM in monogram canvas. "
        "Certificate of authenticity included. Light wear.",
        "starting_bid": Decimal("850.00"),
        "image": "https://picsum.photos/seed/tote/400/300",
        "category": "Fashion",
        "seller": "seed_seller2",
    },
    # Toys (2)
    {
        "title": "LEGO Star Wars Millennium Falcon (75192)",
        "description": "The Ultimate Collector Series Millennium Falcon. "
        "7,541 pieces. Complete and sealed box.",
        "starting_bid": Decimal("600.00"),
        "image": "https://picsum.photos/seed/lego/400/300",
        "category": "Toys",
        "seller": "seed_seller1",
    },
    {
        "title": "Nintendo Switch OLED Model",
        "description": "Nintendo Switch OLED in white. Includes dock, "
        "joy-cons, and 5 games. Excellent condition.",
        "starting_bid": Decimal("280.00"),
        "image": "https://picsum.photos/seed/switch/400/300",
        "category": "Toys",
        "seller": "seed_seller2",
    },
    # Home (2)
    {
        "title": "KitchenAid Stand Mixer - Cobalt Blue",
        "description": "Professional 5-quart KitchenAid Artisan stand mixer. "
        "Used only 5 times. All attachments included.",
        "starting_bid": Decimal("180.00"),
        "image": "https://picsum.photos/seed/mixer/400/300",
        "category": "Home",
        "seller": "seed_seller1",
    },
    {
        "title": "Mid-Century Modern Walnut Desk",
        "description": "Solid walnut wood desk with brass drawer pulls. "
        "60\" x 30\". Minor surface scratches, structurally perfect.",
        "starting_bid": Decimal("320.00"),
        "image": "https://picsum.photos/seed/desk/400/300",
        "category": "Home",
        "seller": "seed_seller2",
    },
    # Books (2)
    {
        "title": "First Edition: Dune by Frank Herbert (1965)",
        "description": "First edition, third printing of Dune. "
        "Chilton Books. Good condition, dust jacket intact.",
        "starting_bid": Decimal("500.00"),
        "image": "https://picsum.photos/seed/dune/400/300",
        "category": "Books",
        "seller": "seed_seller1",
    },
    {
        "title": "Complete Calvin and Hobbes Collection",
        "description": "The Complete Calvin and Hobbes 3-volume hardcover set "
        "by Bill Watterson. Near mint condition.",
        "starting_bid": Decimal("95.00"),
        "image": "https://picsum.photos/seed/calvinhobbes/400/300",
        "category": "Books",
        "seller": "seed_seller2",
    },
    # Other (2)
    {
        "title": "Gibson Les Paul Standard 1959 Reissue",
        "description": "Gibson Custom Shop 1959 Les Paul Standard reissue in "
        "Iced Tea burst. OHSC included. Mint condition.",
        "starting_bid": Decimal("3500.00"),
        "image": "https://picsum.photos/seed/guitar/400/300",
        "category": "Other",
        "seller": "seed_seller1",
    },
    {
        "title": "Trek Domane SL 6 Road Bike (54cm)",
        "description": "2022 Trek Domane SL 6 with Shimano 105 groupset. "
        "Carbon frame, 54cm. Less than 500 miles.",
        "starting_bid": Decimal("2200.00"),
        "image": "https://picsum.photos/seed/bike/400/300",
        "category": "Other",
        "seller": "seed_seller2",
    },
]

SEED_COMMENTS = [
    "Excellent condition! Can you provide more photos?",
    "Is this still available? Very interested.",
]


class Command(BaseCommand):
    help = "Populate the database with sample data for development and E2E tests"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all seed data before creating new records",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_seed_data()

        users = self._create_users()
        listings = self._create_listings(users)
        self._create_bids(users, listings)
        self._create_comments(users, listings)
        self._create_watchlists(users, listings)

        self.stdout.write(self.style.SUCCESS("Seed data ready."))

    def _reset_seed_data(self):
        usernames = [u["username"] for u in SEED_USERS]
        seed_users = User.objects.filter(username__in=usernames)
        # Cascade deletes listings, bids, comments, watchlist entries
        deleted, _ = seed_users.delete()
        self.stdout.write(f"Reset: removed {deleted} seed records")

    def _create_users(self) -> dict[str, User]:
        users = {}
        for data in SEED_USERS:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "is_staff": data.get("is_staff", False),
                    "is_superuser": data.get("is_superuser", False),
                },
            )
            if created:
                user.set_password(SEED_PASSWORD)
                user.save()
                self.stdout.write(f"  Created user: {user.username}")
            users[user.username] = user
        return users

    def _create_listings(self, users: dict) -> list[Listing]:
        listings = []
        for data in SEED_LISTINGS:
            listing, created = Listing.objects.get_or_create(
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "starting_bid": data["starting_bid"],
                    "image": data["image"],
                    "category": data["category"],
                    "user": users[data["seller"]],
                    "active": True,
                },
            )
            if created:
                self.stdout.write(f"  Created listing: {listing.title[:40]}")
            listings.append(listing)
        return listings

    def _create_bids(self, users: dict, listings: list[Listing]) -> None:
        buyers = [users["seed_buyer1"], users["seed_buyer2"], users["seed_buyer3"]]
        for listing in listings:
            base = listing.starting_bid
            amounts = [base + Decimal("10.00"), base + Decimal("25.00"), base + Decimal("50.00")]
            for i, (buyer, amount) in enumerate(zip(buyers, amounts)):
                if not Bid.objects.filter(listing=listing, user=buyer).exists():
                    try:
                        listing.place_bid(buyer, amount)
                    except Exception:
                        pass

    def _create_comments(self, users: dict, listings: list[Listing]) -> None:
        commenters = [users["seed_buyer1"], users["seed_buyer2"]]
        for listing in listings:
            for commenter, text in zip(commenters, SEED_COMMENTS):
                Comment.objects.get_or_create(
                    listing=listing,
                    user=commenter,
                    defaults={"text": text},
                )

    def _create_watchlists(self, users: dict, listings: list[Listing]) -> None:
        buyers = [users["seed_buyer1"], users["seed_buyer2"], users["seed_buyer3"]]
        for buyer in buyers:
            for listing in listings[:3]:
                Watchlist.objects.get_or_create(
                    user=buyer,
                    listing=listing,
                    defaults={"active": True},
                )
