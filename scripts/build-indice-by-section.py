#!/usr/bin/env python3
"""
Build indice-by-section.md using the two files you provided
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

FULL_BOOK = PROJECT_ROOT / "lde-minus-indice.md"      # book without index
INDEX_FILE = PROJECT_ROOT / "indice-minus-lde.md"    # only the index
OUTPUT_FILE = PROJECT_ROOT / "indice-by-section.md"

def main():
    print("🔄 Building indice-by-section.md...")

    # Load index terms
    terms = {}
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("🏷️ "):
                term = line[4:].strip()
                terms[term] = []
            elif term and line and not line.startswith("🏷️"):
                match = re.search(r'\[#([^\]]+)\]', line)
                if match:
                    terms[term].append(match.group(1))

    print(f"✅ Loaded {len(terms)} terms from index.")

    # Load full book and split into sections
    with open(FULL_BOOK, encoding="utf-8") as f:
        book_content = f.read()

    output = ["# Índice de Termos por Seção\n"]

    # Find major sections (## or ###)
    section_pattern = re.compile(r'^(#{2,4})\s+(.+?)(?:\s*{#|$)', re.MULTILINE)
    sections = list(section_pattern.finditer(book_content))

    for i, match in enumerate(sections):
        title = match.group(2).strip()
        start = match.start()
        
        # Find end of this section (next heading)
        end = sections[i+1].start() if i+1 < len(sections) else len(book_content)
        section_text = book_content[start:end].lower()

        # Find matching terms
        found = []
        for term in terms:
            if term.lower() in section_text:
                found.append(term)

        if found:
            output.append(f"## {title}\n")
            for term in sorted(found)[:25]:
                anchor = terms[term][0] if terms[term] else ""
                output.append(f"🏷️ [{term}](#{anchor})")
            output.append("\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"✅ Successfully created: {OUTPUT_FILE}")
    print("You can now open it.")

if __name__ == "__main__":
    main()