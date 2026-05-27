# Convenções de Referências Cruzadas (Cross-References)

**Versão 1.0** — 27 de Maio de 2026

Este documento define a convenção oficial para criar links **dentro de um mesmo livro** e **entre os cinco livros** da coleção, usando Markdown puro sempre que possível.

## 1. Princípios

- Priorizar **Markdown padrão** (`[texto](#ancora)` ou links por referência).
- Usar **prefixos estáveis e previsíveis** por livro para âncoras.
- Facilitar tanto a leitura humana no fonte quanto o processamento automático (11ty, scripts, busca).
- Manter os arquivos de conteúdo o mais limpos e portáveis possível.

## 2. Prefixos Oficiais de Âncoras por Livro

| Livro                        | Prefixo | Exemplo de Âncora     | Unidade Principal (H5)      |
|------------------------------|---------|-----------------------|-----------------------------|
| O Livro dos Espíritos (LDE)  | `lde-q` | `lde-q-847`           | Questões (Q.1 – Q.1019)     |
| O Livro dos Médiuns (LDM)    | `ldm-m` | `ldm-m-142`           | Parágrafos / Itens          |
| Evangelho s/ Espiritismo     | `ese-e` | `ese-e-153`           | Itens (I)                   |
| O Céu e o Inferno (CEU)      | `ceu-c` | `ceu-c-247`           | Exemplos / Casos (E)        |
| A Gênese (GEN)               | `gen-g` | `gen-g-089`           | Seções (S)                  |

**Regras para IDs:**
- Sempre use letras minúsculas + hífen: `lde-q-847` (nunca `LDE-Q-847` ou `q847` sozinho para referências cruzadas).
- Para seções estruturais (Introdução, Capítulos, etc.) mantenha os IDs descritivos já em uso (`#0-04-01`, `#2-05`, etc.).
- Prefira IDs explícitos via `{#id}` quando necessário.

## 3. Sintaxe de Links Recomendada

### 3.1 Links Inline (preferencial para a maioria dos casos)

```markdown
[O Livro dos Espíritos, Q.847](lde-q-847)

[ver também LDM §142](ldm-m-142)
```

### 3.2 Links por Referência (melhor para Índice Geral e notas densas)

```markdown
[ver Q.847][lde-q-847]

[lde-q-847]: lde-q-847
```

### 3.3 No Índice Geral (H6)

```markdown
###### 🔖 Ação
reciprocidade de – [LDM §375a](ldm-m-375a)
```

## 4. Boas Práticas

- **Dentro do mesmo livro**: use apenas o prefixo + número (ex: `[Q.400](lde-q-400)`).
- **Entre livros**: sempre inclua uma referência clara no texto do link.
- Evite depender de slugs gerados automaticamente pelo GitHub ou renderizador.
- Mantenha consistência entre o texto do índice e os links inline.
- Para referências a seções estruturais, use os IDs descritivos já existentes (ex: `[Introdução 15](lde:0-04-15)`).

## 5. Futuro (11ty / Build)

No processo de build do site (doutrina-11ty), esses prefixos poderão ser resolvidos automaticamente para:
- URLs finais corretas
- Títulos expandidos ("O Livro dos Espíritos, questão 847")
- Seções "Referências em outras obras"
- Validação de links quebrados

O conteúdo fonte deve permanecer o mais puro possível em Markdown.

## 6. Exemplos Completos

**No corpo do texto (LDM referenciando LDE):**

> Como já foi amplamente tratado em [O Livro dos Espíritos, Q.400](lde-q-400) e seguintes...

**No Índice Geral do LDE:**

```markdown
###### 🔖 Sonhos
recordação das experiências do Espírito – [LDM §400 a 418](ldm-m-400)
```

**Referência cruzada complexa:**

```markdown
[ver também ESE, cap. XV, item 4](ese-e-XXX) e [CEU, ex. 127](ceu-c-127)
```

---

**Documento complementar ao** [style-guide.md](./style-guide.md).

Mantido como fonte de verdade para todas as decisões de linking entre os livros da coleção.