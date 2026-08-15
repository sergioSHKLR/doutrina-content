/* Multi-book mark tool: PDF | MD | HTML — layout presets + page sync */

(() => {
  "use strict";

  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

  const $ = (id) => document.getElementById(id);
  const editor = $("editor");
  const htmlFrame = $("htmlFrame");
  const pdfCanvas = $("pdfCanvas");
  const pdfTextLayer = $("pdfTextLayer");
  const pdfPageEl = $("pdfPage");
  const pdfScroll = $("pdfScroll");
  const statusEl = $("status");
  const mdPathEl = $("mdPath");
  const bookSelect = $("bookSelect");
  const pdfSelect = $("pdfSelect");
  const pageJump = $("pageJump");
  const pdfPageLabel = $("pdfPageLabel");
  const pdfZoomLabel = $("pdfZoomLabel");
  const mdZoomLabel = $("mdZoomLabel");
  const htmlZoomLabel = $("htmlZoomLabel");
  const searchBox = $("searchBox");
  const findMeta = $("findMeta");
  const layoutSelect = $("layoutSelect");
  const syncToggle = $("syncToggle");
  const syncMeta = $("syncMeta");
  const brandTitle = $("brandTitle");
  const paneMd = $("paneMd");
  const paneHtml = $("paneHtml");

  const LS_LAYOUT = "book-preview-layout";
  const LS_SYNC = "book-preview-sync";
  const LS_MD_ZOOM = "book-preview-md-zoom";
  const LS_HTML_ZOOM = "book-preview-html-zoom";
  const LS_BOOK = "book-preview-book";
  // Migrate prefs from the old LDE-only tool once
  const LS_LEGACY = {
    layout: "lde-preview-layout",
    sync: "lde-preview-sync",
    mdZoom: "lde-preview-md-zoom",
    htmlZoom: "lde-preview-html-zoom",
  };
  const LAYOUTS = new Set(["mark", "verify-l", "verify-r"]);

  let bookId = "lde";
  let bookShort = "LDE";
  let pdfDoc = null;
  let pdfPage = 1; // PDF.js file page (1-based)
  let pdfZoom = 1; // user zoom multiplier on top of fit-width base
  let mdZoom = 1;
  let htmlZoom = 1;
  const ZOOM_MIN = 0.5;
  const ZOOM_MAX = 3;
  const ZOOM_STEP = 0.15;
  // Book / MD page number = file page − offset (cover/front-matter skip); from /api/defaults
  let pageNumOffset = 1;
  let rendering = false;
  let pendingPage = null;
  let renderTimer = null;

  /** Page-level PDF ↔ HTML (and MD jump) sync */
  let syncByPage = false;
  let syncLock = false; // prevent feedback loops
  let htmlScrollHandler = null;
  let htmlScrollTimer = null;
  let htmlWheelHandler = null;
  let layoutMode = "mark";

  /** Logical page used in []{#page-N} and the Page box */
  function logicalPage(filePage = pdfPage) {
    return filePage - pageNumOffset;
  }

  /** PDF.js file page for a logical book page */
  function filePageFromLogical(logical) {
    return logical + pageNumOffset;
  }

  function syncPageJumpUi(filePage = pdfPage) {
    const logical = logicalPage(filePage);
    if (pageJump) {
      pageJump.value = logical;
      if (pdfDoc) {
        pageJump.min = 1 - pageNumOffset; // 0 when offset=1
        pageJump.max = pdfDoc.numPages - pageNumOffset;
      }
    }
    if (pdfPageLabel) {
      const maxL = pdfDoc ? pdfDoc.numPages - pageNumOffset : "?";
      pdfPageLabel.textContent = `p. ${logical} / ${maxL} · file ${filePage}`;
    }
  }

  function updateDocumentTitle() {
    document.title = `${bookShort} — PDF · MD · HTML`;
  }

  function fillPdfSelect(pdfOptions, selectedPath) {
    pdfSelect.innerHTML = "";
    for (const opt of pdfOptions) {
      const o = document.createElement("option");
      o.value = opt.path;
      o.textContent = opt.label;
      if (opt.path === selectedPath) o.selected = true;
      pdfSelect.appendChild(o);
    }
  }

  function fillBookSelect(books, selectedId) {
    if (!bookSelect) return;
    bookSelect.innerHTML = "";
    for (const b of books) {
      const o = document.createElement("option");
      o.value = b.id;
      o.textContent = b.label;
      if (b.id === selectedId) o.selected = true;
      bookSelect.appendChild(o);
    }
  }

  // find state
  let findTarget = "md"; // 'md' | 'html'
  let mdFindIndex = -1;
  let htmlFindIndex = -1;
  let htmlMarks = [];

  // Last MD caret (button clicks blur the textarea and wipe selectionStart)
  let mdSelStart = 0;
  let mdSelEnd = 0;
  let mdScrollTop = 0;
  let mdScrollLeft = 0;

  function rememberMdCaret() {
    if (document.activeElement !== editor && mdSelStart === 0 && mdSelEnd === 0) {
      // still update scroll if user scrolled without focus
    }
    mdSelStart = editor.selectionStart;
    mdSelEnd = editor.selectionEnd;
    mdScrollTop = editor.scrollTop;
    mdScrollLeft = editor.scrollLeft;
  }

  editor.addEventListener("select", rememberMdCaret);
  editor.addEventListener("keyup", rememberMdCaret);
  editor.addEventListener("mouseup", rememberMdCaret);
  editor.addEventListener("input", rememberMdCaret);
  editor.addEventListener("scroll", () => {
    mdScrollTop = editor.scrollTop;
    mdScrollLeft = editor.scrollLeft;
  }, { passive: true });
  editor.addEventListener("blur", rememberMdCaret);

  function setStatus(msg, kind) {
    statusEl.textContent = msg;
    statusEl.className = "status" + (kind ? " " + kind : "");
  }

  async function apiGet(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(await r.text());
    const ct = r.headers.get("content-type") || "";
    if (ct.includes("application/json")) return r.json();
    return r;
  }

  async function apiPost(url, body) {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || r.statusText);
    return data;
  }

  // --- PDF render with selectable text layer ---
  async function loadPdf(relPath) {
    setStatus("Loading PDF…");
    const url = `/api/file?path=${encodeURIComponent(relPath)}`;
    pdfDoc = await pdfjsLib.getDocument(url).promise;
    pdfPage = Math.min(pdfPage, pdfDoc.numPages) || 1;
    syncPageJumpUi(pdfPage);
    await renderPdfPage(pdfPage);
    if (syncByPage) propagateFromPdf();
    setStatus(
      `PDF ready · ${bookShort} · file ${pdfDoc.numPages} pp · book page = file−${pageNumOffset} · select text to search`,
      "ok"
    );
  }

  async function renderPdfPage(num) {
    if (!pdfDoc) return;
    if (rendering) {
      pendingPage = num;
      return;
    }
    rendering = true;
    pdfPage = num;
    syncPageJumpUi(num);
    try {
      const page = await pdfDoc.getPage(num);
      const base = page.getViewport({ scale: 1 });
      const maxW = Math.max(280, pdfScroll.clientWidth - 32);
      // Fit-width base, then user zoom (+ / −)
      const fitScale = Math.min(1.35, maxW / base.width);
      const cssScale = fitScale * pdfZoom;
      const dpr = window.devicePixelRatio || 1;
      const viewport = page.getViewport({ scale: cssScale * dpr });
      if (pdfZoomLabel) {
        pdfZoomLabel.textContent = `${Math.round(pdfZoom * 100)}%`;
      }

      const ctx = pdfCanvas.getContext("2d");
      pdfCanvas.width = viewport.width;
      pdfCanvas.height = viewport.height;
      const cssW = viewport.width / dpr;
      const cssH = viewport.height / dpr;
      pdfCanvas.style.width = `${cssW}px`;
      pdfCanvas.style.height = `${cssH}px`;
      pdfPageEl.style.width = `${cssW}px`;
      pdfPageEl.style.height = `${cssH}px`;

      await page.render({ canvasContext: ctx, viewport }).promise;

      // Selectable text layer
      pdfTextLayer.innerHTML = "";
      pdfTextLayer.style.width = `${cssW}px`;
      pdfTextLayer.style.height = `${cssH}px`;

      const textContent = await page.getTextContent();
      const textViewport = page.getViewport({ scale: cssScale });

      // pdf.js 3.x renderTextLayer
      await pdfjsLib.renderTextLayer({
        textContentSource: textContent,
        container: pdfTextLayer,
        viewport: textViewport,
        textDivs: [],
      }).promise;

      // Scale text layer to match canvas CSS size (dpr already in canvas)
      pdfTextLayer.style.setProperty("--scale-factor", String(cssScale));
    } finally {
      rendering = false;
      if (pendingPage !== null && pendingPage !== pdfPage) {
        const p = pendingPage;
        pendingPage = null;
        await renderPdfPage(p);
      } else {
        pendingPage = null;
      }
    }
  }

  /**
   * Go to PDF.js file page (1-based).
   * @param {number} fileNum
   * @param {{ fromSync?: boolean }} [opts] fromSync=true when driven by HTML scroll
   */
  function goPdfFilePage(fileNum, opts = {}) {
    if (!pdfDoc) return;
    const p = Math.max(1, Math.min(pdfDoc.numPages, fileNum));
    const fromSync = !!opts.fromSync;
    renderPdfPage(p)
      .then(() => {
        if (syncByPage && !fromSync && !syncLock) {
          propagateFromPdf();
        }
      })
      .catch((e) => setStatus(e.message, "err"));
  }

  /** Go to logical/book page (Page box / []{#page-N}) */
  function goPdfLogicalPage(logicalNum, opts = {}) {
    goPdfFilePage(filePageFromLogical(logicalNum), opts);
  }

  function updateSyncMeta() {
    if (!syncMeta) return;
    if (!syncByPage) {
      syncMeta.textContent = "sync off";
      return;
    }
    const n = logicalPage();
    syncMeta.textContent = n >= 1 ? `sync · p.${n}` : "sync · cover";
  }

  /** PDF page changed → scroll HTML #page-N and MD []{#page-N} */
  function propagateFromPdf() {
    const n = logicalPage();
    if (n < 1) {
      updateSyncMeta();
      return;
    }
    syncLock = true;
    scrollHtmlToPage(n);
    scrollMdToPage(n);
    updateSyncMeta();
    window.setTimeout(() => {
      syncLock = false;
    }, 180);
  }

  function scrollHtmlToPage(logical) {
    const doc = htmlFrame.contentDocument;
    const win = htmlFrame.contentWindow;
    if (!doc || !win) return false;
    const el =
      doc.getElementById(`page-${logical}`) ||
      doc.querySelector(`.pdf-page-start[data-page="${logical}"]`);
    if (!el) {
      if (syncMeta) syncMeta.textContent = `sync · no #page-${logical}`;
      return false;
    }
    el.scrollIntoView({ block: "start", behavior: "auto" });
    return true;
  }

  function scrollMdToPage(logical) {
    if (!editor) return false;
    const needle = `[]{#page-${logical}}`;
    const idx = editor.value.indexOf(needle);
    if (idx < 0) return false;
    // Don't steal focus while verifying in HTML/PDF
    const hadFocus = document.activeElement === editor;
    mdSelStart = idx;
    mdSelEnd = idx + needle.length;
    editor.setSelectionRange(idx, idx + needle.length);
    scrollTextareaToIndex(editor, idx, "top");
    if (hadFocus) editor.focus();
    return true;
  }

  function detachHtmlScrollSync() {
    const win = htmlFrame.contentWindow;
    if (win && htmlScrollHandler) {
      win.removeEventListener("scroll", htmlScrollHandler);
    }
    if (win && htmlWheelHandler) {
      win.removeEventListener("wheel", htmlWheelHandler);
    }
    htmlScrollHandler = null;
    htmlWheelHandler = null;
    if (htmlScrollTimer) {
      clearTimeout(htmlScrollTimer);
      htmlScrollTimer = null;
    }
  }

  /** Ctrl+wheel inside the iframe (events don't bubble to parent) */
  function attachHtmlWheelZoom() {
    const win = htmlFrame.contentWindow;
    const doc = htmlFrame.contentDocument;
    if (!win || !doc) return;
    if (htmlWheelHandler) {
      win.removeEventListener("wheel", htmlWheelHandler);
    }
    htmlWheelHandler = (ev) => {
      if (!(ev.ctrlKey || ev.metaKey)) return;
      ev.preventDefault();
      if (ev.deltaY < 0) setHtmlZoom(htmlZoom + ZOOM_STEP);
      else setHtmlZoom(htmlZoom - ZOOM_STEP);
    };
    win.addEventListener("wheel", htmlWheelHandler, { passive: false });
  }

  /** HTML scroll → PDF (and MD) when the topmost visible page marker changes */
  function attachHtmlScrollSync() {
    detachHtmlScrollSync();
    const win = htmlFrame.contentWindow;
    const doc = htmlFrame.contentDocument;
    if (!win || !doc || !doc.body) return;

    htmlScrollHandler = () => {
      if (!syncByPage || syncLock || !pdfDoc) return;
      if (htmlScrollTimer) clearTimeout(htmlScrollTimer);
      htmlScrollTimer = setTimeout(() => {
        if (!syncByPage || syncLock) return;
        const markers = doc.querySelectorAll(".pdf-page-start[data-page]");
        if (!markers.length) return;
        // Marker whose top is at or above ~12% of the iframe viewport
        const threshold = win.innerHeight * 0.12;
        let current = null;
        for (const el of markers) {
          const top = el.getBoundingClientRect().top;
          if (top <= threshold) current = el;
          else break;
        }
        if (!current) current = markers[0];
        const n = parseInt(current.getAttribute("data-page"), 10);
        if (!n || Number.isNaN(n)) return;
        if (n === logicalPage()) {
          updateSyncMeta();
          return;
        }
        syncLock = true;
        goPdfFilePage(filePageFromLogical(n), { fromSync: true });
        scrollMdToPage(n);
        updateSyncMeta();
        window.setTimeout(() => {
          syncLock = false;
        }, 200);
      }, 90);
    };

    win.addEventListener("scroll", htmlScrollHandler, { passive: true });
  }

  function applyLayout(mode, { persist = true, userAction = false } = {}) {
    const next = LAYOUTS.has(mode) ? mode : "mark";
    layoutMode = next;
    document.body.dataset.layout = next;
    if (layoutSelect && layoutSelect.value !== next) layoutSelect.value = next;

    if (brandTitle) {
      brandTitle.textContent =
        next === "mark" ? `${bookShort} mark` : `${bookShort} verify`;
    }

    // Verify modes: prefer sync on (first time / when user switches)
    if (userAction && next.startsWith("verify") && syncToggle && !syncToggle.checked) {
      syncToggle.checked = true;
      setSyncByPage(true, { persist: true, quiet: true });
    }

    if (persist) {
      try {
        localStorage.setItem(LS_LAYOUT, next);
      } catch {
        /* ignore */
      }
    }

    // Re-fit PDF to new pane width
    if (pdfDoc) {
      renderPdfPage(pdfPage).catch(() => {});
    }
    if (userAction) {
      setStatus(
        next === "mark"
          ? "Layout: Mark (PDF · MD · HTML)"
          : next === "verify-l"
            ? "Layout: Verify L (MD · PDF · HTML)"
            : "Layout: Verify R (PDF · HTML · MD)",
        "ok"
      );
    }
  }

  function setSyncByPage(on, { persist = true, quiet = false } = {}) {
    syncByPage = !!on;
    if (syncToggle) syncToggle.checked = syncByPage;
    updateSyncMeta();
    if (persist) {
      try {
        localStorage.setItem(LS_SYNC, syncByPage ? "1" : "0");
      } catch {
        /* ignore */
      }
    }
    if (syncByPage && pdfDoc) {
      propagateFromPdf();
    }
    if (!quiet) {
      setStatus(syncByPage ? "Sync by page ON (PDF ↔ HTML ↔ MD)" : "Sync by page OFF", "ok");
    }
  }

  function clampZoom(next) {
    return Math.round(Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, next)) * 100) / 100;
  }

  function setPdfZoom(next) {
    const z = clampZoom(next);
    if (z === pdfZoom) return;
    pdfZoom = z;
    if (pdfZoomLabel) pdfZoomLabel.textContent = `${Math.round(pdfZoom * 100)}%`;
    if (pdfDoc) {
      renderPdfPage(pdfPage).catch((e) => setStatus(e.message, "err"));
    }
  }

  function setMdZoom(next, { persist = true } = {}) {
    const z = clampZoom(next);
    mdZoom = z;
    if (mdZoomLabel) mdZoomLabel.textContent = `${Math.round(mdZoom * 100)}%`;
    if (editor) editor.style.setProperty("--md-zoom", String(mdZoom));
    if (persist) {
      try {
        localStorage.setItem(LS_MD_ZOOM, String(mdZoom));
      } catch {
        /* ignore */
      }
    }
  }

  function applyHtmlZoomToFrame() {
    const doc = htmlFrame.contentDocument;
    if (!doc) return;
    const root = doc.documentElement;
    const body = doc.body;
    // `zoom` works in Chromium; also set font-size scale fallback via transform on body
    if (root) root.style.zoom = String(htmlZoom);
    if (body && !("zoom" in root.style)) {
      body.style.transformOrigin = "0 0";
      body.style.transform = htmlZoom === 1 ? "" : `scale(${htmlZoom})`;
      body.style.width = htmlZoom === 1 ? "" : `${100 / htmlZoom}%`;
    }
  }

  function setHtmlZoom(next, { persist = true } = {}) {
    const z = clampZoom(next);
    htmlZoom = z;
    if (htmlZoomLabel) htmlZoomLabel.textContent = `${Math.round(htmlZoom * 100)}%`;
    applyHtmlZoomToFrame();
    if (persist) {
      try {
        localStorage.setItem(LS_HTML_ZOOM, String(htmlZoom));
      } catch {
        /* ignore */
      }
    }
  }

  /** Ctrl/Cmd + wheel over a pane → zoom that pane */
  function bindCtrlWheelZoom(el, getZoom, setZoom) {
    if (!el) return;
    el.addEventListener(
      "wheel",
      (ev) => {
        if (!(ev.ctrlKey || ev.metaKey)) return;
        ev.preventDefault();
        if (ev.deltaY < 0) setZoom(getZoom() + ZOOM_STEP);
        else setZoom(getZoom() - ZOOM_STEP);
      },
      { passive: false }
    );
  }

  // Capture PDF selection → search box
  function grabPdfSelection() {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed) return;
    // Only if selection is inside text layer
    const anchor = sel.anchorNode;
    if (!anchor || !pdfTextLayer.contains(anchor.nodeType === 3 ? anchor.parentNode : anchor)) {
      return;
    }
    const t = sel.toString().replace(/\s+/g, " ").trim();
    if (t) {
      searchBox.value = t;
      setStatus(`Selected: “${t.slice(0, 60)}${t.length > 60 ? "…" : ""}”`, "ok");
    }
  }

  document.addEventListener("mouseup", () => {
    setTimeout(grabPdfSelection, 0);
  });
  document.addEventListener("keyup", (ev) => {
    if (ev.key === "Shift" || ev.shiftKey) grabPdfSelection();
  });

  // --- Find in MD ---
  let mdLastNeedle = "";

  function clearMdFind() {
    mdFindIndex = -1;
    mdLastNeedle = "";
    findMeta.textContent = "";
  }

  /**
   * Scroll textarea so character `index` sits near the top/middle of the viewport
   * (not below the fold). Mirrors soft-wrap layout; reapplies after selection
   * because setSelectionRange often scrolls the caret to the bottom edge.
   */
  function scrollTextareaToIndex(textarea, index, align = "top") {
    const style = window.getComputedStyle(textarea);
    const div = document.createElement("div");
    const props = [
      "boxSizing", "fontSize", "fontFamily", "fontWeight", "fontStyle",
      "lineHeight", "letterSpacing", "textTransform", "wordSpacing",
      "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
      "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth",
      "whiteSpace", "wordBreak", "overflowWrap", "tabSize",
    ];
    for (const p of props) {
      div.style[p] = style[p];
    }
    // Content width must match the textarea's visible text area (minus scrollbar)
    const padX =
      (parseFloat(style.paddingLeft) || 0) + (parseFloat(style.paddingRight) || 0);
    const borderX =
      (parseFloat(style.borderLeftWidth) || 0) +
      (parseFloat(style.borderRightWidth) || 0);
    const contentWidth = Math.max(
      50,
      textarea.clientWidth - padX - borderX
    );
    div.style.boxSizing = "content-box";
    div.style.width = `${contentWidth}px`;
    div.style.position = "absolute";
    div.style.left = "-99999px";
    div.style.top = "0";
    div.style.visibility = "hidden";
    div.style.whiteSpace = "pre-wrap";
    div.style.overflowWrap = "anywhere";
    div.style.wordBreak = "break-word";
    div.style.height = "auto";
    div.style.maxHeight = "none";
    div.style.overflow = "hidden";

    const text = textarea.value;
    // Mirror text up to the hit; use a marker span at the caret
    div.appendChild(document.createTextNode(text.slice(0, index)));
    const marker = document.createElement("span");
    marker.textContent = "\u200b";
    div.appendChild(marker);
    // trailing context helps wrap match the real layout slightly better
    div.appendChild(document.createTextNode(text.slice(index, index + 80)));
    document.body.appendChild(div);

    const padTop = parseFloat(style.paddingTop) || 0;
    const top = marker.offsetTop; // already includes padding in content-box mirror
    document.body.removeChild(div);

    const view = textarea.clientHeight;
    // "top" ≈ 22% from top (was 12%; +10% lower); "middle" ≈ center
    const frac = align === "middle" ? 0.45 : 0.22;
    const target = Math.max(0, top - view * frac - padTop);

    const apply = () => {
      textarea.scrollTop = target;
      mdScrollTop = target;
    };
    apply();
    // Override browser scroll-into-view from setSelectionRange
    requestAnimationFrame(() => {
      apply();
      requestAnimationFrame(apply);
    });
  }

  function countMatches(lower, needle) {
    if (!needle) return 0;
    let count = 0;
    let p = 0;
    while ((p = lower.indexOf(needle, p)) !== -1) {
      count++;
      p += Math.max(1, needle.length);
    }
    return count;
  }

  function matchNumberAt(lower, needle, idx) {
    let c = 0;
    let i = 0;
    while (true) {
      const j = lower.indexOf(needle, i);
      if (j < 0 || j > idx) break;
      c++;
      i = j + Math.max(1, needle.length);
    }
    return c;
  }

  /**
   * Find in MD — each click advances to the *next* match (never sticks on first).
   * Resets when the query string changes. Wraps at end of file.
   */
  function findInMd(_nextOnly) {
    const q = searchBox.value;
    if (!q) {
      setStatus("Enter or select a search phrase", "err");
      return;
    }
    findTarget = "md";
    const text = editor.value;
    const lower = text.toLowerCase();
    const needle = q.toLowerCase();

    if (needle !== mdLastNeedle) {
      mdLastNeedle = needle;
      mdFindIndex = -1;
    }

    // Always search after the previous hit (or from 0 on first search)
    let from = mdFindIndex < 0 ? 0 : mdFindIndex + Math.max(1, needle.length);

    let idx = lower.indexOf(needle, from);
    let wrapped = false;
    if (idx < 0 && from > 0) {
      idx = lower.indexOf(needle, 0);
      wrapped = true;
    }
    if (idx < 0) {
      clearMdFind();
      setStatus(`Not found in MD: “${q.slice(0, 40)}”`, "err");
      findMeta.textContent = "0 in MD";
      return;
    }

    mdFindIndex = idx;
    mdSelStart = idx;
    mdSelEnd = idx + q.length;

    editor.focus();
    editor.setSelectionRange(idx, idx + q.length);
    // Bring hit to top of viewport (browser would leave it on the bottom edge)
    scrollTextareaToIndex(editor, idx, "top");

    const count = countMatches(lower, needle);
    const n = matchNumberAt(lower, needle, idx);
    findMeta.textContent = `${n}/${count} in MD` + (wrapped ? " (wrapped)" : "");
    setStatus(`MD match ${n}/${count}${wrapped ? " · wrapped" : ""}`, "ok");
  }

  // --- Find in HTML ---
  function clearHtmlMarks() {
    const doc = htmlFrame.contentDocument;
    if (!doc) return;
    doc.querySelectorAll("mark.find-hit").forEach((m) => {
      const t = doc.createTextNode(m.textContent);
      m.replaceWith(t);
    });
    // normalize
    doc.body && doc.body.normalize();
    htmlMarks = [];
    htmlFindIndex = -1;
  }

  function findInHtml(nextOnly) {
    const q = searchBox.value;
    if (!q) {
      setStatus("Enter or select a search phrase", "err");
      return;
    }
    findTarget = "html";
    const doc = htmlFrame.contentDocument;
    const win = htmlFrame.contentWindow;
    if (!doc || !doc.body) {
      setStatus("Render HTML first", "err");
      return;
    }

    if (!nextOnly || !htmlMarks.length) {
      clearHtmlMarks();
      const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
      const needle = q.toLowerCase();
      const nodes = [];
      while (walker.nextNode()) {
        const node = walker.currentNode;
        if (!node.nodeValue || !node.nodeValue.trim()) continue;
        // skip script-ish
        const p = node.parentElement;
        if (p && (p.tagName === "SCRIPT" || p.tagName === "STYLE")) continue;
        nodes.push(node);
      }
      for (const node of nodes) {
        const text = node.nodeValue;
        const lower = text.toLowerCase();
        let start = 0;
        const parts = [];
        let idx;
        while ((idx = lower.indexOf(needle, start)) !== -1) {
          parts.push(text.slice(start, idx));
          parts.push(null); // placeholder for mark
          parts.push({ hit: text.slice(idx, idx + q.length) });
          start = idx + q.length;
        }
        if (!parts.length) continue;
        parts.push(text.slice(start));
        const frag = doc.createDocumentFragment();
        for (const part of parts) {
          if (part === null) continue;
          if (typeof part === "string") {
            if (part) frag.appendChild(doc.createTextNode(part));
          } else {
            const mark = doc.createElement("mark");
            mark.className = "find-hit";
            mark.style.background = "rgba(255, 212, 59, 0.85)";
            mark.style.color = "#111";
            mark.textContent = part.hit;
            frag.appendChild(mark);
            htmlMarks.push(mark);
          }
        }
        node.parentNode.replaceChild(frag, node);
      }
    }

    if (!htmlMarks.length) {
      findMeta.textContent = "0 in HTML";
      setStatus(`Not found in HTML: “${q.slice(0, 40)}”`, "err");
      return;
    }

    htmlFindIndex = nextOnly
      ? (htmlFindIndex + 1) % htmlMarks.length
      : 0;
    const el = htmlMarks[htmlFindIndex];
    el.scrollIntoView({ block: "center", behavior: "smooth" });
    // flash
    el.style.outline = "2px solid #e67700";
    setTimeout(() => {
      el.style.outline = "";
    }, 800);
    findMeta.textContent = `${htmlFindIndex + 1}/${htmlMarks.length} in HTML`;
    setStatus(`HTML match ${htmlFindIndex + 1}/${htmlMarks.length}`, "ok");
  }

  function findNext() {
    if (findTarget === "html") findInHtml(true);
    else findInMd(true);
  }

  // --- MD load / save / render ---
  async function loadMd() {
    const path = mdPathEl.value.trim();
    setStatus("Loading MD…");
    const data = await apiGet(`/api/md?path=${encodeURIComponent(path)}`);
    editor.value = data.text;
    clearMdFind();
    setStatus(`Loaded ${data.path}`, "ok");
    await renderHtml();
  }

  async function saveMd() {
    const path = mdPathEl.value.trim();
    setStatus("Saving…");
    const data = await apiPost("/api/save", {
      path,
      markdown: editor.value,
      book: bookId,
    });
    setStatus(`Saved ${data.path} (${data.bytes} bytes)`, "ok");
  }

  async function renderHtml() {
    setStatus("Rendering HTML…");
    const t0 = performance.now();
    try {
      clearHtmlMarks();
      detachHtmlScrollSync();
      const { html } = await apiPost("/api/render", {
        markdown: editor.value,
        book: bookId,
      });
      htmlFrame.srcdoc = html;
      await new Promise((res) => {
        htmlFrame.onload = res;
        setTimeout(res, 400);
      });
      applyHtmlZoomToFrame();
      attachHtmlWheelZoom();
      attachHtmlScrollSync();
      if (syncByPage && pdfDoc) {
        // Align HTML to current PDF page after re-render
        syncLock = true;
        scrollHtmlToPage(logicalPage());
        window.setTimeout(() => {
          syncLock = false;
        }, 180);
      }
      updateSyncMeta();
      setStatus(`HTML rendered in ${Math.round(performance.now() - t0)} ms`, "ok");
    } catch (e) {
      setStatus(`Render error: ${e.message}`, "err");
    }
  }

  function scheduleRender() {
    clearTimeout(renderTimer);
    renderTimer = setTimeout(renderHtml, 1200);
  }

  function readLs(key, legacyKey) {
    try {
      const v = localStorage.getItem(key);
      if (v != null) return v;
      if (legacyKey) {
        const old = localStorage.getItem(legacyKey);
        if (old != null) {
          localStorage.setItem(key, old);
          return old;
        }
      }
    } catch {
      /* ignore */
    }
    return null;
  }

  function resolveInitialBookId(books, defaultBook) {
    const ids = new Set((books || []).map((b) => b.id));
    try {
      const params = new URLSearchParams(window.location.search);
      const fromUrl = params.get("book");
      if (fromUrl && ids.has(fromUrl)) return fromUrl;
    } catch {
      /* ignore */
    }
    const saved = readLs(LS_BOOK);
    if (saved && ids.has(saved)) return saved;
    if (defaultBook && ids.has(defaultBook)) return defaultBook;
    return (books && books[0] && books[0].id) || "lde";
  }

  /** Load MD + PDF defaults for a book (first load or book switch). */
  async function applyBook(book, { persist = true } = {}) {
    bookId = book.book || book.id || bookId;
    bookShort = book.short || bookShort;
    pageNumOffset = Number.isFinite(book.page_offset) ? book.page_offset : 1;
    mdPathEl.value = book.md_path;
    fillPdfSelect(book.pdf_options || [], book.pdf_path);
    updateDocumentTitle();
    // Refresh brand for current layout mode
    applyLayout(layoutMode, { persist: false, userAction: false });
    if (persist) {
      try {
        localStorage.setItem(LS_BOOK, bookId);
      } catch {
        /* ignore */
      }
      try {
        const url = new URL(window.location.href);
        url.searchParams.set("book", bookId);
        window.history.replaceState({}, "", url);
      } catch {
        /* ignore */
      }
    }
    pdfPage = 1;
    pdfDoc = null;
    clearMdFind();
    clearHtmlMarks();
    await loadMd();
    await loadPdf(pdfSelect.value);
  }

  // --- Init ---
  async function init() {
    // Restore layout + sync + zoom prefs (with LDE-tool migration)
    let savedLayout = readLs(LS_LAYOUT, LS_LEGACY.layout) || "mark";
    let savedSync = readLs(LS_SYNC, LS_LEGACY.sync);
    let savedMdZoom = readLs(LS_MD_ZOOM, LS_LEGACY.mdZoom);
    let savedHtmlZoom = readLs(LS_HTML_ZOOM, LS_LEGACY.htmlZoom);

    applyLayout(savedLayout, { persist: false, userAction: false });
    // Default: sync ON for verify presets, OFF for mark (unless user saved a choice)
    if (savedSync === "1") setSyncByPage(true, { persist: false, quiet: true });
    else if (savedSync === "0") setSyncByPage(false, { persist: false, quiet: true });
    else setSyncByPage(layoutMode.startsWith("verify"), { persist: false, quiet: true });

    const mdZ = savedMdZoom != null ? parseFloat(savedMdZoom) : 1;
    const htmlZ = savedHtmlZoom != null ? parseFloat(savedHtmlZoom) : 1;
    setMdZoom(Number.isFinite(mdZ) ? mdZ : 1, { persist: false });
    setHtmlZoom(Number.isFinite(htmlZ) ? htmlZ : 1, { persist: false });

    if (layoutSelect) {
      layoutSelect.addEventListener("change", () => {
        applyLayout(layoutSelect.value, { persist: true, userAction: true });
      });
    }
    if (syncToggle) {
      syncToggle.addEventListener("change", () => {
        setSyncByPage(syncToggle.checked, { persist: true, quiet: false });
      });
    }

    // Probe default book list, then load the chosen book fully
    const probe = await apiGet("/api/defaults");
    const initialBook = resolveInitialBookId(probe.books, probe.default_book || probe.book);
    fillBookSelect(probe.books || [], initialBook);

    const defaults =
      initialBook === probe.book
        ? probe
        : await apiGet(`/api/defaults?book=${encodeURIComponent(initialBook)}`);

    if (bookSelect) {
      bookSelect.addEventListener("change", () => {
        const id = bookSelect.value;
        setStatus(`Switching to ${id}…`);
        apiGet(`/api/defaults?book=${encodeURIComponent(id)}`)
          .then((d) => applyBook(d, { persist: true }))
          .catch((e) => setStatus(e.message, "err"));
      });
    }

    $("btnLoad").onclick = () => loadMd().catch((e) => setStatus(e.message, "err"));
    $("btnSave").onclick = () => saveMd().catch((e) => setStatus(e.message, "err"));
    $("btnRender").onclick = () => renderHtml();
    $("btnJump").onclick = () =>
      goPdfLogicalPage(parseInt(pageJump.value, 10) || logicalPage());
    $("btnPrev").onclick = () => goPdfFilePage(pdfPage - 1);
    $("btnNext").onclick = () => goPdfFilePage(pdfPage + 1);
    $("btnZoomIn").onclick = () => setPdfZoom(pdfZoom + ZOOM_STEP);
    $("btnZoomOut").onclick = () => setPdfZoom(pdfZoom - ZOOM_STEP);
    $("btnZoomReset").onclick = () => setPdfZoom(1);

    $("btnMdZoomIn").onclick = () => setMdZoom(mdZoom + ZOOM_STEP);
    $("btnMdZoomOut").onclick = () => setMdZoom(mdZoom - ZOOM_STEP);
    $("btnMdZoomReset").onclick = () => setMdZoom(1);

    $("btnHtmlZoomIn").onclick = () => setHtmlZoom(htmlZoom + ZOOM_STEP);
    $("btnHtmlZoomOut").onclick = () => setHtmlZoom(htmlZoom - ZOOM_STEP);
    $("btnHtmlZoomReset").onclick = () => setHtmlZoom(1);

    // Ctrl/Cmd + wheel over each pane zooms that pane
    bindCtrlWheelZoom(pdfScroll, () => pdfZoom, setPdfZoom);
    bindCtrlWheelZoom(paneMd || editor, () => mdZoom, setMdZoom);
    bindCtrlWheelZoom(paneHtml || htmlFrame, () => htmlZoom, setHtmlZoom);
    pageJump.addEventListener("change", () =>
      goPdfLogicalPage(parseInt(pageJump.value, 10) || logicalPage())
    );
    pdfSelect.addEventListener("change", () =>
      loadPdf(pdfSelect.value).catch((e) => setStatus(e.message, "err"))
    );

    // Each click steps to next match (same as Next for MD)
    $("btnFindMd").onclick = () => findInMd(true);
    $("btnFindHtml").onclick = () => findInHtml(false);
    $("btnFindNext").onclick = () => findNext();

    // Changing the query resets MD find position
    searchBox.addEventListener("input", () => {
      if (searchBox.value.toLowerCase() !== mdLastNeedle) {
        mdFindIndex = -1;
        mdLastNeedle = "";
      }
    });
    $("btnCopy").onclick = async () => {
      try {
        await navigator.clipboard.writeText(searchBox.value);
        setStatus("Copied to clipboard", "ok");
      } catch {
        searchBox.select();
        setStatus("Select and copy manually (clipboard blocked)", "err");
      }
    };

    function insertPageAnchorAtCursor() {
      // Book page N = PDF file page − pageNumOffset
      const n = logicalPage(pdfPage);
      if (n < 1) {
        setStatus(
          `File page ${pdfPage} → book page ${n}; move past the cover (offset ${pageNumOffset})`,
          "err"
        );
        return;
      }
      // Spaces on both sides (trim doubles later in a cleanup pass)
      const token = ` []{#page-${n}} `;

      // Prefer remembered caret — clicking the toolbar button blurs the textarea
      // and browsers often report selection at 0 or end of the file.
      let start = mdSelStart;
      let end = mdSelEnd;
      const liveStart = editor.selectionStart;
      const liveEnd = editor.selectionEnd;
      if (document.activeElement === editor) {
        start = liveStart;
        end = liveEnd;
      }
      // Clamp
      const len = editor.value.length;
      start = Math.max(0, Math.min(start, len));
      end = Math.max(0, Math.min(end, len));
      if (end < start) end = start;

      const scrollTop = mdScrollTop || editor.scrollTop;
      const scrollLeft = mdScrollLeft || editor.scrollLeft;

      const before = editor.value.slice(0, start);
      const after = editor.value.slice(end);
      editor.value = before + token + after;

      // Caret after the trailing space of the token
      const caret = start + token.length;
      mdSelStart = caret;
      mdSelEnd = caret;

      editor.focus();
      editor.setSelectionRange(caret, caret);
      // Restoring value resets scroll; put it back (rAF for stubborn browsers)
      editor.scrollTop = scrollTop;
      editor.scrollLeft = scrollLeft;
      requestAnimationFrame(() => {
        editor.scrollTop = scrollTop;
        editor.scrollLeft = scrollLeft;
        editor.setSelectionRange(caret, caret);
      });

      syncPageJumpUi(pdfPage);
      setStatus(
        `Inserted ${token} (file p.${pdfPage} → book p.${n})`,
        "ok"
      );
      scheduleRender();
    }

    // preventDefault on mousedown keeps focus in the textarea so the caret is not lost
    $("btnInsertPage").addEventListener("mousedown", (ev) => {
      ev.preventDefault();
      if (document.activeElement === editor) rememberMdCaret();
    });

    $("btnInsertPage").onclick = () => insertPageAnchorAtCursor();

    // Shortcut: Ctrl+Shift+P (or Cmd+Shift+P) inserts page anchor
    document.addEventListener("keydown", (ev) => {
      if ((ev.ctrlKey || ev.metaKey) && ev.shiftKey && (ev.key === "P" || ev.key === "p")) {
        ev.preventDefault();
        insertPageAnchorAtCursor();
      }
    });

    searchBox.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        if (ev.shiftKey) findInHtml(false);
        else findInMd(false);
      }
    });

    editor.addEventListener("input", scheduleRender);

    /**
     * PDF page navigation shortcuts.
     * - Alt+← / Alt+→ (or Alt+PageUp/PageDown): always, even while typing in MD
     * - ← / → / PageUp / PageDown / [ / ]: when focus is not in an input/textarea
     * (HTML iframe steals keys when focused — click the PDF pane or use Alt+arrows.)
     */
    function isTypingTarget(el) {
      if (!el || el === document.body) return false;
      const tag = (el.tagName || "").toUpperCase();
      if (tag === "TEXTAREA" || tag === "INPUT" || tag === "SELECT") return true;
      if (el.isContentEditable) return true;
      return false;
    }

    function pdfPageKeyHandler(ev) {
      if (!pdfDoc) return;
      if (ev.altKey && !ev.ctrlKey && !ev.metaKey) {
        if (ev.key === "ArrowRight" || ev.key === "PageDown") {
          ev.preventDefault();
          goPdfFilePage(pdfPage + 1);
          return;
        }
        if (ev.key === "ArrowLeft" || ev.key === "PageUp") {
          ev.preventDefault();
          goPdfFilePage(pdfPage - 1);
          return;
        }
      }
      if (isTypingTarget(ev.target)) return;
      if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
      if (ev.key === "ArrowRight" || ev.key === "PageDown" || ev.key === "]") {
        ev.preventDefault();
        goPdfFilePage(pdfPage + 1);
      } else if (ev.key === "ArrowLeft" || ev.key === "PageUp" || ev.key === "[") {
        ev.preventDefault();
        goPdfFilePage(pdfPage - 1);
      }
    }

    // Capture phase: Alt+arrows still fire when focus is in MD or other panes
    document.addEventListener("keydown", pdfPageKeyHandler, true);

    await applyBook(defaults, { persist: true });
  }

  init().catch((e) => setStatus(e.message, "err"));
})();
