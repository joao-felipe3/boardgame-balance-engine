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

* **Apenas Gerar Traces e Atualizar Visualizador HTML:**
  ```bash
  python run.py --dashboard
  ```

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
│       └── tracer.py        # Serializador de traces para o dashboard
│
├── simulations/
│   ├── run_monte_carlo.py   # Simulação estatística massiva
│   ├── benchmark_profiles.py # Comparador de performance de IA
│   └── analyze_causality.py # Motor de inferência causal (Árvores, RF, SHAP)
│
├── visualizer/
│   ├── create_dashboard.py  # Renderizador do visualizador interativo
│   ├── match_visualizer.html # Dashboard visual standalone
│   └── data/
│       └── game_traces.json # Dados gravados das partidas
│
├── docs/
│   └── manual_regras_v14.md # Manual de regras oficial consolidado
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
└── run.py                   # Ponto de entrada CLI
```

