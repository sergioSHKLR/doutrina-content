# Estilo de Marção para a Coleção Digital Espírita (dc)
**Versão 1.2** — Atualizado em 27 de Maio de 2026

### 1. Princípios Gerais
- h1 = Título completo do livro
- h2 = Partes / Pré-textual / Pós-textual
- h3 = Capítulos
- h4 = Seções / Tópicos principais
- **h5 = Unidade principal de conteúdo** (Questões no LDE, parágrafos numerados, itens principais)
- **h6 = Termos de Índice / Referências Cruzadas** (exclusivo para Índice Geral)

### 2. Hierarquia por Livro

**LDE – O Livro dos Espíritos**
- H5 = Questões (Q.1 a Q.1019)
- H6 = Índice completo (648 termos)

**LDM, ESE, CEU, GEN**
- H5 = Parágrafos / Itens principais
- H6 = Índice (placeholder até expansão completa)

### 3. Regras Específicas
- Apenas **LDE** deve ter alto número de H6 atualmente.
- Outros livros devem manter H6 ~25 (placeholders) até o índice completo ser construído.
- Não usar H6 fora da seção **Índice Geral** do Pós-textual.

### 4. Prefixos de Âncoras para Referências Cruzadas

Para permitir interligações consistentes entre os cinco livros, use os seguintes prefixos quando criar IDs de âncoras e links:

- **LDE**: `lde-q` (ex: `lde-q-847`)
- **LDM**: `ldm-m` (ex: `ldm-m-142`)
- **ESE**: `ese-e`
- **CEU**: `ceu-c`
- **GEN**: `gen-g`

Esses prefixos devem ser usados nos arquivos Markdown fonte para referências estáveis (dentro do livro e entre livros).

---

**Rationale detalhado** (do Índice Geral dos PDFs originais)

LDE — Já ótimo (QXXXX). O índice é extremamente detalhado por número de questão. H5 = questões individuais é a unidade mais natural.

LDM — PXXX é excelente. O índice referencia parágrafos diretamente (ex. §142).

ESE — IXXX (Item) é a melhor simplificação.

CEU — EXXX (Exemplo) encaixa perfeitamente.

GEN — SXXX (Seção) é o mais prático.

Veja o documento completo de convenções de referências cruzadas em [cross-reference.md](./cross-reference.md).