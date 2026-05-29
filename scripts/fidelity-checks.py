#!/usr/bin/env python3
"""
fidelity-checks.py
Exhaustive fidelity checks between source PDFs and Markdown content
for the doutrina.org project.

Currently focused on LDE, designed to be extended to other books.

Usage:
    python scripts/fidelity-checks.py --book lde --check index-fidelity
    python scripts/fidelity-checks.py --book lde --check all --report
"""

import argparse
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import fitz  # pymupdf

# ============== CONFIG ==============
BOOKS = {
    "lde": {
        "name": "O Livro dos Espíritos",
        "pdf": "books/pdf/1-Livro-dos-Espíritos.pdf",
        "md_full": "books/md/1-lde/full/1-lde-full.md",
        "md_dir": "books/md/1-lde",
    }
}

# ============== HELPERS ==============
def load_md(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def extract_index_terms_from_md(md_text: str) -> list[str]:
    """Extract all H6 terms from the 'Índice geral' section."""
    match = re.search(
        r"Índice geral.*?(?=^## |^# |\Z)", 
        md_text, 
        re.DOTALL | re.MULTILINE | re.IGNORECASE
    )
    if not match:
        return []
    
    index_text = match.group(0)
    terms = re.findall(
        r"^######\s+🔖\s+(.+?)(?:\s*\{#.*?\})?$", 
        index_text, 
        re.MULTILINE
    )
    return [t.strip() for t in terms if t.strip()]

def extract_index_terms_from_pdf(pdf_path: Path) -> list[str]:
    """
    High-accuracy extractor for the detailed alphabetical Índice Geral
    in the 2020 FEB historical edition of O Livro dos Espíritos.

    Based on actual geometry analysis of the real index (pages 527+):
    - Main terms: x0 ≈ 42.5, size ≈ 10.0
    - Sub-entries: x0 ≈ 53.9, size ≈ 9.0
    """
    doc = fitz.open(str(pdf_path))

    # Find pages containing "Índice geral"
    index_pages = []
    for i, page in enumerate(doc):
        if "Índice geral" in page.get_text():
            index_pages.append(i)

    if not index_pages:
        doc.close()
        return []

    # Use only the last occurrence (the real detailed alphabetical index at the back)
    start_page = max(index_pages)

    terms = []

    for page_num in range(start_page, len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict", flags=11)["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                spans = line.get("spans", [])
                if not spans:
                    continue

                span = spans[0]
                text = span["text"].strip()
                size = round(span["size"], 1)
                x0 = round(line["bbox"][0], 1)

                if len(text) < 3 or len(text) > 75:
                    continue
                if not text[0].isupper() or text[0].isdigit():
                    continue

                # Main entry criteria for this specific PDF (very reliable)
                is_main_x0 = 38 <= x0 <= 48
                is_main_size = 9.7 <= size <= 10.3

                if not (is_main_x0 and is_main_size):
                    continue

                # Clean trailing page numbers and references
                cleaned = re.sub(r"\s+\d+[a-z]?\s*$", "", text)
                cleaned = re.sub(r"\s+[–—-]\s*\d+.*$", "", cleaned)
                cleaned = cleaned.strip(".,;:").strip()

                if cleaned and 3 <= len(cleaned) <= 65:
                    terms.append(cleaned)

    doc.close()

    # Deduplicate preserving order
    seen = set()
    unique = []
    for t in terms:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique
