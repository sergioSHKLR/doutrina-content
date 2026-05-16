#!/usr/bin/env python3
"""
Simple script: Parse 6.02 and group terms by section
"""

from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent
PARTIAL_DIR = PROJECT_ROOT / "books/md/1-lde/partial"
INDEX_FILE = PARTIAL_DIR / "lde-6.md"

def main():
    print("🔍 Parsing master index (6.02) and grouping terms by section...\n")

    # Load all terms from lde-6.md
    terms = {}
    current_term = None

    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("🏷️ "):
                current_term = line[4:].strip()
                terms[current_term] = []
            elif current_term and line and not line.startswith("🏷️"):
                match = re.search(r'\[#([^\]]+)\]', line)
                if match:
                    terms[current_term].append(match.group(1))

    print(f"✅ Loaded {len(terms)} unique terms from 6.02\n")

    # Now check which terms appear in each section
    print("📊 Terms grouped by section:\n")

    for i in range(6):  # lde-0.md to lde-5.md
        section_file = PARTIAL_DIR / f"lde-{i}.md"
        if not section_file.exists():
            continue

        content = section_file.read_text(encoding="utf-8").lower()
        section_name = f"Section {i} (lde-{i}.md)"

        print(f"→ {section_name}")
        found = []

        for term in terms:
            if term.lower() in content:
                found.append(term)

        if found:
            for term in sorted(found)[:25]:   # limit display
                print(f"   • {term}")
            if len(found) > 25:
                print(f"   ... and {len(found)-25} more")
        else:
            print("   (no terms found)")

        print()

    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()