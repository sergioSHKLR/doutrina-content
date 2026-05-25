#!/usr/bin/env python3
"""
Detailed Heading Compliance Analyzer for doutrina-content
- Smarter contextual nesting detection
- More tolerant of h6 directly under h4 (common pattern)
"""

import re
from pathlib import Path
from datetime import datetime

def remove_frontmatter(content: str) -> str:
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content

def analyze_file_detailed(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    clean_content = remove_frontmatter(content)
    lines = clean_content.splitlines()
    
    h_counts = {i: 0 for i in range(1, 7)}
    issues = []
    h6_samples = []
    last_level = 0
    last_h5_line = 0
    
    for i, line in enumerate(lines, 1):
        match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{.*?\})?$', line.strip())
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            h_counts[level] += 1

            # h6 Samples
            if level == 6 and len(h6_samples) < 12:
                h6_samples.append(f"Line {i:5d}: {text[:85]}")

            # === Smarter Nesting Logic ===
            if level > last_level + 1 and not (level == 6 and last_level in (4, 5)):
                issues.append(f"Line {i:5d}: Large jump h{last_level} → h{level} | {text[:60]}")

            # Specific h6 warning only in problematic cases
            if level == 6:
                if last_level == 3:   # Too high
                    issues.append(f"Line {i:5d}: h6 directly under h3 (should be under h4/h5) → {text[:55]}")
                elif last_level == 2:
                    issues.append(f"Line {i:5d}: h6 under h2 → {text[:55]}")

            if level == 5:
                last_h5_line = i

            last_level = level

    total = sum(h_counts.values())
    
    # Scoring
    score = 75
    if h_counts[1] == 1: score += 8
    if h_counts[6] > 200: score += 10
    if h_counts[5] > 100: score += 7
    if h_counts[5] == 0 and h_counts[6] > 300: score -= 15
    score = min(100, max(50, score))
    
    report = f"""# Heading Compliance Report - {md_path.name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

- Total Headings: {total}
h1: {h_counts[1]}
h2: {h_counts[2]}
h3: {h_counts[3]}
h4: {h_counts[4]}
h5: {h_counts[5]}
h6: {h_counts[6]}

## Compliance Score: **{score}%**

## Observations
"""

    if h_counts[1] != 1:
        report += f"- ⚠️ Found {h_counts[1]} h1 headings\n"
    if h_counts[5] == 0 and h_counts[6] > 100:
        report += f"- ⚠️ Note: {h_counts[6]} h6 with no h5 (common in LDM/ESE/CEU/GEN)\n"
    
    report += "\n## Sample h6 (Index Terms):\n"
    for sample in h6_samples:
        report += f"- {sample}\n"
    
    if issues:
        report += f"\n## Nesting Issues Detected ({len(issues)}):\n"
        for issue in issues[:20]:
            report += f"- {issue}\n"
    else:
        report += "\n## Nesting Issues: None detected ✅\n"
    
    return report.strip()


# ====================== MAIN ======================
root = Path("books/md")
reports_dir = Path("reports")
reports_dir.mkdir(exist_ok=True)

print("🔍 Generating Final Detailed Reports...\n")

for book_dir in sorted(root.glob("*/full")):
    full_md = book_dir / f"{book_dir.parent.name}-full.md"
    if full_md.exists():
        report_text = analyze_file_detailed(full_md)
        report_path = reports_dir / f"compliance_{book_dir.parent.name}.md"
        report_path.write_text(report_text, encoding='utf-8')
        print(f"✅ Saved: reports/compliance_{book_dir.parent.name}.md")

print("\n🎉 Analysis completed with improved logic!")