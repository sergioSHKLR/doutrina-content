import re
from pathlib import Path

# --- CONFIGURATION ---
COMBINED_BOOK_FILE = Path("lde-minus-indice.md") 
INDEX_FILE = Path("indice-minus-lde.md")
OUTPUT_FILE = Path("lde-com-indice.md")


def parse_index(index_path):
    """Phase 1: Parses the index using fast line-by-line reading."""
    inverted_index = {}
    current_term = ""

    if not index_path.exists():
        print(f"❌ Error: Index file '{index_path}' not found.")
        return None

    term_pattern = re.compile(r"🏷️\s*\[([^\]]+)\]\s*\{#([^}]+)\}")
    link_pattern = re.compile(r"\[[^\]]+\]\s*\(\s*#([^)]+)\s*\)")

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            term_match = term_pattern.match(line)
            if term_match:
                current_term = term_match.group(1).strip()
                continue

            if current_term:
                links = link_pattern.findall(line)
                for anchor in links:
                    anchor_id = anchor.strip()
                    if anchor_id not in inverted_index:
                        inverted_index[anchor_id] = set()
                    inverted_index[anchor_id].add(current_term)

    return {k: sorted(list(v)) for k, v in inverted_index.items()}


def update_book_fast(book_path, output_path, mapping):
    """Phase 2: High-performance sequential line parser."""
    if not book_path.exists():
        print(f"❌ Error: Book file '{book_path}' not found.")
        return

    # Matches standard markdown headers with an anchor ID, e.g., ### Title {#lde-0-02}
    header_pattern = re.compile(r"^###\s+.*?\{#([^}]+)\}")
    
    current_anchor = None
    output_lines = []
    inside_placeholder = False

    with open(book_path, "r", encoding="utf-8") as f:
        for line in f:
            # Track which subsection we are currently passing through
            header_match = header_pattern.match(line)
            if header_match:
                current_anchor = header_match.group(1).strip()

            # Identify the start of a placeholder block
            if line.strip().startswith("::: expand 🏷️"):
                inside_placeholder = True
                
                # Check if we have terms collected for this section's active anchor
                if current_anchor and current_anchor in mapping:
                    terms = mapping[current_anchor]
                    output_lines.append("::: expand 🔗\n")
                    for term in terms:
                        slug = (
                            term.lower()
                            .replace(" ", "-")
                            .replace("(", "")
                            .replace(")", "")
                        )
                        output_lines.append(f"🏷️ [{term}](#{slug})\n")
                    output_lines.append(":::\n")
                continue

            # Identify the end of a placeholder block
            if inside_placeholder:
                if line.strip() == ":::":
                    inside_placeholder = False
                continue  # Skip everything inside the old block

            # Keep all normal text lines intact
            output_lines.append(line)

    # Write out the generated file sequentially
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print(f"✨ Success! Cleaned and updated book saved to: {output_path}")


if __name__ == "__main__":
    print("Parsing index allocations...")
    index_mapping = parse_index(INDEX_FILE)

    if index_mapping:
        print(f"Mapped {len(index_mapping)} unique subsection targets.")
        print("Injecting ordered terms using high-performance stream tracking...")
        update_book_fast(COMBINED_BOOK_FILE, OUTPUT_FILE, index_mapping)
