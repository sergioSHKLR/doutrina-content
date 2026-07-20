# Project Milestones — Doutrina Digital

**Historical Progression Checklist**  
Reconstructed from local git histories (`doutrina.org`, `doutrina-content`, `doutrina-11ty`, `doutrina-prod`), file timestamps, commit messages, `scrap.md`, `style-guide.md` evolution, validation/fidelity reports, and direct project context (May 2026).

> **Note on accuracy**: Much early detail has been lost to daily syncs, large refactors, and the 2026 content/presentation split. This is a *plausible, evidence-based* chronology that matches all available artifacts. The foundational act — manual paragraph-by-paragraph transcription from PDF — is treated as the true inception moment per explicit project memory.

**Core Intent (unchanged since 2023)**  
1. Painstakingly redo all source Markdown with complete, high-fidelity **Índice Geral** + rich pure-MD interlinking (no unnecessary HTML).  
2. Re-create the beloved **4-column vanilla study interface** (main text + contextual panels + personal notes).  
3. Establish **CSS variables + theming** for customizable, themeable presentations.

The project evolved from a single monolithic Jekyll site (`doutrina.org`) into a deliberate modular architecture: **Content** (`doutrina-content`) → **Style** (CSS vars) → **Interface** (`doutrina-11ty`).

---

## Phase 1: Inception & Pure Manual Transcription (March – June 2023)

- [x] **2023-03-19** — First commits in `doutrina.org` repo ("Add files via upload", "init"). Project born as a personal digital adaptation of the five Obras Básicas.
- [x] **Foundational labor** — Every single paragraph of the five books (starting with *O Livro dos Espíritos*) manually copied and pasted directly from the source PDFs (Guillon Ribeiro / FEB Edição Histórica 2020 reprint and equivalents) into plain text / early Markdown / HTML drafts. No OCR, no automated extraction at this stage.
- [x] Initial Jekyll scaffolding (`_config.yml`, `_layouts`, `_includes`, `assets/`) and basic book page structure.
- [x] First rough organization of the five books into the site navigation.
- [x] Early experiments with reading experience (single long pages, basic internal jumps).

## Phase 2: Structuring, Anchors & Index Experiments (July – October 2023)

- [x] Conversion of the massive flat pasted text into proper hierarchical Markdown (headings for Parts, Chapters, Questions/Paragraphs).
- [x] **2023-07** — "added anchors", "scrap", "scrap.css" commits. First systematic attempts to create stable internal link targets and visual/index experiments.
- [x] **2023-07-20 to 2023-07-24** — Scrap work (early index extraction tooling + CSS). "toc paste" experiments.
- [x] **2023-10-15** — "toc paste" milestone. Table-of-contents / navigation improvements.
- [x] Initial smart linking patterns and side-panel concepts that would later become the signature 4-column experience.
- [x] Hypothesis annotation layer added for personal study notes.

## Phase 3: Maturation of the Vanilla 4-Column Reader (Late 2023 – Early 2026)

- [x] Full Markdown versions of all five books stabilized inside `doutrina.org/books/`.
- [x] The classic **4-column vanilla interface** reaches maturity:
  - Main reading column (pure text with smart links `.w`/`.d`/`.m`)
  - Contextual side panels (definitions, maps, videos, cross-refs)
  - Personal notes / Hypothesis integration
  - librus.app as companion/experimental surface sharing the same DNA
- [x] Daily/periodic sync workflows, PWA support, accessibility improvements, and continuous content polish.
- [x] `combined.js` and class-based linking patterns refined in production.
- [x] Hundreds of commits (repo eventually reaches >2,200 total) reflecting real daily study-driven refinements.
- [x] Public site at doutrina.org serving the five books with the distinctive non-framework, high-signal reading experience.

## Phase 4: The Great Content Fidelity Split & Í ndice Geral Project (May 2026 — Ongoing)

This is the current high-precision era: deliberate separation of concerns and a "painful" top-to-bottom redo of the source Markdown for long-term maintainability and rich linking.

- [x] **2026-05-16** — `doutrina-content` repo created (first commit "iiitial"). Explicit decision to extract pure, reusable Markdown + PDFs from the presentation layer.
- [x] Books become a submodule (later simple copy) in `doutrina.org` and `doutrina-prod`.
- [x] **Full hierarchical standardization** applied to all books:
  - H1 = Book title
  - H2 = Parts / Pré-textual / Pós-textual
  - H3 = Chapters
  - H4/H5 = Enumerated content units (Questions in LDE, numbered paragraphs/items elsewhere)
  - H6 = Reserved exclusively for **Índice Geral** terms
- [x] Creation of `scrap.md` (root of `doutrina-content`): complete manual cut-and-paste of the PDF *Índice Geral* treated as highest-trust gold standard.
- [x] **LDE receives the full rigorous treatment first**:
  - 637+ H6 terms with 100% explicit `{#anchors}`
  - 1,215+ stable H5 question anchors (`#q847` style)
  - Roman numeral cleanup (except personal/historical titles)
- [x] **Tooling created for auditability**:
  - `scripts/validate-book.py` (heading gaps, H5 patterns, H6 anchor quality, Roman detection, `--report` mode)
  - `scripts/fidelity-checks.py` (PyMuPDF/fitz dict-mode geometric extraction from PDF index pages, auto x0 indentation detection, gold-vs-MD comparison reports)
  - `reports/` directory with dated fidelity and validation artifacts
- [x] **Anchor normalization rule** formally codified (lowercase, diacritic removal via unidecode, `(s)`/`/s` stripping, "Espírito(s)" → `espiritos`, hyphen collapsing, etc.).
- [x] `cross-reference.md` created as the authoritative spec (in-book short anchors vs. cross-book `lde:q-847` / `ldm:m-142` syntax, book prefixes table).
- [x] `style-guide.md` updated to v1.3 (heading discipline, prefix table `lde-q` / `ldm-m` / `ese-e` / `ceu-c` / `gen-g`, reference to normalization rule).
- [x] **Manual letter-by-letter H6 audit begins** (the highest-precision method after automated PDF↔MD comparisons proved noisy):
  - [x] **A** — Manually verified against PDF. All H6 terms spot-on. Anchors not checked.
  - [x] **B**
  - [x] **C** — 16 value-added items added (marked with NEW emoji); some still missing slugs and sub-items.
  - [ ] D–Z (in progress)
- [x] Acceptance that MD can (and should) contain useful extra terms beyond strict PDF index when they improve study value.
- [x] Root-level working snapshots (`1-lde-full.md` etc. dated 2026-05-24) used during the transition.

**Focus (May 2026):** Finish LDE Índice Geral audit (D onward) + complete slugs/sub-items for the 16 NEW C items. Then repeat the entire fidelity + tooling discipline for LDM, ESE, CEU, and GEN.

## Phase 5: Interface Rebuild on Modern Foundations (2026 — Ongoing)

Parallel track to the content work: faithfully recreate the soul of the original 4-column experience using clean modern primitives while preserving the "vanilla" character.

- [x] `doutrina-11ty` repo created (117+ commits).
- [x] "Initial Eleventy setup" and rapid iteration on `.eleventy.js`, Nunjucks layouts, passthroughs.
- [x] Sync scripts (`🔄 Sync: Atualização automática dos livros full.md do doutrina-content`) pulling the new clean full Markdown files.
- [x] `doutrina_modular_plan.pdf` articulates the three-repo vision (content + style/CSS-vars + interface).
- [x] Early 11ty builds of individual books (`lde/`, `ldm/`, etc.) and pure-MD test surfaces.
- [x] TOC / nesting plugins, safe filters, GitHub Pages deployment experiments.
- [ ] Full faithful recreation of the 4-column layout (main text column + dynamic side panels + notes layer).
- [ ] CSS custom properties / theming system (body classes + `:root` variables) so the same content can be presented in multiple visual personalities.
- [ ] Feature flags for study tools (Hypothesis, reading rulers, font controls, etc.).
- [ ] Parity with (and eventual supersession of) the old Jekyll + `combined.js` experience.

## Phase 6: PDF Page Markers & HTML Fidelity Loop (July 2026 — Ongoing)

Goal: physical PDF page anchors in source MD so doutrina.org / librus can offer “navigate by reference PDF page,” while reading order may differ from the print edition.

- [x] **Repo hygiene (2026-07-18)** — Resolve merge conflicts in `style-guide.md` / `cross-reference.md`; document partials+shared as edit SoT and full as publish artifact; tree cleanup.
- [x] **Tooling layout** — Multi-book scripts under `scripts/`; LDE-only under `scripts/lde/`; retired tools under `scripts/used/` (+ `used/lde/`).
- [x] **HTML verification renderer** — `scripts/lde/md_render.py` + `render_md_to_html.py` + detached `books/html/layout.css`.
- [x] **Page marker convention** — `[]{#page-N}` (prefer ` []{#page-N} ` with spaces); LDE tool: book page N = PDF **file − 1**; Prefácio may precede Introdução in MD order.
- [x] **LDE working PDF parts** — Local split under `books/pdf/work/1-lde/` (`part-0`…`part-6`). `*.pdf` gitignored.
- [x] **Auto-insert experiments (2026-07-19)** — First-words PDF matching with quote/punct/hyphen normalize + sequential QA (`insert_page_anchors.py`, `qa_page_anchors.py`, `page_anchor_exceptions.py`). Useful but incomplete; false TOC hits taught hard lessons (cursor poison, grid-era markers untrusted).
- [x] **Three-pane manual mark tool (2026-07-19)** — `scripts/lde/preview_tool/` (PDF select → Find in MD/HTML → Insert page#; book page = file−1; zoom; port free on start).
- [x] **Verify layouts + page sync (2026-07-20)** — Mark / Verify L / Verify R presets; Sync by page (PDF ↔ HTML `#page-N` ↔ MD); MD/HTML zoom.
- [x] **Manual LDE page anchors complete (2026-07-20)** — Unique `[]{#page-N}` for book pages **1–482** (omit blank 478–481 inside shared Nota; keep 477/482 boundaries). Link/footnote QA clean.
- [x] **Shared Legal/Nota book-agnostic** — Strip LDE-only page anchors from `nota-explicativa.md`; `INSERT_SHARED` restored in LDE partials 00/06.
- [x] **LDE split + concat round-trip (2026-07-20)** — Normalized H2 (no leading space); split 00–06; concat injects shared; block/link/Q validators pass.
- [ ] Extend page markers + work PDFs to LDM, ESE, CEU, GEN.
- [ ] Reader UX: jump to `#page-N` + optional open canonical PDF at N (doutrina.org / 11ty toolbar).
- [ ] Optional: formalize START_SHARED/END_SHARED if split must extract shared automatically (today: INSERT_SHARED in partials + manual restore after full campaigns).

**Docs bump (2026-07-20):** `style-guide.md` → **v1.6**; `cross-reference.md` → **v1.5**.

## Phase 7: Completion & Future Horizons (Planned)

- [ ] Complete, verified **Índice Geral** (full H6 + sub-items + anchors) for LDM, ESE, CEU, and GEN using the same scrap + validate + manual-audit workflow.
- [ ] Universal rich cross-book linking throughout all five full Markdown files using the documented prefix + slug rules.
- [ ] Production-grade `doutrina-11ty` / doutrina.org reader with PDF-page navigation + 4-column vanilla interface + theming.
- [ ] `doutrina-content` potentially published as reusable, versioned Markdown modules (or npm-equivalent for 11ty/ other consumers).
- [ ] Optional higher-level tooling (search index generation, graph of cross-references, export formats).
- [ ] Continued personal daily study use as the ultimate measure of success.

---

## Sources & Artifacts Used for Reconstruction

- Git histories (all four local repos): first commits, commit messages containing "scrap", "anchor", "índice", "sync", "11ty", "modular", daily snapshots.
- `doutrina-content/scrap.md` (May 27 2026) + `reports/` fidelity artifacts (historical; later cleaned).
- `doutrina-content/style-guide.md` v1.6 (20 Jul 2026) and `cross-reference.md` v1.5.
- `doutrina-11ty/doutrina_modular_plan.pdf` and commit messages around Eleventy setup + content syncs.
- Filesystem timestamps on root-level full MD snapshots (2026-05-24) and current `books/md/*/full/*.md`.
- Embedded "MD Quality & Fidelity Checklist" inside `1-lde-full.md`.
- User-provided progress markers (A/B/C manual verification + 16 NEW items).
- Architectural signals in `doutrina.org` (Jekyll + books submodule transitions) and the persistent 4-column "vanilla" DNA visible in both old site and new 11ty experiments.
- July 2026: PDF part splits, page-marker workflow, scripts/`lde` layout.

---

**This document itself is a living artifact.** Update it whenever a new major phase completes or when more early history surfaces from backups or memory. The real measure of progress remains the same as in March 2023: producing the highest-fidelity, most study-worthy digital versions of these five books possible.

**Next immediate actions (as of 2026-07-20):**  
Ship LDE full to doutrina.org / linker; reader toolbar PDF page nav (`#page-N`). Then page markers for other books; Índice audit D–Z; optional START_SHARED automation.

### Future Improvement: Short Machine Codex (3-5 char alphanumeric)

**Idea**: Introduce a parallel ultra-compact codex (mixed-case alphanum, 3-5 chars) for internal/machine use (data layer, 11ty collections, future graph DB, compact cross-refs) while keeping all human-readable anchors (`q847`, `1-03-05`, `lde-1-01`) for source and reader UI.

**Proposed schemes** (documented for later implementation):
- Option A (recommended for atomic): `L847` style → `LNp`, `MCS`, `ECd`, `CD9`, `GBb` (BookLetter + Base62 number). 3-4 chars.
- Option B: Packed hierarchical Base62 (e.g. `0axX` for LDE 1-03-05).
- Option C: Deterministic 4-5 char short hash of stable path/title for maximum stability.

**Rationale**: Current human codex is excellent for study fidelity. A second short layer enables clean internals without polluting Markdown or reader experience. Can be auto-generated at build time and stored in sidecar JSON or heading frontmatter.

This was explored in detail May 2026. Implementation deferred until after core content fidelity and basic 4-col 11ty demo.

---

## Codex Schema Evolution & Stress Test (May 2026 Analysis)

### The Journey from Uniform `trigraph-X-YY-ZZ` to Dual Specialized Addressing

**2023 (Early doutrina.org era)**  
The project adopted a classic library-style "codex" hierarchical numbering for stable addresses:
- `1-01-01`, `2-05-03`, `0-04-07`
- When content from multiple books coexisted: `lde-1-01-01`, `ese-X-10`, `gen-2-11-03` (the **trigraph-X-YY-ZZ** form).

This was documented in commits such as `ba52e3e1 1-01-01` and a series of `ESE-1-xx done` entries. It treated the entire collection as a single classified filing system — elegant and uniform.

**Limitation discovered during the 2026 fidelity work**  
The five books have fundamentally different "natural keys" that real readers and the printed *Índice Geral* actually use:

- **LDE**: Pure question numbers (the entire intellectual structure is question-driven).
- **LDM**: Numbered paragraphs / items about mediums.
- **ESE**: Roman chapter + item (`X, 19`, `XXIII, 10`, `introd., IV`).
- **CEU**: Mix of numbered items + named spirit cases/examples (the second half of the book is dominated by individual stories).
- **GEN**: Roman chapter + item, heavily mixed with scientific/doctrinal sections (`VI, 24`, `XVIII, 32`).

A single uniform `trigraph-X-YY-ZZ` codex worked for structural navigation but was a poor fit for the actual citation patterns that serious students use.

**Current Dual System (codified May 2026)**

1. **Structural / Hierarchical Layer** (descendant of the old codex)
   - `1-03-05`, `0-04-07`, `ese-1-01`, `gen-2-11-03`
   - Excellent for book outlines, TOCs, and fidelity to the physical book's organization.

2. **Atomic Content Unit Layer** (specialized per book)
   - LDE → `q-847` / cross: `lde:q-847`
   - LDM → `m-142` / `ldm:m-142`
   - ESE → `e-153` / `ese:e-153`
   - CEU → `c-247` / `ceu:c-247`
   - GEN → `g-089` / `gen:g-089`

This is documented in `style-guide.md` v1.3 (Detailed Rationale section) and `cross-reference.md` v1.2, including the book-specific prefixes (`lde-q`, `ldm-m`, `ese-e`, `ceu-c`, `gen-g`).

The old trigraph-X-YY-ZZ system was not discarded — it was deliberately scoped to structural headings while the atomic layer was specialized to match how each book's own *Índice Geral* actually addresses content.

### Stress Test: Real Index Addressing in ESE, CEU & GEN (extracted from source PDFs)

**ESE – O Evangelho segundo o Espiritismo** (417 pages)
- Dominant pattern: **Roman Chapter + Arabic item** (`X, 19-21`, `XXIII, 10`, `XIV, 3`, `introd., IV`).
- Many sub-entries under main concepts.
- Current proposed `e-XXX` (flat) is a reasonable simplification but loses the chapter context that readers are accustomed to.

**CEU – O Céu e o Inferno** (409 pages)
- Heavy use of simple Arabic numbers for many items (`– 365`, `– 282`, `– 49, nota`).
- Equally important: **named individual cases** ("Julienne-Marie, a mendiga", "Jobard, Espírito feliz", "Irmão do Sr. J.-B. D., ateu").
- The second part of the book is essentially a collection of spirit stories. A pure sequential `c-XXX` works for navigation but may need supplementary name-based or category-based anchors for usability.

**GEN – A Gênese** (417 pages)
- Strong **Roman Chapter + Arabic item** (`XV, 19`, `XVIII, 32`, `VI, 24`, `Introd.`).
- Mix of astronomical/scientific topics and doctrinal sections.
- Similar tension as ESE: the `g-XXX` proposal is clean, but the printed index heavily relies on chapter context.

**Overall Stress Test Verdict on Current Schema**
- The dual system is **sound and necessary**.
- The specialized atomic letters (`e-`, `c-`, `g-`) are a pragmatic compromise.
- For ESE and GEN, there is a real usability cost to completely abandoning chapter+item references. A hybrid approach (primary `e-XXX` + secondary structural `ese-X-10` aliases) may be required.
- CEU is the most challenging because of its heavy reliance on named cases rather than pure numbers.

### Feasibility of a Global Master Index (All Five Books)

**High feasibility for a unified search/cross-reference layer**, moderate-to-high effort for a traditional alphabetical "Índice Geral" style master index.

**Positive factors**
- Once Phase 1 (content fidelity) is complete for all five books, we will have:
  - Consistent H5 atomic anchors (`q-`/`m-`/`e-`/`c-`/`g-`).
  - Consistent H6 term anchors (after normalization rule).
  - Rich internal linking already present in the full Markdown.
- A global index becomes mostly a **merge + deduplication + cross-linking** problem rather than a transcription problem.
- Tooling already exists (`validate-book.py`, `fidelity-checks.py`, scrap.md process) that can be extended.
- The 11ty layer (Phase 5) can consume a generated master index for powerful cross-book search and "see also across the collection" features.

**Challenges & Required Work**
- Each book’s printed *Índice Geral* has its own depth, style, and addressing method (as shown in the stress test). A naive merge would produce an inconsistent or overwhelming result.
- CEU’s named cases and ESE/GEN’s chapter+item references need thoughtful normalization or dual representation.
- Many terms overlap across books (e.g. "Perispírito", "Reencarnação", "Obsessão"). These need smart grouping rather than simple concatenation.
- Sub-item depth varies wildly.

**Recommended Approach (once LDE audit + other books reach similar maturity)**
1. Generate per-book clean H6 term lists (with their atomic targets).
2. Create a master term list with:
   - Normalized anchor
   - List of occurrences across books with precise links (`lde:q-847`, `ese:e-153`, `ceu:c-247` + structural fallback when useful)
   - Optional grouping by theme (e.g. "Mediunidade", "Vida futura", "Moral")
3. Keep the individual book indices intact (they remain the most faithful to the printed source).
4. Offer the global master index as a powerful digital-only study tool (searchable, filterable by book, with strength-of-connection indicators).

**Verdict**: Very worthwhile and aligned with the original project intent ("rich pure-MD interlinking"). It is one of the highest-leverage deliverables once the five full Markdown files reach comparable fidelity. It would be a genuine scholarly contribution, not just a convenience feature.

This analysis (May 2026) should be revisited after the ESE/CEU/GEN index audits are complete, as the real printed indexes may reveal additional nuances.