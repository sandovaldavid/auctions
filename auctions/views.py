from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import BidForm, CommentForm, ListingForm, RegistrationForm
from .models import Listing, Watchlist


def index(request):
    list_user = Listing.objects.filter(active=True).order_by("-created")
    paginator = Paginator(list_user, 10)
    page_number = request.GET.get("page")
    page_listings = paginator.get_page(page_number)
    return render(request, "auctions/index.html", {"listings": page_listings})


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(
            request,
            "auctions/login.html",
            {"message": "Invalid username and/or password."},
        )
    return render(request, "auctions/login.html")


@require_POST
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                form.add_error("username", "Username already taken.")
            else:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
        message = " ".join(msg for errors in form.errors.values() for msg in errors)
        return render(request, "auctions/register.html", {"message": message})
    return render(request, "auctions/register.html")


@login_required
def new_auctions(request):
    category_choices = ListingForm.CATEGORY_CHOICES
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            # Set the logged-in user
            new_listing = form.save(commit=False)  # Don't save yet
            new_listing.user = request.user  # Set the user
            new_listing.save()  # Now save the Listing
            messages.success(request, "Your listing has been created.")
            return redirect("index")
        messages.error(request, "There was an error with created your listing.")
        return render(
            request,
            "auctions/newAuctions.html",
            {"form": form, "category_choices": category_choices},
        )
    form = ListingForm()
    return render(
        request,
        "auctions/newAuctions.html",
        {"form": form, "category_choices": category_choices},
    )


def listing(request, listing_id):
    auction = get_object_or_404(Listing, id=listing_id)
    comments = auction.comments.all()
    form = CommentForm()
    return render(
        request,
        "auctions/auction.html",
        {"listing": auction, "comments": comments, "form": form},
    )


@login_required
def bid(request, listing_id):
    auction = get_object_or_404(Listing, pk=listing_id)
    bid_count = auction.bids.count()
    if request.method == "POST":
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            bid_value = bid_form.cleaned_data["amount"]
            try:
                auction.place_bid(user=request.user, bid_value=bid_value)
                messages.success(request, "Your bid has been placed successfully.")
                messages.info(
                    request,
                    f"({bid_count + 1}) bid(s) so far. Your bid is the current bid.",
                )
                return redirect("listing", listing_id=listing_id)
            except ValidationError as e:
                bid_form.add_error("amount", str(e)[2:-2])
        else:
            messages.error(
                request,
                "There was an error with your bid. Please review and try again.",
            )
        return render(
            request,
            "auctions/auction.html",
            {"listing": auction, "form": bid_form, "comments": auction.comments.all()},
        )
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def watchlist(request, listing_id):
    user = request.user
    if request.method == "POST":
        current_listing = get_object_or_404(Listing, pk=listing_id)
        watchlist_item, created = Watchlist.objects.get_or_create(
            user=user, listing=current_listing
        )
        if created:
            watchlist_item.active = True
        else:
            watchlist_item.active = not watchlist_item.active
        watchlist_item.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    listings_in_watchlist = Listing.objects.filter(
        watchlist__user=user, watchlist__active=True
    ).order_by("-created")
    paginator = Paginator(listings_in_watchlist, 10)
    page_number = request.GET.get("page")
    page_listings = paginator.get_page(page_number)
    return render(request, "auctions/watchList.html", {"listings": page_listings})


@login_required
@require_POST
def watchlist_remove(request, listing_id):
    user = request.user
    current_listing = get_object_or_404(Listing, pk=listing_id)
    watchlist_item = get_object_or_404(Watchlist, user=user, listing=current_listing)
    watchlist_item.active = False
    watchlist_item.save()
    return HttpResponseRedirect(reverse("watchlist", args=[user.id]))


@login_required
@require_POST
def close_auction(request, listing_id):
    auction_listing = get_object_or_404(Listing, id=listing_id)

    if request.user != auction_listing.user:
        messages.error(request, "You are not authorized to close this auction.")
        return redirect("listing", listing_id=listing_id)
    highest_bid = auction_listing.bids.order_by("-amount").first()
    if highest_bid:
        auction_listing.winner = highest_bid.user
    else:
        messages.warning(request, "No bids were placed on this listing.")
    auction_listing.active = False
    auction_listing.save()
    messages.success(request, "The auction has been closed.")
    return redirect("listing", listing_id=listing_id)


def categories(request):
    category = request.GET.get("category")
    if category:
        listings = Listing.objects.filter(category=category, active=True).order_by(
            "-created"
        )
    else:
        listings = Listing.objects.filter(active=True).order_by("-created")
    paginator = Paginator(listings, 10)
    page_number = request.GET.get("page")
    listings = paginator.get_page(page_number)
    return render(
        request,
        "auctions/categories.html",
        {
            "listings": listings,
            "category_choices": [
                (cat, cat)
                for cat in Listing.objects.filter(active=True)
                .values_list("category", flat=True)
                .distinct()
                .order_by("category")
            ],
            "selected_category": category,
        },
    )


@login_required
def comment(request, listing_id):
    auction = get_object_or_404(Listing, pk=listing_id)
    comments = auction.comments.filter(listing=auction)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_auction = form.save(commit=False)
            comment_auction.user = request.user
            comment_auction.listing = auction
            comment_auction.save()
            messages.success(request, "Your comment has been added.")
        else:
            messages.error(request, "There was an error with your comment.")
            return render(
                request,
                "auctions/auction.html",
                {"listing": auction, "comments": comments, "form": form},
            )
    return redirect("listing", listing_id=listing_id)
