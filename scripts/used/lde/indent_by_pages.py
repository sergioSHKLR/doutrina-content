"""
LDE Indentation-Based Page Builder
==================================
Domain: Allan Kardec's "O Livro dos Espíritos" (LDE)
Purpose: Indents content sitting between page markers by 2 spaces, allowing
         VS Code to natively fold pages using structural indentation rules.
"""

import re  # Added the missing core module import statement

INPUT_FILE = "your_book_indexed.md"
OUTPUT_FILE = "your_book_folded.md"
INDEX_BOUNDARY_LINE = 18515

PAGE_PATTERN = r"^\[\]\{#page-\d+\}"

print("=" * 70)
print(f"🏗️  PROCESSING INDENTATION LAYOUT MATRIX FOR: {INPUT_FILE}")
print("=" * 70)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

processed_lines = []
is_inside_page_content = False

for idx, line in enumerate(lines, 1):
    # Stop modifying text indentation the moment we pass into the Index
    if idx > INDEX_BOUNDARY_LINE:
        processed_lines.append(line)
        continue

    # Check if this line is a page anchor row
    if re.match(PAGE_PATTERN, line.strip()):
        processed_lines.append(line) # Keep the marker flush left
        is_inside_page_content = True
        continue

    # Indent the body paragraph content rows by 2 spaces if inside a page block
    if is_inside_page_content and line.strip() != "":
        processed_lines.append(f"  {line}")
    else:
        processed_lines.append(line)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(processed_lines)

print("✅ SUCCESS: Indentation matrix generated!")
print(f"🚀 Aligned Master Document Deployed To: {OUTPUT_FILE}")
print("=" * 70)
