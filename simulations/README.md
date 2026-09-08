# 🎲 Motores de Simulação e Análise — BTG Madagascar (v14.0)

Este diretório concentra os **seis motores analíticos oficiais** do projeto, projetados para execução em alta escala com suporte a multiprocessamento e integração direta com o ponto de entrada principal (`run.py`).

---

simulations/
├── run_monte_carlo.py       # Simulação Monte Carlo Massiva (Telemetria dos 7 Tiers)
├── benchmark_profiles.py    # Comparativo Multidimensional & Matriz Cruzada de Perfis
├── analyze_causality.py     # Análise Causal, Explainable AI (Árvores, RF) & SHAP
├── analyze_markov.py        # Resolvedor Analítico de Cadeias de Markov Absorventes
├── analyze_game_theory.py   # Teoria dos Jogos, Equilíbrio de Nash & Fictitious Play
├── stress_test_economy.py   # Teste de Estresse Econômico & Choques de Liquidez
└── analyze_information.py   # Teoria da Informação & Entropia de Shannon (Fluxo Dedutivo)
```

---

## 1. `run_monte_carlo.py` — Simulação Massiva & Telemetria
Executa centenas de milhares de partidas paralelas com telemetria detalhada de cada fase do jogo:
- **Equilíbrio Global & Placar:** Distribuição dos 8 placares possíveis (de 4x0 a 0x4), taxa de vitórias e índice de clímax na 7ª rodada.
- **Funil dos 7 Tiers:** Taxa de aprovação, índice de infiltração de estagiários e causa predominante de reprovação (Falta de Insumo vs Falta de Valor vs Ativos Tóxicos).
- **Governança & Política da Mesa:** Média de vetos por rodada, frequência de comitês forçados (3 vetos) e ativação da regra de expansão da R5.
- **Economia & Dedução Social:** Queima de tokens de rendimento, tamanho médio das mãos ao final do jogo, taxa de *lockout* e acurácia bayesiana dos banqueiros.

### Execução direta:
```bash
python simulations/run_monte_carlo.py --games 100000 --export visualizer/data/simulation_summary.json
```

---

## 2. `benchmark_profiles.py` — Matriz de Confronto entre IAs
Avalia o desempenho de cada arquétipo de jogador sob condições controladas:
- **Banqueiros:** `BALANCED`, `CONSERVATIVE`, `PRAGMATIC`, `STRATEGIST`.
- **Estagiários:** `A_AGGRESSIVE`, `B_SLEEPER`, `C_HEDGE`, `D_OPPORTUNIST`, `E_TECHNICIAN`.
- Produz a **Matriz Cruzada $4 \times 5$** com a probabilidade de vitória de cada matchup específico.

### Execução direta:
```bash
python simulations/benchmark_profiles.py --games 5000 --matrix-sample 1000
```

---

## 3. `analyze_causality.py` — Inferência Causal & Machine Learning
Supera a visão estática de probabilidade ao extrair as relações de causa e efeito ocultas nas dinâmicas de jogo:
- **Árvores de Decisão Rasas:** Extração de regras *SE-ENTÃO* que levam a 99.9% de vitória ou 100% de derrota.
- **Random Forest & Regressão Logística:** Ranking de importância com cálculo de *Odds Ratios* padronizados.
- **Valores SHAP (`TreeExplainer`):** Atribuição marginal do impacto e direção causal de cada variável.
- **Tipping Points:** Fronteiras críticas de infiltrações toleradas, saturação de queima de tokens e impacto comparado (ex: Tier 1 vs Tier 3).

### Execução direta:
```bash
python simulations/analyze_causality.py --games 20000 --export visualizer/data/causal_analysis_summary.json
```

---

## 4. `analyze_markov.py` — Resolvedor Analítico de Cadeias de Markov
Modela as 7 rodadas e pontuações $(b, i)$ como uma **Cadeia de Markov Absorvente finita**, calculando valores exatos sem ruído amostral:
- **Matriz Fundamental $N = (I - Q)^{-1}$:** Tempo de permanência e duração esperada até o encerramento do jogo.
- **Probabilidades Analíticas de Absorção ($B = N \cdot R$):** Distribuição exata dos 8 placares possíveis e probabilidade analítica de vitória global.
- **Matriz de Viradas (*Comeback Probabilities*):** Probabilidade matemática exata de um lado vencer partindo de qualquer déficit ($0 \times 1, 0 \times 2, 0 \times 3, 1 \times 2, 1 \times 3$, etc.).
- **Gradientes de Sensibilidade de Game Design ($\frac{\partial P(Win)}{\partial p_t}$):** Elasticidade marginal de cada um dos 7 Tiers de contrato no resultado global.

### Execução direta:
```bash
# Modo calibrado por telemetria
python simulations/analyze_markov.py --calibrate 10000 --export visualizer/data/markov_chain_summary.json

# Modo puramente analítico nominal (execução instantânea)
python simulations/analyze_markov.py --calibrate 0
```

---

## 5. `analyze_game_theory.py` — Teoria dos Jogos & Equilíbrio de Nash
Modela a tensão estratégica entre **Banqueiros (Auditores)** e **Estagiários (Sabotadores)** como jogos não-cooperativos em forma normal:
- **Matrizes de Payoff Markovianas:** Payoffs de cada ação $(A_k, S_j)$ derivados analiticamente do ganho/perda de probabilidade global $\Delta V_B$ de cada rodada.
- **Estratégias Mistas em Equilíbrio de Nash:** Calcula as probabilidades ideais $p^*$ de sabotagem/camuflagem e $q^*$ de veto/aprovação via programação linear / Minimax.
- **Frequência Crítica de Blefe na Abertura:** Determina exatamente a taxa em que o Estagiário deve sabotar no Tier 1 (19.4%) para manter o Banco indiferente entre vetar ou aprovar.
- **Dinâmica de Aprendizagem de Fictitious Play:** Simula a convergência da melhor resposta adaptativa em 1.200 iterações.

### Execução direta:
```bash
python simulations/analyze_game_theory.py --export visualizer/data/game_theory_summary.json
```

---

## 6. `stress_test_economy.py` — Teste de Estresse Econômico & Choques de Liquidez
Avalia a resiliência atuarial do jogo simulando **cenários extremos de ruptura e crise de liquidez**:
- **Cenário de Seca Severa de Commodity:** Redução de 75% na oferta de Titânio e Safiras no baralho (mede o impacto da escassez de matérias-primas críticas).
- **Cenário de Contágio de Ativos Tóxicos:** Triplica a densidade de toxinas no baralho para 9 cartas.
- **Cenário de Falência de Tokens (Credit Crunch):** Proibição total de queima de tokens de rendimento (avalia a viabilidade dos Tiers 4 e 5 apenas com cartas brutas).
- **Congelamento do Mercado de Balcão (OTC Freeze):** Desativação do balcão aberto para mensurar o **Prêmio de Liquidez (+3.7 p.p.)** proporcionado pela vitrine pública de compras.
- **Crise Sistêmica Combinada:** Seca somada a zero tokens para testar a resiliência no pior caso possível.

### Execução direta:
```bash
python simulations/stress_test_economy.py --games 2000 --export visualizer/data/economic_stress_summary.json
```

---

## 7. `analyze_information.py` — Teoria da Informação & Entropia de Shannon
Mede o **vazamento de informação e a taxa de dedução da mesa**, quantificando como a incerteza dos Banqueiros decai ao longo das 7 rodadas:
- **Espaço Amostral de Hipóteses:** $\Omega = \binom{4}{2} = 6$ pares de estagiários possíveis. Entropia inicial máxima: $H_0 = \log_2(6) \approx 2.585$ bits.
- **Entropia de Shannon ($H(S)$):** Rastreia $H(S) = -\sum_{h} P(h) \log_2 P(h)$ rodada a rodada com atualização bayesiana rigorosa a cada voto e comitê.
- **Ganho de Informação ($IG$ / Divergência KL):** Quantifica o impacto revelador de cada ação (reprovação por ativo tóxico vs falta de insumo vs votos de veto).
- **Eficiência de Camuflagem dos Arquétipos:** Avalia quais perfis de estagiário (`B_SLEEPER`, `C_HEDGE`, `D_OPPORTUNIST`, etc.) conseguem manter a entropia mais alta na mesa (maior ambiguidade até a 7ª rodada).
- **Taxa de Eliminação de Mundos Possíveis:** Quantos cenários de suspeita restam viáveis em média a cada rodada.

### Execução direta:
```bash
python simulations/analyze_information.py --games 3000 --export visualizer/data/information_entropy_summary.json
```

---

## 🚀 Como Executar via CLI Unificado (`run.py`)

Todos os motores podem ser disparados a partir da raiz:
```bash
# Executar simulação Monte Carlo massiva
python run.py --sim 100000

# Executar benchmark comparativo
python run.py --benchmark

# Executar análise causal completa
python run.py --causal --sim 20000

# Executar resolvedor analítico de Markov
python run.py --markov

# Executar motor de Teoria dos Jogos & Nash
python run.py --nash

# Executar teste de estresse econômico
python run.py --stress

# Executar análise de teoria da informação & entropia
python run.py --entropy --sim 3000

# Executar tudo em sequência e atualizar o visualizador HTML
python run.py --all
```
