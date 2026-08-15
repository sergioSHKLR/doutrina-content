#!/usr/bin/env python3
"""
One-shot migration: serial heading codex + emoji ladder + strip outline numbers.

  s = LDE, m = LDM, e = ESE, c = CEU, g = GEN
  {#s0001} … document-order H1–H6 (body only; YAML front matter untouched)

Edits books/md/*/full/*-full.md in place. Safe to re-run only on backups.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

BOOKS = [
    ("s", REPO / "books/md/1-lde/full/1-lde-full.md"),
    ("m", REPO / "books/md/2-ldm/full/2-ldm-full.md"),
    ("e", REPO / "books/md/3-ese/full/3-ese-full.md"),
    ("c", REPO / "books/md/4-ceu/full/4-ceu-full.md"),
    ("g", REPO / "books/md/5-gen/full/5-gen-full.md"),
]

BOOK_H1_EMOJI = {
    "s": "✨",
    "m": "✒️",
    "e": "🕊️",
    "c": "🔥",
    "g": "🌱",
}

# Optional leading indent (LDE full has many " ### …" lines)
HEAD_RE = re.compile(r"^[ \t]*(#{1,6})\s+(.*?)\s*$")
ID_RE = re.compile(r"\{#([a-zA-Z0-9_.:-]+)\}")
# Outline path at start: "0. ", "1.05. ", "0.04.01. "
OUTLINE_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
# Leading emoji cluster (incl. keycap #️⃣)
EMOJI_RE = re.compile(
    r"^("
    r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF"
    r"\U0000FE0F\U0000200D#*0-9⃣️‍]+"
    r")\s*"
)
H3_EXCEPTIONS = {
    "⚖️",
    "📋",
    "📝",
    "📑",  # rare; keep if intentional
}
# Content that should stay as nota glyph at H5
NOTA_RE = re.compile(r"nota", re.I)
Q_RE = re.compile(r"^Q\.?\s*(\d+)\s*\.?\s*([a-z])?\s*$", re.I)
Q_INLINE_RE = re.compile(r"^Q\.?\s*(\d+)\s*\.?\s*([a-z])?", re.I)
NUM_ONLY_RE = re.compile(r"^(\d+)\s*\.?\s*([a-z])?\s*$", re.I)
# "790.a" or "790a"
NUM_DOT_LETTER_RE = re.compile(r"^(\d+)\.([a-z])\s*$", re.I)


@dataclass
class Heading:
    line_index: int  # 0-based in full file lines
    raw_line: str
    level: int
    old_ids: list[str]
    title_core: str  # without {#ids}, before final emoji normalize
    new_level: int = 0
    new_title: str = ""  # final title with emoji, no id
    new_id: str = ""
    is_index_term: bool = False
    is_nota: bool = False


def split_yaml_region(lines: list[str]) -> tuple[int, int]:
    """Return [start, end) line indices of YAML front matter, or (0,0)."""
    if not lines or lines[0].strip() != "---":
        return 0, 0
    for i in range(1, min(len(lines), 120)):
        if lines[i].strip() == "---":
            return 0, i + 1
    return 0, 0


def strip_ids(title: str) -> tuple[str, list[str]]:
    ids = ID_RE.findall(title)
    core = ID_RE.sub("", title).strip()
    core = re.sub(r"\s{2,}", " ", core)
    return core, ids


def strip_outline_prefix(title: str) -> str:
    return OUTLINE_PREFIX_RE.sub("", title).strip()


def peel_emoji(title: str) -> tuple[str, str]:
    """Return (emoji_or_empty, rest)."""
    m = EMOJI_RE.match(title)
    if not m:
        return "", title.strip()
    return m.group(1), title[m.end() :].strip()


def normalize_unit_number(rest: str) -> str | None:
    """
    If rest is a bare unit number (Q.12, 12, 01, 790a, 790.a), return canonical
    display number without padding: '12', '790.a'.
    """
    rest = rest.strip()
    rest = rest.strip("*").strip()
    # *Nota* etc. not a unit number
    if NOTA_RE.search(rest) and not re.match(r"^\d", rest):
        return None

    m = Q_RE.match(rest) or Q_INLINE_RE.match(rest)
    if m and (m.end() >= len(rest) - 1 or rest[m.end() :].strip() in ("", "*", "**")):
        num, letter = m.group(1), m.group(2)
        # only pure Q titles
        if Q_RE.match(rest.strip().strip("*")):
            num = str(int(num))  # strip leading zeros
            if letter:
                return f"{num}.{letter.lower()}"
            return num

    m = NUM_DOT_LETTER_RE.match(rest)
    if m:
        return f"{int(m.group(1))}.{m.group(2).lower()}"

    m = NUM_ONLY_RE.match(rest)
    if m:
        num = str(int(m.group(1)))
        letter = m.group(2)
        if letter:
            return f"{num}.{letter.lower()}"
        return num

    # "Q.790.a" style
    m = re.match(r"^Q\.?\s*(\d+)\.([a-z])\s*$", rest, re.I)
    if m:
        return f"{int(m.group(1))}.{m.group(2).lower()}"

    # "Q.1 …" with trailing text — keep full rest, only strip Q. prefix
    m = re.match(r"^Q\.?\s*(\d+)\.([a-z])?\s+(.*)$", rest, re.I)
    if m:
        num = str(int(m.group(1)))
        letter = m.group(2)
        tail = m.group(3).strip()
        if letter:
            return f"{num}.{letter.lower()} {tail}"
        return f"{num} {tail}" if tail else num

    m = re.match(r"^Q\.?\s*(\d+)\s*$", rest, re.I)
    if m:
        return str(int(m.group(1)))

    return None


def classify_and_build(
    letter: str, level: int, core: str
) -> tuple[int, str, bool, bool]:
    """
    Returns (new_level, new_title_with_emoji, is_index, is_nota).
    """
    core = strip_outline_prefix(core)
    old_emoji, rest = peel_emoji(core)
    rest = rest.strip()

    # Index terms: bookmark → H6
    if old_emoji == "🔖" or rest.startswith("🔖"):
        if rest.startswith("🔖"):
            rest = rest[1:].strip()
        # keep term text; ensure single 🔖
        return 6, f"🔖 {rest}".strip(), True, False

    # Explicit nota
    is_nota = old_emoji == "📝" or bool(NOTA_RE.search(rest)) and level >= 5
    if is_nota and (old_emoji in ("📝", "🔢", "#️⃣", "📃", "") or NOTA_RE.search(rest)):
        # normalize to 📝 on H5
        body = rest if not NOTA_RE.match(rest) else rest
        if old_emoji == "📝":
            body = rest
        return max(level, 5) if level < 5 else level, f"📝 {body}".strip(), False, True

    # H1 book identity
    if level == 1:
        em = BOOK_H1_EMOJI[letter]
        # drop redundant book emoji from rest if duplicate
        return 1, f"{em} {rest}".strip() if rest else em, False, False

    if level == 2:
        return 2, f"🗃️ {rest}".strip(), False, False

    if level == 3:
        if old_emoji in H3_EXCEPTIONS or old_emoji in ("⚖️", "📋", "📝"):
            em = old_emoji if old_emoji in ("⚖️", "📋", "📝") else "🗂️"
            # map known exceptions
            if old_emoji in ("⚖️", "📋", "📝"):
                em = old_emoji
            return 3, f"{em} {rest}".strip(), False, False
        # title-based exceptions
        low = rest.lower()
        if "aviso" in low or "legal" in low:
            return 3, f"⚖️ {rest}".strip(), False, False
        if "sumário" in low or "sumario" in low:
            return 3, f"📋 {rest}".strip(), False, False
        if "nota" in low and "rodapé" in low:
            return 3, f"📝 {rest}".strip(), False, False
        if "folha de rosto" in low:
            return 3, f"🗂️ {rest}".strip(), False, False
        return 3, f"🗂️ {rest}".strip(), False, False

    if level == 4:
        return 4, f"📑 {rest}".strip(), False, False

    if level == 5:
        # unit numbers → #️⃣
        unit = normalize_unit_number(rest)
        if unit is not None and not is_nota:
            return 5, f"#️⃣ {unit}", False, False
        # leftover 🔢 / #️⃣ / 📃 with number
        unit2 = normalize_unit_number(rest)
        if old_emoji in ("#️⃣", "🔢", "📃"):
            unit = normalize_unit_number(rest)
            if unit is not None:
                return 5, f"#️⃣ {unit}", False, False
            return 5, f"#️⃣ {rest}".strip(), False, False
        # letter buckets 📑 in H5 (CEU/GEN index letters?) — if 📑 X keep as filler-ish
        if old_emoji == "📑":
            return 5, f"#️⃣ {rest}".strip() if rest else "#️⃣", False, False
        if NOTA_RE.search(rest):
            return 5, f"📝 {rest}".strip(), False, True
        # default high-count unit level
        if rest:
            return 5, f"#️⃣ {rest}".strip(), False, False
        return 5, "#️⃣", False, False

    if level == 6:
        # already non-index H6 edge cases → treat as index if 🔖 else keep structure
        if old_emoji == "🔖" or True:
            # force bookmark for H6
            body = rest
            if old_emoji and old_emoji != "🔖" and not rest:
                body = ""
            # strip erroneous 🔢 from H6
            body = re.sub(r"^🔢\s*", "", body).strip()
            return 6, f"🔖 {body}".strip(), True, False

    # fallback
    return level, f"{old_emoji} {rest}".strip() if old_emoji else rest, False, False


def parse_headings(lines: list[str], yaml_end: int, letter: str) -> list[Heading]:
    heads: list[Heading] = []
    for i in range(yaml_end, len(lines)):
        line = lines[i]
        # Never treat YAML-style decorator-only lines as headings
        stripped = line.strip()
        m = HEAD_RE.match(line.rstrip("\n"))
        if not m:
            continue
        level = len(m.group(1))
        core, old_ids = strip_ids(m.group(2))
        if re.fullmatch(r"[=*\-\s]+", core) or core.startswith("===="):
            continue
        # Skip metadata section labels that are H1 inside YAML only — yaml_end handles that
        new_level, new_title, is_index, is_nota = classify_and_build(letter, level, core)
        h = Heading(
            line_index=i,
            raw_line=line,
            level=level,
            old_ids=old_ids,
            title_core=core,
            new_level=new_level,
            new_title=new_title,
            is_index_term=is_index,
            is_nota=is_nota,
        )
        heads.append(h)
    return heads


def assign_serials(letter: str, heads: list[Heading]) -> dict[str, str]:
    """Assign new_id and return map old_id -> new_id (and aliases)."""
    id_map: dict[str, str] = {}
    for n, h in enumerate(heads, start=1):
        new_id = f"{letter}{n:04d}"
        h.new_id = new_id
        for oid in h.old_ids:
            id_map[oid] = new_id
            # alias without book prefix quirks
            if oid.startswith("lde-q"):
                id_map[oid.replace("lde-q", "q")] = new_id
                id_map["lde-q-" + oid[5:]] = new_id
            if oid.startswith("lde-"):
                id_map[oid] = new_id
            # q790 style
            mq = re.match(r"lde-q(\d+)([a-z]?)$", oid)
            if mq:
                id_map[f"q-{mq.group(1)}{mq.group(2)}"] = new_id
                id_map[f"q{mq.group(1)}{mq.group(2)}"] = new_id
                id_map[f"lde-q-{mq.group(1)}{mq.group(2)}"] = new_id
        # also map bare previous patterns from title? skip
    return id_map


def format_heading(h: Heading) -> str:
    hashes = "#" * h.new_level
    return f"{hashes} {h.new_title} {{#{h.new_id}}}\n"


def rewrite_links(text: str, id_map: dict[str, str], all_maps: dict[str, dict[str, str]]) -> str:
    """Rewrite markdown links and bare {#old} leftovers."""

    def repl_md_link(m: re.Match[str]) -> str:
        label, target = m.group(1), m.group(2)
        new_t = rewrite_target(target, id_map, all_maps)
        return f"[{label}]({new_t})"

    text = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", repl_md_link, text)

    # cross-book bare forms in prose rarely; handle lde:q-400 in links only above
    return text


def rewrite_target(target: str, id_map: dict[str, str], all_maps: dict[str, dict[str, str]]) -> str:
    t = target.strip()
    # #anchor
    if t.startswith("#"):
        aid = t[1:]
        if aid in id_map:
            return f"#{id_map[aid]}"
        # try all books
        for mp in all_maps.values():
            if aid in mp:
                return f"#{mp[aid]}"
        return t
    # book:ref  e.g. lde:q-400, ldm:m-142
    m = re.match(r"^(lde|ldm|ese|ceu|gen):(.+)$", t, re.I)
    if m:
        book, ref = m.group(1).lower(), m.group(2)
        letter = {"lde": "s", "ldm": "m", "ese": "e", "ceu": "c", "gen": "g"}[book]
        mp = all_maps.get(letter, {})
        # normalize ref to possible old ids
        candidates = [
            ref,
            f"{book}-{ref}",
            f"{book}-{ref.replace('q-', 'q')}",
            ref.replace("q-", "lde-q") if book == "lde" else ref,
            f"lde-q{ref[2:]}" if ref.startswith("q-") else None,
            f"lde-q{ref[1:]}" if ref.startswith("q") and ref[1:].isdigit() else None,
        ]
        if ref.startswith("q-"):
            candidates.append(f"lde-q{ref[2:]}")
            candidates.append(f"q-{ref[2:]}")
        if ref.startswith("m-"):
            candidates.append(f"ldm-{ref[2:]}")
        for c in candidates:
            if c and c in mp:
                return f"#{mp[c]}"
        # letter-prefix serial already?
        if re.match(r"^[smecg]\d{4}$", ref):
            return f"#{ref}"
        return t
    return t


def build_toc(heads: list[Heading], book_title_id: str) -> str:
    """Nested markdown list H2–H4 only."""
    lines_out = [
        "Clique nos itens para navegar ou use `Ctrl + F` (ou ⌘ + F) para busca rápida.",
        "",
    ]
    # Find H1 for root
    h1 = next((h for h in heads if h.new_level == 1), None)
    if h1:
        # title without emoji for cleanliness? keep full new_title
        label = h1.new_title
        lines_out.append(f"- [{label}](#{h1.new_id})")

    # stack of levels currently open in list nesting: only 2,3,4
    for h in heads:
        if h.new_level not in (2, 3, 4):
            continue
        # indent: H2 → 2 spaces under H1 (1 level), H3 → 2, H4 → 3
        # structure:
        # - H1
        #   - H2
        #     - H3
        #       - H4
        depth = h.new_level  # 2,3,4 → indent (depth)*2 spaces from root item
        indent = "  " * depth
        label = h.new_title.replace("]", "\\]")
        lines_out.append(f"{indent}- [{label}](#{h.new_id})")

    return "\n".join(lines_out) + "\n"


def replace_toc_block(text: str, heads: list[Heading]) -> str:
    """
    Replace only the Sumário expand block (or inject one). Never touch other expands.
    """
    toc_body = build_toc(heads, heads[0].new_id if heads else "")

    # ### …Sumário… followed by ::: expand … :::
    pat = re.compile(
        r"(###[^\n]*Sum[aá]rio[^\n]*\n)"
        r"(\s*)"
        r"(::: expand[^\n]*\n)"
        r"(.*?)"
        r"(\n:::)",
        re.S | re.I,
    )

    def repl(m: re.Match[str]) -> str:
        # keep expand title line but ensure name mentions Sumário
        return f"{m.group(1)}{m.group(2)}::: expand Sumário\n{toc_body}{m.group(5)}"

    new_text, n = pat.subn(repl, text, count=1)
    if n:
        return new_text

    # Inject after first Sumário heading
    pat3 = re.compile(r"(###[^\n]*Sum[aá]rio[^\n]*\n)", re.I)
    m = pat3.search(text)
    if m:
        inject = (
            f"{m.group(1)}\n"
            f"::: expand Sumário\n"
            f"{toc_body}"
            f":::\n"
        )
        return text[: m.start()] + inject + text[m.end() :]

    return text


def migrate_book(
    letter: str, path: Path, all_maps: dict[str, dict[str, str]]
) -> tuple[dict[str, str], str, list[Heading]]:
    raw = path.read_text(encoding="utf-8")
    plain = [ln.rstrip("\n\r") for ln in raw.splitlines()]
    had_final_nl = raw.endswith("\n")

    _y0, y1 = split_yaml_region(plain)
    heads = parse_headings(plain, y1, letter)
    id_map = assign_serials(letter, heads)
    all_maps[letter] = id_map

    for h in heads:
        plain[h.line_index] = format_heading(h).rstrip("\n")

    text = "\n".join(plain) + ("\n" if had_final_nl else "")
    return id_map, text, heads


def _ldm_postpass(id_map: dict[str, str]) -> None:
    """Fix LDM index links that used wrong old ids (ldm-ldm-*, phantom 2-33/2-34)."""
    path = REPO / "books/md/2-ldm/full/2-ldm-full.md"
    if not path.is_file():
        return
    # Rebuild old→new from git if available
    import subprocess

    try:
        old = subprocess.check_output(
            ["git", "show", "HEAD:books/md/2-ldm/full/2-ldm-full.md"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        old = ""
    new = path.read_text(encoding="utf-8")
    if not old:
        return

    def body_ids(text: str) -> list[str | None]:
        lines = text.splitlines()
        y1 = 0
        if lines and lines[0].strip() == "---":
            for i in range(1, min(120, len(lines))):
                if lines[i].strip() == "---":
                    y1 = i + 1
                    break
        out: list[str | None] = []
        for line in lines[y1:]:
            m = HEAD_RE.match(line)
            if not m:
                continue
            body = m.group(2)
            core = ID_RE.sub("", body).strip()
            if re.fullmatch(r"[=*\-\s]+", core) or core.startswith("===="):
                continue
            ids = ID_RE.findall(body)
            out.append(ids[0] if ids else None)
        return out

    omap: dict[str, str] = {}
    for a, b in zip(body_ids(old), body_ids(new)):
        if a and b:
            omap[a] = b
            if a.startswith("ldm-"):
                omap["ldm-ldm-" + a[4:]] = b
    # phantom print chapters → Dissertações if present
    diss = omap.get("ldm-2-31")
    if diss:
        omap["ldm-2-33"] = diss
        omap["ldm-2-34"] = diss

    def fix(m: re.Match[str]) -> str:
        tgt = m.group(1)
        if re.match(r"^m\d{4}$", tgt):
            return m.group(0)
        if tgt in omap:
            return f"](#{omap[tgt]})"
        return m.group(0)

    new2 = re.sub(r"\]\(#([^)]+)\)", fix, new)
    new2 = re.sub(
        r"\[(\d+(?:\.\d+)*\.?\s+)([^\]]+)\]\(#(m\d{4})\)",
        r"[\2](#\3)",
        new2,
    )
    path.write_text(new2, encoding="utf-8")
    print("  LDM post-pass link fix done")


def main() -> int:
    # Pass 1: migrate headings, collect maps + new texts
    all_maps: dict[str, dict[str, str]] = {}
    results: dict[str, tuple[Path, str, list[Heading]]] = {}

    for letter, path in BOOKS:
        if not path.is_file():
            print(f"MISSING {path}", file=sys.stderr)
            return 1
        print(f"Migrating {path.relative_to(REPO)} …")
        id_map, text, heads = migrate_book(letter, path, all_maps)
        results[letter] = (path, text, heads)
        print(f"  headings={len(heads)}  last={letter}{len(heads):04d}  old_ids_mapped={len(id_map)}")

    # Pass 2: link rewrite + TOC with full maps
    for letter, (path, text, heads) in results.items():
        id_map = all_maps[letter]
        text = rewrite_links(text, id_map, all_maps)
        text = replace_toc_block(text, heads)
        # Pre-existing LDE missing-paren back-link
        if letter == "s":
            text = text.replace(
                "↩️ Voltar para [2.10. 🗂️ Ocupações e missões](#lde-2-10\n",
                "↩️ Voltar para [🗂️ Ocupações e missões](#s0800)\n",
            )
            m540 = re.search(r"##### #️⃣ 540 \{#(s\d{4})\}", text)
            if m540:
                text = text.replace(
                    "[Q.540](#lde-q540)", f"[#️⃣ 540](#{m540.group(1)})"
                )
            text = re.sub(
                r"\[(\d+(?:\.\d+)*\.?\s+)([^\]]+)\]\(#(s\d{4})\)",
                r"[\2](#\3)",
                text,
            )
            text = re.sub(
                r"\[Q\.(\d+)([a-z])?\]\(#(s\d{4})\)",
                lambda m: (
                    f"[#️⃣ {int(m.group(1))}"
                    + (f".{m.group(2)}" if m.group(2) else "")
                    + f"](#{m.group(3)})"
                ),
                text,
            )
        if letter == "m":
            # broken double-prefix index links + phantom caps 33/34
            # rebuilt after write via post-pass below
            pass
        path.write_text(text, encoding="utf-8")
        print(f"  wrote {path.relative_to(REPO)}")

    # LDM post-pass: old id → new by heading order (handles ldm-ldm-* typos)
    _ldm_postpass(all_maps.get("m", {}))

    # summary dump
    print("\nDone.")
    for letter, (path, _, heads) in results.items():
        by = {}
        for h in heads:
            by[h.new_level] = by.get(h.new_level, 0) + 1
        print(f"  {letter}: {len(heads)}  levels={dict(sorted(by.items()))}  sample H5={[h.new_title for h in heads if h.new_level==5][:3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
