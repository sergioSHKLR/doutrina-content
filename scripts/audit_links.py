"""
Universal Link and Anchor Auditor
==================================
Uso: python3 scripts/audit_links.py <caminho_do_arquivo.md>
"""
import sys
import re

if len(sys.argv) < 2:
    print("❌ Erro: Forneça o caminho do arquivo Markdown.")
    print("Exemplo: python3 scripts/audit_links.py books/md/1-lde/full/1-lde-full.md")
    sys.exit(1)

FILE_PATH = sys.argv[1]
ANCHOR_PATTERN = r"\{\s*#([a-zA-Z0-9\-_.]+)\s*\}"
LINK_PATTERN = r"\(\s*#([a-zA-Z0-9\-_.]+)\s*\)"

defined_anchors = {}
found_links = []
duplicate_anchors = []

print("=" * 70)
print(f"🔗 AUDITANDO LINKS E ÂNCORAS: {FILE_PATH}")
print("=" * 70)

try:
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            clean_line = line.strip()

            # Mapeia todas as âncoras de destino
            for anchor in re.findall(ANCHOR_PATTERN, clean_line):
                if anchor in defined_anchors:
                    duplicate_anchors.append((anchor, line_num, defined_anchors[anchor]))
                else:
                    defined_anchors[anchor] = line_num

            # Coleta os links de navegação
            for link in re.findall(LINK_PATTERN, clean_line):
                found_links.append((link, line_num, clean_line))

    # Verifica links quebrados
    broken_links = []
    for link_id, line_num, context in found_links:
        if link_id not in defined_anchors:
            broken_links.append((link_id, line_num, context))

    print(f"Total de Âncora Únicas: {len(defined_anchors)}")
    print(f"Total de Links Internos: {len(found_links)}")

    if duplicate_anchors:
        print(f"\n⚠️  ÂNCORAS DUPLICADAS DETECTADAS ({len(duplicate_anchors)}):")
        for anchor, line, orig in duplicate_anchors[:5]:
            print(f"  -> #{anchor} na linha {line} (já definida na linha {orig})")

    if broken_links:
        print(f"\n❌ LINKS QUEBRADOS DETECTADOS ({len(broken_links)}):")
        for link, line, ctx in broken_links[:10]:
            print(f"  -> Linha {line}: #{link} apontando para lugar nenhum em: \"{ctx[:40]}...\"")
    else:
        print("\n✅ SUCESSO: Navegação perfeita! 0 links quebrados.")

except FileNotFoundError:
    print(f"❌ Erro: Arquivo não encontrado em '{FILE_PATH}'")
print("=" * 70)
