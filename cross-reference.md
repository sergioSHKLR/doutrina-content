# Convenções de Referências Cruzadas (Cross-References)

**Versão 1.1** — 27 de Maio de 2026

Este documento define a convenção oficial para criar links dentro de um mesmo livro e entre os cinco livros, respeitando a estrutura hierárquica real dos textos e o método de endereçamento dos Índices Gerais originais.

## 1. Hierarquia de Cabeçalhos e Endereçamento

- **H1**: Livro
- **H2**: Partes (Pré-textual, as grandes divisões doutrinárias, Conclusão, Pós-textual)
- **H3**: Capítulos
- **H4**: Seções / tópicos principais (agrupamentos)
- **H5**: Unidade principal de conteúdo enumerada (o alvo mais comum de links)
  - LDE → Questões
  - LDM → Parágrafos / itens
  - ESE → Itens
  - CEU → Exemplos / Casos
  - GEN → Seções
- **H6**: Termos do Índice Geral (camada de navegação e referências cruzadas, **não** conteúdo primário)

**Princípio fundamental**: O modo como o Índice Geral impresso endereça o conteúdo determina como criamos as âncoras.

## 2. Prefixos Oficiais

Usados principalmente para **links entre livros**:

- LDE → `lde-q`
- LDM → `ldm-m` (**m = médiuns**)
- ESE → `ese-e`
- CEU → `ceu-c`
- GEN → `gen-g`

## 3. Âncoras Internas vs Links Entre Livros (Regra Importante)

Porque usamos o trigrafo do livro como permalink (`/lde/`, `/ldm/`, etc.), adotamos esta distinção clara:

### 3.1 Dentro do mesmo livro (in-book)
Use a forma **curta** que corresponde ao ID real presente no arquivo Markdown:

- `[Q.847](#q-847)` ou `[Q.847](#q847)` (conforme o ID efetivo no H5)
- `[§142](#m-142)`

### 3.2 Entre livros (cross-book)
Sempre use o **prefixo completo**:

- `[O Livro dos Espíritos, Q.847](lde:q-847)`
- `[LDM §142](ldm:m-142)`

Esta separação mantém os arquivos fonte limpos e os links entre livros explícitos e portáveis.

## 4. Numeração e Algarismos Romanos

- Substituímos algarismos romanos por arábicos em todo o conteúdo, índices e referências.
- **Exceção**: Mantemos romanos em títulos pessoais ou históricos (ex: "São Luís, IX de França", "Luís IX").

## 5. Âncoras dos Termos do Índice Geral (H6)

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

## 6. Exemplos Práticos

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

## 7. Futuro no Build (11ty)

O sistema de build poderá:
- Resolver automaticamente os links curtos e prefixados
- Gerar seções "Referências em outras obras"
- Validar links cruzados
- Produzir âncoras finais estáveis nos HTMLs gerados

O Markdown fonte deve permanecer o mais limpo e semântico possível.

---

**Documento complementar ao** [style-guide.md](./style-guide.md).