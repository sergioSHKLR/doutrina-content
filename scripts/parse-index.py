#!/usr/bin/env python3
"""
dc Index Parser - Strict letter-based H3 control
"""

import fitz
import re
from pathlib import Path
import sys

def to_superscript(text):
    text = re.sub(r'(\d+)[ªa]', r'\1<sup>a</sup>', text)
    text = re.sub(r'(\d+)[ºo]', r'\1<sup>o</sup>', text)
    return text

def parse_index(pdf_path, start_page=419, end_page=447, output_md=None):
    doc = fitz.open(pdf_path)
    entries = ["# Índice Geral\n"]
    current_letter = None
    current_main = None

    for pnum in range(start_page, end_page + 1):
        page = doc[pnum]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"]).strip()
                if not text or re.match(r'^\d+$', text) or "N.E.:" in text:
                    continue

                if "ÍNDICE GERAL" in text.upper():
                    continue

                x_left = min((span["bbox"][0] for span in line["spans"]), default=0)

                # Letter header
                if re.match(r'^[A-Z]$', text):
                    current_letter = text
                    entries.append(f"\n## {current_letter}")
                    current_main = None
                    continue

                # Main term: left column + starts with current letter
                match = re.match(r'(.+?)\s{2,}[\.\s-]+(.+)', text)
                if (match or text[0].isupper()) and x_left < 170 and current_letter and text[0].upper() == current_letter:
                    if match:
                        term = match.group(1).strip()
                        ref = to_superscript(match.group(2).strip())
                        current_main = f"### {term} — {ref}"
                    else:
                        current_main = f"### {text}"
                    entries.append(f"\n{current_main}")
                else:
                    # Sub-entry / continuation
                    clean = to_superscript(text)
                    if current_main:
                        entries.append(f"- {clean}")
                    else:
                        entries.append(f"- {clean}")

    output_text = "\n".join(entries)

    if output_md:
        Path(output_md).parent.mkdir(parents=True, exist_ok=True)
        Path(output_md).write_text(output_text, encoding="utf-8")
        print(f"✅ Saved to {output_md}")
    else:
        print(output_text[:2500])

    doc.close()
    return output_text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_index.py <pdf_path> [start_page] [end_page] [output.md]")
        sys.exit(1)

    pdf = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 419
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 447
    out = sys.argv[4] if len(sys.argv) > 4 else None

    parse_index(pdf, start, end, out)