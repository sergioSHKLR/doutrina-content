#!/usr/bin/env python3
"""
LDE — MD → HTML verification renderer (CLI)
===========================================
Renders full LDE Markdown to books/html/1-lde-text-rendered.html.

    python3 scripts/lde/render_md_to_html.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.chdir(REPO_ROOT)

from md_render import render_md_to_document  # noqa: E402

INPUT_MD = REPO_ROOT / "books/md/1-lde/full/1-lde-full.md"
OUTPUT_HTML = REPO_ROOT / "books/html/1-lde-text-rendered.html"


def main() -> int:
    print("=" * 70)
    print("🚀 LDE: MD → HTML verification render")
    print("=" * 70)

    if not INPUT_MD.is_file():
        print(f"❌ ERROR: Master Markdown missing: {INPUT_MD}")
        return 1

    md_text = INPUT_MD.read_text(encoding="utf-8")
    full_html = render_md_to_document(
        md_text,
        title="O Livro dos Espíritos — Diagramação Real",
        css_href="layout.css",
    )
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(full_html, encoding="utf-8")
    print(f"✅ REGEN SYSTEM COMPLETE -> Output file written to: {OUTPUT_HTML}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
