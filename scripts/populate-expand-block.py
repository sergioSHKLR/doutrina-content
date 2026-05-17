#!/usr/bin/env python3
"""
Populate ::: expand 🔗 blocks using:
- indice-only.md (source of terms)
- lde-only.md     (the book content)
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# === NEW FILE NAMES ===
BOOK_FILE = PROJECT_ROOT / "lde-only.md"           # Full book without index
INDEX_FILE = PROJECT_ROOT / "indice-only.md"       # Only the index (6.02)
FULL_OUTPUT = PROJECT_ROOT / "books/md/1-lde/full/1-lde-full.md"

def load_master_index():
    """Load all terms from indice-only.md"""
    master = {}
    current_term = None
    with open(INDEX_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("🏷️ "):
                current_term = line[4:].strip()
                master[current_term] = []
            elif current_term and line and not line.startswith("🏷️"):
                match = re.search(r'\[#([^\]]+)\]', line)
                if match:
                    master[current_term].append(match.group(1))
    return master

def main():
    master = load_master_index()
    print(f"✅ Loaded {len(master)} terms from indice-only.md")

    content = BOOK_FILE.read_text(encoding="utf-8")

    def replace_block(match):
        block_start = match.start()
        # Take some context before the block for better matching
        context = content[max(0, block_start - 4000):block_start].lower()

        found = []
        for term, anchors in master.items():
            if not anchors:
                continue
            term_lower = term.lower()
            if term_lower in context or any(word in context for word in term_lower.split() if len(word) > 3):
                found.append((term, anchors[0]))

        # Fallback if too few matches
        if len(found) < 8:
            fallback = list(master.items())[:20]
            found.extend([(t, a[0]) for t, a in fallback if (t, a[0]) not in found])

        # Build the block
        new_block = "::: expand 🔗\n"
        for term, anchor in sorted(found)[:22]:
            new_block += f"🏷️ [{term}](#{anchor})\n"
        new_block += ":::\n"

        print(f"   Updated block with {len(found)} terms")
        return new_block

    # Replace all expand blocks
    new_content = re.sub(r"::: expand 🔗.*?:::", replace_block, content, flags=re.DOTALL | re.IGNORECASE)

    # Save to the full file
    FULL_OUTPUT.write_text(new_content, encoding="utf-8")
    print(f"\n🎉 Successfully updated → {FULL_OUTPUT}")

if __name__ == "__main__":
    main()