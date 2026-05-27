#!/usr/bin/env python3
"""
Ultra Simple Anchor Stripper - Debug Version
"""

import re
from pathlib import Path

def strip_anchors(line: str) -> str:
    """Remove any {#anchor} from the end of heading"""
    return re.sub(r'\s*\{.*?\}\s*$', '', line)

def main():
    path = Path("books/md/1-lde/full/1-lde-full.md")
    
    if not path.exists():
        print(f"❌ File not found: {path}")
        return
    
    print(f"Processing: {path.name}")
    
    content = path.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    new_lines = [strip_anchors(line) for line in lines]
    
    # Backup
    backup = path.with_suffix('.md.bak3')
    path.rename(backup)
    print(f"   Backup created: {backup.name}")
    
    # Write clean file
    path.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"   ✅ Clean file written: {path.name}")
    
    print("Done!")

if __name__ == "__main__":
    main()