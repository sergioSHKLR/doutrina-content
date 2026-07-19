# Scripts

## Layout

```text
scripts/
  # Multi-book pipeline (all 5 obras)
  concat-all.sh
  split-all.sh
  del-full.sh
  del-partials.sh
  end-of-day.sh
  audit_links.py
  check_block_closures.py
  validate_book.py

  lde/                 # LDE-only tools
    render_md_to_html.py
    pandoc-html.sh

  used/                # One-shot / retired (generic)
    lde/               # One-shot / retired (LDE-only)
```

When a book needs its own tooling (render defaults, page campaigns, pandoc metadata), add `scripts/<book>/` using the same ids as under `books/md/` (`lde`, `ldm`, `ese`, `ceu`, `gen`).

## Multi-book (repo root)

```bash
./scripts/concat-all.sh
./scripts/split-all.sh
python3 scripts/audit_links.py books/md/1-lde/full/1-lde-full.md
python3 scripts/check_block_closures.py books/md/1-lde/full/1-lde-full.md
python3 scripts/validate_book.py books/md/1-lde/full/1-lde-full.md 1019
```

## LDE-only

```bash
# Manual page-anchor tool (recommended)
./venv/bin/python scripts/lde/preview_tool/server.py   # http://127.0.0.1:8765/

python3 scripts/lde/render_md_to_html.py   # → books/html/1-lde-text-rendered.html
./scripts/lde/pandoc-html.sh               # → books/html/1-lde-toc.html (needs pandoc)

# Optional auto-insert / QA (helper; verify manually)
python3 scripts/lde/insert_page_anchors.py --parts 1,2,3,4,5
python3 scripts/lde/qa_page_anchors.py --parts 1,2,3,4,5
```

Guide: [lde/HOWTO-page-anchors.md](./lde/HOWTO-page-anchors.md).

Book-specific scripts `chdir` to the repo root so paths stay `books/...` regardless of cwd.
