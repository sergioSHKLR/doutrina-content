#!/usr/bin/env python3
"""
Custom Anchor Generator for GEN Headings (H2-H4 Only)
Phase 1: Extracts clean numeric prefixes from the text.
- H2: #X
- H3: #X-YY
- H4: #X-YY-ZZ
"""

import re
from pathlib import Path

def process_gen(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    new_lines = []
    changes = 0
    
    for line in lines:
        # Match headings from level 2 to 4 (H2, H3, H4)
        # Isolates any old anchor {...} at the end of the line
        match = re.match(r'^(#{2,4})\s+(.+?)(?:\s*\{([^}]+)\})?$', line)
        
        if match:
            hashtags = match.group(1)
            level = len(hashtags)
            text = match.group(2).strip()
            
            # Clean up leading emojis/icons to evaluate pure numbering
            clean_text = re.sub(r'^[^\w\d\s\.]+', '', text).strip()
            
            # Skip front-matter headers that start with structural '0.'
            if re.match(r'^0\.', clean_text):
                new_lines.append(line)
                continue
                
            custom_id = None
            
            # --- H2 RULE: Main Part/Chapter (e.g., "1. Título" -> 1) ---
            if level == 2:
                num_match = re.match(r'^(\d+)\b', clean_text)
                if num_match:
                    x_val = num_match.group(1)
                    custom_id = f"{x_val}"
            
            # --- H3 RULE: Section Level (e.g., "1.05. Título" -> 1-05) ---
            elif level == 3:
                num_match = re.match(r'^(\d+)\.(\d+)\b', clean_text)
                if num_match:
                    x_val = num_match.group(1)
                    yy_val = num_match.group(2).zfill(2)
                    custom_id = f"{x_val}-{yy_val}"
            
            # --- H4 RULE: Subsection Level (e.g., "1.05.02. Tópico" -> 1-05-02) ---
            elif level == 4:
                num_match = re.match(r'^(\d+)\.(\d+)\.(\d+)\b', clean_text)
                if num_match:
                    x_val = num_match.group(1)
                    yy_val = num_match.group(2).zfill(2)
                    zz_val = num_match.group(3).zfill(2)
                    custom_id = f"{x_val}-{yy_val}-{zz_val}"
                else:
                    # Fallback if H4 is a single standalone number
                    fallback = re.match(r'^(\d{1,2})\b', clean_text)
                    if fallback:
                        custom_id = fallback.group(1).zfill(2)

            # Reconstruct heading if an anchor was successfully targeted
            if custom_id:
                new_anchor = f"#{custom_id}"
                new_line = f"{hashtags} {text} {{{new_anchor}}}"
                
                if new_line != line:
                    changes += 1
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    return new_lines, changes

# ====================== EXECUTION ======================
target_file = Path("books/md/5-gen/full/5-gen-full.md")

if target_file.exists():
    print(f"🔄 Processing GEN H2-H4 anchors factually: {target_file.name}...")
    
    # Redundant safety backup generation
    backup_path = target_file.parent / f"{target_file.name}.bak"
    if not backup_path.exists():
        backup_path.write_text(target_file.read_text(encoding='utf-8'), encoding='utf-8')
        print("   💾 Original backup file created.")
        
    updated_content, total_changes = process_gen(target_file)
    
    target_file.write_text('\n'.join(updated_content) + '\n', encoding='utf-8')
    print(f"   ✅ Done! {total_changes} headings updated in GEN.")
else:
    print(f"❌ Error: The file {target_file} could not be located.")
