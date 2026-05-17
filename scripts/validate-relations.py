import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
FULL_BOOK_FILE = ROOT_DIR / "books" / "md" / "1-lde" / "full" / "1-lde-full.md"
REPORT_OUTPUT_DIR = ROOT_DIR / "reports"


def normalize_slug(text):
    """Normalizes Portuguese strings into standardized lowercase URL slugs."""
    slug = text.lower().strip()
    
    # 🌟 INTENTIONAL DESIGN EXCEPTIONS BYPASS (Falsos Positivos)
    # Ignora dinamicamente todas as variações de "intro XX"
    if slug.startswith("intro") and any(c.isdigit() for c in slug):
        num_part = "".join(c for c in slug if c.isdigit())
        return f"lde-0-03-{num_part.zfill(2)}"
        
    # Ignora dinamicamente todas as variações de "conclusão XX"
    if slug.startswith("conclusao") or slug.startswith("conclusão"):
        num_part = "".join(c for c in slug if c.isdigit())
        if num_part:
            return f"lde-5-02-{num_part.zfill(2)}"
        return "lde-5-02"
        
    if slug == "prefácio":
        return "lde-0-02"
        
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
    
    slug = (
        slug.replace(" ", "-")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(".", "")
    )
    return slug


def deep_cross_validate(file_path):
    if not file_path.exists():
        print(f"❌ Error: Target book file not found at expected path:\n   👉 {file_path}")
        return

    log_lines = []
    
    def log(message):
        print(message)
        log_lines.append(message)

    log(f"🕵️  Deep Scanning: {file_path.name} for structural mismatches...\n")

    # Regex para ignorar formatos de perguntas (ex: q919, q919a, q222)
    question_regex = re.compile(r"^q?\d+[a-z]?$")

    defined_index_terms = set()      
    defined_sections = set()         
    section_term_links = []          
    index_to_section_links = []      

    header_pattern = re.compile(r"^#+\s+.*?\{#([^}]+)\}")
    index_decl_pattern = re.compile(r"^######\s+([^{:\n]+?)\s*\{#([^}]+)\}")
    expanded_link_pattern = re.compile(r"\[([^\]]+)\]\s*\(\s*#([^)]+)\s*\)")

    current_section = None
    inside_expand_block = False
    line_number = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_number += 1
            line_str = line.strip()

            # 1. Detect and Map Markdown Headers
            h_match = header_pattern.match(line_str)
            if h_match:
                if line_str.startswith("######"):
                    idx_match = index_decl_pattern.match(line_str)
                    if idx_match:
                        term_slug = idx_match.group(2).strip().lower()
                        defined_index_terms.add(term_slug)
                    continue
                
                current_section = h_match.group(1).strip().lower()
                defined_sections.add(current_section)
                continue

            # 2. Track Multi-line Metadata Expand Containers
            if "::: expand" in line_str:
                inside_expand_block = True
                continue
            if line_str == ":::":
                inside_expand_block = False
                continue

            # 3. Capture Subsection Term Links (Phase A)
            if inside_expand_block:
                el_match = expanded_link_pattern.search(line_str)
                if el_match:
                    term_text = el_match.group(1).strip()
                    term_target = el_match.group(2).strip().lower()
                    
                    # Ignora se for link de pergunta ou número puro como 222
                    if question_regex.match(term_target) or term_target.isdigit():
                        continue
                        
                    section_term_links.append((current_section, term_text, term_target, line_number))
                continue

            # 4. Capture Index Cross-References (Phase B)
            if not line_str.startswith("#"):
                xref_links = expanded_link_pattern.findall(line_str)
                for text, href in xref_links:
                    clean_xref = href.strip().lower()
                    if clean_xref and not clean_xref.startswith("http"):
                        # Ignora se for link de pergunta ou número puro como 222
                        if question_regex.match(clean_xref) or clean_xref.isdigit():
                            continue
                            
                        index_to_section_links.append((clean_xref, line_number, line_str))

    # --- EVALUATION ENGINE ---
    flaws = 0
    log("📋 Testing Phase A: Checking Subsection Links against Index Definitions...")
    for sec, term_txt, term_slug, line in section_term_links:
        expected_slug = normalize_slug(term_txt)
        
        # Filtros de Exceções Intencionais
        is_intro = term_txt.lower().startswith("intro")
        is_conclusao = term_txt.lower().startswith("conclusao") or term_txt.lower().startswith("conclusão")
        is_prefacio = term_txt.lower() == "prefácio"
        is_exception = is_intro or is_conclusao or is_prefacio or term_slug.isdigit()
        
        if term_slug != expected_slug and not is_exception:
            log(f"   ⚠️  Line {line} [Section: #{sec}]: Mismatched target name. Link uses '#{term_slug}' but text normalizes to '#{expected_slug}'")
            flaws += 1
            
        if term_slug not in defined_index_terms and not is_exception:
            log(f"   ❌ Line {line} [Section: #{sec}]: Orphaned link! Term '{term_txt}' (`#{term_slug}`) does not exist inside the general Índice.")
            flaws += 1

    log("\n📋 Testing Phase B: Checking Index Cross-References against Document Structure...")
    for target, line, raw_ctx in index_to_section_links:
        if target not in defined_sections:
            log(f"   ❌ Line {line} [Índice Cross-Ref]: Dead link to target `#{target}`. Target section does not exist in the book content.")
            log(f"      ↳ Context: {raw_ctx}")
            flaws += 1

    log("\n" + "="*60)
    if flaws == 0:
        log("🎉 Integrity Verified! All lists and cross-references match perfectly.")
    else:
        log(f"⚠️  Validation completed with {flaws} discrepancy flaw(s) flagged above.")

    # Save to report file
    REPORT_OUTPUT_DIR.mkdir(exist_ok=True)
    report_file = REPORT_OUTPUT_DIR / "validation_report.txt"
    with open(report_file, "w", encoding="utf-8") as rf:
        rf.write("\n".join(log_lines))
    print(f"\n💾 Report successfully written to: {report_file}")


if __name__ == "__main__":
    deep_cross_validate(FULL_BOOK_FILE)
