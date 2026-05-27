#!/usr/bin/env python3
"""
Find Missing Custom Anchors + Recommend Codex Anchors
"""

import re
from pathlib import Path
from datetime import datetime

# Codex rules per book
CODEX_CONFIG = {
    '1-lde': {'prefix': 'Q', 'padding': 4, 'level': 5},
    '2-ldm': {'prefix': 'P', 'padding': 3, 'level': 5},
    '3-ese': {'prefix': 'I', 'padding': 3, 'level': 5},
    '4-ceu': {'prefix': 'E', 'padding': 3, 'level': 5},
    '5-gen': {'prefix': 'S', 'padding': 3, 'level': 5},
}

def suggest_codex_anchor(book_code: str, text: str, level: int) -> str | None:
    config = CODEX_CONFIG.get(book_code)
    if not config or level != config['level']:
        return None
    
    # Try to extract number from text
    num_match = re.search(r'(\d{1,4})', text)
    if num_match:
        num = int(num_match.group(1))
        padded = str(num).zfill(config['padding'])
        return f"{config['prefix']}{padded}"
    return None

def analyze_missing_anchors(md_path: Path):
    content = md_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    book_code = md_path.name[:5]
    report = []
    missing = []
    
    report.append(f"# Missing Anchors Analysis - {md_path.name}")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for i, line in enumerate(lines, 1):
        match = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{.*?\})?$', line.strip())
        if not match:
            continue
            
        level = len(match.group(1))
        text = match.group(2).strip()
        
        # Check if it has anchor
        has_anchor = '{' in line and '#}' in line
        
        if not has_anchor and level >= 4:   # Focus on important headings
            suggested = suggest_codex_anchor(book_code, text, level)
            missing.append({
                'line': i,
                'level': level,
                'text': text[:80],
                'suggested': suggested
            })
    
    report.append(f"**Total Missing Anchors:** {len(missing)}\n")
    
    if missing:
        report.append("**Recommended Fixes:**")
        for item in missing[:30]:  # Limit output
            report.append(f"- Line {item['line']:5d} | H{item['level']} | {item['text']}")
            if item['suggested']:
                report.append(f"   → Suggested: {{#{item['suggested']}}}")
        if len(missing) > 30:
            report.append(f"\n... and {len(missing)-30} more missing anchors")
    else:
        report.append("✅ **No missing anchors on important headings!**")
    
    report.append("\n---\n")
    return "\n".join(report)


# ====================== MAIN ======================
root = Path("books/md")
report_dir = Path("reports")
report_dir.mkdir(exist_ok=True)

print("🔍 Scanning for missing custom anchors...\n")

full_report = ["# Missing Anchors & Codex Recommendations Report\n"]

for book_dir in sorted(root.glob("*/full")):
    full_md = book_dir / f"{book_dir.parent.name}-full.md"
    if full_md.exists():
        analysis = analyze_missing_anchors(full_md)
        full_report.append(analysis)
        print(f"✅ Analyzed: {full_md.name}")

report_path = report_dir / "missing_anchors_report.md"
report_path.write_text("\n".join(full_report), encoding='utf-8')

print(f"\n📋 Full report saved to: {report_path}")
print("✅ Analysis complete!")