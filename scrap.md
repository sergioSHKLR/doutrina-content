@charset "UTF-8";

:root {
  /* Color Palette */
  --accent: #4EC1F5;
  --bg-light: #ffffff;
  --card-bg: #f8f9fa;
  --text: #222;
  --heading: #1e3a8a;
  --bible-red: #9C2A2A;
  --bible-purple: #9c27b0;
  --spirit-blue: #4dacff;
  --kardec-grey: #757575;
  --kardec-brown: #b85c37;

  /* Shared Greys & Borders */
  --border-light: #eee;
  --border-md: #ddd;
  --border-dark: #e5e5e5;
  --text-muted: #666666;
  --bg-hover: #f0f2f5;
  --bg-box: #f9f9f9;

  /* Layout Dimensions */
  --sidebar-width: 340px;
  --content-max-width: 920px;
  --box-max-width: 720px;
}

/* ==================== BASE ==================== */
*,
*::before,
*::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  line-height: 1.5;
  color: var(--text);
  background: var(--bg-light);
  scroll-behavior: smooth;
}

/* ==================== LAYOUT ==================== */
.container {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
}

.sidebar {
  background: var(--card-bg);
  padding: 2rem 1.5rem;
  border-right: 1px solid var(--border-md);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  align-self: start;
}

.book-content {
  padding: 3rem 4rem;
  max-width: var(--content-max-width);
  margin: 0 auto;
}

/* Mobile Responsiveness */
@media (max-width: 1024px) {
  .container {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    height: auto;
    padding: 1.5rem;
  }

  .book-content {
    padding: 2rem 1.5rem;
  }
}

/* ==================== TYPOGRAPHY ==================== */
h1,
h2,
h3,
h4,
h5 {
  color: var(--heading);
  margin-top: 2.4rem;
  margin-bottom: 1rem;
  scroll-margin-top: 80px;
}

h1 {
  font-size: 2.2rem;
}

h2 {
  font-size: 1.75rem;
}

h3 {
  font-size: 1.45rem;
}

h4 {
  font-size: 1.25rem;
  color: darkred
}

h6 {
  font-size: 1rem;
}

/* Force H5 and its following paragraph to render in-line */
h5 {
  display: inline;
  font-size: 1.1rem;
  margin-top: 0;
  margin-bottom: 0;
}

h5+p {
  display: inline;
  font-weight: 700;
  margin-left: 0.4rem;
}

/* Break the line cleanly after the inline block-group concludes */
h5+p::after {
  content: "";
  display: block;
  margin-bottom: 1.2rem;
}

p {
  margin-bottom: 1.4rem;
}

/* ==================== CUSTOM CONTAINERS ==================== */
.kardec,
.spirit,
.bible {
  padding: 4px 0 4px 1.2rem;
  margin-top: 16px;
  margin-bottom: 16px;      
  border-left: 3px solid;
  border-radius: 0;         
  background: transparent !important;
  box-shadow: none !important;
}

/* Clear 10px spacing block rules that guarantee square edges for touching components */
.spirit+.spirit,
.spirit+.kardec,
.spirit+.bible,
.kardec+.spirit,
.kardec+.kardec,
.kardec+.bible,
.bible+.spirit,
.bible+.kardec,
.bible+.bible {
  margin-top: 10px !important;
}

/* Restoring comfortable readability paragraph gaps within the same named div box */
.kardec p+p,
.spirit p+p,
.bible p+p {
  margin-top: 1rem !important;
}

/* First/Last child padding safety resets inside containers */
.kardec>*:first-child,
.spirit>*:first-child,
.bible>*:first-child {
  margin-top: 0 !important;
}

.kardec>*:last-child,
.spirit>*:last-child,
.bible>*:last-child {
  margin-bottom: 0 !important;
}

.kardec p,
.spirit p,
.bible p {
  line-height: 1.4;
}

.kardec {
  border-color: var(--kardec-brown);
}

.spirit {
  border-color: var(--spirit-blue);
}

.bible {
  border-color: var(--bible-purple);
}

/* Red Letter Bible Styling */
.bible em,
.bible i {
  color: var(--bible-red) !important;
  font-style: italic;
  font-weight: 500;
}

/* Isolated Structural Containers */
.box {
  max-width: var(--box-max-width);
  margin: 3rem auto;
  padding: 1rem 2rem;
  background: var(--bg-box);
  border: 1px solid var(--border-dark);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.center {
  text-align: center;
  max-width: var(--box-max-width);
  margin: 3rem auto;
  padding: 1.5rem 2rem;
  background: var(--bg-box);
  border: 1px solid var(--border-dark);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.left {
  text-align: left;
}

/* ==================== TOC & NAV ==================== */
.toc-title {
  font-weight: 700;
  margin: 0 0 1.2rem 0;
  font-size: 1.2rem;
  color: var(--heading);
}

.toc-tree details {
  margin-bottom: 10px;
}

.toc-tree summary {
  font-weight: 600;
  cursor: pointer;
  padding: 6px 0;
}

.toc-tree ul {
  list-style: none;
  padding-left: 1.4rem;
  margin: 6px 0;
}

/* ==================== EXPANDERS & INDEX (RESET AGRESSIVO TOTAL) ==================== */
details,
.index-section {
  margin: 0.6rem 0 !important;
  /*
  border: 1px solid var(--border-md);
  border-radius: 8px; */
  overflow: hidden;
  /*
  background: var(--bg-light); */
}

details[open],
.index-section {
  margin: 1.2rem 0 !important;
}

details summary,
.index-section summary {
  padding: 0.6rem 1.2rem 0.6rem 2.4rem;
  font-weight: 600;
  cursor: pointer;
  /*
  background: var(--card-bg);
  border-bottom: 1px solid var(--border-light); */
  position: relative;
  list-style: none;
  color: var(--text-muted);
  transition: color 0.15s ease;
}

.index-section summary {
  padding: 0.9rem 1.2rem 0.9rem 2.4rem !important;
  font-size: 1.08rem !important;
  min-height: auto !important;
}

details summary::-webkit-details-marker {
  display: none;
}

details[open] summary {
  color: #000000;
}

/* Custom CSS Chevron */
details summary::before {
  content: "";
  position: absolute;
  left: 1.2rem;
  top: 50%;
  width: 6px;
  height: 6px;
  border-right: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: translateY(-50%) rotate(-45deg);
  transition: transform 0.15s ease;
}

details[open] summary::before {
  transform: translateY(-70%) rotate(45deg);
}


details summary:hover {
  color: black;
} 

/* FAZ QUALQUER TEXTO DENTRO DE DETALHES FICAR COMPACTADO À FORÇA */
details>*:not(summary) {
  padding: 0.4rem 1.2rem !important;
}

/* Caça parágrafos puros e limpa margens para colar as definições */
details p,
details div,
details span {
  margin-top: 0 !important;
  margin-bottom: 3px !important;
  /* Espaço mínimo absoluto entre as linhas */
  padding: 0 !important;
}

/* Evita quebras de linha entre as palavras e os links de referência */
details p:not(:has(strong)):not(:has(b)) {
  padding-left: 1.2rem !important;
  margin-bottom: 10px !important;
  /* Espaço controlado ao fim do bloco completo */
}

/* Remove saltos de bloco de tags inline */
details a,
details span {
  display: inline !important;
}

/* Cabeçalhos de termos ganham pequeno respiro superior */
details strong,
details b {
  display: inline-block;
  margin-top: 8px !important;
  margin-bottom: 1px !important;
}

/* Corrige o topo do primeiro item */
details p:first-child strong,
details p:first-child b {
  margin-top: 0 !important;
}

/* Redução secundária para blocos de índice estruturados em listas */
.index-section>*:not(summary) {
  padding: 0.6rem 1.4rem 0.8rem !important;
  margin: 0 !important;
}

.chapter-toc-content {
  padding: 0.75rem 1.2rem !important;
}

/* ==================== IMAGES & MEDIA ==================== */
img[src*="vine"],
img[src*="Cepa"] {
  max-width: 680px;
  width: 100%;
  height: auto;
  display: block;
  margin: 3rem auto;
  border-radius: 8px;
}

/* ==================== ANCHORS ==================== */
.heading-anchor {
  display: none !important;
  color: var(--accent);
  margin-left: 0.5rem;
  text-decoration: none;
}

h1:hover .heading-anchor,
h2:hover .heading-anchor,
h3:hover .heading-anchor,
h4:hover .heading-anchor {
  display: inline !important;
}

/* ==================== UTILITIES ==================== */
.center-text {
  text-align: center;
}

.small {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.kardec blockquote,
.spirit blockquote,
.bible blockquote {
  padding: 0 !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

