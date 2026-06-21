"""
Accessibility E2E tests using axe-core (WCAG 2.1 AA).

Each test navigates to a page, applies a theme, then runs axe.run() and
asserts that no critical or serious violations exist.

Run: make test-a11y
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import BASE_URL, apply_theme, run_axe

# Impact levels we fail on: critical and serious.
# "moderate" and "minor" are reported but not failed.
FAIL_IMPACTS = {"critical", "serious"}


def _check_axe(page: Page, url: str, theme: str) -> None:
    """Navigate to url, apply theme, run axe, assert no critical/serious violations."""
    page.goto(url)
    apply_theme(page, theme)
    page.wait_for_load_state("networkidle", timeout=10000)

    result = run_axe(page)
    violations = [v for v in result.get("violations", []) if v.get("impact") in FAIL_IMPACTS]

    if violations:
        lines = [f"axe found {len(violations)} WCAG 2.1 AA violations on {url} [{theme} mode]:"]
        for v in violations:
            nodes = ", ".join(
                n["target"][0] if n.get("target") else "?" for n in v.get("nodes", [])[:3]
            )
            lines.append(
                f"  [{v['impact'].upper()}] {v['id']}: {v['description']} — {nodes}"
            )
        pytest.fail("\n".join(lines))


# ── Public pages ──────────────────────────────────────────────────────────────


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_index_a11y(page: Page, theme: str) -> None:
    _check_axe(page, f"{BASE_URL}/", theme)


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_login_a11y(page: Page, theme: str) -> None:
    _check_axe(page, f"{BASE_URL}/login", theme)


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_register_a11y(page: Page, theme: str) -> None:
    _check_axe(page, f"{BASE_URL}/register", theme)


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_categories_a11y(page: Page, theme: str) -> None:
    _check_axe(page, f"{BASE_URL}/categories", theme)


# ── Listing detail ────────────────────────────────────────────────────────────


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_listing_detail_a11y(
    page: Page, theme: str, first_listing_id: int | None
) -> None:
    if first_listing_id is None:
        pytest.skip("No listings in database — run: make seed")
    _check_axe(page, f"{BASE_URL}/listing/{first_listing_id}", theme)


# ── Authenticated pages ───────────────────────────────────────────────────────


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_new_auction_a11y(auth_page: Page, theme: str) -> None:
    auth_page.goto(f"{BASE_URL}/new_auction")
    apply_theme(auth_page, theme)
    auth_page.wait_for_load_state("networkidle", timeout=10000)

    result = run_axe(auth_page)
    violations = [v for v in result.get("violations", []) if v.get("impact") in FAIL_IMPACTS]

    if violations:
        lines = [f"axe found {len(violations)} violations on /new_auction [{theme} mode]:"]
        for v in violations:
            nodes = ", ".join(
                n["target"][0] if n.get("target") else "?" for n in v.get("nodes", [])[:3]
            )
            lines.append(f"  [{v['impact'].upper()}] {v['id']}: {v['description']} — {nodes}")
        pytest.fail("\n".join(lines))


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_watchlist_a11y(auth_page: Page, theme: str) -> None:
    # Navigate to watchlist via index — requires seed data watchlist entries
    auth_page.goto(f"{BASE_URL}/watchlist/1")
    apply_theme(auth_page, theme)
    auth_page.wait_for_load_state("networkidle", timeout=10000)

    result = run_axe(auth_page)
    violations = [v for v in result.get("violations", []) if v.get("impact") in FAIL_IMPACTS]

    if violations:
        lines = [f"axe found {len(violations)} violations on /watchlist [{theme} mode]:"]
        for v in violations:
            nodes = ", ".join(
                n["target"][0] if n.get("target") else "?" for n in v.get("nodes", [])[:3]
            )
            lines.append(f"  [{v['impact'].upper()}] {v['id']}: {v['description']} — {nodes}")
        pytest.fail("\n".join(lines))


# ── Admin pages ───────────────────────────────────────────────────────────────


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_admin_dashboard_a11y(admin_page: Page, theme: str) -> None:
    admin_page.goto(f"{BASE_URL}/admin/dashboard")
    apply_theme(admin_page, theme)
    admin_page.wait_for_load_state("networkidle", timeout=10000)

    result = run_axe(admin_page)
    violations = [v for v in result.get("violations", []) if v.get("impact") in FAIL_IMPACTS]

    if violations:
        lines = [f"axe found {len(violations)} violations on /admin/dashboard [{theme} mode]:"]
        for v in violations:
            nodes = ", ".join(
                n["target"][0] if n.get("target") else "?" for n in v.get("nodes", [])[:3]
            )
            lines.append(f"  [{v['impact'].upper()}] {v['id']}: {v['description']} — {nodes}")
        pytest.fail("\n".join(lines))


# ── Error pages ───────────────────────────────────────────────────────────────


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_404_a11y(page: Page, theme: str) -> None:
    _check_axe(page, f"{BASE_URL}/test/404/", theme)


@pytest.mark.a11y
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_500_a11y(page: Page, theme: str) -> None:
    _check_axe(page, f"{BASE_URL}/test/500/", theme)
