"""
LDE — MD → HTML verification renderer
=====================================
Renders LDE full Markdown to standalone HTML for visual fidelity checks
against the reference PDF (page markers, containers, typography).

Uses books/html/layout.css. Run from anywhere:

    python3 scripts/lde/render_md_to_html.py
"""

import os
import sys
import re
from pathlib import Path

import markdown

# scripts/lde/ → repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
os.chdir(REPO_ROOT)

INPUT_MD = "books/md/1-lde/full/1-lde-full.md"
OUTPUT_HTML = "books/html/1-lde-text-rendered.html"

PAGE_ANCHOR_PATTERN = r"\[\]\{#page-(\d+)\}"
CUSTOM_ID_PATTERN = r"\{\s*#[a-zA-Z0-9\-_.]+\s*\}"

print("=" * 70)
print("🚀 LDE: MD → HTML verification render")
print("=" * 70)

if not os.path.exists(INPUT_MD):
    print(f"❌ ERROR: Master Markdown file missing at: '{INPUT_MD}'")
    sys.exit(1)

with open(INPUT_MD, "r", encoding="utf-8") as f:
    lines = f.readlines()

processed_lines = []
page_counter = 0

for line in lines:
    clean_line = line.strip()

    # Inline page protection
    if re.search(PAGE_ANCHOR_PATTERN, line):
        line = re.sub(PAGE_ANCHOR_PATTERN, lambda m: f'<span id="page-{m.group(1)}" class="pdf-page-marker-inline"></span>', line)
        clean_line = line.strip()

    # Structural heading translation
    header_match = re.match(r"^(#{1,5})\s+(.*)$", clean_line)
    if header_match:
        level = len(header_match.group(1))
        raw_header_text = header_match.group(2)
        header_text = re.sub(CUSTOM_ID_PATTERN, "", raw_header_text).strip()
        processed_lines.append(f'\n\n<h{level}>{header_text}</h{level}>\n\n')
        continue

    processed_lines.append(line)

# Process container blocks (::: spirit, ::: bible, ::: center)
final_lines = []
open_divs_count = 0

for line in "".join(processed_lines).split('\n'):
    clean_line = line.strip()
    if clean_line.startswith(":::"):
        if clean_line == ":::" or clean_line.replace(" ", "") == ":::":
            if open_divs_count > 0:
                final_lines.append("\n</div>\n")
                open_divs_count -= 1
        else:
            container_content = clean_line[3:].strip()
            parts = container_content.split(maxsplit=1)

            if parts:
                class_name = parts[0].strip()
                inline_text = parts[1].strip() if len(parts) > 1 else ""
            else:
                class_name = "generic"
                inline_text = ""

            extra_class = " hide-metadata-box" if class_name == "expand" and any(x in inline_text for x in ["Termos", "Sub-cap", "Índice"]) else ""
            header_html = f"<div class='box-title'>{inline_text}</div>\n" if class_name == "expand" and inline_text else ""

            final_lines.append(f'\n<div class="{class_name}{extra_class}">\n{header_html}\n')
            open_divs_count += 1
            if inline_text and class_name != "expand":
                final_lines.append(inline_text)
        continue

    if open_divs_count > 0 and clean_line.startswith("**"):
        final_lines.append(f"<br />{line}")
    else:
        final_lines.append(line)

while open_divs_count > 0:
    final_lines.append("\n</div>\n")
    open_divs_count -= 1

final_markdown_tree = "\n".join(final_lines)

# 🔬 CORE PRE-PROCESSOR SYNTAX BRIDGES (BLINDING HTML BLOCK CONTAINERS)

# 1. 🖼️ PURE IMAGE CONVERTER: Catches ![Alt](Path) and maps it straight to an HTML image tag
final_markdown_tree = re.sub(
    r"\!\[([^\]\n]*)\]\(([^)\n]+)\)",
    r'<img src="\2" alt="\1" class="embedded-book-graphic" />',
    final_markdown_tree
)

# 2. Hyperlink Selector: Only parses links that do NOT map to graphics
final_markdown_tree = re.sub(r"(?<!\!)\[([^\]\n]+)\]\(([^)\n]+)\)", r'<a href="\2">\1</a>', final_markdown_tree)

# 3. Bold String formatting (**text**)
final_markdown_tree = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", final_markdown_tree)

# 4. Italics formatting (*text*)
final_markdown_tree = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", final_markdown_tree)

# 5. Footnote formatting ([^x])
final_markdown_tree = re.sub(r"\[\^([a-zA-Z0-9]+)\]", r'<sup class="footnote-ref"><a href="#fn-\1">\1</a></sup>', final_markdown_tree)

# Compile body HTML using core extensions
html_raw_body = markdown.markdown(final_markdown_tree, extensions=['extra', 'codehilite'])

# Apply conditional lower-case casing text indentation loops
p_pattern = r"<p>(.*?)</p>"
def conditional_replacer(match):
    p_content = match.group(1).strip()
    plain_text_start = re.sub(r"<[^>]*>", "", p_content).lstrip()
    if plain_text_start and (plain_text_start.islower() or plain_text_start.isdigit()):
        return f'<p class="no-indent-lowercase">{p_content}</p>'
    return f'<p>{p_content}</p>'
html_body = re.sub(p_pattern, conditional_replacer, html_raw_body, flags=re.DOTALL)

# Dynamic badge rendering logic
dynamic_badge_script = """
<script>
    document.addEventListener("DOMContentLoaded", function() {
        document.querySelectorAll('.pdf-page-marker-inline').forEach(function(el) {
            let pageNum = el.id.replace('page-', '');
            let style = document.createElement('style');
            style.innerHTML = 'span[id="' + el.id + '"]::after { content: "📄 FILTRADO: PÁGINA ' + pageNum + '"; font-family: Arial; font-size: 8pt; color: #a89e84; letter-spacing: 2px; font-weight: bold; }';
            document.head.appendChild(style);
        });
    });
</script>
"""

# HTML frame combining the dynamic body with the static external css layer
full_html_document = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>O Livro dos Espíritos — Diagramação Real</title>
    <link rel="stylesheet" href="layout.css">
    {dynamic_badge_script}
</head>
<body>
    {html_body}
</body>
</html>
"""

os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(full_html_document)

print(f"✅ REGEN SYSTEM COMPLETE -> Output file written to: {OUTPUT_HTML}")
