#!/usr/bin/env python3
"""
Custom Anchor Generator for LDE H6 Headings ONLY
Phase 1: Converts '###### 🔖 Allan Kardec' into '###### 🔖 Allan Kardec {#allan-kardec}'
"""

import re
import unicodedata
from pathlib import Path

def slugify(text: str) -> str:
    """
    Remove emojis, limpa diacríticos (acentos) e transforma o texto 
    em um identificador separado por hífens.
    """
    # 1. Remove emojis e caracteres especiais, mantendo apenas texto, números e espaços
    clean_text = re.sub(r'[^\w\s\-]', '', text)
    
    # 2. Remove acentos de forma nativa e limpa
    normalized = unicodedata.normalize('NFD', clean_text)
    no_diacritics = "".join([c for c in normalized if unicodedata.category(c) != 'Mn'])
    
    # 3. Caixa baixa e substituição de espaços por hífen único
    lowered = no_diacritics.lower().strip()
    slug = re.sub(r'[\s_]+', '-', lowered)
    
    # 4. Limpa hífens duplicados ou remanescentes nas bordas
    slug = re.sub(r'-+', '-', slug).strip('-')
    
    return slug

def process_h6_anchors(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    new_lines = []
    changes = 0
    
    for line in lines:
        # Expressão regular restrita: obrigatoriamente 6 hashtags seguidas de espaço
        # Isola qualquer âncora antiga {...} existente no final da linha
        match = re.match(r'^(######)\s+(.+?)(?:\s*\{([^}]+)\})?$', line)
        
        if match:
            hashtags = match.group(1)
            text = match.group(2).strip()
            
            # Gera o ID customizado baseado no texto do H6
            custom_id = slugify(text)
            
            if custom_id:
                new_anchor = f"#{custom_id}"
                new_line = f"{hashtags} {text} {{{new_anchor}}}"
                
                if new_line != line:
                    changes += 1
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            # Mantém absolutamente qualquer outra linha (H1-H5, texto, listas) intocada
            new_lines.append(line)
            
    return new_lines, changes

# ====================== EXECUÇÃO ======================
target_file = Path("books/md/1-lde/full/1-lde-full.md")

if target_file.exists():
    print(f"🔄 Processando estritamente os cabeçalhos H6 do LDE...")
    
    updated_content, total_changes = process_h6_anchors(target_file)
    
    # Grava as modificações de volta no arquivo
    target_file.write_text('\n'.join(updated_content) + '\n', encoding='utf-8')
    print(f"   ✅ Concluído! {total_changes} cabeçalhos H6 modificados. O restante do arquivo ficou intocado.")
else:
    print(f"❌ Erro: O arquivo {target_file} não foi localizado.")
