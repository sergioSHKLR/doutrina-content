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