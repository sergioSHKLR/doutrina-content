"""
Universal Markdown Block Closure Validator
==========================================
Usage: python3 scripts/check_block_closures.py <file_path>
"""
import sys

if len(sys.argv) < 2:
    print("❌ Error: Please provide the Markdown file path.")
    sys.exit(1)

FILE_PATH = sys.argv[1]

block_stack = []
structural_errors = []

print("=" * 60)
print(f"🔍 SCANNING BLOCK CONTAINER CLOSURES FOR: {FILE_PATH}")
print("=" * 60)

with open(FILE_PATH, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        clean_line = line.strip()

        if clean_line.startswith(":::") and len(clean_line) > 3:
            block_type = clean_line.split()[1]
            block_stack.append((block_type, line_num))

        elif clean_line == ":::":
            if block_stack:
                block_stack.pop()
            else:
                structural_errors.append(
                    f"Line {line_num}: Orphaned closing tag ':::' found outside of any container block."
                )

while block_stack:
    unclosed_block, open_line = block_stack.pop()
    structural_errors.append(
        f"Line {open_line}: The container block '::: {unclosed_block}' was opened but never closed."
    )

if not structural_errors:
    print("✅ SUCCESS: Block structures are clean! All containers close perfectly.")
else:
    print(f"❌ ENCLOSURE ERRORS ENCOUNTERED ({len(structural_errors)}):")
    for err in structural_errors[:20]:
        print(f"  -> {err}")
print("=" * 60)
