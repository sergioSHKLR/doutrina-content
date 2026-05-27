#!/usr/bin/env python3
"""
Diagnostic TOC Generator
- Cleans separator lines and legal/disclaimer noise
- Preserves real Pré-textual sections (0.00, 0.01, etc.)
- Shows h5 only when abundant (>20)
"""

import re
from pathlib import Path

def is_technical_noise(text: str) -> bool:
    """Filter technical noise, separators, and legal sections"""
    text_upper = text.upper()
    
    noise_patterns = [
        "METADATA PRINCIPAL",
        "TAXONOMY & ORGANIZATION",
        "SITE & NAVIGATION",
        "LEGAL & DISCLAIMER",
        "=============================================================================",
        "FRONTMATTER",
        "YAML"
    ]
    
    return any(pattern in text_upper for pattern in noise_patterns)

def generate_diagnostic_toc(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    h5_count = len(re.findall(r'^#####\s+', content, re.MULTILINE))
    show_h5 = h5_count > 20
    
    toc = []
    
    for line in lines:
        match = re.match(r'^(#{1,5})\s+(.+?)(?:\s*\{.*?\})?$', line.strip())
        if not match:
            continue
            
        level = len(match.group(1))
        raw_text = match.group(2).strip()
        text = re.sub(r'^[🔖📑🗃️🗂️#️⃣\s]+', '', raw_text).strip()
        
        if not text or is_technical_noise(text):
            continue

        indent = "    " * (level - 1)
        
        if level == 1:
            toc.append(f"\n# {text}")
        elif level == 2:
            toc.append(f"\n## {text}")
        elif level == 3:
            toc.append(f"   - **{text}**")
        elif level == 4:
            toc.append(f"       - {text}")
        elif level == 5 and show_h5:
            toc.append(f"           - {text}")
    
    return "\n".join(toc)


# ====================== MAIN ======================
root = Path("books/md")
output_dir = Path("reports/toc")
output_dir.mkdir(parents=True, exist_ok=True)

print("📋 Generating Clean Diagnostic TOCs...\n")

for book_dir in sorted(root.glob("*/full")):
    full_md = book_dir / f"{book_dir.parent.name}-full.md"
    if full_md.exists():
        toc_text = generate_diagnostic_toc(full_md)
        
        toc_path = output_dir / f"toc_diagnostic_{book_dir.parent.name}.md"
        
        h5_note = " (h5 included)" if len(re.findall(r'^#####\s+', full_md.read_text(encoding='utf-8'), re.MULTILINE)) > 20 else " (h5 collapsed)"
        
        header = f"# Diagnostic TOC - {book_dir.parent.name.upper()}{h5_note}\n"
        header += "Clean version for hierarchy analysis\n\n"
        
        toc_path.write_text(header + toc_text, encoding='utf-8')
        print(f"✅ Saved: reports/toc/toc_diagnostic_{book_dir.parent.name}.md")

print("\n🎉 Clean diagnostic TOCs generated!")