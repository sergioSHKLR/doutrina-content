# Doutrina Content

Repositório **exclusivamente de conteúdo** (Markdown fonte) das Obras Básicas de Allan Kardec, para consumo pelo pipeline de doutrina.org / leitor librus.app.

## Árvore

```text
books/
  md/                     # Fonte Markdown
    shared/               # Blocos reutilizados (avisos-legais, nota-explicativa)
    1-lde/ … 5-gen/
      partial/            # Fonte editável (um arquivo por H2)
      full/               # Artefato gerado (livro completo)
      page_toc.md         # Mapa opcional página PDF ↔ seção (LDE)
      work/               # Snapshots / WIP local (não é fonte canônica)
  pdf/                    # PDFs de referência (gitignored: *.pdf)
    *.pdf                 # Canônicos (ordem e numeração oficiais)
    work/<livro>/         # PDFs H2 reordenados para marcação de páginas
    qa/                   # Extratos / experimentos gerados
  html/                   # Verificação visual (MD ≈ aparência do PDF)
    layout.css            # CSS destacado
    template.html         # Template Pandoc (TOC)
    images/               # Assets do HTML gerado
    *.html                # Gerados (gitignored)
images/                   # Assets referenciados no MD (ex.: vine)
scripts/                  # Pipeline multi-livro
  lde/                    # Ferramentas só LDE (render, pandoc)
  used/                   # One-shot genéricos
    lde/                  # One-shot só LDE
reports/                  # Saídas de auditoria
```

## Fonte canônica vs artefato

| Camada | Caminho | Uso |
|--------|---------|-----|
| **Editar** | `books/md/*/partial/` + `books/md/shared/` | Trabalho diário, IA, shared |
| **Publicar** | `books/md/*/full/*-full.md` | App / injeção de links / leitor |
| **PDF canônico** | `books/pdf/<obra>.pdf` | Numeração `[]{#page-N}` |
| **PDF de trabalho** | `books/pdf/work/<livro>/` | H2 split/reordenados (só QA) |

```bash
# Montar full a partir dos partials (+ shared)
./scripts/concat-all.sh

# Re-segmentar full → partials (após campanha no full)
./scripts/split-all.sh
```

**Regra:** não manter dois masters manuais do mesmo livro. Edite partials; regenere full. Campanhas de páginas no full devem terminar com split de volta aos partials (quando o round-trip de shared estiver confiável).

## Marcadores de página do PDF

```markdown
[]{#page-17}
```

- `N` = página do **PDF canônico**, não da ordem de scroll do MD.
- A ordem editorial do MD pode diferir do PDF (ex.: LDE Prefácio antes da Introdução).
- No leitor: navegação principal = ordem do MD; “página do PDF” = salto para `#page-N`.

## Verificação HTML (fidelidade) — LDE

```bash
source venv/bin/activate   # ou: pip install -r requirements.txt
python3 scripts/lde/render_md_to_html.py
# → books/html/1-lde-text-rendered.html  (+ layout.css)
```

Auditorias multi-livro:

```bash
python3 scripts/audit_links.py books/md/1-lde/full/1-lde-full.md
python3 scripts/check_block_closures.py books/md/1-lde/full/1-lde-full.md
python3 scripts/validate_book.py books/md/1-lde/full/1-lde-full.md 1019
```

HTML com TOC (LDE; requer `pandoc`):

```bash
./scripts/lde/pandoc-html.sh
```

Ver também [scripts/README.md](./scripts/README.md).

## Documentação

- [style-guide.md](./style-guide.md) — hierarquia, prefixos, ordem MD vs PDF
- [cross-reference.md](./cross-reference.md) — âncoras, links, `#page-N`
- [PROJECT-MILESTONES.md](./PROJECT-MILESTONES.md) — histórico do projeto

## Direitos

Textos de Allan Kardec: domínio público. Traduções/edições (ex.: Guillon Ribeiro / FEB): respeitar detentores. Repositório para estudo e desenvolvimento de edições digitais pessoais, sem fins comerciais.

**Projeto pessoal de Sergio.**
