# Guia de Contribuição e Padrões do Projeto

Este documento define as diretrizes de desenvolvimento para garantir que todo o time trabalhe em sintonia, mantendo a consistência do código e do histórico do Git.

---

## 1. Idioma e Nomenclatura

Para manter o projeto profissional e legível, adotaremos uma abordagem híbrida muito comum no mercado:

- **Código em Inglês:** Tudo o que for relacionado à estrutura do código deve ser escrito em inglês. Isso inclui:
  - Nomes de variáveis, funções, classes, métodos e arquivos (ex: `calculate_entropy()`, `bayes_engine.py`).
  - _Exceção:_ Termos próprios do jogo que não possuem tradução exata ou que descaracterizariam o contexto (ex: usar `termo` em vez de `wordle`, se preferirem manter a identidade do jogo brasileiro).
- **Interface (UI) em Português (PT-BR):** Toda string, texto, log ou interface visual que o usuário final ou o testador for visualizar deve ser escrita em português brasileiro (ex: `print("Parabéns! Você acertou.")`).

---

## 2. Padrão de Commits

Adotaremos o padrão **Conventional Commits**, mas com as mensagens escritas em **Português** e utilizando o **verbo no imperativo** (como se fosse uma ordem).

**Estrutura:** `<tipo>: <verbo no imperativo> <descrição curta>`

### Tipos principais:

- `feat`: Nova funcionalidade ou algoritmo (ex: `feat: adiciona motor de busca minimax`)
- `fix`: Correção de algum bug (ex: `fix: corrige filtro de letras amarelas repetidas`)
- `chore`: Configurações, setups, tarefas repetitivas ou estrutura de pastas (ex: `chore: define estrutura base do projeto`)
- `docs`: Mudanças apenas na documentação (ex: `docs: atualiza guia de contribuição`)
- `refactor`: Modificação no código que não altera o comportamento final (ex: `refactor: otimiza loops do naive bayes`)

---

## 3. Fluxo de Trabalho no Git (Git Workflow)

Nenhuma alteração deve ser feita diretamente nas branches principais (`main` ou `develop`).

### 3.1. Nomenclatura de Branches

As novas branches devem ser criadas sempre a partir da branch `develop` atualizada e seguir o padrão:
`tipo/descricao-curta-em-ingles`

- _Exemplos:_ `feat/naive-bayes-implementation`, `fix/feedback-colors-bug`, `chore/project-setup`.

### 3.2. Processo de Código e Integração

1.  Crie sua branch a partir da `develop`.
2.  Desenvolva a task e faça commits atômicos (pequenos e frequentes).
3.  Abra um **Merge Request (MR)** apontando da sua branch para a `develop`.
4.  **Code Review:** \* Pelo menos **1 membro** do time precisa revisar e aprovar o seu MR antes do merge.
    - Se a alteração for muito crítica (mudar a arquitetura principal do jogo, por exemplo), peça o Code Review dos **outros 2 membros** do time.
5.  Após as aprovações, realize o merge na `develop`.

> **Nota:** A branch `develop` será integrada à `main` apenas em momentos específicos de entrega de versões estáveis (milestones/releases) do projeto.

---

## 4. Padrão de Código (Python)

Como o projeto é em Python, seguiremos estritamente as diretrizes da **PEP 8**:

- Utilizar `snake_case` para nomes de funções, variáveis e arquivos (ex: `word_list`).
- Utilizar `PascalCase` para nomes de classes (ex: `NaiveBayesEngine`).
- Evitar commits com códigos comentados ("código morto"). Se não usa mais, delete (o Git guarda o histórico caso precisemos no futuro).
- _(Opcional - Recomendado)_ Usar o formatador de código **Black** ou **Ruff** para garantir que o espaçamento de todo mundo fique igual automaticamente.
