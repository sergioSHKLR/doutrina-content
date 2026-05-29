<<<<<<< HEAD
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
=======
---

## 5. Normalização de Âncoras para Termos do Índice Geral (H6)

Para garantir consistência e links confiáveis entre os cinco livros, todas as âncoras de termos do Índice Geral (H6) devem seguir esta regra de normalização:

### Regra Oficial de Normalização

1. Remova emojis e símbolos iniciais (🔖, 📑, etc.).
2. Converta todo o texto para minúsculas.
3. Remova todos os diacríticos (á → a, ç → c, etc.).
4. **Tratamento de variantes de plural**:
   - `(s)`, `(es)`, `(e)` no final → remova o parênteses e normalize para a forma plural quando apropriado.
   - `/s`, `/es` → remova e normalize para a forma plural.
5. Substitua qualquer sequência de caracteres que não sejam letras ou números por um único hífen.
6. Colapse múltiplos hífens em apenas um.
7. Remova hífens no início ou final da âncora.

**Exemplos:**

| Texto original no PDF / Markdown | Âncora normalizada |
|----------------------------------|----------------------|
| Espírito(s)                     | `espiritos`          |
| Espírito/s                      | `espiritos`          |
| Ação                           | `acao`               |
| Além-túmulo                    | `alem-tumulo`        |
| Agostinho, Santo                 | `agostinho-santo`    |
| Comunicabilidade dos espíritos  | `comunicabilidade-dos-espiritos` |

**Princípio**: Prefira âncoras limpas e legíveis. Informação sobre variantes (singular/plural) deve ficar no texto visível do índice, não na âncora.

---

## 6. Âncoras Internas vs Links Entre Livros (Regra Importante)

Porque usamos o trigrafo do livro como permalink (`/lde/`, `/ldm/`, etc.), adotamos esta distinção clara:

### 6.1 Dentro do mesmo livro (in-book)
Use a forma **curta** que corresponde ao ID real presente no arquivo Markdown:

- `[Q.847](#q-847)` ou `[Q.847](#q847)` (conforme o ID efetivo no H5)
- `[§142](#m-142)`

### 6.2 Entre livros (cross-book)
Sempre use o **prefixo completo**:

- `[O Livro dos Espíritos, Q.847](lde:q-847)`
- `[LDM §142](ldm:m-142)`

Esta separação mantém os arquivos fonte limpos e os links entre livros explícitos e portáveis.

## 7. Numeração e Algarismos Romanos

- Substituímos algarismos romanos por arábicos em todo o conteúdo, índices e referências.
- **Exceção**: Mantemos romanos em títulos pessoais ou históricos (ex: "São Luís, IX de França", "Luís IX").

## 8. Âncoras dos Termos do Índice Geral (H6) - Casos Específicos

Cada termo principal do Índice Geral recebe uma âncora baseada na palavra principal:

- Sem diacríticos
- Minúsculas
- Hífens para separar palavras

Exemplos reais do LDE:

- Aberração → `{#aberracao}`
- Ação → `{#acao}`
- Além-túmulo → `{#alem-tumulo}`
- Agostinho, Santo → `{#agostinho-santo}`
- Allan Kardec → `{#allan-kardec}`

O mesmo padrão deve ser aplicado consistentemente em todos os livros quando o Índice Geral for completado.

## 9. Exemplos Práticos

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

## 10. Futuro no Build (11ty)

O sistema de build poderá:
- Resolver automaticamente os links curtos e prefixados
- Gerar seções "Referências em outras obras"
- Validar links cruzados
- Produzir âncoras finais estáveis nos HTMLs gerados

O Markdown fonte deve permanecer o mais limpo e semântico possível.

---

**Documento complementar ao** [style-guide.md](./style-guide.md).
>>>>>>> c33522679f2cb06e1940d06b2da1180b03c1448c
