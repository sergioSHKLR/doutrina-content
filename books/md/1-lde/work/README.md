# LDE work / snapshots

| File | Role |
|------|------|
| `1-lde-master.md` | Old experiment snapshot (grid-like markers — **not** trusted as PDF-true) |
| `1-lde-full.md` | **Edit via** `books/md/1-lde/full/1-lde-full.md` (canonical working full) |

## Manual page anchors (in progress)

- **Part 0** (pp. 1–55): redo manually (PDF side-by-side / three-pane tool).
- **Parts 1–5**: partial auto + manual polish via preview tool.
- **Part 6**: later.

Tool: `./venv/bin/python scripts/lde/preview_tool/server.py` → http://127.0.0.1:8765/

**Layouts:** Mark (PDF·MD·HTML) · Verify L (MD·PDF·HTML) · Verify R (PDF·HTML·MD).  
**Sync by page** keeps PDF / HTML / MD on the same book page N.

Convention: ` []{#page-N} ` (spaces both sides); book page N = PDF file page − 1 in the tool.
