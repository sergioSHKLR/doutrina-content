# Estilo de Marcação para a Coleção Digital Espírita (dc)
**Versão 1.3** — 27 de Maio de 2026

### 1. Princípios Gerais
- h1 = Título completo do livro
- h2 = Partes / Pré-textual / Pós-textual
- h3 = Capítulos
- h4 = Seções / Tópicos principais (agrupamentos)
- **h5 = Unidade principal de conteúdo** (Questões no LDE, parágrafos numerados, itens principais)
- **h6 = Termos de Índice / Referências Cruzadas** (exclusivo para Índice Geral)

### 2. Hierarquia por Livro

**LDE – O Livro dos Espíritos**
- H5 = Questões (Q.1 a Q.1019)
- H6 = Índice completo (648 termos)

**LDM, ESE, CEU, GEN**
- H5 = Parágrafos / Itens principais
- H6 = Índice (placeholder até expansão completa)

### 3. Prefixos de Âncoras para Referências Cruzadas

Os prefixos abaixo são usados **principalmente para links entre livros**. Para links internos ao mesmo livro, prefere-se a forma curta (ver seção de convenções de links).

- **LDE**: `lde-q`
- **LDM**: `ldm-m` (m = médiuns)
- **ESE**: `ese-e`
- **CEU**: `ceu-c`
- **GEN**: `gen-g`

Exemplos de âncoras completas para cross-book:
- `lde-q-847`
- `ldm-m-142`
- `ese-e-153`
- `ceu-c-247`
- `gen-g-089`

### 4. Numeração e Romanos

- Substituímos algarismos romanos por arábicos em todo o conteúdo e índices, **exceto** em títulos pessoais/históricos (ex: "São Luís, IX de França" mantém o IX).
- O método de endereçamento do Índice Geral original determina diretamente como criamos as âncoras (ver cross-reference.md).

### 5. Âncoras nos Termos do Índice Geral (H6)

Cada termo principal do Índice Geral (H6) recebe uma âncora baseada na palavra principal, sem diacríticos e em minúsculas:

- `Aberração` → `{#aberracao}`
- `Ação` → `{#acao}`
- `Além-túmulo` → `{#alem-tumulo}`
- `Agostinho, Santo` → `{#agostinho-santo}`
- `Allan Kardec` → `{#allan-kardec}`

Ver documento completo em [cross-reference.md](./cross-reference.md).