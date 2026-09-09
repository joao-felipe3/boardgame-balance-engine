# 🏝️ BTG Madagascar: Jogo de Dedução Social & Gestão de Commodities

> Um jogo de estratégia corporativa, blefe e dedução social para 5 jogadores ambientado em operações financeiras e de commodities em Madagascar.

---

## 🚀 Como Executar

### 1. Pré-requisitos
Instale as dependências com:
```bash
pip install -r requirements.txt
```

### 2. Comandos Principais (`run.py`)

* **Simulação Padrão + Atualização do Dashboard:**
  ```bash
  python run.py
  ```

* **Executar Simulação Massiva (ex: 100.000 partidas com Telemetria Completa):**
  ```bash
  python run.py --sim 100000 --export visualizer/data/simulation_100k_summary.json
  ```
  *Opções adicionais:*
  - `--workers 4`: define a quantidade de processos paralelos (padrão: total de núcleos da CPU).
  - `--export <arquivo.json>`: exporta o relatório consolidado com todas as 6 seções de telemetria.

* **Executar Benchmark Comparativo de Perfis:**
  ```bash
  python run.py --benchmark
  ```

* **Executar Análise Causal (Árvores de Decisão, Random Forest, SHAP & Tipping Points):**
  ```bash
  python run.py --causal --sim 20000 --export visualizer/data/causal_analysis_summary.json
  ```
  *O que este módulo entrega:*
  - **Árvores de Decisão Rasas (Explainable AI):** Extração de regras explícitas *SE-ENTÃO* que definem os caminhos matemáticos de vitória/derrota.
  - **Importância de Features & Odds Ratios:** Ranqueamento de impacto relativo e chances multiplicativas calculadas via regressão logística padronizada.
  - **Valores SHAP (TreeExplainer):** Atribuição marginal de impacto e direção causal para cada decisão ou evento da partida.
  - **Tipping Points Não-Óbvios:** Análise do impacto diferencial entre Tiers (ex: Tier 1 vs Tier 3), saturação de queima de tokens de rendimento e limiar crítico de infiltrações toleradas pela mesa.

* **Executar Resolvedor Analítico de Cadeias de Markov (Probabilidades Exatas & Viradas):**
  ```bash
  python run.py --markov
  ```
  *O que este módulo entrega:*
  - **Solução Estocástica Exata:** Matriz fundamental $N = (I - Q)^{-1}$ e probabilidades exatas de absorção eliminando todo o ruído amostral.
  - **Matriz de Viradas (Comeback Probabilities):** Probabilidade matemática exata de um lado vencer partindo de qualquer déficit ($0 \times 1, 0 \times 2, 0 \times 3, 1 \times 2$, etc.).
  - **Gradientes de Sensibilidade:** Elasticidade analítica de vitória para cada um dos 7 Tiers de contratos.

* **Executar Motor de Teoria dos Jogos & Equilíbrio de Nash (Blefe Ótimo & Minimax):**
  ```bash
  python run.py --nash
  ```
  *O que este módulo entrega:*
  - **Estratégias Mistas em Equilíbrio de Nash:** Frequência ótima de sabotagem ($p^*$) e veto ($q^*$) calculadas via Programação Linear.
  - **Taxa Ótima de Blefe na Abertura:** Determinação de que os Estagiários devem sabotar no Tier 1 em exatamente 19.4% das vezes para manter os Banqueiros indiferentes.
  - **Dinâmica de Aprendizagem Competitiva:** Convergência empírica via *Fictitious Play* em 1.200 rodadas adaptativas.

* **Executar Testes de Estresse Econômico & Choques de Liquidez (Stress Testing & Ruin):**
  ```bash
  python run.py --stress
  ```
  *O que este módulo entrega:*
  - **Simulação de Rupturas e Choques:** Seca severa de matérias-primas (75%), contágio extremo de ativos tóxicos (3x), falência de tokens de rendimento e congelamento do balcão aberto.
  - **Prêmio de Liquidez do Mercado de Balcão:** Demonstração empírica de que a vitrine pública de compras protege a taxa de vitória dos honestos em +3.7 p.p.
  - **Métricas Atuariais de Risco:** Probabilidade de ruína do cofre e Value at Risk (VaR 95% e VaR 99%) do tamanho das mãos.

* **Executar Teoria da Informação & Entropia de Shannon (Fluxo Dedutivo da Mesa):**
  ```bash
  python run.py --entropy --sim 3000
  ```
  *O que este módulo entrega:*
  - **Incerteza Inicial da Mesa:** Espaço de 6 hipóteses de traidores $\binom{4}{2} = 6$ com entropia inicial teórica $H_0 = \log_2(6) \approx 2.585$ bits.
  - **Curva de Decaimento da Entropia:** Acompanha o decaimento gradual da incerteza rodada a rodada (R0: 2.585 bits $\to$ R7: ~1.75 bits), comprovando alta tensão preservada até o final.
  - **Ganho de Informação ($IG$) por Evento:** Mensuração em bits de quanto cada tipo de reprovação e voto revela sobre a lealdade dos membros do comitê.
  - **Ranking de Eficiência de Camuflagem:** Identifica quais arquétipos de estagiário (`B_SLEEPER`, `C_HEDGE`, etc.) melhor ocultam sua identidade da dedução bayesiana da mesa.

* **Executar Avaliação Atuarial da DLC de Diretrizes & Poderes Corporativos:**
  ```bash
  python run.py --dlc --sim 2000
  ```
  *O que este módulo entrega:*
  - **Catálogo de 17 Diretrizes Regulatórias:** Compliance, Economia, Governança e Estrutura de Comitê 100% analógicas e universais.
  - **Comparativo de 4 Regimes de Ativação:** Sempre Ativo (R1-R7) vs Dado 1d6 (50%) vs Mid-Game (R3-R5) vs Catch-Up pós-derrota.
  - **Impacto Matemático no Balanceamento:** Demonstração de que a DLC com Dado 1d6 consolida o equilíbrio nominal em **48.97% Banco vs 51.03% Estagiários** em 30.000 partidas.

* **Apenas Gerar Traces e Atualizar Visualizador HTML:**
  ```bash
  python run.py --dashboard
  ```

---

## 🏛️ Evolução do Jogo, Versões & Experimentos

O **BTG Madagascar** é fruto de um extenso processo de engenharia de equilíbrio e game design iterativo apoiado em mais de **200.000 partidas simuladas** e cinco motores analíticos avançados:

| Versão / Ciclo | Foco Principal | Inovações Introduzidas | Diagnóstico & Impacto Matemático |
| :--- | :--- | :--- | :--- |
| **v1.0 – v5.0**<br>*(Protótipos Iniciais)* | Dinâmica de Dedução Clássica | Regras estilo *The Resistance*, votação aberta e cartas genéricas de pontuação. | ❌ **Desequilíbrio Grave:** Estagiários venciam >72% dos jogos. Falta de plausibilidade negável material. |
| **v6.0 – v9.0**<br>*(Economia & Balcão)* | Gestão de Commodities | Introdução dos 4 recursos (Cobalto +1, Baunilha +2, Titânio +3, Safira +4), Mercado de Balcão Aberto e Ativos Tóxicos (-4). | 📈 **Prêmio de Liquidez (+4.55 p.p.):** Compras públicas no balcão provaram proteger os honestos contra volatilidade e criar deniability legítima. |
| **v10.0 – v12.0**<br>*(Mão & Banco)* | Depleção e Incentivos | Kit C assimétrico inicial, Dividendo Completo de Banco (+1 carta e +1 token para quem descansa) e Despertar do Sleeper na R2. | ⚖️ **Ruptura de Sweeps:** Sweeps 4x0 do Banco caíram de 31.3% para ~21%, tornando o jogo disputado até o fim. |
| **v13.0**<br>*(Calibração dos Tiers)* | Balanceamento da Curva | Aperto de liquidez no Tier 2 (meta 5 pts), expansão dinâmica da R5 (3→4 membros sob falha) e resgate do clímax na R7. | 🔥 **Tensão Dramática:** Taxa de clímax na 7ª rodada (3x3) subiu para ~30% e vitórias épicas no Tier 7 foram resgatadas. |
| **v14.0**<br>*(IA & Dedução)* | Agentes Heterogêneos & Ciência | 4 perfis de Banqueiro, 5 perfis de Estagiário (calibração do Técnico `E_TECHNICIAN`), inferência causal (Árvores/SHAP), Markov e Nash. | 🎯 **Padrão Ouro Calibrado:** 46.2% vs 53.8% sem DLC. Mapeamento matemático das regras causais e pontos de inflexão. |
| **v14.1 / DLC**<br>*(Poderes Físicos)* | Variabilidade & Regulação | Baralho de 17 cartas de Diretrizes físicas universais (sem travas de tier) e ativação via Dado 1d6 ($\ge 4$). | ⭐ **Equilíbrio 48.97% / 51.03%:** Média de 2.87 cartas/jogo, eliminando a mão travada, o pânico do 3º veto e a paranoia fratricida. |

---

## 📁 Estrutura do Projeto

```text
BTG/
├── src/
│   └── btg/                 # Motor modular oficial do jogo
│       ├── constants.py     # Enums, valores das cartas e catálogo dos 7 Tiers
│       ├── deck.py          # Gestão do baralho e Mercado de Balcão Aberto
│       ├── player.py        # Jogador, carteira, tokens e dedução bayesiana
│       ├── engine.py        # Motor das rodadas, comitês, votações e avaliação
│       ├── events.py        # Baralho de 17 Diretrizes & Poderes da DLC
│       └── tracer.py        # Serializador de traces para o dashboard
│
├── simulations/
│   ├── run_monte_carlo.py     # Simulação estatística massiva (suporta --dlc)
│   ├── benchmark_profiles.py  # Comparador de performance de IA (4x5)
│   ├── analyze_causality.py   # Motor de inferência causal (Árvores, RF, SHAP)
│   ├── analyze_markov.py      # Resolvedor analítico de Cadeias de Markov Absorventes
│   ├── analyze_game_theory.py # Teoria dos Jogos, Equilíbrio de Nash & Fictitious Play
│   ├── stress_test_economy.py # Teste de Estresse Econômico & Choques de Liquidez
│   ├── analyze_information.py # Teoria da Informação & Entropia de Shannon
│   └── analyze_dlc_events.py  # Avaliação Atuarial da DLC (4 Regimes)
│
├── visualizer/
│   ├── create_dashboard.py  # Renderizador do visualizador interativo
│   ├── match_visualizer.html # Dashboard visual standalone
│   └── data/
│       ├── game_traces.json # Traces gravados das partidas
│       ├── causal_analysis_summary.json
│       ├── markov_chain_summary.json
│       ├── game_theory_summary.json
│       ├── economic_stress_summary.json
│       ├── information_entropy_summary.json
│       └── dlc_events_summary.json
│
├── docs/
│   └── manual_regras_v14.md # Manual de regras oficial consolidado + DLC + Changelog
│
├── experiments/             # Laboratório de pesquisa e histórico de experimentos
│   ├── README.md            # Índice e documentação das fases de pesquisa
│   ├── economy_liquidity/   # Modelos de liquidez, juros e depleção
│   ├── ai_and_sleeper/      # Calibração dos perfis de IA e do Sleeper
│   ├── governance_and_deduction/ # Votação, vetos e dedução bayesiana
│   ├── balance_and_tiers/   # Balanceamento dos 7 Tiers e tensão de clímax
│   └── legacy_prototypes/   # Protótipos monolíticos e utilitários históricos
│
├── requirements.txt         # Dependências do projeto
└── run.py                   # Ponto de entrada CLI unificado
```

