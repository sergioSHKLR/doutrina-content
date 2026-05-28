# Convenções de Referências Cruzadas (Cross-References)

**Versão 1.2** — 28 de Maio de 2026

Este documento define a convenção oficial para criar links dentro de um mesmo livro e entre os cinco livros da coleção, com foco em âncoras limpas e consistentes.

## 1. Hierarquia de Cabeçalhos

- **H1**: Livro
- **H2**: Partes (Pré-textual, divisões doutrinárias principais, Conclusão, Pós-textual)
- **H3**: Capítulos
- **H4**: Seções / tópicos principais (agrupamentos)
- **H5**: Unidade principal de conteúdo enumerada
  - LDE → Questões (`q-XXX`)
  - LDM → Parágrafos / itens (`m-XXX`)
  - ESE → Itens (`e-XXX`)
  - CEU → Exemplos / Casos (`c-XXX`)
  - GEN → Seções (`g-XXX`)
- **H6**: Termos do Índice Geral (camada de navegação e referências cruzadas)

## 2. Prefixos Oficiais para Cross-Book

Usados principalmente para links **entre livros**:

- LDE → `lde-q`
- LDM → `ldm-m` (m = médiuns)
- ESE → `ese-e`
- CEU → `ceu-c`
- GEN → `gen-g`

### In-Book vs Cross-Book

- **Dentro do mesmo livro**: Use a forma curta (ex: `#q-847`, `#m-142`)
- **Entre livros**: Use o prefixo completo (ex: `lde:q-847`, `ldm:m-142`)

## 3. Regra de Normalização de Âncoras (H6 - Índice Geral)

Esta é a regra oficial para gerar âncoras de termos do Índice Geral:

1. Remova emojis e símbolos iniciais.
2. Converta para minúsculas.
3. Remova todos os diacríticos.
4. **Remova marcadores de plural/variante**:
   - `(s)`, `(es)`, `(e)` → remova
   - `/s`, `/es` → remova
5. Substitua sequências de caracteres não alfanuméricos por um único hífen.
6. Colapse hífens múltiplos.
7. Remova hífens no início ou final.

**Exemplos:**

| Texto original              | Âncora normalizada     |
|----------------------------|------------------------|
| Espírito(s)                | `espiritos`            |
| Espírito/s                 | `espiritos`            |
| Ação                       | `acao`                 |
| Além-túmulo                | `alem-tumulo`          |
| Agostinho, Santo           | `agostinho-santo`      |

**Princípio**: A informação de variante (singular/plural) fica no texto visível do índice. A âncora deve ser o mais limpa e estável possível.

## 4. Numeração e Algarismos Romanos

- Substitua algarismos romanos por arábicos na maioria dos casos.
- **Exceção**: Mantenha romanos em títulos pessoais/históricos (ex: "São Luís, IX de França").

---

**Documento complementar ao** `style-guide.md`.