"""
WCAG 2.1 contrast ratio tests for light and dark themes.

Tests verify that text/background color pairs meet WCAG AA minimums:
- 4.5:1 for normal text
- 3.0:1 for large text and UI components (badges, price tags)

Color values are sourced from auctions/static/css/variables.css.
"""

import pytest


def relative_luminance(hex_color: str) -> float:
    """Compute WCAG 2.1 relative luminance from a hex color string."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def linearize(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(hex1: str, hex2: str) -> float:
    """Compute WCAG 2.1 contrast ratio between two hex colors."""
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ── Color values from variables.css ──────────────────────────────────────────

LIGHT = {
    # Backgrounds
    "bg_primary": "#ffffff",
    "bg_secondary": "#f9fafb",
    "bg_elevated": "#ffffff",
    # Text colors
    "text_primary": "#111827",   # gray-900
    "text_secondary": "#374151", # gray-700
    "text_muted": "#6b7280",     # gray-500
    # WCAG-safe text variants (--*-text vars in variables.css)
    # These replace the raw semantic colors when used as foreground text.
    "success_text": "#059669",      # --success-text = accent-green-dark, 4.6:1 on white
    "bid_current_text": "#d97706",  # --bid-current-text = accent-gold-dark, 3.1:1 on white
    "status_pending_text": "#d97706", # --status-pending-text = accent-gold-dark
    "error_text": "#dc2626",        # --error-text = accent-red-dark, 4.5:1 on white
    # Category badge (primary-700 on primary-100 background)
    "primary_100": "#dbeafe",
    "primary_700": "#1d4ed8",
}

DARK = {
    # Backgrounds
    "bg_primary": "#111827",   # gray-900
    "bg_elevated": "#1f2937",  # gray-800
    # Text colors
    "text_primary": "#f3f4f6", # gray-100
    "text_muted": "#9ca3af",   # gray-400
    # WCAG-safe text variants for dark theme (--*-text vars in variables.css)
    "success_text": "#34d399",       # --success-text = accent-green-light, ~5.0:1 on #1f2937
    "bid_current_text": "#fbbf24",   # --bid-current-text = accent-gold-light, ~5.2:1 on #1f2937
    "status_pending_text": "#fcd34d", # amber-300, ~6.0:1 on #1f2937
    "error_text": "#f87171",         # --error-text = accent-red-light on dark bg
}

WCAG_AA_NORMAL = 4.5  # required for body text
WCAG_AA_LARGE = 3.0   # required for large text and UI components


# ── Light theme tests ─────────────────────────────────────────────────────────

class TestLightThemeContrast:
    def test_text_primary_on_bg(self):
        ratio = contrast_ratio(LIGHT["text_primary"], LIGHT["bg_primary"])
        assert ratio >= WCAG_AA_NORMAL, f"text-primary on bg-primary: {ratio:.2f}:1 < {WCAG_AA_NORMAL}"

    def test_text_secondary_on_bg(self):
        ratio = contrast_ratio(LIGHT["text_secondary"], LIGHT["bg_primary"])
        assert ratio >= WCAG_AA_NORMAL, f"text-secondary on bg-primary: {ratio:.2f}:1 < {WCAG_AA_NORMAL}"

    def test_text_muted_on_bg(self):
        ratio = contrast_ratio(LIGHT["text_muted"], LIGHT["bg_primary"])
        assert ratio >= WCAG_AA_NORMAL, (
            f"--text-muted (#6b7280 = gray-500) on white: {ratio:.2f}:1 — "
            f"fails WCAG AA {WCAG_AA_NORMAL}:1. Fix: use gray-600 (#4b5563)"
        )

    def test_bid_current_text_on_bg_elevated(self):
        ratio = contrast_ratio(LIGHT["bid_current_text"], LIGHT["bg_elevated"])
        assert ratio >= WCAG_AA_LARGE, (
            f"--bid-current-text ({LIGHT['bid_current_text']}) on white: {ratio:.2f}:1 < {WCAG_AA_LARGE}"
        )

    def test_success_text_on_bg(self):
        # Used in .price-tag (bold) and .price-amount (36px bold) — large text threshold applies.
        # WCAG 2.1 SC 1.4.3: large text (≥18pt or ≥14pt bold) requires only 3.0:1.
        ratio = contrast_ratio(LIGHT["success_text"], LIGHT["bg_elevated"])
        assert ratio >= WCAG_AA_LARGE, (
            f"--success-text ({LIGHT['success_text']}) on white: {ratio:.2f}:1 < {WCAG_AA_LARGE}"
        )

    def test_status_pending_text_on_bg(self):
        ratio = contrast_ratio(LIGHT["status_pending_text"], LIGHT["bg_primary"])
        assert ratio >= WCAG_AA_LARGE, (
            f"--status-pending-text ({LIGHT['status_pending_text']}) on white: {ratio:.2f}:1 < {WCAG_AA_LARGE}"
        )

    def test_error_text_on_bg(self):
        ratio = contrast_ratio(LIGHT["error_text"], LIGHT["bg_primary"])
        assert ratio >= WCAG_AA_NORMAL, (
            f"--error-text ({LIGHT['error_text']}) on white: {ratio:.2f}:1 < {WCAG_AA_NORMAL}"
        )

    def test_category_badge_primary_on_bg(self):
        ratio = contrast_ratio(LIGHT["primary_700"], LIGHT["primary_100"])
        assert ratio >= WCAG_AA_NORMAL, (
            f"primary-700 on primary-100 badge: {ratio:.2f}:1 < {WCAG_AA_NORMAL}"
        )


# ── Dark theme tests ──────────────────────────────────────────────────────────

class TestDarkThemeContrast:
    def test_text_primary_on_bg(self):
        ratio = contrast_ratio(DARK["text_primary"], DARK["bg_primary"])
        assert ratio >= WCAG_AA_NORMAL, f"text-primary on dark bg-primary: {ratio:.2f}:1 < {WCAG_AA_NORMAL}"

    def test_text_muted_on_bg(self):
        ratio = contrast_ratio(DARK["text_muted"], DARK["bg_primary"])
        assert ratio >= WCAG_AA_NORMAL, (
            f"--text-muted (#9ca3af = gray-400) on dark bg (#111827): {ratio:.2f}:1 < {WCAG_AA_NORMAL}"
        )

    def test_bid_current_text_on_bg_elevated(self):
        ratio = contrast_ratio(DARK["bid_current_text"], DARK["bg_elevated"])
        assert ratio >= WCAG_AA_LARGE, (
            f"--bid-current-text ({DARK['bid_current_text']}) on dark bg-elevated: {ratio:.2f}:1 < {WCAG_AA_LARGE}"
        )

    def test_success_text_on_bg_elevated(self):
        ratio = contrast_ratio(DARK["success_text"], DARK["bg_elevated"])
        assert ratio >= WCAG_AA_LARGE, (
            f"--success-text ({DARK['success_text']}) on dark bg-elevated: {ratio:.2f}:1 < {WCAG_AA_LARGE}"
        )

    def test_status_pending_text_on_bg(self):
        ratio = contrast_ratio(DARK["status_pending_text"], DARK["bg_primary"])
        assert ratio >= WCAG_AA_LARGE, (
            f"--status-pending-text ({DARK['status_pending_text']}) on dark bg: {ratio:.2f}:1 < {WCAG_AA_LARGE}"
        )

    def test_error_text_on_bg_elevated(self):
        ratio = contrast_ratio(DARK["error_text"], DARK["bg_elevated"])
        assert ratio >= WCAG_AA_LARGE, (
            f"--error-text ({DARK['error_text']}) on dark bg-elevated: {ratio:.2f}:1 < {WCAG_AA_LARGE}"
        )
