# Convenções de Referências Cruzadas (Cross-References)

**Versão 2.0** — 26 de Julho de 2026

## 1. Hierarquia de cabeçalhos

- **H1**: Livro (único)
- **H2**: Partes (🗃️)
- **H3**: Capítulos (🗂️; exceções 📋 ⚖️ 📝)
- **H4**: Seções (📑)
- **H5**: Unidade enumerada (#️⃣) ou nota (📝)
- **H6**: Índice Geral (🔖)

Detalhes de emoji e títulos: [style-guide.md](./style-guide.md).

## 2. Codex serial (canônico)

Toda âncora de heading é:

```text
#{s|m|e|c|g}{dddd}
```

| Prefixo | Livro |
|---------|--------|
| `s` | LDE |
| `m` | LDM |
| `e` | ESE |
| `c` | CEU |
| `g` | GEN |

Exemplos:

```markdown
##### #️⃣ 847 {#s0964}
###### 🔖 Ação {#s1456}
```

### In-book

```markdown
Ver [#️⃣ 400](#s0xxx).
Ver também [📑 Objetivo da encarnação](#s0211).
```

### Cross-book

Preferir o serial completo no href (estável para o build):

```markdown
Como em [LDE #️⃣ 400](/lde/#s0xxx) …
```

Formas legadas `lde:q-400`, `ldm:m-142`, `ese-e-153` estão **obsoletas**. O build pode ainda resolvê-las via tabela de migração temporária; o Markdown fonte deve usar serials.

## 3. O que não é o codex

| Tipo | Forma | Notas |
|------|--------|--------|
| Página PDF | `[]{#page-17}` | N = página de livro; ver style-guide |
| URL externa | `https://…` | Intacta |
| YAML front matter | chaves do site | Fora do serial |

## 4. Índice Geral (H6)

O **id do heading** é o serial (`{#s1456}`).

Texto do termo: limpar emojis no *label* visível do índice se necessário; a âncora não depende mais de slug legível.

Regra legada de slug (só se gerar paths humanos auxiliares):

1. Remova emojis iniciais (🔖, 📑, …)
2. Minúsculas, sem diacríticos
3. Remova `(s)` / `/s` etc.
4. Não alfanuméricos → `-`

## 5. Sumário

- Apenas H2–H4
- Hrefs = serials
- Regenerar após qualquer renumeração em massa

## 6. Build (doutrina.org / 11ty / librus)

Poderá:

- Validar que todo `{#xdddd}` é único no livro
- Validar links internos `](#xdddd)`
- Resolver saltos `#page-N` e serials na UI

O Markdown fonte permanece a fonte da verdade dos ids.

---

**Complementa** [style-guide.md](./style-guide.md).
