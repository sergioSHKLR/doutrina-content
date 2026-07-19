# How to use — LDE page anchors

Helpers for placing `[]{#page-N}` in the LDE Markdown so the HTML/reader can jump by **canonical PDF page**.

| File | Role |
|------|------|
| `insert_page_anchors.py` | Match PDF text → propose/insert anchors in MD |
| `render_md_to_html.py` | MD → book-like HTML for visual check |
| `pandoc-html.sh` | Optional full TOC HTML (needs `pandoc`) |

**Working MD:** `books/md/1-lde/full/1-lde-full.md`  
**Canonical PDF:** `books/pdf/1-Livro-dos-Espíritos.pdf`  
**Work PDFs (side-by-side):** `books/pdf/work/1-lde/part-*.pdf`

---

## Semantics (current)

```markdown
[]{#page-17}
```

- `N` = page **N** of the **canonical** PDF (1-based file page).
- Marker sits at the **start (top)** of that page’s text in the MD.
- Prefer spaces on both sides: ` []{#page-N} ` (trim doubles later).
- **Primary workflow:** three-pane tool (PDF select → Find in MD → Insert page#). Book page N = PDF **file page − 1**.
- Optional auto-insert: first 3 words, ignore quotes/punct/hyphenation, sequential QA — verify by hand.
- HTML shows the folio at the **bottom** of each simulated page block.

**Part 0** is manual redo priority. Auto-insert alone is not trusted for full-book fidelity.

---

## 1. Insert page anchors

Run from **repo root** (`doutrina-content/`).

### Dry-run (default — no writes)

```bash
cd ~/doutrina-content
./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 83
```

Part ranges (canonical PDF pages → work PDFs):

| Part | Pages | Work PDF |
|------|-------|----------|
| 0 | 1–55 | `part-0.pdf` / `part-0-reord.pdf` |
| 1 | 56–83 | `part-1.pdf` |
| 2 | 84–293 | `part-2.pdf` |
| 3 | 294–411 | `part-3.pdf` |
| 4 | 412–461 | `part-4.pdf` |
| 5 | 462–477 | `part-5.pdf` |
| 6 | 478–527 | `part-6.pdf` |

Example — part 1 only:

```bash
./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 83
```

Whole book (slow):

```bash
./venv/bin/python scripts/lde/insert_page_anchors.py
```

### Report symbols

| Symbol | Status | Meaning |
|--------|--------|---------|
| `✓` | `ok` | Match after cursor — safe for `--apply` |
| `✗` | `no_match` | Probe not found (or below fuzzy threshold) |
| `∅` | `empty_pdf` | Too little extractable text |
| `·` | `already` | That page already has `[]{#page-N}` |

`start=` is the character offset where the anchor would be inserted (before the match).

### Apply matches (parts 2–5 example; skip 0–1)

```bash
# Prefer part ranges (avoids part-0 cursor poison)
./venv/bin/python scripts/lde/insert_page_anchors.py --parts 2,3,4,5 --apply

# Sequential QA after apply
./venv/bin/python scripts/lde/qa_page_anchors.py --parts 2,3,4,5
```

**Sequential QA** (on by default in insert): rejects anchors that skip non-allowlisted pages.  
Allowlisted blank/TOC pages live in `page_anchor_exceptions.py`.

### Options

```bash
# Probe length (default 3 = first three words at top)
./venv/bin/python scripts/lde/insert_page_anchors.py --words 3 --from 84 --to 120

# Stricter / looser fuzzy match (default 0.50)
./venv/bin/python scripts/lde/insert_page_anchors.py --fuzzy 0.65 --from 84 --to 120

# Retry pages that already have anchors
./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 80 --reinsert --apply

# Custom paths
./venv/bin/python scripts/lde/insert_page_anchors.py \
  --pdf books/pdf/1-Livro-dos-Espíritos.pdf \
  --md books/md/1-lde/full/1-lde-full.md \
  --from 56 --to 100
```

| Flag | Default |
|------|---------|
| `--pdf` | `books/pdf/1-Livro-dos-Espíritos.pdf` |
| `--md` | `books/md/1-lde/full/1-lde-full.md` |
| `--words` | `3` (top of page) |
| `--fuzzy` | `0.50` |
| `--from` / `--to` | `1` / last PDF page |

---

## 2. Why part 0 is weak and 1–6 are stronger

| Band | Typical result | Why |
|------|----------------|-----|
| **Part 0** (1–55) | Many misses | Reordered Prefácio/Intro; blank/title pages; sparse extract |
| **Parts 1–6** | Much higher `ok` | Continuous body prose; first words track MD well |

A full-book dry-run with many `no_match` is often **part 0 + hard pages**, not a failure of parts 1–6. Prefer **per-part** `--from` / `--to`.

Low overall `ok` on a full run is normal; slice by part and expect better rates from page 56 upward.

---

## 3. Recommended workflow

```bash
# A) Dry-run one part (e.g. part 1)
./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 83

# B) Apply
./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 83 --apply

# C) Confirm (those pages → already)
./venv/bin/python scripts/lde/insert_page_anchors.py --from 56 --to 83

# D) Manual fix remaining ✗ with part-1.pdf + MD

# E) Visual check
./venv/bin/python scripts/lde/render_md_to_html.py
# → books/html/1-lde-text-rendered.html  (hard-refresh browser)
```

Repeat for parts 2–6 with the page ranges in the table above.

---

## 4. HTML verification

```bash
./venv/bin/python scripts/lde/render_md_to_html.py
```

- Input: `books/md/1-lde/full/1-lde-full.md`
- Output: `books/html/1-lde-text-rendered.html`
- CSS: `books/html/layout.css`

Optional TOC build (requires `pandoc`):

```bash
./scripts/lde/pandoc-html.sh
```

---

## 5. Three-pane preview tool (MD · HTML · PDF)

Local web UI with three columns:

1. **Markdown** editor (load/save working full MD)  
2. **HTML** preview via the same processor as `render_md_to_html.py`  
3. **PDF** viewer (PDF.js) — canonical or `books/pdf/work/1-lde/part-*.pdf`

```bash
cd ~/doutrina-content
./venv/bin/python scripts/lde/preview_tool/server.py
# open http://127.0.0.1:8765/
```

**Scroll sync:** checkbox “Sync by page” aligns all three on **PDF page number** (`[]{#page-N}` / `#page-N` / PDF.js page), not pixel-perfect free scroll. That is the reliable model for this project.

| Sync type | Doable? |
|-----------|---------|
| Pixel scroll MD ↔ HTML ↔ PDF | No (different heights/layouts) |
| **Page-based** (page N everywhere) | **Yes** — implemented |
| Jump box / ← → keys on PDF | Yes |

See `scripts/lde/preview_tool/`.

## 6. Dependencies

```bash
source venv/bin/activate   # or: pip install -r requirements.txt
# needs: pypdf (insert), markdown (render)
```

---

## 6. Related docs

- Repo root [README.md](../../README.md) — tree and pipeline
- [style-guide.md](../../style-guide.md) — page markers + MD vs PDF order
- [cross-reference.md](../../cross-reference.md) — `#page-N` convention
- Work PDF map: [books/pdf/work/1-lde/README.md](../../books/pdf/work/1-lde/README.md)
