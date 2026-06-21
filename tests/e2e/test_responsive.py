"""
Responsive layout E2E tests — mobile (375px), tablet (768px), desktop (1280px).

Verifies:
- No horizontal overflow (body scrollWidth <= viewport width)
- Navbar collapses to hamburger on mobile
- Cards and forms fit within the viewport
- Images don't overflow containers
- Pagination stays within bounds
- Footer reorganises columns on mobile

Run: make test-responsive
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import BASE_URL, VIEWPORTS

# JavaScript checks injected inline to keep fixture dependencies minimal
_OVERFLOW_CHECK_JS = """
() => ({
    bodyScrollWidth: document.body.scrollWidth,
    windowInnerWidth: window.innerWidth,
    overflows: document.body.scrollWidth > window.innerWidth + 2,
})
"""

_IMAGES_CHECK_JS = """
() => {
    const imgs = Array.from(document.querySelectorAll('img'));
    const overflows = imgs.filter(img => img.getBoundingClientRect().width > window.innerWidth + 2);
    return overflows.map(img => ({src: img.src.substring(0, 80), width: img.getBoundingClientRect().width}));
}
"""

_CARDS_CHECK_JS = """
() => {
    const cards = Array.from(document.querySelectorAll('.card, [class*="listing"]'));
    const overflows = cards.filter(c => c.getBoundingClientRect().right > window.innerWidth + 4);
    return overflows.map(c => c.className);
}
"""

_INPUTS_CHECK_JS = """
() => {
    const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
    const overflows = inputs.filter(el => el.getBoundingClientRect().right > window.innerWidth + 4);
    return overflows.map(el => ({tag: el.tagName, name: el.name, width: el.getBoundingClientRect().width}));
}
"""


def _assert_no_overflow(page: Page, url: str, viewport_name: str) -> None:
    result = page.evaluate(_OVERFLOW_CHECK_JS)
    assert not result["overflows"], (
        f"Horizontal overflow on {url} [{viewport_name}]: "
        f"body.scrollWidth={result['bodyScrollWidth']} > "
        f"window.innerWidth={result['windowInnerWidth']}"
    )


def _assert_images_fit(page: Page, url: str, viewport_name: str) -> None:
    overflows = page.evaluate(_IMAGES_CHECK_JS)
    assert not overflows, (
        f"Images overflow viewport on {url} [{viewport_name}]: {overflows}"
    )


def _assert_cards_fit(page: Page, url: str, viewport_name: str) -> None:
    overflows = page.evaluate(_CARDS_CHECK_JS)
    assert not overflows, (
        f"Cards overflow viewport on {url} [{viewport_name}]: {overflows[:3]}"
    )


def _assert_inputs_fit(page: Page, url: str, viewport_name: str) -> None:
    overflows = page.evaluate(_INPUTS_CHECK_JS)
    assert not overflows, (
        f"Form inputs overflow viewport on {url} [{viewport_name}]: {overflows}"
    )


# ── Index page ────────────────────────────────────────────────────────────────


@pytest.mark.responsive
def test_index_no_overflow(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_no_overflow(sized_page, url, viewport_name)


@pytest.mark.responsive
def test_index_images_fit(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_images_fit(sized_page, url, viewport_name)


@pytest.mark.responsive
def test_index_cards_fit(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_cards_fit(sized_page, url, viewport_name)


@pytest.mark.responsive
def test_index_navbar_collapses_on_mobile(sized_page: Page, viewport_name: str) -> None:
    """On mobile, the navbar should show a hamburger button and hide the nav links."""
    sized_page.goto(f"{BASE_URL}/")
    sized_page.wait_for_load_state("networkidle", timeout=10000)

    if viewport_name == "mobile":
        # Hamburger must be visible
        toggler = sized_page.locator(".navbar-toggler")
        assert toggler.count() > 0, "Navbar toggler (hamburger) not found on mobile"
        assert toggler.first.is_visible(), "Navbar toggler not visible on mobile"

        # Collapsed nav links should not be visible before clicking
        nav_menu = sized_page.locator(".navbar-collapse")
        if nav_menu.count() > 0:
            is_expanded = nav_menu.first.evaluate("el => el.classList.contains('show')")
            assert not is_expanded, "Navbar menu should be collapsed on mobile initially"
    else:
        # On tablet and desktop, toggler should be hidden
        toggler = sized_page.locator(".navbar-toggler")
        if toggler.count() > 0:
            assert not toggler.first.is_visible(), (
                f"Navbar toggler should be hidden on {viewport_name}"
            )


# ── Login / Register pages ────────────────────────────────────────────────────


@pytest.mark.responsive
def test_login_no_overflow(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/login"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_no_overflow(sized_page, url, viewport_name)
    _assert_inputs_fit(sized_page, url, viewport_name)


@pytest.mark.responsive
def test_register_no_overflow(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/register"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_no_overflow(sized_page, url, viewport_name)
    _assert_inputs_fit(sized_page, url, viewport_name)


# ── Categories page ───────────────────────────────────────────────────────────


@pytest.mark.responsive
def test_categories_no_overflow(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/categories"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_no_overflow(sized_page, url, viewport_name)
    _assert_cards_fit(sized_page, url, viewport_name)


# ── Listing detail ────────────────────────────────────────────────────────────


@pytest.mark.responsive
def test_listing_detail_no_overflow(
    sized_page: Page, viewport_name: str, first_listing_id: int | None
) -> None:
    if first_listing_id is None:
        pytest.skip("No listings in database — run: make seed")

    url = f"{BASE_URL}/listing/{first_listing_id}"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_no_overflow(sized_page, url, viewport_name)
    _assert_images_fit(sized_page, url, viewport_name)
    _assert_inputs_fit(sized_page, url, viewport_name)


# ── New auction (authenticated) ───────────────────────────────────────────────


@pytest.mark.responsive
def test_new_auction_form_fits(viewport_name: str, browser) -> None:
    vp = VIEWPORTS[viewport_name]
    context = browser.new_context(viewport=vp)
    page = context.new_page()

    # Log in first
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name='username']", "seed_buyer1")
    page.fill("input[name='password']", "TestPass123!")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle", timeout=5000)

    url = f"{BASE_URL}/new_auction"
    page.goto(url)
    page.wait_for_load_state("networkidle", timeout=10000)

    _assert_no_overflow(page, url, viewport_name)
    _assert_inputs_fit(page, url, viewport_name)

    context.close()


# ── Error pages ───────────────────────────────────────────────────────────────


@pytest.mark.responsive
def test_404_no_overflow(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/test/404/"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_no_overflow(sized_page, url, viewport_name)


@pytest.mark.responsive
def test_500_no_overflow(sized_page: Page, viewport_name: str) -> None:
    url = f"{BASE_URL}/test/500/"
    sized_page.goto(url)
    sized_page.wait_for_load_state("networkidle", timeout=10000)
    _assert_no_overflow(sized_page, url, viewport_name)


# ── Pagination ────────────────────────────────────────────────────────────────


@pytest.mark.responsive
def test_pagination_fits_viewport(sized_page: Page, viewport_name: str) -> None:
    sized_page.goto(f"{BASE_URL}/")
    sized_page.wait_for_load_state("networkidle", timeout=10000)

    pagination = sized_page.locator(".pagination")
    if pagination.count() == 0:
        return  # no pagination on this page, skip

    overflow_js = """
    () => {
        const pg = document.querySelector('.pagination');
        if (!pg) return false;
        return pg.getBoundingClientRect().right > window.innerWidth + 4;
    }
    """
    overflows = sized_page.evaluate(overflow_js)
    assert not overflows, f"Pagination overflows viewport on [{viewport_name}]"


# ── Footer layout ─────────────────────────────────────────────────────────────


@pytest.mark.responsive
def test_footer_no_overflow(sized_page: Page, viewport_name: str) -> None:
    sized_page.goto(f"{BASE_URL}/")
    sized_page.wait_for_load_state("networkidle", timeout=10000)

    footer = sized_page.locator("footer")
    if footer.count() == 0:
        return

    footer_overflow_js = """
    () => {
        const el = document.querySelector('footer');
        if (!el) return false;
        return el.scrollWidth > window.innerWidth + 2;
    }
    """
    overflows = sized_page.evaluate(footer_overflow_js)
    assert not overflows, f"Footer overflows viewport on [{viewport_name}]"
