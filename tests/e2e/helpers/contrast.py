"""
WCAG 2.1 contrast ratio helpers for E2E tests.

Computes contrast ratios from live browser computed styles using Playwright.
WCAG AA thresholds: 4.5:1 for normal text, 3.0:1 for large text (≥18pt or ≥14pt bold).
"""

from __future__ import annotations

import re

from playwright.sync_api import Page


def _linearize(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r: int, g: int, b: int) -> float:
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1 = relative_luminance(*fg)
    l2 = relative_luminance(*bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_rgb(color_str: str) -> tuple[int, int, int] | None:
    """Parse 'rgb(r, g, b)' or 'rgba(r, g, b, a)' into an (r, g, b) tuple."""
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", color_str or "")
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


# JavaScript injected into the browser to resolve effective background color.
# Returns null for bgColor when a gradient is found — caller skips the check.
_GET_STYLES_JS = """
(selector) => {
    const el = document.querySelector(selector);
    if (!el) return null;

    function getEffectiveBg(el) {
        let node = el;
        while (node && node !== document.body.parentElement) {
            const style = window.getComputedStyle(node);
            const bgImage = style.backgroundImage;
            // Gradient backgrounds can't be represented as a single solid color.
            if (bgImage && bgImage !== 'none' && bgImage.includes('gradient')) {
                return '__gradient__';
            }
            const bg = style.backgroundColor;
            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                return bg;
            }
            node = node.parentElement;
        }
        return 'rgb(255, 255, 255)';
    }

    const style = window.getComputedStyle(el);
    return {
        color: style.color,
        bgColor: getEffectiveBg(el),
        fontSize: parseFloat(style.fontSize),
        fontWeight: parseInt(style.fontWeight) || 400,
        visible: style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0',
        text: el.textContent.trim().substring(0, 60),
    };
}
"""


def get_element_styles(page: Page, selector: str) -> dict | None:
    """Return computed color, bgColor, fontSize, fontWeight for the first matching element."""
    return page.evaluate(_GET_STYLES_JS, selector)


def is_large_text(font_size_px: float, font_weight: int) -> bool:
    """WCAG definition: ≥18pt (24px) normal weight OR ≥14pt (18.67px) bold."""
    return font_size_px >= 24 or (font_weight >= 700 and font_size_px >= 18.67)


def compute_element_contrast(page: Page, selector: str) -> dict | None:
    """
    Return a dict with contrast info for the given selector, or None if not found.

    Returns None for elements on gradient backgrounds (can't compute single-color ratio).
    Keys: ratio (float), fg (tuple), bg (tuple), large_text (bool), passes_aa (bool),
          selector (str), text (str), required_ratio (float)
    """
    styles = get_element_styles(page, selector)
    if not styles or not styles.get("visible"):
        return None

    # Gradient backgrounds can't be represented as a single color — skip.
    if styles.get("bgColor") == "__gradient__":
        return None

    fg = parse_rgb(styles["color"])
    bg = parse_rgb(styles["bgColor"])
    if not fg or not bg:
        return None

    large = is_large_text(styles["fontSize"], styles["fontWeight"])
    required = 3.0 if large else 4.5
    ratio = contrast_ratio(fg, bg)

    return {
        "selector": selector,
        "text": styles["text"],
        "ratio": ratio,
        "fg": fg,
        "bg": bg,
        "large_text": large,
        "required_ratio": required,
        "passes_aa": ratio >= required,
    }


def assert_contrast(page: Page, selector: str, description: str, *, theme: str = "") -> None:
    """
    Assert that the element at `selector` meets WCAG AA contrast in the current page state.
    Skips gracefully if the element is not found.
    """
    result = compute_element_contrast(page, selector)
    if result is None:
        return  # element absent on this page — not a failure

    mode_label = f" [{theme} mode]" if theme else ""
    assert result["passes_aa"], (
        f"{description}{mode_label}: contrast {result['ratio']:.2f}:1 "
        f"(fg={result['fg']}, bg={result['bg']}) "
        f"— fails WCAG AA (requires {result['required_ratio']}:1). "
        f"Text: \"{result['text']}\""
    )
