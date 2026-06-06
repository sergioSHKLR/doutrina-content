#!/usr/bin/env python3
"""
Slugify H6 headings for custom anchors
- Removes diacritics (ç → c, ã → a, etc.)
- Lowercase, spaces → -, clean URL-friendly anchors
"""

import re
import unicodedata
from pathlib import Path
import sys

def slugify(text):
    """Convert text to URL-friendly slug, removing diacritics"""
    # Normalize to decompose diacritics
    text = unicodedata.normalize('NFKD', text)
    # Remove diacritics
    text = ''.join(c for c in text if not unicodedata.combining(c))
    # Lowercase
    text = text.lower()
    # Replace non-word chars with hyphen
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Replace spaces and multiple hyphens
    text = re.sub(r'[\s_-]+', '-', text.strip())
    return text.strip('-')


def process_file(input_path, output_path=None):
    content = Path(input_path).read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []

    for line in lines:
        if line.strip().startswith("###### "):
            # Extract title
            title = line.strip()[7:].strip()  # remove ######
            slug = slugify(title)
            new_line = f"###### {title} {{#{slug}}}"
            new_lines.append(new_line)
            print(f"→ Slugified: {title} → #{slug}")
        else:
            new_lines.append(line)

    new_content = "\n".join(new_lines)

    if output_path:
        Path(output_path).write_text(new_content, encoding="utf-8")
        print(f"\n✅ H6 headings slugified and saved to: {output_path}")
    else:
        print(new_content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python slugify_h6.py <input.md> [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    process_file(input_file, output_file)