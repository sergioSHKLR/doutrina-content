"""
LDE Markdown-to-HTML Verification Engine (with Page Dividers)
=============================================================
Domain: Allan Kardec's "O Livro dos Espíritos" (LDE)
Purpose: Extracts the first 50 pages of text, converts custom container blocks,
         injects explicit horizontal lines at every page break, and compiles
         a clean standalone HTML web document for visual auditing.
"""

import os
import sys
import re
import markdown

INPUT_MD = "books/md/1-lde/full/1-lde-full.md"
OUTPUT_HTML = "books/html/1-lde-text-rendered.html"

PAGE_ANCHOR_PATTERN = r"\[\]\{#page-(\d+)\}"
MAX_PAGES_LIMIT = 50

print("=" * 75)
print(f"#️⃣ STEP 1: ISOLATING TEXT BLOCKS FOR THE FIRST {MAX_PAGES_LIMIT} PAGES")
print("=" * 75)

if not os.path.exists(INPUT_MD):
    print(f"❌ ERROR: Master Markdown file missing at: '{INPUT_MD}'")
    sys.exit(1)

extracted_markdown_lines = []
page_count = 0

with open(INPUT_MD, "r", encoding="utf-8") as f:
    for line in f:
        # Check if we are passing a new page transition marker
        matches = re.findall(PAGE_ANCHOR_PATTERN, line)
        if matches:
            page_count += 1
            if page_count > MAX_PAGES_LIMIT:
                print(f"Reached page marker {page_count}. Stopping extraction.")
                break

            # --- DYNAMIC VISUAL PAGE BREAK INJECTION ---
            # Instead of leaving it invisible, we inject a horizontal divider and a visible header
            # into the Markdown processing array stream dynamically during runtime.
            page_num = matches[0]
            divider_block = f"\n\n---\n\n### 📄 QUEBRA DE PÁGINA IMPRESSA: PÁGINA {page_num} {{#visual-page-{page_num}}}\n\n"
            extracted_markdown_lines.append(divider_block)

        extracted_markdown_lines.append(line)

raw_sliced_markdown = "".join(extracted_markdown_lines)
print(f"Extracted {len(extracted_markdown_lines)} lines of text context for conversion.")


# --- 🛠️ THE CONTAINER BLOCK BRIDGE PRE-PROCESSOR ---
def parse_custom_containers(md_text):
    """
    Transforms your custom `::: spirit` markdown blocks into standard
    HTML `<div class="spirit">` containers so they can be styled via CSS.
    """
    pattern = r":::\s*([a-zA-Z0-9\-_]+)\s*\n(.*?)\n:::"

    def replace_with_div(match):
        class_name = match.group(1)
        body_content = match.group(2)
        return f'<div class="{class_name}">\n\n{body_content}\n\n</div>'

    return re.sub(pattern, replace_with_div, md_text, flags=re.DOTALL)


print("\n" + "=" * 75)
print("🎨 STEP 2: TRANSLATING CONTENT FLOWS & CONTAINERS TO STYLIZED HTML")
print("=" * 75)

# Bridge the containers first, then pass to markdown pipeline
processed_markdown = parse_custom_containers(raw_sliced_markdown)
html_body = markdown.markdown(processed_markdown, extensions=['extra', 'codehilite'])

# Styling configurations for clean readability
custom_css = """
<style>
    body {
        font-family: 'Georgia', 'Times New Roman', serif;
        line-height: 1.6;
        color: #111;
        font-size: 12pt;
        max-width: 800px;
        margin: 40px auto;
        padding: 0 20px;
        background-color: #fdfdfd;
    }
    h1, h2, h3, h4, h5 {
        color: #2c3e50;
        font-family: 'Helvetica', 'Arial', sans-serif;
        margin-top: 1.5em;
    }
    p {
        margin-bottom: 1.2em;
        text-align: justify;
    }

    /* 🛑 STYLING FOR THE INJECTED HORIZONTAL PAGE BREAKS */
    hr {
        border: 0;
        height: 2px;
        background-image: linear-gradient(to right, rgba(231, 76, 60, 0), rgba(231, 76, 60, 0.75), rgba(231, 76, 60, 0));
        margin: 40px 0 10px 0;
    }
    h3[id^="visual-page-"] {
        text-align: center;
        color: #e74c3c;
        font-size: 10pt;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 30px;
        font-weight: bold;
    }

    /* 🏛️ Production Styling For Your Custom Containers */
    .spirit {
        background-color: #f4f7f9;
        border-left: 4px solid #3498db;
        padding: 12px 18px;
        margin: 18px 0;
        font-style: italic;
        border-radius: 0 4px 4px 0;
    }
    .kardec {
        background-color: #fffbf5;
        border-left: 4px solid #e67e22;
        padding: 12px 18px;
        margin: 18px 0;
        border-radius: 0 4px 4px 0;
    }
    .expand {
        border: 1px solid #e0e0e0;
        padding: 12px;
        border-radius: 6px;
        background-color: #fafafa;
        margin: 15px 0;
    }
    .center {
        text-align: center;
        display: block;
    }
</style>
"""

full_html_document = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LDE Verification Stream (Pages 1-50)</title>
    {custom_css}
</head>
<body>
    {html_body}
</body>
</html>
"""

os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(full_html_document)

print("✅ SUCCESS: Standalone verification HTML compiled flawlessly!")
print(f"🚀 Open this file in your browser to verify layouts: {OUTPUT_HTML}")
print("=" * 75)
