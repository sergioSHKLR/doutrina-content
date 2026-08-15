#!/usr/bin/env python3
"""
Add Pandoc-style heading anchors {#id} derived from numerical prefixes.

DOUTRINA compile (tools/markdown-to-html.mjs) only puts headings in the reader
TOC when they end with an explicit {#anchor}. LDE already has them; imports
like ESE often do not.

Examples
  ## 0. 🗃️ Pré-textual          →  ## 0. 🗃️ Pré-textual {#ese-0}
  ### 0.00. 📄 Folha de rosto   →  ### 0.00. 📄 Folha de rosto {#ese-0-00}
  #### 1.01.01. 📄 Moisés       →  #### 1.01.01. 📄 Moisés {#ese-1-01-01}
  # Title (H1, no number)       →  # Title {#ese}

Also handles:
  ##### #️⃣ 01                  →  {#<parent>-n01}   (paragraph numbers)
  ##### 🔖 Termo                →  {#ese-<slug>}    (glossary; --no-glossary to skip)
  double prefixes (import noise)
    #### 1.25.01. 📄 0.04.01. … → prefers the prefix that nests under the parent

Usage
  # Preview (no write)
  python3 scripts/add-heading-anchors.py src/content/books/ese/book.md

  # Write in place (backup: book.md.bak)
  python3 scripts/add-heading-anchors.py src/content/books/ese/book.md --write

  # Replace existing {#…} on headings/
  python3 scripts/add-heading-anchors.py src/content/books/ese/book.md --write --force

  # Explicit slug (default: front-matter `slug:` or folder name)
  python3 scripts/add-heading-anchors.py path/to/book.md --slug ese --write

Then rebuild:
  npm run build
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

HEADING_RE = re.compile(r"^([ \t]{0,3})(#{1,6})([ \t]+)(.*)$")
EXISTING_ANCHOR_RE = re.compile(r"\s*\{#([a-zA-Z0-9-_:.]+)\}\s*$")
NUM_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)*)\.\s+")
HASH_NUM_RE = re.compile(r"^(?:#️⃣|🔢)\s*(\d+)\s*$")
GLOSSARY_RE = re.compile(r"^🔖\s*(.+?)\s*$")
FM_SLUG_RE = re.compile(r"(?m)^slug:\s*[\"']?([A-Za-z0-9_-]+)[\"']?\s*$")
NON_WORD = re.compile(r"[^a-z0-9]+")


def strip_accents(s: str) -> str:
    nk = unicodedata.normalize("NFD", s)
    return "".join(c for c in nk if unicodedata.category(c) != "Mn")


def slugify_text(text: str) -> str:
    """LDE-style glossary slug: accent-fold, lowercase, hyphenate."""
    base = strip_accents(text).casefold()
    # Drop common “ver X” tails noise lightly — keep full phrase otherwise
    base = NON_WORD.sub("-", base).strip("-")
    return base


def parse_front_matter_slug(raw: str) -> str | None:
    if not raw.startswith("---"):
        return None
    end = raw.find("\n---", 3)
    if end < 0:
        return None
    fm = raw[3:end]
    m = FM_SLUG_RE.search(fm)
    return m.group(1) if m else None


def strip_existing_anchor(text: str) -> tuple[str, str | None]:
    m = EXISTING_ANCHOR_RE.search(text)
    if not m:
        return text.rstrip(), None
    return text[: m.start()].rstrip(), m.group(1)


def extract_numeric_prefixes(text: str) -> list[str]:
    """
    Leading hierarchical numbers, allowing an icon/token between doubles:
      '0. 🗃️ Pré'              → ['0']
      '0.00. 📄 Folha'         → ['0.00']
      '1.25.01. 📄 0.04.01. …' → ['1.25.01', '0.04.01']
      '1.28.02. 📄 01. Preces' → ['1.28.02', '01']
    """
    prefs: list[str] = []
    rest = text
    while True:
        m = NUM_PREFIX_RE.match(rest)
        if not m:
            break
        prefs.append(m.group(1))
        rest = rest[m.end() :]
        # optional single non-numeric token, then maybe another N.N. prefix
        m2 = re.match(r"^(\S+)\s+", rest)
        if not m2 or re.match(r"^\d", m2.group(1)):
            break
        peek = rest[m2.end() :]
        if NUM_PREFIX_RE.match(peek):
            rest = peek
            continue
        break
    return prefs


def nests_under(child: str, parent: str | None) -> bool:
    if parent is None:
        return True
    return child == parent or child.startswith(parent + ".")


def choose_prefix(prefs: list[str], parent_num: str | None) -> str | None:
    if not prefs:
        return None
    if len(prefs) == 1:
        return prefs[0]
    for p in prefs:
        if nests_under(p, parent_num):
            return p
    return prefs[0]


def num_to_anchor(slug: str, num: str) -> str:
    return f"{slug}-" + num.replace(".", "-")


def unique_id(base: str, used: set[str]) -> str:
    if base not in used:
        used.add(base)
        return base
    n = 2
    while f"{base}-{n}" in used:
        n += 1
    out = f"{base}-{n}"
    used.add(out)
    return out


def process(
    raw: str,
    slug: str,
    *,
    force: bool,
    glossary: bool,
    slugify_rest: bool,
) -> tuple[str, dict]:
    lines = raw.splitlines(keepends=True)
    out: list[str] = []
    stats = {
        "headings": 0,
        "added": 0,
        "kept": 0,
        "replaced": 0,
        "skipped": 0,
        "collisions_resolved": 0,
    }
    used: set[str] = set()
    # stack of (level, numeric_path|None, anchor_id|None)
    stack: list[tuple[int, str | None, str | None]] = []

    for line in lines:
        # preserve newline style
        if line.endswith("\r\n"):
            nl, body = "\r\n", line[:-2]
        elif line.endswith("\n"):
            nl, body = "\n", line[:-1]
        else:
            nl, body = "", line

        m = HEADING_RE.match(body)
        if not m:
            out.append(line)
            continue

        indent, hashes, sp, rest = m.group(1), m.group(2), m.group(3), m.group(4)
        level = len(hashes)
        text, existing = strip_existing_anchor(rest)
        stats["headings"] += 1

        while stack and stack[-1][0] >= level:
            stack.pop()
        parent_num = next((p[1] for p in reversed(stack) if p[1] is not None), None)
        parent_id = next((p[2] for p in reversed(stack) if p[2] is not None), None)

        new_id: str | None = None
        num_path: str | None = None

        prefs = extract_numeric_prefixes(text)
        chosen = choose_prefix(prefs, parent_num)
        if chosen is not None:
            num_path = chosen
            new_id = num_to_anchor(slug, chosen)
        else:
            hm = HASH_NUM_RE.match(text)
            if hm:
                base_parent = parent_id or slug
                new_id = f"{base_parent}-n{hm.group(1)}"
            elif glossary and GLOSSARY_RE.match(text):
                term = GLOSSARY_RE.match(text).group(1)  # type: ignore[union-attr]
                # Drop trailing “ver …” for stabler ids when present
                term = re.split(r"\s+ver\s+", term, maxsplit=1, flags=re.I)[0]
                s = slugify_text(term)
                if s:
                    new_id = f"{slug}-{s}"
            elif level == 1:
                new_id = slug
            elif slugify_rest:
                s = slugify_text(re.sub(r"^(?:#️⃣|🔢)\s*", "", text))
                if s:
                    base_parent = parent_id or slug
                    new_id = f"{base_parent}-{s}"

        if existing and not force:
            # Keep authored id; still track for parent chain
            used.add(existing)
            stats["kept"] += 1
            stack.append((level, num_path if num_path else parent_num, existing))
            out.append(body + nl)
            continue

        if not new_id:
            stats["skipped"] += 1
            stack.append((level, parent_num, parent_id))
            # strip stale anchor if force and we could not compute a new one
            if existing and force:
                out.append(f"{indent}{hashes}{sp}{text}{nl}")
            else:
                out.append(body + nl)
            continue

        before = new_id
        new_id = unique_id(new_id, used)
        if new_id != before:
            stats["collisions_resolved"] += 1

        if existing and force:
            stats["replaced"] += 1
        else:
            stats["added"] += 1

        stack.append((level, num_path if num_path else parent_num, new_id))
        out.append(f"{indent}{hashes}{sp}{text} {{#{new_id}}}{nl}")

    return "".join(out), stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Add {#slug-…} heading anchors from numerical prefixes (TOC ids)."
    )
    ap.add_argument(
        "path",
        type=Path,
        help="Markdown book file (e.g. src/content/books/ese/book.md)",
    )
    ap.add_argument(
        "--slug",
        help="Book slug for ids (default: front-matter slug or parent folder name)",
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Write changes in place (default is dry-run to stdout summary only)",
    )
    ap.add_argument(
        "--stdout",
        action="store_true",
        help="Print full rewritten markdown to stdout (implies dry-run of file)",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Replace existing {#…} anchors on headings",
    )
    ap.add_argument(
        "--no-glossary",
        action="store_true",
        help="Do not invent anchors for 🔖 glossary headings",
    )
    ap.add_argument(
        "--slugify-rest",
        action="store_true",
        help="Also slugify non-numeric leftover headings (titled #️⃣ blocks, etc.)",
    )
    ap.add_argument(
        "--no-backup",
        action="store_true",
        help="With --write, do not create path.bak",
    )
    args = ap.parse_args(argv)

    path: Path = args.path
    if not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        return 1

    raw = path.read_text(encoding="utf-8")
    slug = args.slug or parse_front_matter_slug(raw) or path.parent.name
    if not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
        print(f"error: invalid slug {slug!r}", file=sys.stderr)
        return 1

    new_raw, stats = process(
        raw,
        slug,
        force=args.force,
        glossary=not args.no_glossary,
        slugify_rest=args.slugify_rest,
    )

    changed = new_raw != raw
    print(f"file:     {path}")
    print(f"slug:     {slug}")
    print(f"headings: {stats['headings']}")
    print(f"added:    {stats['added']}")
    print(f"kept:     {stats['kept']}")
    print(f"replaced: {stats['replaced']}")
    print(f"skipped:  {stats['skipped']}")
    print(f"id fixes: {stats['collisions_resolved']} (duplicate base ids)")
    print(f"changed:  {changed}")

    if args.stdout:
        sys.stdout.write(new_raw)
        return 0

    if not args.write:
        print("dry-run:  pass --write to save (creates .bak unless --no-backup)")
        # Sample a few planned anchors for confidence
        if changed:
            print("sample:")
            n = 0
            for a, b in zip(raw.splitlines(), new_raw.splitlines()):
                if a != b and "{#" in b:
                    print(f"  {b.strip()[:120]}")
                    n += 1
                    if n >= 8:
                        break
        return 0

    if not changed:
        print("write:    nothing to do")
        return 0

    if not args.no_backup:
        bak = path.with_suffix(path.suffix + ".bak")
        bak.write_text(raw, encoding="utf-8")
        print(f"backup:   {bak}")

    path.write_text(new_raw, encoding="utf-8")
    print(f"wrote:    {path}")
    print("next:     npm run build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
