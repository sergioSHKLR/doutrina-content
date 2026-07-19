#!/usr/bin/env python3
"""
LDE — insert []{#page-N} from PDF *first* words (top of page)
============================================================
Extracts the first few content words of each PDF page (default: 3), finds them
in the Markdown (fuzzy), and inserts a zero-length anchor *before* the match.

Semantics: []{#page-N} marks the *start* (top) of PDF page N.

Parts 1–6 usually match well; pré-textual (part 0) is harder (reordered MD,
sparse extract). Always dry-run before --apply.

Usage (repo root):

  ./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 83
  ./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 83 --apply
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Need pypdf: pip install pypdf", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
DEFAULT_PDF = REPO_ROOT / "books/pdf/1-Livro-dos-Espíritos.pdf"
DEFAULT_MD = REPO_ROOT / "books/md/1-lde/full/1-lde-full.md"

from page_anchor_exceptions import (  # noqa: E402
    PART_RANGES,
    expand_allowed_between,
    is_allowed_gap,
)

HEADER_NOISE = re.compile(
    r"^(?:"
    r"parte\s+(?:primeira|segunda|terceira|quarta)\b|"
    r"cap[ií]tulo\s+[ivxlcdm\d]+\b|"
    r"o\s+livro\s+dos\s+esp[ií]ritos\b|"
    r"allan\s+kardec\b|"
    r"do\s+mundo\s+esp[ií]rita\b|"
    r"dos\s+esp[ií]ritos\b|"
    r"da\s+encarna[cç][aã]o\b|"
    r"m\s+do\s+mundo\b|"
    r"leis\s+morais\b"
    r").*",
    re.I,
)

PAGE_ANCHOR_RE = re.compile(r"\[\]\{#page-(\d+)\}")
DEFAULT_FUZZY = 0.50

# Quotes / dashes / punctuation stripped for matching (MD often has none)
_QUOTE_CHARS = (
    "\"'«»„‟‚'′″`´"
    "\u2018\u2019\u201a\u201b\u201c\u201d\u201e\u201f"  # curly quotes
    "\u00ab\u00bb"  # guillemets
)
_HYPHEN_JOIN = re.compile(
    r"(?<=\w)[\-\u2010\u2011\u2012\u2013\u00ad]\s*(?:\n\s*)?(?=\w)",
    re.UNICODE,
)


def normalize_word(w: str) -> str:
    """
    Match key for a token: lowercased, no diacritics, no quotes/punct/hyphens.
    Aligns PDF extract (with «…», commas, hyphenation) to clean MD prose.
    """
    if not w:
        return ""
    w = w.replace("\u00ad", "")  # soft hyphen
    nk = unicodedata.normalize("NFD", w)
    w = "".join(c for c in nk if unicodedata.category(c) != "Mn")
    w = w.lower()
    for q in _QUOTE_CHARS:
        w = w.replace(q, "")
    # Drop every non-letter/digit (punctuation, hyphens, underscores, symbols)
    w = re.sub(r"[^\w]", "", w, flags=re.UNICODE)
    # \w still has underscore in some engines after punct strip — remove residual _
    w = w.replace("_", "")
    return w


def prepare_text_for_tokenize(text: str) -> str:
    """Join hyphenation and flatten whitespace before word split."""
    if not text:
        return ""
    text = text.replace("\u00ad", "")
    # conheci-\nmento / conheci- mento → conhecimento
    text = _HYPHEN_JOIN.sub("", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_words(text: str) -> list[str]:
    """Normalized word list (quotes/punct/hyphens discarded)."""
    text = prepare_text_for_tokenize(text)
    words: list[str] = []
    for w in re.findall(r"\S+", text):
        n = normalize_word(w)
        if not n:
            continue
        if n.isdigit() and len(n) <= 3:
            continue
        if len(n) == 1 and n not in {"a", "o", "e"}:
            continue
        words.append(n)
    return words


def extract_page_start_probe(text: str, n_words: int = 3) -> list[str]:
    """First n content words at top of page after stripping header chrome."""
    if not text or not text.strip():
        return []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    while lines:
        ln = lines[0]
        if (
            HEADER_NOISE.match(ln)
            or (len(ln) < 48 and ln.isupper())
            or re.fullmatch(r"\d{1,3}", ln)
            or (len(ln) < 60 and re.search(r"\b\d{1,3}\s*$", ln))
        ):
            lines.pop(0)
            continue
        break
    return tokenize_words("\n".join(lines))[:n_words]


@dataclass
class PageHit:
    page: int
    probe: list[str]
    status: str  # ok | no_match | empty_pdf | already
    char_pos: int | None = None
    detail: str = ""
    score: float = 0.0


def find_probe_in_md(
    md_words: list[tuple[str, int, int]],
    probe: list[str],
    *,
    prefer_after: int = 0,
    fuzzy: float = DEFAULT_FUZZY,
) -> tuple[str, int | None, str, float]:
    """
    Return (status, start_char_pos, detail, score).

    Important: take the *first* hit in document order after prefer_after that
    clears the fuzzy threshold — NOT the globally best score. Picking the best
    score jumps the cursor into the index / later chapters and poisons the rest
    of a full-book run (false "no_match" flood).
    """
    if not probe:
        return "empty_pdf", None, "no extractable words", 0.0

    L = len(probe)
    probe_string = " ".join(probe)

    # Seed positions in document order (first word, then second if sparse)
    candidates = [i for i, w in enumerate(md_words) if w[0] == probe[0]]
    if len(candidates) < 3 and L >= 2:
        candidates = sorted(
            set(candidates)
            | {i for i, w in enumerate(md_words) if w[0] == probe[1]}
        )

    for i in candidates:
        if i + L > len(md_words):
            continue
        start_pos = md_words[i][1]
        if start_pos < prefer_after:
            continue
        window = " ".join(md_words[i + k][0] for k in range(L))
        score = SequenceMatcher(None, window, probe_string).ratio()
        if score < fuzzy:
            continue
        # First monotonic accept — preserves Gemini-style part 1–6 quality
        return "ok", start_pos, f"probe={probe} score={score:.2f}", score

    return "no_match", None, f"probe={probe}", 0.0


def build_md_word_index(md: str) -> list[tuple[str, int, int]]:
    """
    Index MD as (normalized_word, start, end).
    Skips []{#page-N}. Same normalize_word as PDF (no quotes/punct/hyphens).
    """
    words: list[tuple[str, int, int]] = []
    i = 0
    nlen = len(md)
    while i < nlen:
        if md.startswith("[]{#page-", i):
            j = md.find("}", i)
            i = j + 1 if j >= 0 else i + 1
            continue
        ch = md[i]
        if ch.isalnum() or (ord(ch) > 127 and ch.isalpha()):
            j = i + 1
            while j < nlen and (
                md[j].isalnum()
                or (ord(md[j]) > 127 and md[j].isalpha())
                or md[j] in "-'\u2019\u00ad"
            ):
                j += 1
            n = normalize_word(md[i:j])
            if n and not (n.isdigit() and len(n) <= 3):
                if not (len(n) == 1 and n not in {"a", "o", "e"}):
                    words.append((n, i, j))
            i = j
            continue
        i += 1
    return words


def existing_pages(md: str) -> set[int]:
    return {int(x) for x in PAGE_ANCHOR_RE.findall(md)}


def insert_anchors(md: str, hits: list[PageHit]) -> str:
    """Insert before match start (top of page), reverse order."""
    ordered = sorted(
        [h for h in hits if h.status == "ok" and h.char_pos is not None],
        key=lambda h: h.char_pos or 0,
        reverse=True,
    )
    out = md
    for h in ordered:
        pos = h.char_pos
        assert pos is not None
        # Spaces on both sides (trim doubles / blank lines in a later cleanup)
        anchor = f" []{{#page-{h.page}}} "
        window = out[max(0, pos - 40) : pos + 40]
        if f"#page-{h.page}" in window:
            continue
        out = out[:pos] + anchor + out[pos:]
    return out


def filter_sequential(
    hits: list[PageHit],
    *,
    existing: set[int],
    existing_pos: dict[int, int],
    page_from: int,
    page_to: int,
) -> list[PageHit]:
    """
    Keep only hits that extend a sequential chain in *both* page number and
    file offset (char_pos must increase with page number).

    Sequence starts at page_from-1 so earlier parts (e.g. skipped part 0)
    do not block part 1+. Only anchors inside [page_from, page_to] count
    as "already" for the chain.
    """
    last = page_from - 1
    last_pos = -1
    out: list[PageHit] = []

    for h in sorted(hits, key=lambda x: x.page):
        page = h.page
        if h.status == "already":
            # Only in-range anchors participate in the sequence
            if page_from <= page <= page_to:
                last = page
                if page in existing_pos:
                    last_pos = max(last_pos, existing_pos[page])
            out.append(h)
            continue

        if h.status == "empty_pdf" or (
            h.status == "no_match" and is_allowed_gap(page)
        ):
            if h.status == "empty_pdf" or is_allowed_gap(page):
                out.append(
                    PageHit(
                        page,
                        h.probe,
                        "skipped_gap",
                        None,
                        "allowed blank/TOC/empty gap",
                        h.score,
                    )
                )
                continue

        if h.status != "ok" or h.char_pos is None:
            out.append(h)
            continue

        pos = h.char_pos
        # File-order gate: never insert before the previous accepted marker
        if pos <= last_pos:
            out.append(
                PageHit(
                    page,
                    h.probe,
                    "seq_reject",
                    pos,
                    f"char pos {pos} not after previous marker pos {last_pos}",
                    h.score,
                )
            )
            continue

        # Page-number gate
        if page > last and (page == last + 1 or expand_allowed_between(last, page)):
            out.append(h)
            last = page
            last_pos = pos
        elif page <= last:
            out.append(
                PageHit(
                    page,
                    h.probe,
                    "seq_reject",
                    pos,
                    f"not after last accepted page {last}",
                    h.score,
                )
            )
        else:
            out.append(
                PageHit(
                    page,
                    h.probe,
                    "seq_reject",
                    pos,
                    f"breaks sequence after {last} (gap not allowlisted)",
                    h.score,
                )
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Match PDF page *starts* (first words) → MD page anchors"
    )
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--md", type=Path, default=DEFAULT_MD)
    ap.add_argument("--from", dest="page_from", type=int, default=1)
    ap.add_argument("--to", dest="page_to", type=int, default=None)
    ap.add_argument(
        "--parts",
        type=str,
        default=None,
        help="comma-separated parts, e.g. 2,3,4,5 (sets --from/--to)",
    )
    ap.add_argument(
        "--words",
        type=int,
        default=3,
        help="first-N words at top of page (default 3)",
    )
    ap.add_argument(
        "--fuzzy",
        type=float,
        default=DEFAULT_FUZZY,
        help=f"min SequenceMatcher ratio (default {DEFAULT_FUZZY})",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="write anchors into MD (default dry-run)",
    )
    ap.add_argument(
        "--reinsert",
        action="store_true",
        help="also try pages that already have an anchor",
    )
    ap.add_argument(
        "--no-seq-qa",
        action="store_true",
        help="disable sequential gap QA (not recommended)",
    )
    args = ap.parse_args()

    pdf_path = args.pdf if args.pdf.is_absolute() else REPO_ROOT / args.pdf
    md_path = args.md if args.md.is_absolute() else REPO_ROOT / args.md
    if not pdf_path.is_file():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 1
    if not md_path.is_file():
        print(f"MD not found: {md_path}", file=sys.stderr)
        return 1

    import os

    os.chdir(REPO_ROOT)

    if args.parts:
        parts = [int(x.strip()) for x in args.parts.split(",")]
        for p in parts:
            if p not in PART_RANGES:
                print(f"Unknown part {p}", file=sys.stderr)
                return 2
        page_from = min(PART_RANGES[p][0] for p in parts)
        page_to = max(PART_RANGES[p][1] for p in parts)
    else:
        page_from = max(1, args.page_from)
        page_to = args.page_to

    reader = PdfReader(str(pdf_path))
    n_pages = len(reader.pages)
    page_to = min(page_to or n_pages, n_pages)

    md = md_path.read_text(encoding="utf-8")
    have = existing_pages(md)
    existing_pos = {
        int(m.group(1)): m.start()
        for m in re.finditer(r"\[\]\{#page-(\d+)\}", md)
    }
    word_index = build_md_word_index(md)

    hits: list[PageHit] = []
    # Cursor only follows in-range markers (skipping part 0 must not pin us to front matter)
    cursor = 0
    in_range_pos = [
        pos for p, pos in existing_pos.items() if page_from <= p <= page_to
    ]
    if in_range_pos:
        cursor = min(in_range_pos)  # will advance as we walk pages

    print(f"PDF: {pdf_path.name} ({n_pages} pages)")
    print(f"MD:  {md_path} ({len(md)} chars, {len(have)} existing anchors)")
    print(
        f"Mode: TOP of page (first {args.words} words, fuzzy≥{args.fuzzy})  "
        f"Range: {page_from}–{page_to}  apply={args.apply}  seq_qa={not args.no_seq_qa}"
    )
    print("-" * 72)

    for page in range(page_from, page_to + 1):
        if page in have and not args.reinsert:
            hits.append(PageHit(page, [], "already", detail="anchor exists"))
            if page_from <= page <= page_to and page in existing_pos:
                cursor = max(cursor, existing_pos[page] + 1)
            continue

        raw = reader.pages[page - 1].extract_text() or ""
        probe = extract_page_start_probe(raw, n_words=args.words)
        if len(probe) < min(2, args.words):
            hits.append(
                PageHit(page, probe, "empty_pdf", detail="too few start words")
            )
            continue

        status, pos, detail, score = find_probe_in_md(
            word_index, probe, prefer_after=cursor, fuzzy=args.fuzzy
        )
        if status == "ok" and pos is not None:
            cursor = pos + 1
        hits.append(PageHit(page, probe, status, pos, detail, score))

    if not args.no_seq_qa:
        hits = filter_sequential(
            hits,
            existing=have,
            existing_pos=existing_pos,
            page_from=page_from,
            page_to=page_to,
        )

    counts: dict[str, int] = {}
    for h in hits:
        counts[h.status] = counts.get(h.status, 0) + 1
        flag = {
            "ok": "✓",
            "no_match": "✗",
            "empty_pdf": "∅",
            "already": "·",
            "skipped_gap": "○",
            "seq_reject": "⛔",
        }.get(h.status, "?")
        probe_s = " ".join(h.probe) if h.probe else "—"
        pos_s = str(h.char_pos) if h.char_pos is not None else "—"
        sc = f" {h.score:.2f}" if h.score else ""
        print(f"{flag} p.{h.page:3d}  start={pos_s:>8}{sc}  [{probe_s}]  {h.detail}")

    print("-" * 72)
    print("Summary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to insert ok matches.")
        print("Sequential QA rejects out-of-order / non-allowlisted gaps.")
        return 0

    to_insert = [h for h in hits if h.status == "ok" and h.char_pos is not None]
    if not to_insert:
        print("Nothing to insert.")
        return 0

    new_md = insert_anchors(md, to_insert)
    md_path.write_text(new_md, encoding="utf-8")
    print(f"\nWrote {len(to_insert)} start-of-page anchors → {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
