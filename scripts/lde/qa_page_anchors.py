#!/usr/bin/env python3
"""
QA: page anchors must be sequential without gaps (except allowlisted blank/TOC).

  ./venv/bin/python scripts/lde/qa_page_anchors.py
  ./venv/bin/python scripts/lde/qa_page_anchors.py --from 84 --to 477
  ./venv/bin/python scripts/lde/qa_page_anchors.py --md books/md/1-lde/full/1-lde-full.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from page_anchor_exceptions import (  # noqa: E402
    ALLOWED_MISSING_PAGES,
    PART_RANGES,
    is_allowed_gap,
)

PAGE_ANCHOR_RE = re.compile(r"\[\]\{#page-(\d+)\}")
DEFAULT_MD = REPO_ROOT / "books/md/1-lde/full/1-lde-full.md"


def collect_anchors(md: str) -> list[tuple[int, int]]:
    """Return list of (page, char_offset) in document order."""
    return [(int(m.group(1)), m.start()) for m in PAGE_ANCHOR_RE.finditer(md)]


def qa(
    md: str,
    *,
    page_from: int,
    page_to: int,
) -> dict:
    pairs = [(p, off) for p, off in collect_anchors(md) if page_from <= p <= page_to]
    counts = Counter(p for p, _ in pairs)
    dups = sorted(p for p, n in counts.items() if n > 1)

    present = set(counts)
    missing = [p for p in range(page_from, page_to + 1) if p not in present]
    missing_allowed = [p for p in missing if is_allowed_gap(p)]
    missing_bad = [p for p in missing if not is_allowed_gap(p)]

    # Document order: page numbers must be non-decreasing along the file
    # (strictly increasing after collapsing dups). Allow going "backward"
    # only outside our window.
    order_errors: list[str] = []
    last_page = None
    last_off = -1
    for p, off in pairs:
        if off < last_off:
            order_errors.append(f"offset went backward at page {p} (pos {off})")
        if last_page is not None and p < last_page:
            order_errors.append(
                f"page number decreased in file order: {last_page} → {p} (pos {off})"
            )
        if last_page is not None and p == last_page:
            order_errors.append(f"duplicate page {p} in sequence at pos {off}")
        if last_page is not None and p > last_page + 1:
            gap = list(range(last_page + 1, p))
            bad = [g for g in gap if not is_allowed_gap(g)]
            if bad:
                order_errors.append(
                    f"gap {last_page}→{p}: missing {bad} (not in allowlist)"
                )
        last_page = p
        last_off = off

    # Strict coverage: every non-allowlisted page in range must appear once
    ok = not dups and not missing_bad and not order_errors

    return {
        "ok": ok,
        "page_from": page_from,
        "page_to": page_to,
        "anchors_in_range": len(pairs),
        "unique": len(present),
        "duplicates": dups,
        "missing_allowed": missing_allowed,
        "missing_bad": missing_bad,
        "order_errors": order_errors[:50],
        "order_error_count": len(order_errors),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="QA sequential page anchors")
    ap.add_argument("--md", type=Path, default=DEFAULT_MD)
    ap.add_argument("--from", dest="page_from", type=int, default=None)
    ap.add_argument("--to", dest="page_to", type=int, default=None)
    ap.add_argument(
        "--parts",
        type=str,
        default=None,
        help="comma-separated part numbers, e.g. 2,3,4,5 (overrides --from/--to)",
    )
    args = ap.parse_args()

    md_path = args.md if args.md.is_absolute() else REPO_ROOT / args.md
    text = md_path.read_text(encoding="utf-8")

    if args.parts:
        ranges = []
        for part in args.parts.split(","):
            part_i = int(part.strip())
            if part_i not in PART_RANGES:
                print(f"Unknown part {part_i}", file=sys.stderr)
                return 2
            ranges.append(PART_RANGES[part_i])
        page_from = min(a for a, _ in ranges)
        page_to = max(b for _, b in ranges)
    else:
        all_pages = [int(x) for x in PAGE_ANCHOR_RE.findall(text)]
        page_from = args.page_from or (min(all_pages) if all_pages else 1)
        page_to = args.page_to or (max(all_pages) if all_pages else 1)

    report = qa(text, page_from=page_from, page_to=page_to)

    print(f"MD: {md_path}")
    print(f"Range: {report['page_from']}–{report['page_to']}")
    print(f"Anchors in range: {report['anchors_in_range']} unique={report['unique']}")
    print(f"Allowlist size: {len(ALLOWED_MISSING_PAGES)}")
    if report["duplicates"]:
        print(f"DUPLICATES ({len(report['duplicates'])}): {report['duplicates'][:40]}")
    if report["missing_allowed"]:
        print(
            f"Missing (allowed blank/TOC): {report['missing_allowed'][:40]}"
            + ("…" if len(report["missing_allowed"]) > 40 else "")
        )
    if report["missing_bad"]:
        print(
            f"Missing (BAD gaps): {report['missing_bad'][:40]}"
            + ("…" if len(report["missing_bad"]) > 40 else "")
        )
    if report["order_errors"]:
        print(f"Order errors ({report['order_error_count']}):")
        for e in report["order_errors"][:20]:
            print(f"  - {e}")
    print("-" * 60)
    if report["ok"]:
        print("QA PASS: sequential numbering OK (allowlisted gaps only).")
        return 0
    print("QA FAIL: fix duplicates, bad gaps, or out-of-order anchors.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
