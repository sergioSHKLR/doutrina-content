# Convenções de Referências Cruzadas (Cross-References)

**Versão 1.4** — 19 de Julho de 2026

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

Porque usamos o trigráfico do livro como permalink (`/lde/`, `/ldm/`, etc.), esta distinção mantém o Markdown fonte limpo e os links entre livros explícitos.

## 3. Regra de Normalização de Âncoras (H6 - Índice Geral)

Esta é a regra oficial para gerar âncoras de termos do Índice Geral:

1. Remova emojis e símbolos iniciais (🔖, 📑, etc.).
2. Converta para minúsculas.
3. Remova todos os diacríticos.
4. **Remova marcadores de plural/variante**:
   - `(s)`, `(es)`, `(e)` → remova
   - `/s`, `/es` → remova
5. Substitua sequências de caracteres não alfanuméricos por um único hífen.
6. Colapse hífens múltiplos.
7. Remova hífens no início ou final.

**Exemplos:**

| Texto original | Âncora normalizada |
|----------------|--------------------|
| Espírito(s) | `espiritos` |
| Espírito/s | `espiritos` |
| Ação | `acao` |
| Além-túmulo | `alem-tumulo` |
| Agostinho, Santo | `agostinho-santo` |
| Comunicabilidade dos espíritos | `comunicabilidade-dos-espiritos` |

**Princípio**: A informação de variante (singular/plural) fica no texto visível do índice. A âncora deve ser o mais limpa e estável possível.

## 4. Numeração e Algarismos Romanos

- Substitua algarismos romanos por arábicos na maioria dos casos.
- **Exceção**: Mantenha romanos em títulos pessoais/históricos (ex: "São Luís, IX de França").

## 5. Exemplos Práticos

**No Índice Geral do LDE (H6):**

```markdown
###### 🔖 Ação
reciprocidade de – [LDM §375a](ldm:m-375a)
```

**No corpo de texto do LDM referenciando LDE (cross-book):**

```markdown
Como foi amplamente tratado em [O Livro dos Espíritos, Q.400](lde:q-400) e seguintes...
```

**Link interno no mesmo livro (in-book):**

```markdown
Ver também [Q.400](#q-400) acima.
```

## 6. Marcadores de página do PDF

```markdown
[]{#page-17}
```

- `N` é a página do **PDF canônico** em `books/pdf/`.
- O marcador fica no **início** (topo lógico) do texto da página N — antes das primeiras palavras dessa página no MD.
- O HTML de verificação ainda desenha o número no **rodapé visual** do bloco da página (entre `#page-N` e `#page-N+1`).
- Podem ser não monotônicos na ordem de leitura do MD (ex.: Prefácio com páginas posteriores à Introdução no PDF).
- Destinam-se à navegação “página do PDF” no leitor (doutrina.org / librus), não à paginação automática do HTML.

## 7. Futuro no Build

O sistema de build (doutrina.org / 11ty / librus) poderá:

- Resolver automaticamente os links curtos e prefixados
- Validar links cruzados e âncoras de página
- Produzir HTML de leitura com saltos para `#page-N`

O Markdown fonte deve permanecer o mais limpo e semântico possível.

---

**Documento complementar ao** [style-guide.md](./style-guide.md).
