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
    {
        "username": "seed_admin",
        "email": "admin@seed.dev",
        "is_staff": True,
        "is_superuser": True,
    },
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
        "description": """\
## Apple MacBook Pro 14" M3 — Sealed Box

**Condition:** Brand new, factory sealed. Never opened.

Unleash professional-grade performance with the latest **Apple M3 chip**:

- **CPU:** 8-core (4 performance + 4 efficiency)
- **RAM:** 16 GB unified memory
- **Storage:** 512 GB SSD
- **Display:** 14.2" Liquid Retina XDR (3024×1964)
- **Battery:** Up to 18 hours

> Perfect for developers, video editors, and creatives who demand the best.

**Included in box:**
1. MacBook Pro 14"
2. 67W USB-C Power Adapter
3. USB-C to MagSafe 3 Cable

*Ships same day. Original Apple warranty applies.*""",
        "starting_bid": Decimal("1200.00"),
        "image": "https://picsum.photos/seed/macbook/400/300",
        "category": "Electronics",
        "seller": "seed_seller1",
    },
    {
        "title": "Sony WH-1000XM5 Headphones",
        "description": """\
## Sony WH-1000XM5 — Industry-Leading Noise Cancellation

**Condition:** Like new — used for 2 months, no visible wear.

The **WH-1000XM5** sets the standard for over-ear noise-canceling headphones.

### Key Features

| Feature | Detail |
|---------|--------|
| Noise cancellation | 8 microphones + 2 processors |
| Battery life | **30 hours** (ANC on) |
| Charge time | 3.5 hours (USB-C) |
| Quick charge | 3 min → 3 hours playback |
| Codec support | LDAC, AAC, SBC |

### What's Included
- Headphones
- Carrying case
- USB-C charging cable
- 3.5mm audio cable

> "The best noise-canceling headphones you can buy" — *The Verge*

*Reason for selling: upgraded to IEM setup.*""",
        "starting_bid": Decimal("250.00"),
        "image": "https://picsum.photos/seed/headphones/400/300",
        "category": "Electronics",
        "seller": "seed_seller2",
    },
    # Fashion (2)
    {
        "title": "Vintage Levi's 501 Jeans (32x32)",
        "description": """\
## Authentic 1990s Levi's 501 — True Vintage

**Condition:** Excellent. Minimal fading, no rips or repairs.

These are the **real deal** — not a modern reproduction. Made in USA.

### Details
- **Waist:** 32"
- **Inseam:** 32"
- **Rise:** High (classic 501 cut)
- **Wash:** Medium blue, natural fading at knees

### Authenticity Markers
- Original copper rivets intact
- Leather patch readable
- Interior tag: "MADE IN USA"
- Single-stitch construction (pre-1990s indicator)

> "Style never goes out of fashion" — Coco Chanel

**Care:** Machine wash cold, hang dry to preserve fit.

*Free shipping on orders over $50!*""",
        "starting_bid": Decimal("45.00"),
        "image": "https://picsum.photos/seed/jeans/400/300",
        "category": "Fashion",
        "seller": "seed_seller1",
    },
    {
        "title": "Louis Vuitton Monogram Tote Bag",
        "description": """\
## Louis Vuitton Neverfull MM — Monogram Canvas

**Condition:** Very good. Light patina on handles (expected with use).

One of the most iconic bags in fashion history. The **Neverfull MM** is the
perfect everyday tote — spacious, structured, and timeless.

### Specifications
- **Model:** Neverfull MM
- **Canvas:** Classic monogram
- **Interior:** Red striped lining with removable pochette
- **Dimensions:** 31 × 28 × 14 cm
- **Hardware:** Golden brass

### Included
- ✅ Certificate of authenticity
- ✅ Original dust bag
- ✅ Original receipt (price redacted)
- ❌ Box not included

### Condition Notes
- Handles show natural vachetta patina (honey tone)
- Canvas: no scratches, peeling, or cracks
- Interior: clean, no stains
- Zipper: smooth operation

*All sales final. Happy to provide additional photos on request.*""",
        "starting_bid": Decimal("850.00"),
        "image": "https://picsum.photos/seed/tote/400/300",
        "category": "Fashion",
        "seller": "seed_seller2",
    },
    # Toys (2)
    {
        "title": "LEGO Star Wars Millennium Falcon (75192)",
        "description": """\
## LEGO® Millennium Falcon™ — Ultimate Collector Series

**Condition:** Complete and **factory sealed**. Never opened.

The crown jewel of LEGO Star Wars collecting. Set **75192** is the largest
LEGO set ever produced at time of release.

### By the Numbers

| Stat | Value |
|------|-------|
| Piece count | **7,541** |
| Minifigures | 4 (Han, Leia, Chewie, C-3PO + R2-D2 + BB-8) |
| Dimensions | 84 × 56 × 21 cm (built) |
| Recommended age | 16+ |

### Why It's Special
- Iconic design from *A New Hope* and *The Force Awakens*
- Highly detailed interior: cockpit, lounge, engine room
- Consistent resale value appreciation year-over-year

> Sealed sets from this series have sold for **2–3× retail** in recent years.

*Ships double-boxed with full insurance. Collector's item — priced to move.*""",
        "starting_bid": Decimal("600.00"),
        "image": "https://picsum.photos/seed/lego/400/300",
        "category": "Toys",
        "seller": "seed_seller1",
    },
    {
        "title": "Nintendo Switch OLED Model",
        "description": """\
## Nintendo Switch OLED — White Edition + 5 Games Bundle

**Condition:** Excellent. No scratches on screen (used with screen protector).

The best version of the Switch, with the gorgeous **7" OLED display**.

### What's Included

**Hardware:**
- Nintendo Switch OLED (White)
- Dock with LAN port
- White Joy-Con pair (L+R)
- Joy-Con grip
- HDMI cable + power adapter

**Games:**
1. The Legend of Zelda: Tears of the Kingdom
2. Mario Kart 8 Deluxe
3. Animal Crossing: New Horizons
4. Splatoon 3
5. Super Mario Odyssey

### Condition Details
- Screen: Perfect, no scratches (used with tempered glass protector)
- Dock: Minor dust, no damage
- Joy-Cons: No drift (tested extensively)
- Battery: Holds ~5 hours charge

*Selling because I got a Steam Deck. Great bundle for a first-time Switch owner.*""",
        "starting_bid": Decimal("280.00"),
        "image": "https://picsum.photos/seed/switch/400/300",
        "category": "Toys",
        "seller": "seed_seller2",
    },
    # Home (2)
    {
        "title": "KitchenAid Stand Mixer - Cobalt Blue",
        "description": """\
## KitchenAid Artisan Stand Mixer — Cobalt Blue

**Condition:** Like new. Used only 5 times for light baking.

The **KitchenAid Artisan** is the gold standard of home stand mixers, beloved
by professional bakers and home cooks alike.

### Specifications
- **Capacity:** 5-quart stainless steel bowl
- **Motor:** 325W with 10 speeds
- **Color:** Cobalt Blue (discontinued — rare find!)
- **Dimensions:** 36 × 22 × 36 cm

### Included Attachments
- ✅ Flat beater
- ✅ Dough hook
- ✅ Wire whip
- ✅ Pouring shield
- ✅ Original box and manual

> Still under manufacturer warranty (expires March 2026).

**Why I'm selling:** Moving to a smaller apartment, no counter space.

*Local pickup available in Austin, TX. Can ship with extra padding.*""",
        "starting_bid": Decimal("180.00"),
        "image": "https://picsum.photos/seed/mixer/400/300",
        "category": "Home",
        "seller": "seed_seller1",
    },
    {
        "title": "Mid-Century Modern Walnut Desk",
        "description": """\
## Mid-Century Modern Solid Walnut Desk

**Condition:** Good. Minor surface scratches (see photos). Structurally perfect.

A stunning piece of **American Black Walnut** craftsmanship from a local
Portland woodworker. This desk is both functional and a conversation piece.

### Dimensions
- **Width:** 60" (152 cm)
- **Depth:** 30" (76 cm)
- **Height:** 29.5" (75 cm)
- **Weight:** ~85 lbs

### Features
- 2 drawers with **solid brass pulls**
- Tapered walnut legs (removable for transport)
- Hand-rubbed tung oil finish
- Cable management hole (3" diameter)

### Condition Notes
- Two minor surface scratches (~1" each) on top — not visible from seated position
- All drawers slide smoothly
- No wobble or structural issues

> Would pair beautifully with an Eames chair or any mid-century seating.

*Local pickup preferred (Seattle area). Will consider freight shipping at buyer's cost.*""",
        "starting_bid": Decimal("320.00"),
        "image": "https://picsum.photos/seed/desk/400/300",
        "category": "Home",
        "seller": "seed_seller2",
    },
    # Books (2)
    {
        "title": "First Edition: Dune by Frank Herbert (1965)",
        "description": """\
## *Dune* by Frank Herbert — First Edition, Third Printing (1965)

**Condition:** Good. Dust jacket intact with minor edge wear.

One of the most important science fiction novels ever written. This is a
**true first edition** (Chilton Books, 1965), third printing.

### Bibliographic Details
- **Publisher:** Chilton Books, Philadelphia
- **Year:** 1965
- **Printing:** Third (identified by number line)
- **ISBN:** Pre-ISBN era
- **Pages:** 412

### Condition Assessment (using Bauman's scale)
- **Binding:** Tight, no cracking
- **Pages:** Tanning consistent with age, no foxing or water damage
- **Dust jacket:** Present, intact; small chip at top spine corner
- **Boards:** Clean under jacket

> *"I must not fear. Fear is the mind-killer."* — Paul Atreides

### Provenance
Purchased at a San Francisco estate sale in 2019. No prior ownership stamps.

**Comparable sales:** Similar copies have sold $400–$800 at auction houses.

*Will ship insured and tracked. Happy to provide more photos of any specific detail.*""",
        "starting_bid": Decimal("500.00"),
        "image": "https://picsum.photos/seed/dune/400/300",
        "category": "Books",
        "seller": "seed_seller1",
    },
    {
        "title": "Complete Calvin and Hobbes Collection",
        "description": """\
## *The Complete Calvin and Hobbes* — 3-Volume Hardcover Slipcase

**Condition:** Near mint. Read once, stored in climate-controlled room.

Bill Watterson's magnum opus, collected in a **gorgeous three-volume hardcover
set** that belongs on every bookshelf.

### What's Included
- All 3 volumes in original slipcase
- **1,456 pages** of strips in chronological order
- Introduction by Watterson himself
- Over **3,000 comic strips** spanning 1985–1995

### Condition
| Component | Condition |
|-----------|-----------|
| Slipcase | Near mint, no tears |
| Spines | No fading or creasing |
| Pages | Bright white, no yellowing |
| Binding | Tight on all 3 volumes |

> *"I've never had a reader tell me they spent too much time with Calvin and Hobbes."*
> — Bill Watterson

This edition is **out of print** and consistently sells above retail.

*Ships via UPS Ground, double-boxed. Signature required on delivery.*""",
        "starting_bid": Decimal("95.00"),
        "image": "https://picsum.photos/seed/calvinhobbes/400/300",
        "category": "Books",
        "seller": "seed_seller2",
    },
    # Other (2)
    {
        "title": "Gibson Les Paul Standard 1959 Reissue",
        "description": """\
## Gibson Custom Shop 1959 Les Paul Standard Reissue

**Condition:** Mint. Never gigged. Stored in original hard case.

The holy grail of electric guitars — Gibson's exacting recreation of the
legendary **1959 Les Paul Standard**, widely considered the finest electric
guitar ever made.

### Specifications

| Spec | Detail |
|------|--------|
| Body | Mahogany with AAA Figured Maple top |
| Neck | 1-piece Mahogany, C-profile |
| Fretboard | Indian Rosewood, 22 frets |
| Pickups | Burstbucker 1 & 2 (matched pair) |
| Hardware | Nickel Tune-O-Matic bridge |
| Finish | **Iced Tea Burst** (hand-applied nitro) |
| Weight | 8.6 lbs |
| Serial | CS230547 |

### Included
- ✅ Original brown Gibson hard shell case (OHSC)
- ✅ Certificate of Authenticity
- ✅ Gibson case candy (strap, polish cloth, warranty card)

> *"Playing a '59 reissue is as close to time travel as a guitarist can get."*

**Reason for selling:** Downsizing collection. This guitar deserves to be played.

*Serious buyers only. No trades. Will not ship internationally.*""",
        "starting_bid": Decimal("3500.00"),
        "image": "https://picsum.photos/seed/guitar/400/300",
        "category": "Other",
        "seller": "seed_seller1",
    },
    {
        "title": "Trek Domane SL 6 Road Bike (54cm)",
        "description": """\
## 2022 Trek Domane SL 6 — Carbon Endurance Road Bike

**Condition:** Excellent. Less than **500 miles**. No crashes or damage.

The Domane SL 6 is Trek's flagship endurance road bike — built for long days
in the saddle with **IsoSpeed decoupler** technology that absorbs road chatter.

### Build Spec

| Component | Detail |
|-----------|--------|
| Frame | 500 Series OCLV Carbon |
| Fork | Full carbon, IsoSpeed |
| Groupset | **Shimano 105 R7000 (11-speed)** |
| Brakes | Shimano 105 hydraulic disc |
| Wheels | Bontrager Paradigm Comp TLR |
| Tires | Bontrager R2 32c (tubeless-ready) |
| Saddle | Bontrager Montrose Comp |
| Size | **54 cm** (fits riders ~5'9"–6'0") |

### What's Included
- ✅ Bike (as specced above)
- ✅ Original pedals (never used)
- ✅ Trek seat bag
- ❌ Cycling computer not included

### Upgrades Made
- Replaced stock saddle with **Specialized Power Comp** (included)
- Added Garmin mount (included)

> Perfect for centuries, gran fondos, or daily training rides.

*Local pickup preferred in Denver, CO. Can ship via BikeFlights at buyer's cost (~$85).*""",
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
            amounts = [
                base + Decimal("10.00"),
                base + Decimal("25.00"),
                base + Decimal("50.00"),
            ]
            for buyer, amount in zip(buyers, amounts, strict=False):
                if not Bid.objects.filter(listing=listing, user=buyer).exists():
                    try:
                        listing.place_bid(buyer, amount)
                    except Exception:
                        pass

    def _create_comments(self, users: dict, listings: list[Listing]) -> None:
        commenters = [users["seed_buyer1"], users["seed_buyer2"]]
        for listing in listings:
            for commenter, text in zip(commenters, SEED_COMMENTS, strict=False):
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
