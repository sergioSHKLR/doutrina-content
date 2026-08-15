# Estilo de Marcação para a Coleção Digital Espírita (dc)

**Versão 2.0** — 26 de Julho de 2026

### 1. Princípios Gerais

- **h1** = Título do livro (um por obra)
- **h2** = Partes / caixas grandes (Pré-textual, divisões, Pós-textual)
- **h3** = Capítulos / pastas
- **h4** = Seções (folhas múltiplas)
- **h5** = Unidade enumerada de conteúdo (maior volume de headings no livro)
- **h6** = Termos do **Índice Geral** apenas

Não usar prefixos numéricos de outline nos títulos (`0.`, `1.05.`, `0.04.01.`).  
Números de trabalho (questões, itens) ficam no texto do H5 com #️⃣.

### 2. Escada de emojis

| Nível | Papel | Emoji padrão |
|------:|-------|----------------|
| H1 | Identidade da obra | **Por livro:** LDE ✨ · LDM ✒️ · ESE 🕊️ · CEU 🔥 · GEN 🌱 |
| H2 | Caixa | 🗃️ |
| H3 | Pasta | 🗂️ |
| H4 | Folhas (conjunto) | 📑 |
| H5 | Unidade (#) | #️⃣ |
| H6 | Índice (marcador) | 🔖 |

**Exceções de H3 (papel semântico):**

| Emoji | Uso |
|-------|-----|
| 📋 | Sumário |
| ⚖️ | Avisos legais |
| 📝 | Notas (rodapé / nota de seção; mesmo espírito das notas de rodapé) |

**H5 notas:** 📝 (não #️⃣), p.ex. `##### 📝 Nota`.

Fillers de hierarquia (evitar saltos de nível) são headings reais e **entram no codex serial**.

### 3. Codex serial de âncoras (máquina)

Formato: **`{letra}{nnnn}`** — sempre 4 dígitos, zeros à esquerda.

| Letra | Livro |
|-------|--------|
| `s` | LDE (*Espíritos*; evita `l` confuso com `1`) |
| `m` | LDM |
| `e` | ESE |
| `c` | CEU |
| `g` | GEN |

**Regra de atribuição**

1. Ignorar o bloco YAML inicial `---` … `---` (não serializar `#` de metadados).
2. Percorrer o corpo do full em ordem de documento.
3. Cada heading ATX H1–H6 recebe o próximo inteiro: `s0001`, `s0002`, …
4. Uma âncora por heading: `## 🗃️ Pré-textual {#s0002}`
5. **Substituir** ids antigos (`lde-q12`, `ese-1-05-01-n03`, …); não manter dual ids.
6. Inserir/apagar heading **renumeram** o serial a partir daí — campanhas grandes = reexecutar o migrador.

Ordem de grandeza atual (fulls, pós-migração):

| Livro | ≈ último id |
|-------|-------------|
| LDE | `s2136` |
| LDM | `m1902` |
| ESE | `e1172` |
| CEU | `c0847` |
| GEN | `g1235` |

**Não** codificar capítulo/questão no id. O número legível fica no título (`##### #️⃣ 12`).

### 4. Unidades enumeradas (H5)

| Livro | Forma do título H5 |
|-------|-------------------|
| LDE | `##### #️⃣ 12` · variantes `##### #️⃣ 790.a` (sem `Q.`) |
| LDM / ESE / CEU / GEN | `##### #️⃣ 3` (sem padding `03`) |

### 5. Índice Geral (H6)

- Sempre `###### 🔖 Termo {#s1xxx}` (ou m/e/c/g).
- LDE: termos de índice **não** ficam em H5.
- Normalização legada de slugs de termo (se ainda existir texto): ver [cross-reference.md](./cross-reference.md). O **id canônico** do heading é o serial.

### 6. Sumário (TOC)

- Bloco `::: expand` sob o H3 📋 Sumário.
- Links **apenas H2–H4** (não H5/H6).
- Alvos = serials novos.

### 7. Marcadores de página do PDF

```markdown
 []{#page-N} 
```

- **N** = página de livro = página de arquivo do PDF − offset (LDE/tool: offset 1).
- Shared (`avisos-legais`, `nota-explicativa`) sem `[]{#page-N}`.
- Independentes do codex serial de headings.

### 8. Fonte canônica de edição

- **Editar agora (campanha codex):** `books/md/*/full/*-full.md`
- **Depois:** `split` → partials; rotina futura: partials + shared como SoT, `concat-all.sh` para full.
- Front matter YAML: **não alterar** nesta convenção.

### 9. Script

Migração / reaplicação: `scripts/migrate_heading_codex.py`  
(Reexecutar só com backup: renumera tudo.)

---

Documento irmão: [cross-reference.md](./cross-reference.md).
