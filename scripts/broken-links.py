#!/usr/bin/env python3
"""
Broken Internal Links Checker
- Finds all [#anchor] links
- Checks if the anchor exists in the file
- Reports broken links with line numbers
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def remove_frontmatter(content: str) -> str:
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content

def analyze_links(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    clean_content = remove_frontmatter(content)
    lines = clean_content.splitlines()
    
    anchors = set()
    links = []  # (line_number, link_text, anchor)
    
    for i, line in enumerate(lines, 1):
        # Find anchors {#id}
        for match in re.finditer(r'\{#([^}]+)\}', line):
            anchors.add(match.group(1).strip())
        
        # Find internal links [#anchor]
        for match in re.finditer(r'\[([^\]]+)\]\(#([^)]+)\)', line):
            link_text = match.group(1).strip()
            anchor = match.group(2).strip()
            links.append((i, link_text, anchor))
    
    # Find broken links
    broken = [(ln, text, anc) for ln, text, anc in links if anc not in anchors]
    
    report = [f"# Broken Links Analysis - {md_path.name}",
              f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    
    report.append(f"**Total Internal Links Found:** {len(links)}")
    report.append(f"**Total Unique Anchors Found:** {len(anchors)}")
    report.append(f"**Broken Links:** {len(broken)}\n")
    
    if broken:
        report.append("**⚠️ Broken Links:**")
        for line_num, link_text, anchor in broken[:30]:
            report.append(f"- Line {line_num:5d}: [{link_text}](#{anchor}) → **Target not found**")
        if len(broken) > 30:
            report.append(f"... and {len(broken)-30} more broken links")
    else:
        report.append("✅ **No broken internal links!**")
    
    report.append("\n---\n")
    return "\n".join(report)


# ====================== MAIN ======================
root = Path("books/md")
report_dir = Path("reports")
report_dir.mkdir(exist_ok=True)

print("🔍 Checking for broken internal links...\n")

full_report = ["# Broken Internal Links Report\n"]

for book_dir in sorted(root.glob("*/full")):
    full_md = book_dir / f"{book_dir.parent.name}-full.md"
    if full_md.exists():
        analysis = analyze_links(full_md)
        full_report.append(analysis)
        print(f"✅ Checked: {full_md.name}")

report_path = report_dir / "broken_links_report.md"
report_path.write_text("\n".join(full_report), encoding='utf-8')

print(f"\n📋 Report saved to: {report_path}")
print("✅ Link check complete!")