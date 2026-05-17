import re
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(__file__).resolve().parent.parent
BOOK_FILE = ROOT_DIR / "lde-only.md"
INDEX_FILE = ROOT_DIR / "indice-only.md"
TODO_OUTPUT = ROOT_DIR / "reports" / "index_remediation_todo.txt"

# Your exact 52 verified unlinked slugs
TARGET_SLUGS = {
    "acerto", "autenticidade", "batista-joao", "bencao", "caligrafia", "condenacao",
    "cristo", "critica", "desanimo", "descanso", "desigualdades-sociais", "diluvio",
    "discriminacao", "elias", "espirito", "espiritos-benevolos", "evocacao", "excessos",
    "extase", "funeral", "geracoes", "hereditariedade", "ideia-religiosa", "investigacao",
    "isolamento", "juizo-final", "lamennais", "lei-de-atracao", "lei-natural", 
    "lucidez-sonambulica", "maldicao", "metempsicose", "minerais", "mundo", "namoro",
    "oriente", "pactos", "paulo-apostolo", "penas-futuras", "perfeicao-moral", "platao",
    "pluralidade-dos-mundos-habitados", "raciocinio", "racismo", "reinos", "relacoes",
    "ressurreicao", "sentido", "seres-inorganicos", "teologia", "vida-social", "vista"
}


def build_remediation_guide(book_path, index_path):
    if not book_path.exists() or not index_path.exists():
        print("❌ Error: Verification file targets are missing.")
        return

    print("📋 Phase 1: Mapping target links directly out of the Index...")
    index_decl_pattern = re.compile(r"^######\s+([^{:\n]+?)\s*\{#([^}]+)\}")
    link_pattern = re.compile(r"\[([^\]]+)\]\s*\(\s*#([^)]+)\s*\)")

    term_todo_map = {}  # { raw_name: [list of target anchors/questions] }
    current_term = None
    current_slug = None

    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            
            if line_str.startswith("######"):
                match = index_decl_pattern.match(line_str)
                if match:
                    current_term = match.group(1).strip()
                    current_slug = match.group(2).strip().lower()
                continue
                
            if current_slug in TARGET_SLUGS:
                if current_term not in term_todo_map:
                    term_todo_map[current_term] = []
                
                # Gather all section/question cross-references on the lines below the heading
                found_links = link_pattern.findall(line_str)
                for text, href in found_links:
                    term_todo_map[current_term].append((text, href))

    # --- REPORT FILE WRITING ---
    log_lines = [
        "📝 CONTENT COVERAGE REMEDIATION GUIDE",
        "The following guide shows exactly where the 52 unlinked terms are referenced",
        "in the Index, but are missing from the book's metadata blocks.",
        "=" * 65 + "\n"
    ]

    for term, references in sorted(term_todo_map.items()):
        if not references:
            continue
        log_lines.append(f"📌 Term: {term}")
        for label, target_id in references:
            log_lines.append(f"   📍 Needs to be added to block under section/question: {label} (`#{target_id}`)")
        log_lines.append("")

    TODO_OUTPUT.parent.mkdir(exist_ok=True)
    with open(TODO_OUTPUT, "w", encoding="utf-8") as rf:
        rf.write("\n".join(log_lines))

    print(f"🎉 Guide generated successfully!")
    print(f"💾 Open this file to see exactly where to inject the terms: {TODO_OUTPUT}")


if __name__ == "__main__":
    build_remediation_guide(BOOK_FILE, INDEX_FILE)
