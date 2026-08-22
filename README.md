# doutrina-content

**Build step 1 of 4** · Content source (maintainers & volunteers)

---

## 📑 Table of contents

1. 🇺🇸 [English](#-english--build-step-1-of-4)
   1. 🎯 [Audience](#-audience)
   2. 🗺️ [Pipeline position](#-pipeline-position)
   3. 📦 [What lives here](#-what-lives-here)
   4. 🛠️ [Day-to-day workflow](#️-day-to-day-workflow)
   5. 📎 [Related docs](#-related-docs)
   6. ⚖️ [Rights](#️-rights)
2. 🇧🇷 [Português](#-português--etapa-1-de-4)
   1. 🎯 [Público](#-público)
   2. 🗺️ [Posição no pipeline](#-posição-no-pipeline)
   3. 📦 [O que vive aqui](#-o-que-vive-aqui)
   4. 🛠️ [Rotina de trabalho](#️-rotina-de-trabalho)
   5. 📎 [Documentação relacionada](#-documentação-relacionada)
   6. ⚖️ [Direitos](#️-direitos-1)

---

# 🇺🇸 English — Build step 1 of 4

Editorial **Markdown source** for Kardec’s basic works. Not the reader SPA. Not the live site.

## 🎯 Audience

1. Content curators and proofreaders  
2. Volunteers marking PDF page anchors  
3. Maintainers who feed the linker and shell  

**Not** for end readers — they use [doutrina.org](https://doutrina.org) / [librus.app](https://librus.app).

## 🗺️ Pipeline position

1. **This repo** — edit Markdown (`partial/` → `full/`)  
2. [`librus-linker`](https://github.com/sergioSHKLR/librus-linker) — provider link injection  
3. [`librus-shell`](https://github.com/sergioSHKLR/librus-shell) — SPA + books → `dist`  
4. Host repos — GitHub Pages (`librus` · `doutrina` · `centro`)  

```text
doutrina-content  →  librus-linker  →  librus-shell  →  host Pages
     (1/4)              (2/4)             (3/4)            (4/4)
```

## 📦 What lives here

1. **Edit:** `books/md/*/partial/` + `books/md/shared/`  
2. **Publish artifact:** `books/md/*/full/*-full.md`  
3. **Canonical PDFs:** `books/pdf/<obra>.pdf` (gitignored binaries; numbering authority)  
4. **QA tools:** `scripts/` (concat, split, page anchors, audits)  

## 🛠️ Day-to-day workflow

1. Edit **partials** (one file per H2), not two manual masters.  
2. Rebuild fulls: `./scripts/concat-all.sh`  
3. After full-file campaigns, split back: `./scripts/split-all.sh`  
4. Page markers use `[]{#page-N}` (book page = PDF file page − offset for LDE).  
5. Preview / mark pages:  

```bash
source venv/bin/activate   # or: pip install -r requirements.txt
./venv/bin/python scripts/preview_tool/server.py
# → http://127.0.0.1:8765/
```

## 📎 Related docs

1. [style-guide.md](./style-guide.md)  
2. [cross-reference.md](./cross-reference.md)  
3. [scripts/preview_tool/README.md](./scripts/preview_tool/README.md)  
4. [PROJECT-MILESTONES.md](./PROJECT-MILESTONES.md)  

## ⚖️ Rights

1. Kardec texts: public domain.  
2. Translations/editions (e.g. Guillon Ribeiro / FEB): respect rights holders.  
3. Personal study / digital-edition development — non-commercial intent.  

**Personal project of Sergio.**

---

# 🇧🇷 Português — Etapa 1 de 4

Fonte editorial em **Markdown** das Obras Básicas de Allan Kardec. Não é a SPA. Não é o site publicado.

## 🎯 Público

1. Curadores e revisores de texto  
2. Voluntários que marcam âncoras de página do PDF  
3. Mantenedores que alimentam o linker e o shell  

**Não** é para o leitor final — use [doutrina.org](https://doutrina.org) / [librus.app](https://librus.app).

## 🗺️ Posição no pipeline

1. **Este repositório** — editar Markdown (`partial/` → `full/`)  
2. [`librus-linker`](https://github.com/sergioSHKLR/librus-linker) — injeção de ligações  
3. [`librus-shell`](https://github.com/sergioSHKLR/librus-shell) — SPA + livros → `dist`  
4. Repos host — GitHub Pages (`librus` · `doutrina` · `centro`)  

## 📦 O que vive aqui

1. **Editar:** `books/md/*/partial/` + `books/md/shared/`  
2. **Artefato de publicação:** `books/md/*/full/*-full.md`  
3. **PDFs canônicos:** `books/pdf/<obra>.pdf`  
4. **Ferramentas de QA:** `scripts/`  

## 🛠️ Rotina de trabalho

1. Edite **partials** (um arquivo por H2).  
2. Monte os fulls: `./scripts/concat-all.sh`  
3. Após campanhas no full, reaplique: `./scripts/split-all.sh`  
4. Marcadores: `[]{#page-N}` (página de livro = PDF − offset no LDE).  
5. Pré-visualização / marcação:  

```bash
source venv/bin/activate
./venv/bin/python scripts/preview_tool/server.py
# → http://127.0.0.1:8765/
```

## 📎 Documentação relacionada

1. [style-guide.md](./style-guide.md)  
2. [cross-reference.md](./cross-reference.md)  
3. [scripts/preview_tool/README.md](./scripts/preview_tool/README.md)  
4. [PROJECT-MILESTONES.md](./PROJECT-MILESTONES.md)  

## ⚖️ Direitos

1. Textos de Kardec: domínio público.  
2. Traduções/edições: respeitar detentores.  
3. Estudo e desenvolvimento de edições digitais pessoais, sem fins comerciais.  

**Projeto pessoal de Sergio.**
