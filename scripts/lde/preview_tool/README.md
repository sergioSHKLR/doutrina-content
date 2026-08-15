# Moved → multi-book preview tool

The three-pane preview tool now supports **all five books** (LDE, LDM, ESE, CEU, GEN).

```bash
# Preferred
./venv/bin/python scripts/preview_tool/server.py
# open http://127.0.0.1:8765/
# open http://127.0.0.1:8765/?book=ldm

# Still works (same server)
./venv/bin/python scripts/lde/preview_tool/server.py
```

Sources live in [`scripts/preview_tool/`](../../preview_tool/). Static files here (`app.js`, `index.html`, …) are **stale leftovers** and are not served by the shim.
