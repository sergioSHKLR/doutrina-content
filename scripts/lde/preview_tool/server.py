#!/usr/bin/env python3
"""
Backward-compatible entry point for the multi-book preview tool.

Prefer:

    ./venv/bin/python scripts/preview_tool/server.py

This wrapper runs the same server (all five books; default LDE).
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2] / "preview_tool" / "server.py"
if not TARGET.is_file():
    print(f"error: multi-book preview tool not found at {TARGET}", file=sys.stderr)
    raise SystemExit(1)

runpy.run_path(str(TARGET), run_name="__main__")
