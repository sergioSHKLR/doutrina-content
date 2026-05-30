#!/usr/bin/env python3
"""
health-fidelity-check.py
ULTIMATE Health + Fidelity + Integrity Checker for doutrina.org
"""

import re
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import fitz
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# ========================= DISCOVERY =========================
def discover_books(md_root: Path = Path("books/md")):
    books = {}
    for book_dir in sorted(md_root.iterdir()):
        if not book_dir.is_dir(): continue
        full_md = book_dir / "full" / f"{book_dir.name}-full.md"
        if full_md.exists():
            code = book_dir.name
            name = code.upper().replace("-", " ")
            books[code] = {"name": name, "code": code, "md_full": str(full_md)}
    return books


# ========================= HELPERS =========================
def load_md(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'^[🔖📑🗃️🗂️#️⃣\s]+', '', text)
    replacements = {'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','õ':'o','ô':'o','ú':'u','ç':'c'}
    for acc, plain in replacements.items():
        text = text.replace(acc, plain)
    text = re.sub(r'\(s\)|\(es\)|\(e\)|/s\b|/es\b', '', text)
    text = re.sub(r'[^a-z0-9-]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def extract_index_terms_from_md(md_text: str):
    index_match = re.search(r"(?i)índice geral", md_text)
    if not index_match: return []
    start = max(0, index_match.start() - 300)
    end = min(len(md_text), index_match.end() + 20000)
    index_text = md_text[start:end]

    patterns = [
        r"^\s*-\s+(.+?)(?:\s*\{#.*?\})?\s*$",
        r"^######\s+🔖\s+(.+?)(?:\s*\{#.*?\})?$",
        r"^######\s+(.+?)(?:\s*\{#.*?\})?$",
    ]
    terms = []
    for pat in patterns:
        terms.extend(re.findall(pat, index_text, re.MULTILINE))
    return [t.strip() for t in terms if t.strip() and len(t.strip()) > 2]


def extract_index_terms_from_pdf(pdf_path: Path) -> list[str]:
    if not pdf_path or not pdf_path.exists():
        return []
    terms = []
    try:
        doc = fitz.open(str(pdf_path))
        index_pages = [i for i, page in enumerate(doc) if re.search(r"índice geral", page.get_text(), re.I)]
        if index_pages:
            for page_num in range(max(index_pages), min(max(index_pages)+45, len(doc))):
                page = doc[page_num]
                for b in page.get_text("blocks"):
                    text = b[4].strip()
                    if 5 < len(text) < 90 and text and text[0].isupper() and not text[0].isdigit():
                        cleaned = re.sub(r"\s+\d+[a-z]?\s*$", "", text)
                        cleaned = re.sub(r"\s+[–—-].*$", "", cleaned).strip(".,;:")
                        if cleaned and len(cleaned) > 3:
                            terms.append(cleaned)
    except:
        pass
    seen = set()
    return [t for t in terms if not (t in seen or seen.add(t))]


# ========================= ANALYSIS =========================
def full_analysis(md_path: Path, book_code: str):
    content = load_md(md_path)
    lines = content.splitlines()

    issues = defaultdict(list)
    passed = []
    stats = {
        "total_headings": 0, "h5_count": 0, "h6_count": 0,
        "h5_with_anchor": 0, "h6_with_anchor": 0,
        "anchors": set(), "anchor_to_line": defaultdict(list),
        "duplicate_anchors": defaultdict(list),
        "internal_links": set(), "broken_links": set(),
        "long_lines": 0, "images": 0, "external_links": 0,
    }

    current_level = 0
    in_index_section = False

    for i, line in enumerate(lines, 1):
        if re.search(r"índice geral", line, re.I) and line.startswith("#"):
            in_index_section = True

        for m in re.finditer(r'\{#([^}]+)\}', line):
            anc = m.group(1).strip()
            stats["anchors"].add(anc)
            stats["anchor_to_line"][anc].append(i)
            if len(stats["anchor_to_line"][anc]) > 1:
                stats["duplicate_anchors"][anc] = stats["anchor_to_line"][anc]

        if re.search(r'!\[.*?\]\(', line) or re.search(r'\.(jpg|png|jpeg)', line, re.I):
            stats["images"] += 1
        if re.search(r'\[.*?\]\(https?://', line):
            stats["external_links"] += 1
        if match := re.search(r'\[.*?\]\(#([^)]+)\)', line):
            stats["internal_links"].add(match.group(1))

        if len(line) > 180:
            stats["long_lines"] += 1

        m = re.match(r'^(#{1,6})\s+(.+?)(?:\s*\{.*?\})?$', line.strip())
        if not m: continue

        stats["total_headings"] += 1
        level = len(m.group(1))
        raw = m.group(2).strip()
        clean = re.sub(r'^[🔖📑🗃️🗂️#️⃣\s]+', '', raw).strip()

        if level > current_level + 1:
            issues["ERROR"].append(f"L{i:5d}: Heading jump H{current_level}→H{level}")
        current_level = level

        if level == 5:
            stats["h5_count"] += 1
            if "{" in line: stats["h5_with_anchor"] += 1
            if not in_index_section and book_code == "1-lde" and not re.search(r'^Q\.\s*\d+', clean):
                issues["WARNING"].append(f"L{i:5d}: H5 pattern → {clean[:50]}")

        if level == 6:
            stats["h6_count"] += 1
            if "{" in line:
                stats["h6_with_anchor"] += 1
                if am := re.search(r'\{#([^}]+)\}', line):
                    got = am.group(1)
                    expected = slugify(clean)
                    if got != expected and not any(p in clean for p in ["(s)", "(es)"]):
                        issues["WARNING"].append(f"L{i:5d}: Anchor mismatch '{clean[:60]}'")

    # Final checks
    if not issues.get("ERROR"):
        passed.append("No heading level jumps")
    if stats["h5_count"] == 0 or stats["h5_with_anchor"] / stats["h5_count"] >= 0.95:
        passed.append("H5 anchor coverage good")
    if stats["h6_count"] == 0 or stats["h6_with_anchor"] / stats["h6_count"] >= 0.95:
        passed.append("H6 anchor coverage good")
    if not stats["duplicate_anchors"]:
        passed.append("No duplicate anchors")
    if not stats["broken_links"]:
        passed.append("No broken internal links")

    stats["broken_links"] = stats["internal_links"] - stats["anchors"]
    if stats["broken_links"]:
        issues["ERROR"].append(f"Broken internal links: {len(stats['broken_links'])}")

    if stats["long_lines"] > 300:
        issues["WARNING"].append(f"High long lines: {stats['long_lines']} (normal)")

    return {
        "stats": stats,
        "issues": dict(issues),
        "passed": passed
    }


def run_full_check(book_code: str, books: dict, skip_pdf: bool = False):
    book = books[book_code]
    md_path = Path(book["md_full"])
    pdf_path = next((p for p in Path("books/pdf").glob("*.pdf") if book_code.split("-")[0] in str(p)), None)

    print(f"🌌 Running FULL INTEGRITY SCAN on: {book['name']}\n")

    result = full_analysis(md_path, book_code)
    
    if skip_pdf:
        pdf_terms = []
        print("   ⏭️  PDF index check skipped")
    else:
        pdf_terms = extract_index_terms_from_pdf(pdf_path)
    
    md_terms = extract_index_terms_from_md(load_md(md_path))
    match_ratio = len(set(pdf_terms) & set(md_terms)) / len(pdf_terms) if pdf_terms else 0.0

    # === REPORT ===
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"full-integrity_{book_code}_{timestamp}.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# FULL INTEGRITY REPORT — {book['name']}\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"**Markdown:** {md_path.name}\n")
        f.write(f"**PDF:** {pdf_path.name if pdf_path else 'Not found'}\n\n")

        f.write("## 📊 STATISTICS\n")
        s = result["stats"]
        f.write(f"- Total Headings: {s['total_headings']}\n")
        f.write(f"- H5: {s['h5_count']} (anchored: {s['h5_with_anchor']})\n")
        f.write(f"- H6: {s['h6_count']} (anchored: {s['h6_with_anchor']})\n")
        f.write(f"- Unique Anchors: {len(s['anchors'])}\n")
        f.write(f"- Index Fidelity: {match_ratio:.1%} (PDF: {len(pdf_terms)} | MD: {len(md_terms)})\n")
        f.write(f"- Long Lines (>180): {s['long_lines']}\n\n")

        f.write("## ✅ PASSED CHECKS\n")
        for check in result["passed"]:
            f.write(f"- {check}\n")
        f.write("\n")

        f.write("## ⚠️ ISSUES FOUND\n")
        has_issues = False
        for sev in ["ERROR", "WARNING"]:
            if sev in result["issues"] and result["issues"][sev]:
                has_issues = True
                f.write(f"### {sev}\n")
                for msg in result["issues"][sev]:
                    f.write(f"- {msg}\n")
                f.write("\n")
        if not has_issues:
            f.write("✅ No issues detected.\n")

    print(f"✅ Report written to: {report_path}")
    return report_path


# ========================= MAIN =========================
def main():
    parser = argparse.ArgumentParser(description="Health & Fidelity Checker")
    parser.add_argument("--book", help="Specific book code (e.g. 1-lde)")
    parser.add_argument("--skip-pdf", action="store_true", help="Skip PDF index extraction")
    args = parser.parse_args()

    books = discover_books()

    if args.book:
        if args.book in books:
            run_full_check(args.book, books, args.skip_pdf)
        else:
            print(f"❌ Book {args.book} not found.")
    else:
        print("🌌 Available books:\n")
        for i, (code, info) in enumerate(books.items(), 1):
            print(f"  {i:2d}. {info['name']} ({code})")

        while True:
            try:
                choice = int(input("\nSelect book number: ").strip())
                book_code = list(books.keys())[choice - 1]
                break
            except:
                print("Invalid input.")

        run_full_check(book_code, books, args.skip_pdf)


if __name__ == "__main__":
    main()