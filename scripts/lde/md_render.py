"""
Shared LDE MD → HTML body renderer (used by CLI + preview tool).
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parents[2]

PAGE_ANCHOR_PATTERN = r"\[\]\{#page-(\d+)\}"
PAGE_TOKEN = "§§PDFPAGE:{num}§§"
CUSTOM_ID_PATTERN = r"\{\s*#[a-zA-Z0-9\-_.]+\s*\}"


def inject_bottom_page_chrome(html: str) -> str:
    """
    []{#page-N} marks the *start* (top) of PDF page N.
    Visible folio N is drawn at the bottom of that page's block.
    """
    token_re = re.compile(r"§§PDFPAGE:(\d+)§§")
    parts = token_re.split(html)
    if len(parts) == 1:
        return html

    out = [parts[0]]
    prev_page = None
    i = 1
    while i < len(parts):
        page_num = parts[i]
        following = parts[i + 1] if i + 1 < len(parts) else ""

        if prev_page is not None:
            out.append(
                f'<div class="pdf-page-footer" data-page-end="{prev_page}" '
                f'aria-label="Fim da página PDF {prev_page}">'
                f'<span class="pdf-page-number">{prev_page}</span>'
                f"</div>\n"
            )
            out.append('<div class="pdf-page-gutter" aria-hidden="true"></div>\n')

        out.append(
            f'<div class="pdf-page-start" id="page-{page_num}" '
            f'data-page="{page_num}" '
            f'aria-label="Início da página PDF {page_num}"></div>\n'
        )
        out.append(following)
        prev_page = page_num
        i += 2

    if prev_page is not None:
        out.append(
            f'<div class="pdf-page-footer" data-page-end="{prev_page}" '
            f'aria-label="Fim da página PDF {prev_page}">'
            f'<span class="pdf-page-number">{prev_page}</span>'
            f"</div>\n"
        )

    html = "".join(out)
    html = re.sub(
        r"<p>\s*(?=<div class=\"pdf-page-(?:footer|start|gutter)\")",
        "",
        html,
    )
    html = re.sub(r"(</div>)\s*</p>", r"\1", html)
    return html


def render_md_to_body(md_text: str) -> str:
    """Convert LDE-flavored Markdown string to HTML body fragment."""
    lines = md_text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n") and md_text and not md_text.endswith("\n"):
        pass  # fine

    processed_lines: list[str] = []
    for line in lines:
        clean_line = line.strip()

        if re.search(PAGE_ANCHOR_PATTERN, line):
            line = re.sub(
                PAGE_ANCHOR_PATTERN,
                lambda m: PAGE_TOKEN.format(num=m.group(1)),
                line,
            )
            clean_line = line.strip()

        header_match = re.match(r"^(#{1,5})\s+(.*)$", clean_line)
        if header_match:
            level = len(header_match.group(1))
            raw_header_text = header_match.group(2)
            header_text = re.sub(CUSTOM_ID_PATTERN, "", raw_header_text).strip()
            processed_lines.append(f"\n\n<h{level}>{header_text}</h{level}>\n\n")
            continue

        processed_lines.append(line)

    final_lines: list[str] = []
    open_divs_count = 0

    for line in "".join(processed_lines).split("\n"):
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

                extra_class = (
                    " hide-metadata-box"
                    if class_name == "expand"
                    and any(x in inline_text for x in ["Termos", "Sub-cap", "Índice"])
                    else ""
                )
                header_html = (
                    f"<div class='box-title'>{inline_text}</div>\n"
                    if class_name == "expand" and inline_text
                    else ""
                )
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

    final_markdown_tree = re.sub(
        r"\!\[([^\]\n]*)\]\(([^)\n]+)\)",
        r'<img src="\2" alt="\1" class="embedded-book-graphic" />',
        final_markdown_tree,
    )
    final_markdown_tree = re.sub(
        r"(?<!\!)\[([^\]\n]+)\]\(([^)\n]+)\)",
        r'<a href="\2">\1</a>',
        final_markdown_tree,
    )
    final_markdown_tree = re.sub(
        r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", final_markdown_tree
    )
    final_markdown_tree = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", final_markdown_tree)
    final_markdown_tree = re.sub(
        r"\[\^([a-zA-Z0-9]+)\]",
        r'<sup class="footnote-ref"><a href="#fn-\1">\1</a></sup>',
        final_markdown_tree,
    )

    html_raw_body = markdown.markdown(
        final_markdown_tree, extensions=["extra", "codehilite"]
    )

    def conditional_replacer(match: re.Match[str]) -> str:
        p_content = match.group(1).strip()
        plain_text_start = re.sub(r"<[^>]*>", "", p_content).lstrip()
        if plain_text_start and (
            plain_text_start.islower() or plain_text_start.isdigit()
        ):
            return f'<p class="no-indent-lowercase">{p_content}</p>'
        return f"<p>{p_content}</p>"

    html_body = re.sub(
        r"<p>(.*?)</p>", conditional_replacer, html_raw_body, flags=re.DOTALL
    )
    return inject_bottom_page_chrome(html_body)


def render_md_to_document(
    md_text: str,
    *,
    title: str = "O Livro dos Espíritos — Preview",
    css_href: str = "layout.css",
) -> str:
    body = render_md_to_body(md_text)
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="stylesheet" href="{css_href}">
</head>
<body>
    {body}
</body>
</html>
"""
