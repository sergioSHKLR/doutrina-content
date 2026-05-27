#!/usr/bin/env python3
"""
LDM Anchor Adder - Robust Nota Handling
"""

import re
from pathlib import Path
from datetime import datetime

def add_ldm_anchors():
    md_path = Path("books/md/2-ldm/full/2-ldm-full.md")
    
    if not md_path.exists():
        print("❌ File not found!")
        return
    
    content = md_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    new_lines = []
    changes = 0
    current_h4 = None
    last_h5_num = None
    
    for line in lines:
        stripped = line.strip()
        match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{.*?\})?$', stripped)
        if not match:
            new_lines.append(line)
            continue
            
        level = len(match.group(1))
        text = match.group(2).strip()
        
        new_anchor = None
        
        if level == 4:
            # H4: Main paragraph number
            num_match = re.search(r'(\d{1,3})', text)
            if num_match:
                current_h4 = num_match.group(1)
                new_anchor = f"m{current_h4}"
                
        elif level == 5:
            # Check if it's a Nota line
            if "Nota" in text or "nota" in text.lower() or "📝" in stripped:
                if current_h4 and last_h5_num:
                    new_anchor = f"m{current_h4}-{last_h5_num}-nota"
                elif current_h4:
                    new_anchor = f"m{current_h4}-nota"
            else:
                # Normal H5
                num_match = re.search(r'(\d{1,3})', text)
                if num_match and current_h4:
                    last_h5_num = num_match.group(1)
                    new_anchor = f"m{current_h4}-{last_h5_num}"
        
        if new_anchor:
            new_line = f"{match.group(1)} {text} {{#{new_anchor}}}"
            if new_line != line:
                changes += 1
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    # Backup and Save
    backup = md_path.with_suffix('.md.bak_ldm_final2')
    md_path.rename(backup)
    md_path.write_text('\n'.join(new_lines), encoding='utf-8')
    
    print(f"✅ LDM anchors updated successfully!")
    print(f"   Changes made: {changes}")
    print(f"   Backup: {backup.name}")

if __name__ == "__main__":
    add_ldm_anchors()