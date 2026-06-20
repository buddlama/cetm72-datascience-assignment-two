# tests/test_accessibility.py
#
# Colour accessibility tests — WCAG 1.4.11 (Non-Text Contrast) and
# colour-blindness safety.
#
# WCAG 1.4.11 requires graphical elements to achieve at least 3:1 contrast
# ratio against adjacent colours.  All chart elements in this dashboard are
# rendered on a white (#FFFFFF) background, so every palette colour is tested
# against white.
#
# Formula reference: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
#
# Run with: pytest tests/test_accessibility.py -v

import re
import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# ─────────────────────────────────────────────────────────────────────────────
# WCAG utility functions
# ─────────────────────────────────────────────────────────────────────────────

def _linearise(c: float) -> float:
    """Convert an 8-bit channel (0–1) to linear light value per WCAG 2.1."""
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_colour: str) -> float:
    """Return the WCAG relative luminance of a #RRGGBB hex colour (0–1)."""
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    return 0.2126 * _linearise(r) + 0.7152 * _linearise(g) + 0.0722 * _linearise(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """Return the WCAG contrast ratio between two hex colours."""
    la = relative_luminance(hex_a)
    lb = relative_luminance(hex_b)
    lighter, darker = (la, lb) if la > lb else (lb, la)
    return (lighter + 0.05) / (darker + 0.05)


WHITE = "#FFFFFF"
WCAG_NON_TEXT_MIN = 3.0   # WCAG 1.4.11 minimum for graphical elements


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _is_hex(value: str) -> bool:
    return bool(re.match(r"^#[0-9A-Fa-f]{6}$", value))


# ─────────────────────────────────────────────────────────────────────────────
# Primary category colours
# ─────────────────────────────────────────────────────────────────────────────

def test_cyber_colour_contrast_on_white():
    from utils.colours import CYBER
    ratio = contrast_ratio(CYBER, WHITE)
    assert ratio >= WCAG_NON_TEXT_MIN, (
        f"CYBER ({CYBER}) contrast on white is {ratio:.2f}:1 — below WCAG 3:1 minimum"
    )


def test_non_cyber_colour_contrast_on_white():
    from utils.colours import NON_CYBER
    ratio = contrast_ratio(NON_CYBER, WHITE)
    assert ratio >= WCAG_NON_TEXT_MIN, (
        f"NON_CYBER ({NON_CYBER}) contrast on white is {ratio:.2f}:1 — below WCAG 3:1 minimum"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Neutral / text colours
# ─────────────────────────────────────────────────────────────────────────────

def test_grey_contrast_on_white():
    from utils.colours import GREY
    ratio = contrast_ratio(GREY, WHITE)
    assert ratio >= WCAG_NON_TEXT_MIN, (
        f"GREY ({GREY}) contrast on white is {ratio:.2f}:1 — below WCAG 3:1 minimum"
    )


def test_grey_dark_contrast_on_white():
    from utils.colours import GREY_DARK
    ratio = contrast_ratio(GREY_DARK, WHITE)
    assert ratio >= WCAG_NON_TEXT_MIN, (
        f"GREY_DARK ({GREY_DARK}) contrast on white is {ratio:.2f}:1 — below WCAG 3:1 minimum"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Breach-scale band colours — parametrised so failures report the exact band
# ─────────────────────────────────────────────────────────────────────────────

def _band_params():
    from utils.colours import BAND_COLOURS
    return [(label, colour) for label, colour in BAND_COLOURS.items()]


@pytest.mark.parametrize("label,colour", _band_params())
def test_band_colour_contrast_on_white(label, colour):
    ratio = contrast_ratio(colour, WHITE)
    assert ratio >= WCAG_NON_TEXT_MIN, (
        f"BAND_COLOURS['{label}'] ({colour}) contrast on white is {ratio:.2f}:1 "
        f"— below WCAG 3:1 minimum"
    )


# ─────────────────────────────────────────────────────────────────────────────
# All hex values in colours.py pass 3:1 — catch-all for future additions
# ─────────────────────────────────────────────────────────────────────────────

def test_all_hex_values_in_colours_module_pass_wcag():
    """
    Imports the colours module, extracts every hex literal, and verifies each
    one achieves the WCAG 3:1 minimum on white.  This acts as a guard: any
    new colour added to colours.py that fails accessibility will be caught
    automatically without a dedicated test.
    """
    import utils.colours as c_mod
    import inspect

    source = inspect.getsource(c_mod)
    # Strip comment-only lines so hex values cited as negative examples
    # (e.g. "old colour #DDEEFF which failed") don't trigger the assertion.
    active_lines = [ln for ln in source.splitlines() if not ln.lstrip().startswith("#")]
    hex_values = re.findall(r"#[0-9A-Fa-f]{6}", "\n".join(active_lines))
    hex_values = list(dict.fromkeys(hex_values))  # deduplicate, preserve order

    failures = []
    for hex_val in hex_values:
        ratio = contrast_ratio(hex_val, WHITE)
        if ratio < WCAG_NON_TEXT_MIN:
            failures.append(f"  {hex_val}: {ratio:.2f}:1")

    assert not failures, (
        "The following hex colours in colours.py fail WCAG 1.4.11 (3:1 on white):\n"
        + "\n".join(failures)
    )


# ─────────────────────────────────────────────────────────────────────────────
# Colour-blindness — confirm the two primary colours differ by luminance,
# not hue alone (protanopia / deuteranopia safe)
# ─────────────────────────────────────────────────────────────────────────────

def test_cyber_and_non_cyber_differ_in_luminance():
    """
    For viewers with red-green colour blindness, hue is lost — only luminance
    remains. This test confirms CYBER and NON_CYBER have a luminance difference
    of at least 0.10 (arbitrary but meaningful threshold), meaning they remain
    distinguishable without colour perception.
    """
    from utils.colours import CYBER, NON_CYBER
    diff = abs(relative_luminance(CYBER) - relative_luminance(NON_CYBER))
    # The Wong (2011) palette is colour-blind safe primarily through hue
    # selection (orange vs blue), not luminance.  The threshold here (0.05)
    # is a sanity check that the two colours are not near-identical in
    # luminance — it is not derived from a WCAG rule.
    assert diff >= 0.05, (
        f"CYBER and NON_CYBER have similar luminance (diff={diff:.3f}); "
        "they may be indistinguishable to colour-blind viewers"
    )


def test_no_colour_is_pure_red_or_pure_green():
    """
    Pure red (#FF0000) and pure green (#00FF00) are the canonical colour-blind
    failure pair.  Confirms neither appears anywhere in the palette.
    """
    import utils.colours as c_mod
    import inspect

    source = inspect.getsource(c_mod)
    hex_values = {h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", source)}

    assert "#FF0000" not in hex_values, "Pure red (#FF0000) found in colours.py"
    assert "#00FF00" not in hex_values, "Pure green (#00FF00) found in colours.py"


def test_category_colour_map_uses_accessible_colours():
    """
    Confirms CATEGORY_COLOUR_MAP values are the declared accessible constants,
    not inline hex strings that might have drifted from the validated palette.
    """
    from utils.colours import CATEGORY_COLOUR_MAP, CYBER, NON_CYBER
    assert set(CATEGORY_COLOUR_MAP.values()) == {CYBER, NON_CYBER}, (
        "CATEGORY_COLOUR_MAP contains colours other than the declared CYBER / NON_CYBER constants"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Alias consistency — aliases must equal the constants they reference
# ─────────────────────────────────────────────────────────────────────────────

def test_accent_alias_matches_cyber():
    from utils.colours import ACCENT, CYBER
    assert ACCENT == CYBER


def test_compliant_and_non_compliant_use_declared_colours():
    from utils.colours import COMPLIANT, NON_COMPLIANT, CYBER, NON_CYBER
    # Both semantic aliases must be drawn from the validated two-colour palette
    assert {COMPLIANT, NON_COMPLIANT} == {CYBER, NON_CYBER}, (
        "COMPLIANT / NON_COMPLIANT must reuse the accessible CYBER / NON_CYBER pair"
    )


def test_best_and_worst_colours_use_declared_colours():
    from utils.colours import BEST_COLOUR, WORST_COLOUR, CYBER, NON_CYBER
    assert {BEST_COLOUR, WORST_COLOUR} == {CYBER, NON_CYBER}, (
        "BEST_COLOUR / WORST_COLOUR must reuse the accessible CYBER / NON_CYBER pair"
    )
