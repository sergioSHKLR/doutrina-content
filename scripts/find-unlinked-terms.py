import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
BOOK_FILE = ROOT_DIR / "lde-only.md"
INDEX_FILE = ROOT_DIR / "indice-only.md"
REPORT_OUTPUT = ROOT_DIR / "reports" / "unlinked_terms_report.txt"


def audit_unlinked_separated_files(book_path, index_path):
    if not book_path.exists():
        print(f"❌ Error: Book file not found at {book_path}")
        return
    if not index_path.exists():
        print(f"❌ Error: Index file not found at {index_path}")
        return

    print(f"🕵️‍♂️ Auditing links between {book_path.name} and {index_path.name}...\n")

    # Patterns
    index_decl_pattern = re.compile(r"^######\s+([^{:\n]+?)\s*\{#([^}]+)\}")
    subsection_link_pattern = re.compile(r"🏷️\s*\[([^\]]+)\]\s*\(\s*#([^)]+)\s*\)")

    all_index_slugs = {}       # { slug: raw_name }
    incoming_link_counts = {}  # { slug: count }

    # Pass 1: Gather all real Level-6 Index Terms from the index-only file
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("######"):
                match = index_decl_pattern.match(line.strip())
                if match:
                    term_name = match.group(1).strip()
                    term_slug = match.group(2).strip().lower()
                    all_index_slugs[term_slug] = term_name
                    incoming_link_counts[term_slug] = 0

    # Pass 2: Global traffic scanner reading purely from the book content file
    with open(book_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            
            # Scan for subsection generated link strings
            links = subsection_link_pattern.findall(line_str)
            for text, href in links:
                clean_href = href.strip().lower()
                if clean_href in incoming_link_counts:
                    incoming_link_counts[clean_href] += 1

    # Isolate terms with exactly 0 incoming hits
    unlinked_terms = {slug: all_index_slugs[slug] for slug, count in incoming_link_counts.items() if count == 0}

    # --- REPORT GENERATION ---
    log_lines = [
        f"📊 UNLINKED TERMS TRAFFIC AUDIT REPORT (SEPARATED FILES)",
        f"Source Book File: {book_path.name}",
        f"Source Index File: {index_path.name}",
        f"Total Index Terms defined: {len(all_index_slugs)}",
        f"Total Unlinked Terms found: {len(unlinked_terms)}",
        "=" * 50,
        "\nThe following terms exist in the Índice but are NEVER linked to from any book subsection:\n"
    ]

    for slug in sorted(unlinked_terms.keys()):
        log_lines.append(f"   ❌ [ ] {unlinked_terms[slug]} (`#{slug}`)")

    REPORT_OUTPUT.parent.mkdir(exist_ok=True)
    with open(REPORT_OUTPUT, "w", encoding="utf-8") as rf:
        rf.write("\n".join(log_lines))

    print(f"🎉 Audit complete! Found {len(unlinked_terms)} unlinked terms out of {len(all_index_slugs)} total entries.")
    print(f"💾 Detailed report written to: {REPORT_OUTPUT}")


if __name__ == "__main__":
    # Adjust paths if your layout files sit in a different subfolder directory
    audit_unlinked_separated_files(BOOK_FILE, INDEX_FILE)
