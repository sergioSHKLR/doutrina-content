import re
from pathlib import Path

INDEX_FILE = Path("indice-minus-lde.md")
TEMP_OUTPUT = Path("indice-minus-lde.md.tmp")

def convert_indice_format(file_path, output_path):
    if not file_path.exists():
        print(f"❌ Erro: Arquivo {file_path} não encontrado.")
        return

    # Procura por: 🏷️ NomeDoTermo {#id}
    # group(1) captura o nome do termo, group(2) captura o id
    pattern = re.compile(r"^🏷️\s*([^{:\n]+?)\s*\{#([^}]+)\}")
    
    updated_lines = []
    converted_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                term = match.group(1).strip()
                anchor_id = match.group(2).strip()
                # Substitui pelo formato puro markdown entre colchetes
                new_line = f"🏷️ [{term}]{{#{anchor_id}}}\n"
                updated_lines.append(new_line)
                converted_count += 1
            else:
                updated_lines.append(line)

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    # Substitui o arquivo original com segurança
    output_path.replace(file_path)
    print(f"✨ Sucesso! {converted_count} termos foram convertidos para o formato puro markdown.")

if __name__ == "__main__":
    convert_indice_format(INDEX_FILE, TEMP_OUTPUT)
