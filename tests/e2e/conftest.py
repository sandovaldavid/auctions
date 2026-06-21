"""
Shared fixtures for Playwright E2E tests.

Requires the dev stack running: make up && make seed
Then run tests via: make test-e2e  (inside Docker)
Or locally: pytest tests/e2e/ --browser chromium --base-url http://localhost:8000
"""

from __future__ import annotations

import os
import re
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
SEED_USER = "seed_buyer1"
SEED_PASSWORD = "TestPass123!"
ADMIN_USER = "seed_admin"

VIEWPORTS = {
    "mobile": {"width": 375, "height": 667},
    "tablet": {"width": 768, "height": 1024},
    "desktop": {"width": 1280, "height": 800},
}

AXE_PATH = Path(__file__).parent / "fixtures" / "axe.min.js"
AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"


# ── axe-core setup ────────────────────────────────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def ensure_axe_js() -> None:
    """Download axe.min.js once per session if not already present."""
    if not AXE_PATH.exists():
        AXE_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(AXE_CDN, str(AXE_PATH))
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"Could not download axe-core ({exc}). Run: make download-axe")


# ── base_url override ─────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


# ── theme helpers ─────────────────────────────────────────────────────────────


def apply_theme(page: Page, theme: str) -> None:
    """Inject data-theme attribute and let CSS transitions settle."""
    page.evaluate(f"document.body.setAttribute('data-theme', '{theme}')")
    page.wait_for_timeout(150)


def run_axe(page: Page) -> dict:
    """Inject axe-core and run a WCAG 2.1 AA audit. Returns the axe result object."""
    page.add_script_tag(path=str(AXE_PATH))
    return page.evaluate(
        "axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa']}})"
    )


# ── viewport fixtures ─────────────────────────────────────────────────────────


@pytest.fixture(params=["mobile", "tablet", "desktop"], ids=["mobile", "tablet", "desktop"])
def viewport_name(request) -> str:
    return request.param


@pytest.fixture
def sized_page(browser: Browser, viewport_name: str) -> Page:
    """A fresh page sized to the given viewport."""
    vp = VIEWPORTS[viewport_name]
    context = browser.new_context(viewport=vp)
    page = context.new_page()
    yield page
    context.close()


# ── authenticated page fixtures ───────────────────────────────────────────────


def _login(page: Page, username: str, password: str) -> None:
    page.goto(f"{BASE_URL}/login")
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    page.wait_for_selector("input[name='username']", timeout=10000)
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_load_state("domcontentloaded", timeout=10000)


@pytest.fixture
def auth_page(page: Page) -> Page:
    """Page with seed_buyer1 logged in."""
    _login(page, SEED_USER, SEED_PASSWORD)
    return page


@pytest.fixture
def admin_page(page: Page) -> Page:
    """Page with seed_admin logged in."""
    _login(page, ADMIN_USER, SEED_PASSWORD)
    return page


# ── listing discovery ─────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def first_listing_id(browser: Browser) -> int | None:
    """Scrape the index page to find the first available listing ID."""
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{BASE_URL}/")
    page.wait_for_load_state("domcontentloaded", timeout=10000)

    listing_id = None
    for selector in ["a[href*='/listing/']", "a[href^='/listing/']"]:
        for link in page.locator(selector).all():
            href = link.get_attribute("href") or ""
            m = re.search(r"/listing/(\d+)", href)
            if m:
                listing_id = int(m.group(1))
                break
        if listing_id:
            break

    context.close()
    return listing_id
