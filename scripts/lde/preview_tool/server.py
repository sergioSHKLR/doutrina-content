#!/usr/bin/env python3
"""
LDE three-pane preview tool (MD | HTML | PDF)
=============================================
Local HTTP server — do not use file:// (PDF + APIs need http).

    cd ~/doutrina-content
    ./venv/bin/python scripts/lde/preview_tool/server.py
    # open http://127.0.0.1:8765/

On start, frees port 8765 if a previous server left it open (ss/lsof/fuser).
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import signal
import subprocess
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
LDE_DIR = TOOL_DIR.parent
REPO_ROOT = LDE_DIR.parents[1]
sys.path.insert(0, str(LDE_DIR))
os.chdir(REPO_ROOT)

from md_render import render_md_to_document  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765

DEFAULT_MD = REPO_ROOT / "books/md/1-lde/full/1-lde-full.md"
DEFAULT_PDF = REPO_ROOT / "books/pdf/1-Livro-dos-Espíritos.pdf"
LAYOUT_CSS = REPO_ROOT / "books/html/layout.css"
WORK_PDF_DIR = REPO_ROOT / "books/pdf/work/1-lde"


def _pids_on_port(port: int) -> set[int]:
    """Return PIDs listening on TCP `port` (Linux ss/lsof/fuser)."""
    pids: set[int] = set()
    me = os.getpid()

    # ss -lptn 'sport = :PORT'
    try:
        out = subprocess.check_output(
            ["ss", "-lptn", f"sport = :{port}"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        for m in re.finditer(r"pid=(\d+)", out):
            pids.add(int(m.group(1)))
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        pass

    # lsof -tiTCP:PORT -sTCP:LISTEN
    if not pids:
        try:
            out = subprocess.check_output(
                ["lsof", f"-tiTCP:{port}", "-sTCP:LISTEN"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for line in out.split():
                if line.strip().isdigit():
                    pids.add(int(line.strip()))
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            pass

    # fuser PORT/tcp
    if not pids:
        try:
            out = subprocess.check_output(
                ["fuser", f"{port}/tcp"],
                text=True,
                stderr=subprocess.STDOUT,
            )
            for m in re.finditer(r"\b(\d+)\b", out):
                pids.add(int(m.group(1)))
        except (FileNotFoundError, subprocess.CalledProcessError, OSError):
            pass

    pids.discard(me)
    return pids


def free_port(port: int, *, host: str = HOST) -> None:
    """
    Kill leftover processes still bound to `port` so a restart succeeds.
    Safe: never uses pkill -f on our own command line.
    """
    pids = _pids_on_port(port)
    if not pids:
        return

    print(f"Freeing port {port}: stopping PID(s) {', '.join(map(str, sorted(pids)))}")
    for pid in sorted(pids):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except PermissionError as exc:
            print(f"  warn: cannot SIGTERM {pid}: {exc}", file=sys.stderr)

    # brief wait, then SIGKILL stragglers
    deadline = time.time() + 1.5
    while time.time() < deadline:
        left = _pids_on_port(port)
        if not left:
            break
        time.sleep(0.1)
    else:
        left = _pids_on_port(port)
        for pid in sorted(left):
            try:
                os.kill(pid, signal.SIGKILL)
                print(f"  SIGKILL {pid}")
            except ProcessLookupError:
                pass
            except PermissionError as exc:
                print(f"  warn: cannot SIGKILL {pid}: {exc}", file=sys.stderr)
        time.sleep(0.15)

    still = _pids_on_port(port)
    if still:
        print(
            f"  warn: port {port} may still be busy (PIDs {sorted(still)})",
            file=sys.stderr,
        )
    else:
        print(f"  port {port} is free")


def safe_repo_path(rel: str) -> Path | None:
    """Resolve path under REPO_ROOT only."""
    rel = rel.lstrip("/")
    candidate = (REPO_ROOT / rel).resolve()
    try:
        candidate.relative_to(REPO_ROOT.resolve())
    except ValueError:
        return None
    return candidate


class Handler(BaseHTTPRequestHandler):
    server_version = "LdePreview/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, obj: object) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(code, data, "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            html = (TOOL_DIR / "index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return

        if path == "/api/defaults":
            pdfs = []
            if WORK_PDF_DIR.is_dir():
                for p in sorted(WORK_PDF_DIR.glob("*.pdf")):
                    pdfs.append(
                        {
                            "label": p.name,
                            "path": str(p.relative_to(REPO_ROOT)),
                        }
                    )
            canon = str(DEFAULT_PDF.relative_to(REPO_ROOT))
            pdfs.insert(0, {"label": f"canonical ({DEFAULT_PDF.name})", "path": canon})
            self._send_json(
                200,
                {
                    "md_path": str(DEFAULT_MD.relative_to(REPO_ROOT)),
                    "pdf_path": canon,
                    "pdf_options": pdfs,
                },
            )
            return

        if path == "/api/md":
            rel = (qs.get("path") or [str(DEFAULT_MD.relative_to(REPO_ROOT))])[0]
            fp = safe_repo_path(rel)
            if not fp or not fp.is_file():
                self._send_json(404, {"error": f"MD not found: {rel}"})
                return
            text = fp.read_text(encoding="utf-8")
            self._send_json(200, {"path": rel, "text": text, "bytes": len(text.encode())})
            return

        if path == "/api/file":
            rel = (qs.get("path") or [""])[0]
            fp = safe_repo_path(rel)
            if not fp or not fp.is_file():
                self._send(404, b"not found", "text/plain")
                return
            data = fp.read_bytes()
            ctype = mimetypes.guess_type(str(fp))[0] or "application/octet-stream"
            if fp.suffix.lower() == ".pdf":
                ctype = "application/pdf"
            self._send(200, data, ctype)
            return

        if path == "/layout.css":
            if LAYOUT_CSS.is_file():
                self._send(200, LAYOUT_CSS.read_bytes(), "text/css; charset=utf-8")
            else:
                self._send(404, b"missing layout.css", "text/plain")
            return

        # static tool assets
        static = TOOL_DIR / path.lstrip("/")
        if static.is_file() and TOOL_DIR in static.resolve().parents or static.parent == TOOL_DIR:
            if static.resolve().is_relative_to(TOOL_DIR.resolve()):
                ctype = mimetypes.guess_type(str(static))[0] or "application/octet-stream"
                self._send(200, static.read_bytes(), ctype)
                return

        self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/render":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid JSON"})
                return
            md_text = payload.get("markdown") or ""
            # Cap accidental huge pastes in interactive use (full LDE is ~1.2MB OK)
            if len(md_text) > 5_000_000:
                self._send_json(400, {"error": "markdown too large"})
                return
            try:
                doc = render_md_to_document(
                    md_text,
                    title="LDE Preview",
                    css_href="/layout.css",
                )
            except Exception as exc:  # noqa: BLE001 — surface to UI
                self._send_json(500, {"error": str(exc)})
                return
            self._send_json(200, {"html": doc})
            return

        if path == "/api/save":
            try:
                payload = self._read_json()
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid JSON"})
                return
            rel = payload.get("path") or str(DEFAULT_MD.relative_to(REPO_ROOT))
            text = payload.get("markdown")
            if text is None:
                self._send_json(400, {"error": "missing markdown"})
                return
            fp = safe_repo_path(rel)
            if not fp:
                self._send_json(400, {"error": "path outside repo"})
                return
            if fp.suffix.lower() != ".md":
                self._send_json(400, {"error": "only .md saves allowed"})
                return
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(text, encoding="utf-8")
            self._send_json(200, {"ok": True, "path": rel, "bytes": len(text.encode())})
            return

        self._send(404, b"not found", "text/plain")


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> int:
    free_port(PORT, host=HOST)

    try:
        httpd = ReusableThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        print(f"Failed to bind {HOST}:{PORT}: {exc}", file=sys.stderr)
        print("Try: free the port manually, then re-run.", file=sys.stderr)
        return 1

    print(f"LDE preview tool → http://{HOST}:{PORT}/")
    print(f"  MD default:  {DEFAULT_MD.relative_to(REPO_ROOT)}")
    print(f"  PDF default: {DEFAULT_PDF.relative_to(REPO_ROOT)}")
    print("  Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
