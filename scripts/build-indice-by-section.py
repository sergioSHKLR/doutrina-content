#!/usr/bin/env python3
"""
Build indice-by-section.md using the FULL lde-full.md
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
FULL_FILE = PROJECT_ROOT / "books/md/1-lde/full/1-lde-full.md"
INDEX_FILE = PROJECT_ROOT / "books/md/1-lde/partial/lde-6.md"
OUTPUT_FILE = PROJECT_ROOT / "indice-by-section.md"

def load_master_index():
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
    return terms

def main():
    master = load_master_index()
    print(f"✅ Loaded {len(master)} terms.")

    content = FULL_FILE.read_text(encoding="utf-8")
    output = ["# Índice de Termos por Seção\n"]

    # Find major sections (## or ### headings)
    sections = re.finditer(r'^(#{2,4})\s+(.+?)(?:\s*{#|$)', content, re.MULTILINE)

    for match in sections:
        level = match.group(1)
        title = match.group(2).strip()
        start = match.start()

        # Get content until next major heading
        next_match = re.search(r'^(#{2,4})\s+', content[start+1:], re.MULTILINE)
        end = start + next_match.start() if next_match else len(content)
        section_content = content[start:end].lower()

        found = []
        for term in master.keys():
            if term.lower() in section_content:
                found.append(term)

        if found:
            output.append(f"## {title}\n")
            for term in sorted(found)[:25]:
                anchor = master[term][0] if master[term] else ""
                output.append(f"🏷️ [{term}](#{anchor})")
            output.append("\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"✅ Created {OUTPUT_FILE}")
    print("Open it and check the grouping.")

if __name__ == "__main__":
    main()