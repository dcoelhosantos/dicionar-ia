# Dicionar-IA: O Solucionador Automatizado de Termo

> Um laboratório prático de Inteligência Artificial comparando paradigmas lógicos, probabilísticos e de busca adversarial na resolução do jogo [Termo](https://term.ooo).

---

## Visão Geral do Projeto

O **Dicionar-IA** não é apenas um "bot que joga Termo", mas sim um ambiente de avaliação comparativa. O objetivo deste projeto é colocar diferentes abordagens teóricas de Inteligência Artificial para resolver o mesmo problema: adivinhar uma palavra secreta de 5 letras em até 6 tentativas, com base em um feedback de cores (Verde, Amarelo, Cinza).

---

## Os Motores de IA (Paradigmas Avaliados)

Este projeto implementa e compara quatro motores de Inteligência Artificial distintos:

* **Minimax:** Modela o jogo como um confronto contra um "juiz adversário". Utiliza heurística para minimizar o pior cenário possível de palavras restantes e poda Alpha-Beta para otimização. É o único motor do projeto que consegue contornar a armadilha das palavras semelhantes fazendo jogadas de sacrifício.
* **DPLL Solver:** Converte as regras do jogo e o feedback de cores em uma Base de Conhecimento em Formato Normal Conjuntivo (CNF). Utiliza inferência lógica e o algoritmo DPLL para deduzir certezas absolutas.
* **Model Checking:** Substitui as variáveis proposicionais pelas letras de cada palavra candidata para validar se aquele "Mundo Possível" satisfaz a Base de Conhecimento unificada.
  * **Nota:** Devido ao altíssimo custo computacional das substituições, este motor foi intencionalmente excluído do lote de avaliação de 50 partidas, ficando disponível apenas para partidas individuais.
* **Naive Bayes:** Calcula a probabilidade logarítmica (para evitar *underflow*) de uma palavra ser a correta com base na frequência histórica das letras em suas respectivas posições.

---

## Tecnologias Utilizadas

A stack foi escolhida priorizando performance e foco no domínio do problema:

* **Linguagem:** Python 3.10+
* **SymPy:** Motor matemático para modelagem simbólica, formulação CNF e avaliação do Model Checking.
* **Rich:** Renderização avançada da interface de linha de comando (CLI), painéis e tabelas.
* **Módulos Nativos:** `math` (logaritmos), `collections` (Counter, defaultdict), `dataclasses`, `typing` (Protocol), `unittest`.

---

## Como Executar

**1. Clone o repositório e acesse a pasta:**
```bash
git clone https://github.com/dcoelhosantos/dicionar-ia.git
cd dicionar-ia
```

**2. Instale as dependências (Recomendamos uso de ambiente virtual - venv):**
```bash
pip install -r requirements.txt
```

**3. Inicie a Interface (CLI):**
```bash
python main.py
```

---

## Opções do Menu na CLI

Ao executar o projeto, você terá acesso ao nosso painel interativo:

* **Jogar Manualmente:** Teste suas próprias habilidades contra o dicionário.
* **Escolher um Motor:** Jogue partidas assistidas onde a IA sugere o próximo palpite, ou deixe a IA jogar sozinha para você observar as deduções.
* **Comparar Motores:** Coloca as IAs ativas para jogar a exata mesma semente de palavra secreta e compara as tentativas e o tempo gasto lado a lado.
* **Avaliar Motores:** Roda um lote de 50 partidas automatizadas (benchmark) para extrair métricas de Win Rate, média de tentativas e tempo total de execução.

---

## Arquitetura do Projeto

* `game/`: Lógica central do Termo, validação de regras, processamento de feedback e UI (CLI).
* `engines/`: Onde habitam os motores, isolados por domínio (`logic`, `minimax`, `bayes`). Motores lógicos compartilham código através da `BaseLogicEngine`.
* `metrics/`: Avaliador de partidas em massa (`Evaluator`).
* `tests/`: Suíte de testes automatizados validando as Bases de Conhecimento e regras fundamentais do jogo.
