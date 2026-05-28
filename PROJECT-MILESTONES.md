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

**Current Focus (late May 2026):** Finish LDE Índice Geral audit (D onward) + complete slugs/sub-items for the 16 NEW C items. Then repeat the entire fidelity + tooling discipline for LDM, ESE, CEU, and GEN.

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

## Phase 6: Completion & Future Horizons (Planned)

- [ ] Complete, verified **Índice Geral** (full H6 + sub-items + anchors) for LDM, ESE, CEU, and GEN using the same scrap + validate + manual-audit workflow.
- [ ] Universal rich cross-book linking throughout all five full Markdown files using the documented prefix + slug rules.
- [ ] Production-grade `doutrina-11ty` site deployed (replacing or augmenting doutrina.org) with the full 4-column vanilla interface + theming.
- [ ] `doutrina-content` potentially published as reusable, versioned Markdown modules (or npm-equivalent for 11ty/ other consumers).
- [ ] Optional higher-level tooling (search index generation, graph of cross-references, export formats).
- [ ] Continued personal daily study use as the ultimate measure of success.

---

## Sources & Artifacts Used for Reconstruction

- Git histories (all four local repos): first commits, commit messages containing "scrap", "anchor", "índice", "sync", "11ty", "modular", daily snapshots.
- `doutrina-content/scrap.md` (May 27 2026) + `reports/` fidelity artifacts.
- `doutrina-content/style-guide.md` v1.3 (28 May 2026) and `cross-reference.md`.
- `doutrina-11ty/doutrina_modular_plan.pdf` and commit messages around Eleventy setup + content syncs.
- Filesystem timestamps on root-level full MD snapshots (2026-05-24) and current `books/md/*/full/*.md`.
- Embedded "MD Quality & Fidelity Checklist" inside `1-lde-full.md`.
- User-provided progress markers (A/B/C manual verification + 16 NEW items).
- Architectural signals in `doutrina.org` (Jekyll + books submodule transitions) and the persistent 4-column "vanilla" DNA visible in both old site and new 11ty experiments.

---

**This document itself is a living artifact.** Update it whenever a new major phase completes or when more early history surfaces from backups or memory. The real measure of progress remains the same as in March 2023: producing the highest-fidelity, most study-worthy digital versions of these five books possible.

**Next immediate actions (as of this writing):**  
Continue the manual H6 letter audit in LDE (D+), resolve the 16 NEW C items, then expand the same discipline to the other four books while the 11ty interface layer matures in parallel.