#!/usr/bin/env python3
"""
Clean duplicate / compounded slugs from H6 headings
"""

import re
from pathlib import Path
import sys

def clean_slugs(content):
    lines = content.splitlines()
    new_lines = []

    for line in lines:
        if line.strip().startswith("###### "):
            # Find all slugs
            slug_matches = re.findall(r'\{#([^}]+)\}', line)
            
            if slug_matches:
                # Take the simplest (shortest) slug - usually the first clean one
                best_slug = min(slug_matches, key=len)
                
                # Remove ALL existing slug markers
                clean_line = re.sub(r'\s*\{#[^}]+\}', '', line).strip()
                
                # Add back only one clean slug
                new_line = f"{clean_line} {{#{best_slug}}}"
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def process_file(input_path, output_path=None):
    content = Path(input_path).read_text(encoding="utf-8")
    cleaned = clean_slugs(content)

    if output_path:
        Path(output_path).write_text(cleaned, encoding="utf-8")
        print(f"✅ Duplicate slugs cleaned → {output_path}")
    else:
        print(cleaned[:1500])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_duplicate_slugs.py <input.md> [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file

    process_file(input_file, output_file)