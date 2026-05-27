#!/usr/bin/env python3
"""
Numerical Sequence Analyzer
- Counts all headings
- Finds the largest unbroken numerical sequence per level
- Identifies main content feature per book
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

def find_largest_sequence(numbers):
    if not numbers:
        return 0, []
    numbers = sorted(set(numbers))
    max_len = 1
    current_len = 1
    best_start = numbers[0]
    
    for i in range(1, len(numbers)):
        if numbers[i] == numbers[i-1] + 1:
            current_len += 1
            if current_len > max_len:
                max_len = current_len
                best_start = numbers[i] - current_len + 1
        else:
            current_len = 1
    return max_len, list(range(best_start, best_start + max_len))

def analyze_book(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    clean_content = remove_frontmatter(content)
    lines = clean_content.splitlines()
    
    h_counts = {i: 0 for i in range(1, 7)}
    sequences = defaultdict(list)
    book_name = md_path.name.replace('-full.md', '').upper()
    
    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{.*?\})?$', line.strip())
        if not match:
            continue
            
        level = len(match.group(1))
        text = match.group(2).strip()
        h_counts[level] += 1
        
        # Extract numbers
        num_matches = re.findall(r'(?:^|\s|Q\.|\#️⃣|\d+\.)(\d+)', text)
        for n in num_matches:
            try:
                sequences[level].append(int(n))
            except:
                pass
    
    report = []
    report.append(f"# Numerical Sequence Analysis - {md_path.name}")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total = sum(h_counts.values())
    report.append(f"**Total Headings:** {total}")
    for lvl in range(1, 7):
        report.append(f"- H{lvl}: {h_counts[lvl]}")
    
    report.append("\n**Largest Unbroken Sequences:**")
    for lvl in range(4, 7):  # Focus on content levels
        if sequences[lvl]:
            length, seq = find_largest_sequence(sequences[lvl])
            report.append(f"- H{lvl}: **{length}** consecutive numbers ({seq[0]}-{seq[-1] if seq else ''})")
    
    # Main Feature
    if h_counts[5] > 1000:
        feature = f"LDE - {h_counts[5]} Questions at H5 level"
    elif "ldm" in book_name.lower():
        feature = f"LDM - ~{h_counts[5]} Paragraphs at H5 level"
    else:
        feature = f"Main sequential content at H5 level ({h_counts[5]} units)"
    
    report.append(f"\n**Main Book Feature:** {feature}")
    report.append("\n---\n")
    return "\n".join(report)


# ====================== MAIN ======================
root = Path("books/md")
report_dir = Path("reports")
report_dir.mkdir(exist_ok=True)

print("🔍 Analyzing numerical sequences and structure...\n")

full_report = ["# Numerical Sequence & Structure Analysis Report\n"]

for book_dir in sorted(root.glob("*/full")):
    full_md = book_dir / f"{book_dir.parent.name}-full.md"
    if full_md.exists():
        analysis = analyze_book(full_md)
        full_report.append(analysis)
        print(f"✅ Analyzed: {full_md.name}")

report_path = report_dir / "numerical_sequence_analysis.md"
report_path.write_text("\n".join(full_report), encoding='utf-8')

print(f"\n📋 Report saved to: {report_path}")