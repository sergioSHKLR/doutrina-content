"""
Shared MD → HTML body renderer (used by CLI + multi-book preview tool).
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parents[2]

PAGE_ANCHOR_RE = re.compile(r"\[\]\{#page-(\d+)\}")
# HTML comments survive markdown without becoming visible text.
PAGE_TOKEN = "<!--PDFPAGE:{num}-->"
PAGE_TOKEN_RE = re.compile(r"<!--PDFPAGE:(\d+)-->")
CUSTOM_ID_PATTERN = r"\{\s*#[a-zA-Z0-9\-_.]+\s*\}"
PAGE_CHROME_DIV_RE = (
    r'(?:<div class="pdf-page-(?:footer|start|gutter)"[^>]*>\s*</div>\s*)+'
)


def _is_structural_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.startswith("#"):
        return True
    if s.startswith(":::"):
        return True
    if s.startswith("@@HEADING:"):
        return True
    return False


def normalize_page_anchors(md_text: str) -> str:
    """
    Convert []{#page-N} to HTML comment tokens without breaking Markdown lists
    or polluting heading lines.

    Anchor-only lines (common mid-TOC) attach to the previous non-structural
    content line.  They must not sit alone between nested list items (that
    terminates the list → indented lines become code) and must not be glued
    onto # headings (tokens would land inside <summary>).
    """
    lines = md_text.splitlines(keepends=True)
    out: list[str] = []
    pending: list[str] = []

    def emit_pending_freestanding() -> None:
        nonlocal pending
        for n in pending:
            out.append(PAGE_TOKEN.format(num=n) + "\n")
        pending = []

    def attach_to_previous(nums: list[str]) -> bool:
        comments = "".join(" " + PAGE_TOKEN.format(num=n) for n in nums)
        for j in range(len(out) - 1, -1, -1):
            if not out[j].strip():
                continue
            if _is_structural_line(out[j]):
                return False
            if out[j].endswith("\n"):
                out[j] = out[j][:-1] + comments + "\n"
            else:
                out[j] = out[j] + comments
            return True
        return False

    for line in lines:
        if not PAGE_ANCHOR_RE.search(line):
            if pending and line.strip():
                if _is_structural_line(line):
                    emit_pending_freestanding()
                    out.append(line)
                else:
                    # Prefer end of this content line (keeps lists intact when
                    # a pending token was waiting from a leading anchor line).
                    comments = "".join(PAGE_TOKEN.format(num=n) for n in pending)
                    pending = []
                    if line.endswith("\n"):
                        out.append(line[:-1] + " " + comments + "\n")
                    else:
                        out.append(line + " " + comments)
            else:
                out.append(line)
            continue

        nums = [m.group(1) for m in PAGE_ANCHOR_RE.finditer(line)]
        residual = PAGE_ANCHOR_RE.sub("", line)

        if residual.strip():
            # Inline / mixed on a content line
            new_line = PAGE_ANCHOR_RE.sub(
                lambda m: PAGE_TOKEN.format(num=m.group(1)), line
            )
            if pending:
                if _is_structural_line(new_line):
                    emit_pending_freestanding()
                    out.append(new_line)
                else:
                    comments = "".join(PAGE_TOKEN.format(num=n) for n in pending)
                    pending = []
                    if new_line.endswith("\n"):
                        out.append(new_line[:-1] + " " + comments + "\n")
                    else:
                        out.append(new_line + " " + comments)
            else:
                if _is_structural_line(new_line):
                    # Rare: heading with inline page marker — pull tokens out.
                    pulled = PAGE_TOKEN_RE.findall(new_line)
                    cleaned = PAGE_TOKEN_RE.sub("", new_line)
                    for n in pulled:
                        out.append(PAGE_TOKEN.format(num=n) + "\n")
                    out.append(cleaned)
                else:
                    out.append(new_line)
            continue

        # Anchor-only line
        if not attach_to_previous(nums):
            pending.extend(nums)

    emit_pending_freestanding()
    return "".join(out)


def _extract_chrome_from_containers(html: str) -> str:
    """
    Block-level page chrome must not stay inside <p> or <summary>.
    Single-pass split (no iterative regex — that hung on full-book HTML).
    """
    chrome_split = re.compile(f"({PAGE_CHROME_DIV_RE})")

    def split_tag(tag: str, html_in: str) -> str:
        pattern = re.compile(
            rf"<{tag}(\s[^>]*)?>(.*?)</{tag}>",
            flags=re.DOTALL | re.IGNORECASE,
        )

        def repl(m: re.Match[str]) -> str:
            attrs = m.group(1) or ""
            inner = m.group(2)
            if "pdf-page-" not in inner:
                return m.group(0)
            pieces = chrome_split.split(inner)
            parts: list[str] = []
            for i, piece in enumerate(pieces):
                if i % 2 == 1:
                    # chrome run
                    parts.append(piece)
                elif piece.strip():
                    parts.append(f"<{tag}{attrs}>{piece}</{tag}>")
                elif tag == "summary" and i == 0 and not any(
                    pieces[j].strip() for j in range(0, len(pieces), 2)
                ):
                    # chrome-only summary → drop label, keep chrome
                    pass
            return "\n".join(parts) if parts else m.group(0)

        return pattern.sub(repl, html_in)

    html = split_tag("p", html)
    html = split_tag("summary", html)
    html = re.sub(r"<summary(\s[^>]*)?>\s*</summary>", "", html)
    return html


def inject_bottom_page_chrome(html: str) -> str:
    """
    []{#page-N} marks the *start* (top) of PDF page N.
    Visible folio N is drawn at the bottom of that page's block.
    """
    parts = PAGE_TOKEN_RE.split(html)
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
    html = _extract_chrome_from_containers(html)
    return html


def render_md_to_body(md_text: str, *, open_foldables: bool = True) -> str:
    """
    Convert book Markdown string to HTML body fragment.

    open_foldables: when True (default), emit <details open> so page chrome and
    prose are visible in the preview tool without manually expanding every heading.
    """
    md_text = normalize_page_anchors(md_text)
    lines = md_text.splitlines(keepends=True)
    open_attr = " open" if open_foldables else ""

    processed_lines: list[str] = []
    for line in lines:
        clean_line = line.strip()
        # Strip any page tokens that still sit on a heading line
        if PAGE_TOKEN_RE.search(clean_line):
            if re.match(r"^#{1,5}\s+", PAGE_TOKEN_RE.sub("", clean_line).strip()):
                for n in PAGE_TOKEN_RE.findall(clean_line):
                    processed_lines.append(PAGE_TOKEN.format(num=n) + "\n")
                clean_line = PAGE_TOKEN_RE.sub("", clean_line).strip()
                line = clean_line + ("\n" if line.endswith("\n") else "")

        header_match = re.match(r"^(#{1,5})\s+(.*)$", clean_line)
        if header_match:
            level = len(header_match.group(1))
            raw_header_text = header_match.group(2)
            header_text = re.sub(CUSTOM_ID_PATTERN, "", raw_header_text).strip()
            # page tokens must never enter the summary label
            header_text = PAGE_TOKEN_RE.sub("", header_text).strip()
            processed_lines.append(f"@@HEADING:{level}|{header_text}@@")
            continue

        processed_lines.append(line)

    final_lines: list[str] = []
    open_block_depth = 0
    open_heading_levels: list[int] = []

    for line in "".join(processed_lines).splitlines():
        clean_line = line.strip()

        if clean_line.startswith("@@HEADING:"):
            level_str, title = clean_line[len("@@HEADING:") :].split("|", 1)
            level = int(level_str[:-2] if level_str.endswith("@@") else level_str)
            title = title[:-2] if title.endswith("@@") else title
            while open_heading_levels and open_heading_levels[-1] >= level:
                final_lines.append("</details>\n")
                open_heading_levels.pop()
            final_lines.append(
                f'<details class="foldable-section foldable-heading" markdown="1"{open_attr}>\n'
                f'<summary class="foldable-summary">{title}</summary>\n'
            )
            open_heading_levels.append(level)
            continue

        if clean_line.startswith(":::"):
            if clean_line == ":::" or clean_line.replace(" ", "") == ":::":
                if open_block_depth > 0:
                    final_lines.append("</details>\n")
                    open_block_depth -= 1
            else:
                container_content = clean_line[3:].strip()
                parts = container_content.split(maxsplit=1)
                if parts:
                    class_name = parts[0].strip()
                    inline_text = parts[1].strip() if len(parts) > 1 else ""
                else:
                    class_name = "generic"
                    inline_text = ""

                summary_text = inline_text or class_name
                final_lines.append(
                    f'<details class="foldable-section foldable-block {class_name}" '
                    f'markdown="1"{open_attr}>\n'
                    f'<summary class="foldable-summary">{summary_text}</summary>\n'
                )
                open_block_depth += 1
            continue

        final_lines.append(line)

    while open_heading_levels:
        final_lines.append("</details>\n")
        open_heading_levels.pop()

    while open_block_depth > 0:
        final_lines.append("</details>\n")
        open_block_depth -= 1

    final_markdown_tree = "\n".join(final_lines)

    final_markdown_tree = re.sub(
        r"\!\[([^\]\n]*)\]\(([^)\n]+)\)",
        r'<img src="\2" alt="\1" class="embedded-book-graphic" />',
        final_markdown_tree,
    )
    # Bold/italic as HTML so <summary> labels (not processed by md_in_html) still
    # render emphasis. Do NOT pre-bake [text](url) → <a>: that + list indentation
    # turns nested TOCs into code blocks.
    final_markdown_tree = re.sub(
        r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", final_markdown_tree
    )
    final_markdown_tree = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", final_markdown_tree)
    final_markdown_tree = re.sub(
        r"\[\^([a-zA-Z0-9]+)\]",
        r'<sup class="footnote-ref"><a href="#fn-\1">\1</a></sup>',
        final_markdown_tree,
    )

    # No codehilite: nested TOC indents must remain lists.
    html_raw_body = markdown.markdown(
        final_markdown_tree, extensions=["extra", "md_in_html"]
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
    title: str = "Book Preview",
    css_href: str = "layout.css",
    open_foldables: bool = True,
) -> str:
    body = render_md_to_body(md_text, open_foldables=open_foldables)
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
