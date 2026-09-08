# 🎲 Motores de Simulação e Análise — BTG Madagascar (v14.0)

Este diretório concentra os **três motores analíticos oficiais** do projeto, projetados para execução em alta escala com suporte a multiprocessamento e integração direta com o ponto de entrada principal (`run.py`).

---

## 📁 Estrutura dos Motores

```text
simulations/
├── run_monte_carlo.py     # Simulação Monte Carlo Massiva (Telemetria dos 7 Tiers)
├── benchmark_profiles.py  # Comparativo Multidimensional & Matriz Cruzada de Perfis
└── analyze_causality.py   # Análise Causal, Explainable AI (Árvores, RF) & SHAP
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

## 🚀 Como Executar via CLI Unificado (`run.py`)

Todos os motores podem ser disparados a partir da raiz:
```bash
# Executar simulação Monte Carlo massiva
python run.py --sim 100000

# Executar benchmark comparativo
python run.py --benchmark

# Executar análise causal completa
python run.py --causal --sim 20000

# Executar tudo em sequência e atualizar o visualizador HTML
python run.py --all
```
