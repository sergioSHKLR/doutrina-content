# LDE work / snapshots

| File | Role |
|------|------|
| `1-lde-master.md` | Old experiment snapshot (grid-like markers — **not** trusted as PDF-true) |
| `1-lde-full.md` | Publish artifact via `books/md/1-lde/full/1-lde-full.md` (from partials + shared) |

## Page anchors (2026-07-20)

- Book pages **1–482** marked (`[]{#page-N}`; N = PDF file − 1).
- Shared Nota has **no** page anchors; LDE keeps `page-477` / `page-482` outside inject.
- Edit **partials** + `shared/`; rebuild with `./scripts/concat-all.sh`.

Tool: `./venv/bin/python scripts/preview_tool/server.py` → http://127.0.0.1:8765/?book=lde

**Layouts:** Mark · Verify L · Verify R · **Sync by page** · MD/HTML/PDF zoom.
