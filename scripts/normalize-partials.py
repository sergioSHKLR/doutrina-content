import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
PARTIAL_DIR = ROOT_DIR / "books" / "md" / "1-lde" / "partial"


def advanced_slugify(text):
    """Normalizes complex book terms into unified index slugs."""
    slug = text.lower().strip()
    
    # 1. Clean up trailing gendered articles
    slug = re.sub(r"\s*\([oa]s?\)$", "", slug)
    
    # 2. Convert parenthetical plurals to standardized plurals: "espírito(s)" -> "espíritos"
    slug = slug.replace("(s)", "s")
    
    # 3. Standardize Portuguese diacritics
    accent_mapping = {
        "á": "a", "à": "a", "ã": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c"
    }
    for accented_char, clean_char in accent_mapping.items():
        slug = slug.replace(accented_char, clean_char)
    
    # 4. Strip leftover punctuation and map spaces to dashes
    slug = (
        slug.replace(" ", "-")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(".", "")
    )
    return slug


def normalize_all_partials():
    if not PARTIAL_DIR.exists():
        print(f"❌ Error: Partial folder path not found at: {PARTIAL_DIR}")
        return

    partial_files = sorted(list(PARTIAL_DIR.glob("lde-*.md")))
    
    if not partial_files:
        print(f"⚠️  No partial files found in: {PARTIAL_DIR}")
        return

    print(f"📚 Found {len(partial_files)} partial files to process.")

    global_index_mapping = {}  
    header_pattern = re.compile(r"^######\s+([^{:\n]+?)\s*\{#([^}]+)\}")
    expand_link_pattern = re.compile(r"🏷️\s*\[([^\]]+)\]\s*\(\s*#([^)]+)\s*\)")

    # ==========================================
    # --- STAGE 1: GLOBAL SCAN ACROSS CHUNKS ---
    # ==========================================
    print("📋 Stage 1: Scanning all files to build global Index term map...")
    for file_path in partial_files:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str.startswith("######"):
                    match = header_pattern.match(line_str)
                    if match:
                        raw_term = match.group(1).strip()
                        normalized_slug = advanced_slugify(raw_term)
                        global_index_mapping[raw_term.lower()] = normalized_slug
                        
                        if "(s)" in raw_term.lower():
                            singular_base = raw_term.lower().replace("(s)", "")
                            global_index_mapping[singular_base] = normalized_slug

    print(f"   Registered {len(global_index_mapping)} cross-file index mappings.")

    # ==========================================
    # --- STAGE 2: IN-PLACE PARSED REWRITING ---
    # ==========================================
    print("📋 Stage 2: Rewriting metadata links and headers safely...")
    for file_path in partial_files:
        print(f"   📄 Processing: {file_path.name}")
        
        is_index_file = (file_path.name == "lde-6.md")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated_lines = []
        inside_expand_block = False

        for line in lines:
            line_str = line.strip()

            # Update level-6 headings in ALL files (including lde-6.md)
            if line_str.startswith("######"):
                match = header_pattern.match(line_str)
                if match:
                    raw_term = match.group(1).strip()
                    normalized_slug = advanced_slugify(raw_term)
                    # FIXED: Readded explicit single space pad before the custom anchor block
                    updated_lines.append(f"###### {raw_term} {{#{normalized_slug}}}\n")
                    continue

            # Track block state
            if "::: expand" in line_str:
                inside_expand_block = True
                updated_lines.append(line)
                continue
            if line_str == ":::":
                inside_expand_block = False
                updated_lines.append(line)
                continue

            # Safely rewrite links only if inside text files (lde-0 to lde-5)
            if inside_expand_block and not is_index_file:
                link_match = expand_link_pattern.search(line_str)
                if link_match:
                    term_text = link_match.group(1).strip()
                    
                    lookup_key = term_text.lower()
                    if lookup_key in global_index_mapping:
                        target_slug = global_index_mapping[lookup_key]
                    else:
                        target_slug = advanced_slugify(term_text)
                    
                    new_line = f"🏷️ [{term_text}](#{target_slug})\n"
                    updated_lines.append(new_line)
                    continue

            updated_lines.append(line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

    print("\n🎉 Success! Part files normalized safely with perfect header spacing formatting.")
