import re
from pathlib import Path

# --- CONFIGURATION ---
BOOK_FILE = Path("1-lde-full.md")  # Adjust this if your filename changes


def check_links(file_path):
    if not file_path.exists():
        print(f"❌ Error: {file_path} not found. Ensure you are running from the repo root.")
        return

    print(f"🔍 Analyzing links inside {file_path}...\n")

    # 1. Collect all valid Anchor targets defined in headers or terms
    # Captures: {#anchor-id} anywhere in a line
    anchor_pattern = re.compile(r"\{#([^}]+)\}")
    
    # 2. Collect all Markdown anchor links used
    # Captures: [Text](#link-id)
    link_pattern = re.compile(r"\[[^\]]+\]\s*\(\s*#([^)]+)\s*\)")

    defined_anchors = set()
    used_links = []
    line_number = 0

    # Scan the file line by line
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_number += 1
            
            # Find defined targets
            anchors = anchor_pattern.findall(line)
            for a in anchors:
                defined_anchors.add(a.strip().lower())
                
                     # Find clicked references
            links = link_pattern.findall(line)
            for l in links:
                link_clean = l.strip().lower()
                # SKIP checking questions (e.g., q222, q357) for now
                if link_clean.startswith('q') and link_clean[1:].isdigit():
                    continue
                used_links.append((link_clean, line_number, line.strip()))


    # 3. Cross-Check matching
    broken_links = []
    for link, line_num, raw_line in used_links:
        if link not in defined_anchors:
            broken_links.append((link, line_num, raw_line))

    # --- REPORTING ---
    print(f"📊 Scan Results Summary:")
    print(f"   - Total unique anchor targets found: {len(defined_anchors)}")
    print(f"   - Total clickable references checked: {len(used_links)}")
    print("-" * 50)

    if broken_links:
        print(f"⚠️ FOUND {len(broken_links)} BROKEN LINK REFERENCES:\n")
        for target, line_num, content in broken_links:
            print(f"   📍 Line {line_num}: Destination '#{target}' does not exist!")
            print(f"      ↳ Context: {content}\n")
        print("❌ Validation Failed. Please fix the missing target IDs listed above.")
    else:
        print("🎉 Perfect! Every related term link points to a valid destination anchor.")


if __name__ == "__main__":
    check_links(BOOK_FILE)
