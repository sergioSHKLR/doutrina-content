"""
LDE Page Spacing Optimizer
===========================
Domain: Allan Kardec's "O Livro dos Espíritos" (LDE)
Purpose: Cleans up empty vertical gaps between page blocks. Completely removes
         blank lines between normal pages, but leaves exactly ONE empty line
         every 10 pages to establish clean visual layout chapters.
"""

import re

INPUT_FILE = "your_book_folded.md"
OUTPUT_FILE = "your_book_folded_clean.md"

PAGE_PATTERN = r"^\[\]\{#page-(\d+)\}"

print("=" * 70)
print(f"🧹 OPTIMIZING INTER-PAGE GAP SPACING FOR: {INPUT_FILE}")
print("=" * 70)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

optimized_lines = []
skip_next_empty = False

for idx, line in enumerate(lines):
    clean_line = line.strip()
    match = re.match(PAGE_PATTERN, clean_line)

    if match:
        page_num = int(match.group(1))

        # 1. Backwards cleaning: Remove any trailing empty lines added by previous blocks
        while optimized_lines and optimized_lines[-1].strip() == "":
            optimized_lines.pop()

        # 2. Rule: Every 10 pages, prepend exactly ONE clean empty line to act as a spacer
        if page_num > 1 and page_num % 10 == 0:
            optimized_lines.append("\n")

        optimized_lines.append(line)
        continue

    # Fall-through handler for all standard content body rows
    optimized_lines.append(line)

# Commit the optimized text stream layout back to disk
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(optimized_lines)

print("✅ SUCCESS: Inter-page structural spacing optimized!")
print(f"📝 Original layout file lines : {len(lines)}")
print(f"✨ Optimized layout file lines: {len(optimized_lines)}")
print(f"🚀 Refined File Deployed Safely To: {OUTPUT_FILE}")
print("=" * 70)
