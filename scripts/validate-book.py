#!/usr/bin/env python3
"""
validate-book.py
Enforces and highlights structural, anchoring, and indexing problems
in the full Markdown files for doutrina-content.

Focus: LDE and LDM (with extensibility for ESE, CEU, GEN)

Usage examples:
    python scripts/validate-book.py books/md/1-lde/full/1-lde-full.md --book lde
    python scripts/validate-book.py books/md/2-ldm/full/2-ldm-full.md --book ldm --report
"""

import re
import argparse
import io
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Book-specific configuration
BOOK_CONFIG = {
    "lde": {
        "name": "O Livro dos Espíritos",
        "h5_prefix": "q",
        "h5_pattern": r"Q\.\s*(\d+)",
        "index_section_title": "Índice geral",
    },
    "ldm": {
        "name": "O Livro dos Médiuns",
        "h5_prefix": "m",
        "h5_pattern": r"(?:§\s*)?(\d+)",
        "index_section_title": "Índice geral",
    },
}

ROMAN_PATTERN = re.compile(r'\b([IVXLCDM]{2,})\b')
PERSONAL_TITLE_HINTS = ["são", "santo", "luís", "francisco", "agostinho", "vicente", "paulo"]

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'^[🔖📑🗓️🔂#️️\s]+', '', text)
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'õ': 'o', 'ô': 'o',
        'ú': 'u',
        'ç': 'c',
    }
    for acc, plain in replacements.items():
        text = text.replace(acc, plain)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text.strip())
    return text.strip('-')

def is_personal_title(text: str) -> bool:
    text_lower = text.lower()
    return any(hint in text_lower for hint in PERSONAL_TITLE_HINTS)

def analyze_file(md_path: Path, book_code: str):
    if book_code not in BOOK_CONFIG:
        raise ValueError(f"Unknown book code: {book_code}")

    config = BOOK_CONFIG[book_code]
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    issues = defaultdict(list)
    stats = {
        "total_headings": 0,
        "h5_count": 0,
        "h6_count": 0,
        "h6_with_anchor": 0,
        "h5_with_anchor": 0,
        "roman_candidates": 0,
    }

    current_level = 0
    in_index_section = False
    anchors = set()

    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\{#([^}]+)\}', line):
            anchors.add(m.group(1).strip())

        heading_match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{.*?\})?$', line.strip())
        if not heading_match:
            continue

        stats["total_headings"] += 1
        hashes = heading_match.group(1)
        level = len(hashes)
        raw_text = heading_match.group(2).strip()
        clean_text = re.sub(r'^[🔖📑🗓️🔂#️️\s]+', '', raw_text).strip()

        if level > current_level + 1:
            issues["ERROR"].append(f"Line {i:5d}: Heading level jump H{current_level} → H{level} ({clean_text[:60]})")
        current_level = level

        if level == 5:
            stats["h5_count"] += 1
            if re.search(r'\{#', line):
                stats["h5_with_anchor"] += 1
            if not re.search(config["h5_pattern"], clean_text, re.IGNORECASE):
                issues["WARNING"].append(f"Line {i:5d}: H5 does not match expected pattern for {book_code.upper()}: {clean_text[:70]}")

        if level == 6:
            stats["h6_count"] += 1
            if re.search(r'\{#', line):
                stats["h6_with_anchor"] += 1
            if in_index_section:
                anchor_match = re.search(r'\{#([^}]+)\}', line)
                if anchor_match:
                    anchor = anchor_match.group(1)
                    expected = slugify(clean_text)
                    if anchor != expected:
                        issues["WARNING"].append(f"Line {i:5d}: H6 anchor mismatch. Got '{anchor}', expected '{expected}'")
                else:
                    issues["ERROR"].append(f"Line {i:5d}: H6 index term missing explicit anchor: {clean_text[:70]}")

        if config["index_section_title"].lower() in clean_text.lower() and level <= 3:
            in_index_section = True

        if level >= 5:
            for r in ROMAN_PATTERN.findall(clean_text):
                if not is_personal_title(clean_text):
                    stats["roman_candidates"] += 1
                    issues["INFO"].append(f"Line {i:5d}: Possible Roman numeral to convert: '{r}' in '{clean_text[:60]}'")

    if stats["h6_count"] > 0 and stats["h6_with_anchor"] < stats["h6_count"] * 0.9:
        issues["WARNING"].append(f"Many H6 index terms are missing explicit anchors ({stats['h6_with_anchor']}/{stats['h6_count']})")

    if stats["roman_candidates"] > 0:
        issues["INFO"].append(f"Found {stats['roman_candidates']} potential Roman numerals (review for personal titles).")

    return {
        "stats": stats,
        "issues": dict(issues),
        "anchors_found": len(anchors),
    }

def run_validation(md_path: Path, book_code: str):
    """Run analysis and return (console_output, result_dict)"""
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = buffer

    try:
        print(f"🔍 Validating {md_path} as {book_code.upper()}...\n")
        result = analyze_file(md_path, book_code)

        stats = result["stats"]
        issues = result["issues"]

        print("=== SUMMARY ===")
        print(f"Total headings:     {stats['total_headings']}")
        print(f"H5 units found:     {stats['h5_count']}  (with anchors: {stats['h5_with_anchor']})")
        print(f"H6 index terms:     {stats['h6_count']}  (with anchors: {stats['h6_with_anchor']})")
        print(f"Unique anchors:     {result['anchors_found']}")
        print()

        severity_order = ["ERROR", "WARNING", "INFO"]
        has_problems = False

        for sev in severity_order:
            if sev in issues and issues[sev]:
                has_problems = True
                print(f"⚠️  {sev} ({len(issues[sev])})")
                for msg in issues[sev][:30]:
                    print(f"    {msg}")
                if len(issues[sev]) > 30:
                    print(f"    ... and {len(issues[sev]) - 30} more")
                print()

        if not has_problems:
            print("✅ No major structural or anchoring issues detected.")

        return buffer.getvalue(), result
    finally:
        sys.stdout = original_stdout

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", help="Path to *-full.md file")
    parser.add_argument("--book", choices=["lde", "ldm"], required=True)
    parser.add_argument("--report", action="store_true", help="Write full report to reports/ folder")
    args = parser.parse_args()

    if args.file:
        md_path = Path(args.file)
    else:
        md_path = Path(f"books/md/{args.book}/full/{args.book}-full.md")

    if not md_path.exists():
        print(f"❌ File not found: {md_path}")
        return

    output, result = run_validation(md_path, args.book)

    # Always print to console
    print(output, end="")

    if args.report:
        report_dir = Path("reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = report_dir / f"validation_{args.book}_{timestamp}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Validation Report - {args.book.upper()}\n")
            f.write(f"File: {md_path}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(output)

        print(f"\n📋 Full report written to: {report_path}")

if __name__ == "__main__":
    main()
