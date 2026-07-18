"""
Global Book Architecture Validator
==================================
Uso: python3 scripts/validate_book.py <caminho_do_arquivo.md> <total_entradas_esperadas>
Exemplo: python3 scripts/validate_book.py books/md/1-lde/full/1-lde-full.md 1019
"""
import sys
import re

if len(sys.argv) < 3:
    print("❌ Erro: Forneça o arquivo e o número esperado de questões.")
    print("Uso: python3 scripts/validate_book.py <arquivo.md> <total_questoes>")
    sys.exit(1)

FILE_PATH = sys.argv[1]
TOTAL_ENTRIES = int(sys.argv[2])

QUESTION_PATTERN = r"^#####\s+#️⃣\s+Q\.(\d+)(?:\.([a-e]))?\b"
PROSE_PATTERN = r"^#####\s+📃\s+(\d+)\b"

found_questions = set()
found_prose = set()
subquestions_count = 0
structural_errors = []

print("=" * 70)
print(f"📊 VALIDANDO ESTRUTURA GERAL: {FILE_PATH}")
print("=" * 70)

try:
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_block = None
    has_spirit = False

    for idx, line in enumerate(lines, 1):
        clean_line = line.strip()
        q_match = re.match(QUESTION_PATTERN, clean_line)
        p_match = re.match(PROSE_PATTERN, clean_line)

        if q_match or p_match:
            if current_block and current_block["type"] == "question" and not has_spirit:
                structural_errors.append(f"Linha {current_block['line']}: {current_block['label']} não possui bloco '::: spirit'")

            has_spirit = False

            if q_match:
                q_num = int(q_match.group(1))
                sub_letter = q_match.group(2)
                current_block = {"type": "question", "num": q_num, "line": idx, "label": f"Q.{q_num}.{sub_letter}" if sub_letter else f"Q.{q_num}"}
                if sub_letter: subquestions_count += 1
                else: found_questions.add(q_num)
            elif p_match:
                p_num = int(p_match.group(1))
                found_prose.add(p_num)
                current_block = {"type": "prose", "num": p_num, "line": idx, "label": f"Prose {p_num}"}
            continue

        if current_block and current_block["type"] == "question" and "::: spirit" in clean_line:
            has_spirit = True

    all_tracked_numbers = found_questions | found_prose
    missing_sequence = [n for n in range(1, TOTAL_ENTRIES + 1) if n not in all_tracked_numbers]

    print(f"Perguntas Principais: {len(found_questions)} | Notas/Prosa: {len(found_prose)} | Subperguntas: {subquestions_count}")

    if structural_errors:
        print(f"\n⚠️  ALERTAS ESTRUTURAIS ({len(structural_errors)}):")
        for err in structural_errors[:5]: print(f"  -> {err}")

    if not missing_sequence and len(all_tracked_numbers) == TOTAL_ENTRIES:
        print("\n✅ SUCESSO: Sequência numérica impecável!")
    else:
        print(f"\n❌ ERRO NA SEQUÊNCIA: Itens ausentes: {missing_sequence[:20]}")

except FileNotFoundError:
    print(f"❌ Erro: Arquivo não encontrado em '{FILE_PATH}'")
print("=" * 70)
