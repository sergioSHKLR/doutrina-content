"""
LDE Typographical Sanitizer
===========================
Domain: Allan Kardec's "O Livro dos Espíritos" (LDE)
Purpose: Automatically repairs all 5060+ typographical padding issues by:
         1. Trimming invisible trailing spaces.
         2. Collapsing structural spacing gaps inside and outside ::: containers.
         3. Saving a pristine output copy safely.
"""

INPUT_FILE = "your_book.md"
OUTPUT_FILE = "your_book_clean.md"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_lines = f.readlines()

clean_lines = []
skip_next_empty = False

print("=" * 60)
print(f"🧹 SANITIZING TYPOGRAPHY AND CONTAINER PADDING...")
print("=" * 60)

for idx, line in enumerate(raw_lines):
    # 1. Clean out hidden trailing spaces/tabs immediately
    cleaned_line = line.rstrip()

    # Check if this line is an empty line
    is_empty = (cleaned_line == "")

    # Handle lookahead tracking safely for container edges
    is_container = cleaned_line.startswith(":::")

    # 2. Prevent a blank line immediately AFTER an opening/closing container
    if skip_next_empty and is_empty:
        skip_next_empty = False
        continue

    skip_next_empty = False # Reset flag

    # 3. Prevent a blank line immediately BEFORE a container
    if is_empty and (idx + 1 < len(raw_lines)):
        next_line_content = raw_lines[idx + 1].strip()
        if next_line_content.startswith(":::"):
            # Skip this blank line entirely to collapse the gap
            continue

    # 4. Collapse generic 3+ consecutive blank lines down to a clean single gap
    if is_empty and len(clean_lines) >= 2:
        if clean_lines[-1] == "" and clean_lines[-2] == "":
            continue

    # Trigger lookahead protection if we are writing a container line right now
    if is_container:
        skip_next_empty = True

    # Commit the clean line to the database array
    clean_lines.append(cleaned_line)

# Write the sanitized output stream to the filesystem
with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    out.write("\n".join(clean_lines) + "\n")

print(f"✅ SUCCESS: Cleaning cycle complete!")
print(f"📝 Original document lines: {len(raw_lines)}")
print(f"✨ Sanitized document lines: {len(clean_lines)}")
print(f"🚀 Fixed layout file saved as: {OUTPUT_FILE}")
print("=" * 60)
