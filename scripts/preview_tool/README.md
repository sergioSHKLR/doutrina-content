# Book preview tool (PDF · MD · HTML)

Local three-pane UI for placing and verifying `[]{#page-N}` anchors against the canonical PDF.

Supports all five obras:

| Id | MD | Canonical PDF |
|----|----|---------------|
| `lde` | `books/md/1-lde/full/1-lde-full.md` | `books/pdf/1-Livro-dos-Espíritos.pdf` |
| `ldm` | `books/md/2-ldm/full/2-ldm-full.md` | `books/pdf/2-Livro-dos-Mediuns.pdf` |
| `ese` | `books/md/3-ese/full/3-ese-full.md` | `books/pdf/3-O-Evangelho-segundo-o-Espiritismo.pdf` |
| `ceu` | `books/md/4-ceu/full/4-ceu-full.md` | `books/pdf/4-O-Ceu-e-o-inferno.pdf` |
| `gen` | `books/md/5-gen/full/5-gen-full.md` | `books/pdf/5-A-Genese-Guillon.pdf` |

Work PDFs (if any) are listed from `books/pdf/work/<n>-<id>/`.

## Run

```bash
cd ~/doutrina-content   # repo root
./venv/bin/python scripts/preview_tool/server.py
# open http://127.0.0.1:8765/
# deep-link: http://127.0.0.1:8765/?book=ese
```

Legacy path `scripts/lde/preview_tool/server.py` launches this same server.

## UI

- **Book** selector — switches MD defaults, canonical PDF, work PDFs, and page offset
- **Layout** — Mark / Verify L / Verify R
- **Sync by page** — page-level PDF ↔ HTML ↔ MD (`[]{#page-N}`)
- **Insert page#** — inserts ` []{#page-N} ` at the MD caret (N = file page − offset)

Catalog and offsets are defined in `server.py` (`BOOKS`). Adjust `page_offset` per book if the cover/front-matter skip differs from 1.
