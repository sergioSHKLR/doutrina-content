import re
from pathlib import Path

# --- CONFIGURATION ---
BOOK_FILE = Path("lde-minus-indice.md")
INDEX_FILE = Path("indice-minus-lde.md")
OUTPUT_FILE = Path("lde-com-indice.md")  # Keeps your original safe


def parse_index(index_path):
    """
    Phase 1: Parses the index file to map subsection anchors to their related terms.
    Returns a dictionary: { "anchor_id": ["Term 1", "Term 2", ...] }
    """
    inverted_index = {}
    current_term = ""

    if not index_path.exists():
        print(f"❌ Error: Index file '{index_path}' not found.")
        return None

    # Matches lines like: 🏷️ Aberração {#aberracao}
    term_pattern = re.compile(r"🏷️\s*([^{]+)\s*\{#([^}]+)\}")
    # Matches markdown links like: [Q.847](#q847) or [Prefácio](#lde-0-02)
    link_pattern = re.compile(r"\[[^\]]+\]\s*\(\s*#([^)]+)\s*\)")

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Check if this line introduces a new term
            term_match = term_pattern.match(line)
            if term_match:
                current_term = term_match.group(1).strip()
                continue

            # If we are tracking a term, look for subsection references on subsequent lines
            if current_term:
                links = link_pattern.findall(line)
                for anchor in links:
                    # Clean the anchor ID just in case
                    anchor_id = anchor.strip()
                    if anchor_id not in inverted_index:
                        inverted_index[anchor_id] = set()
                    # Use a set to prevent duplicate terms in the same subsection
                    inverted_index[anchor_id].add(current_term)

    # Convert sets to sorted lists for predictable ordering
    return {k: sorted(list(v)) for k, v in inverted_index.items()}


def update_book(book_path, output_path, mapping):
    """
    Phase 2: Reads the book, identifies subsection blocks, and replaces the
    ::: expand 🏷️ ... ::: blocks with updated ordered term listings.
    """
    if not book_path.exists():
        print(f"❌ Error: Book file '{book_path}' not found.")
        return

    with open(book_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to find subsections, extract their anchor, and capture the 'expand' placeholder block
    # Looks for ### ... {#anchor-id} ... ::: expand 🏷️ ... :::
    section_pattern = re.compile(
        r"(###\s+.*?\{#([^}]+)\}.*?)(:::\s*expand\s*🏷️.*?:::)", re.DOTALL
    )

    def replace_placeholder(match):
        header_and_body = match.group(1)
        anchor_id = match.group(2).strip()

        # Check if we have gathered any indexed terms for this specific anchor
        if anchor_id in mapping and mapping[anchor_id]:
            terms = mapping[anchor_id]
            # Construct the new clean, ordered Markdown list block
            new_block = "::: expand 🏷️\n"
            for term in terms:
                # Creates a clean clean lowercase slug for the anchor link
                slug = (
                    term.lower()
                    .replace(" ", "-")
                    .replace("(", "")
                    .replace(")", "")
                )
                new_block += f"[{term}](#{slug})\n"
            new_block += ":::"
            return header_and_body + new_block

        # If no terms found in the index for this section, keep the original placeholder
        return match.group(0)

    updated_content = section_pattern.sub(replace_placeholder, content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"✨ Success! Updated book saved to: {output_path}")


# --- EXECUTION ---
if __name__ == "__main__":
    print("Parsing index allocations...")
    index_mapping = parse_index(INDEX_FILE)

    if index_mapping:
        print(f"Mapped {len(index_mapping)} unique subsection targets.")
        print("Injecting ordered terms into book structure...")
        update_book(BOOK_FILE, OUTPUT_FILE, index_mapping)
