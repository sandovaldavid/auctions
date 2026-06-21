"""
Color contrast E2E tests — WCAG 2.1 AA compliance in light and dark modes.

Tests the actual computed styles served by the running application, catching
rendering bugs like the dark-mode heading/price visibility issue shown in
the design screenshots (dark text on dark background).

Run: make test-contrast
"""

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import BASE_URL, apply_theme
from tests.e2e.helpers.contrast import assert_contrast


# ── Selectors checked across themes ──────────────────────────────────────────
#
# These are checked on each page. assert_contrast() silently skips selectors
# that don't exist on a given page, so listing extra selectors is safe.

# Note: .nav-link and .navbar-toggler sit on a CSS gradient background
# and can't be tested via simple solid-color contrast ratio.
# They are covered by the axe-core tests in test_accessibility.py.
NAV_SELECTORS = [
    (".navbar-brand",      "navbar brand/logo"),
]

HEADING_SELECTORS = [
    ("h1",                 "page h1 heading"),
    ("h2",                 "page h2 heading"),
    (".lead",              "lead/subtitle text"),
    ("p",                  "body paragraph text"),
    (".text-muted",        "muted text"),
]

CARD_SELECTORS = [
    (".card-title",        "listing card title"),
    (".card-text",         "listing card description"),
    (".badge",             "category badge"),
]

PRICE_SELECTORS = [
    (".listing-price",     "listing price"),
    (".bid-amount",        "bid amount"),
    (".price",             "price text"),
    (".fw-bold",           "bold text (prices)"),
    (".text-success",      "success-colored text"),
]

FORM_SELECTORS = [
    ("label",              "form label"),
    (".form-control",      "form input"),
    (".form-select",       "form select dropdown"),
    (".btn-primary",       "primary button"),
    (".btn-outline-primary", "outline primary button"),
    (".btn-secondary",     "secondary button"),
]

PAGINATION_SELECTORS = [
    (".page-link",         "pagination link"),
    (".pagination",        "pagination container"),
]

FOOTER_SELECTORS = [
    ("footer",             "footer text"),
    ("footer h5",          "footer heading"),
    ("footer a",           "footer link"),
    ("footer p",           "footer paragraph"),
]


# ── Index page ────────────────────────────────────────────────────────────────


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_index_headings(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/")
    apply_theme(page, theme)

    for selector, description in HEADING_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_index_cards(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/")
    apply_theme(page, theme)

    for selector, description in CARD_SELECTORS + PRICE_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_index_navigation(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/")
    apply_theme(page, theme)

    for selector, description in NAV_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_index_pagination(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/")
    apply_theme(page, theme)

    for selector, description in PAGINATION_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_index_footer(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/")
    apply_theme(page, theme)

    for selector, description in FOOTER_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


# ── Auth pages ────────────────────────────────────────────────────────────────


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_login_form_contrast(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/login")
    apply_theme(page, theme)

    for selector, description in HEADING_SELECTORS + FORM_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_register_form_contrast(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/register")
    apply_theme(page, theme)

    for selector, description in HEADING_SELECTORS + FORM_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


# ── Categories page ───────────────────────────────────────────────────────────


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_categories_page_contrast(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/categories")
    apply_theme(page, theme)

    for selector, description in HEADING_SELECTORS + CARD_SELECTORS + FORM_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)


# ── Listing detail page ───────────────────────────────────────────────────────


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_listing_detail_contrast(
    page: Page, theme: str, first_listing_id: int | None
) -> None:
    if first_listing_id is None:
        pytest.skip("No listings in database — run: make seed")

    page.goto(f"{BASE_URL}/listing/{first_listing_id}")
    apply_theme(page, theme)

    all_selectors = (
        HEADING_SELECTORS
        + CARD_SELECTORS
        + PRICE_SELECTORS
        + FORM_SELECTORS
        + FOOTER_SELECTORS
    )
    for selector, description in all_selectors:
        assert_contrast(page, selector, description, theme=theme)


# ── New auction page (authenticated) ─────────────────────────────────────────


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_new_auction_form_contrast(auth_page: Page, theme: str) -> None:
    auth_page.goto(f"{BASE_URL}/new_auction")
    apply_theme(auth_page, theme)

    for selector, description in HEADING_SELECTORS + FORM_SELECTORS:
        assert_contrast(auth_page, selector, description, theme=theme)


# ── Error pages ───────────────────────────────────────────────────────────────


@pytest.mark.contrast
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_404_page_contrast(page: Page, theme: str) -> None:
    page.goto(f"{BASE_URL}/test/404/")
    apply_theme(page, theme)

    for selector, description in HEADING_SELECTORS + NAV_SELECTORS:
        assert_contrast(page, selector, description, theme=theme)
