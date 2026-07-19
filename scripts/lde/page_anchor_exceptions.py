"""
Allowed gaps in LDE PDF page-anchor sequence.

Pages listed here may be missing `[]{#page-N}` without failing QA.
Includes blank/image plates and TOC-only surfaces where body text
should not receive a start-of-page anchor (or PDF extract is empty).

Edit this set as you confirm more blank/TOC pages against the canonical PDF.
"""

from __future__ import annotations

# Canonical PDF page numbers (1-based) that may lack anchors.
ALLOWED_MISSING_PAGES: set[int] = {
    # --- Part 0 / front matter (often blank, title, or TOC-only) ---
    1,   # cover / plate (often empty extract)
    11,  # sparse / image
    # Add confirmed blank/TOC pages here, e.g.:
    # 2, 3, …
    # --- Structural blanks observed in extract ---
    85,
    115,
    295,
    297,
    317,
    327,
    347,
    351,
    371,
    401,
    413,
    414,
    431,
    477,
    483,
    528,
}

# Part ranges (canonical PDF pages) — for tooling / CLI helpers
PART_RANGES: dict[int, tuple[int, int]] = {
    0: (1, 55),
    1: (56, 83),
    2: (84, 293),
    3: (294, 411),
    4: (412, 461),
    5: (462, 477),
    6: (478, 527),
}


def is_allowed_gap(page: int) -> bool:
    return page in ALLOWED_MISSING_PAGES


def expand_allowed_between(prev: int, nxt: int) -> bool:
    """True if every page in (prev, nxt) is an allowed gap (or empty span)."""
    if nxt <= prev + 1:
        return nxt == prev + 1
    return all(is_allowed_gap(p) for p in range(prev + 1, nxt))
