#!/usr/bin/env python3
"""
Full Quality Check - Dynamic Scoring (0-100%)
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

def analyze_book(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    clean_content = remove_frontmatter(content)
    lines = clean_content.splitlines()
    
    book_name = md_path.name.replace('-full.md', '').upper()
    is_lde = 'LDE' in book_name
    
    h_counts = {i: 0 for i in range(1, 7)}
    anchor_locations = defaultdict(list)
    nesting_issues = []
    index_terms = 0
    question_numbers = []
    in_index_section = False
    prev_level = 0
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if "Índice Geral" in stripped or "Pós-textual" in stripped:
            in_index_section = True
        
        match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{(.*?)\})?$', stripped)
        if not match:
            continue
            
        level = len(match.group(1))
        text = match.group(2).strip()
        anchor = match.group(3)
        
        h_counts[level] += 1
        
        if level > prev_level + 1 and prev_level != 0:
            nesting_issues.append(f"Line {i:5d}: h{prev_level} → h{level}")
        
        if anchor and anchor != "related-term":
            anchor_locations[anchor].append(i)
        
        if level == 6 and in_index_section:
            index_terms += 1
        
        q_match = re.search(r'Q\.(\d+)', text)
        if q_match:
            question_numbers.append(int(q_match.group(1)))
        
        prev_level = level
    
    total = sum(h_counts.values())
    duplicates = {a: lines for a, lines in anchor_locations.items() if len(lines) > 1}
    
    # === Dynamic Scoring (starts at 100) ===
    score = 100
    
    if h_counts[1] != 1:
        score -= 8
    if len(nesting_issues) > 0:
        score -= 15
    if len(duplicates) > 0:
        score -= 12
    if is_lde and index_terms < 500:
        score -= 10
    if h_counts[5] < 300:          # Very low H5 usage
        score -= 8
    
    score = max(0, min(100, score))   # Clamp between 0-100
    
    # Main Feature
    if is_lde:
        feature = f"LDE - {h_counts[5]} Questions at H5 level"
    else:
        feature = f"{book_name} - {h_counts[5]} main units at H5 level"
    
    # Report
    report = [f"# Quality Analysis - {md_path.name}",
              f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    
    report.append(f"**Main Feature:** {feature}")
    report.append(f"**Overall Score:** **{score}%**\n")
    
    report.append("**Heading Counts:**")
    for lvl in range(1, 7):
        report.append(f"- H{lvl}: {h_counts[lvl]}")
    
    report.append(f"\n**Index Terms (H6):** {index_terms}")
    
    if nesting_issues:
        report.append(f"\n**⚠️ Nesting Issues:** {len(nesting_issues)}")
        for issue in nesting_issues[:8]:
            report.append(f"- {issue}")
    else:
        report.append("\n✅ **No nesting issues**")
    
    if duplicates:
        report.append(f"\n**⚠️ Real Duplicate Anchors:** {len(duplicates)}")
        for anchor, line_nums in list(duplicates.items())[:6]:
            report.append(f"- `#{anchor}` → Lines: {line_nums}")
    else:
        report.append("\n✅ **No real duplicate anchors**")
    
    report.append("\n---\n")
    return "\n".join(report)


# ====================== MAIN ======================
root = Path("books/md")
report_dir = Path("reports")
report_dir.mkdir(exist_ok=True)

print("🔍 Running Full Quality Check with Dynamic Scoring...\n")

full_report = ["# Full Quality Check Report\n"]

for book_dir in sorted(root.glob("*/full")):
    full_md = book_dir / f"{book_dir.parent.name}-full.md"
    if full_md.exists():
        analysis = analyze_book(full_md)
        full_report.append(analysis)
        print(f"✅ Analyzed: {full_md.name}")

report_path = report_dir / "full_quality_check.md"
report_path.write_text("\n".join(full_report), encoding='utf-8')

print(f"\n📋 Report saved to: {report_path}")
print("✅ Analysis complete!")