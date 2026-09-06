# 🔬 Laboratório de Experimentos & Pesquisa de Balanceamento

Este diretório preserva o histórico cronológico e temático de todos os experimentos, simulações exploratórias e protótipos desenvolvidos durante a concepção, calibração e refinamento do **BTG Madagascar**.

---

## 📁 Estrutura Temática

```text
experiments/
├── economy_liquidity/          # Modelos de liquidez, juros, depleção e rendimento de bancada
├── ai_and_sleeper/             # Calibração dos perfis de IA (Agressivo, Sleeper, Hedge)
├── governance_and_deduction/   # Votação, vetos, dedução bayesiana e pares de conflito
├── balance_and_tiers/          # Balanceamento dos 7 Tiers, tamanho de comitês e clímax
└── legacy_prototypes/          # Protótipos monolíticos e ferramentas pré-Engine v14.0
```

---

## 1. 💰 Economia & Liquidez (`economy_liquidity/`)
Pesquisas dedicadas a criar uma economia de recursos funcional sem inflação, resolvendo a escassez de cartas e criando dilemas estratégicos para os Banqueiros honestos:
* **`experiment_resource_economy.py`**: Primeiro estudo empírico sobre taxas de depleção por participação em comitês.
* **`test_liquidity_model.py`**: Modelagem da circulação de cartas na mão vs. cartas investidas nos contratos.
* **`test_yield_model.py`**: Experimento precursor do sistema de dividendos (geração de juros para quem fica fora da operação).
* **`test_hold.py`**: Avaliação de estratégias de retenção de commodities valiosas (Safira e Titânio) para rodadas finais.

---

## 2. 🤖 IA & Calibração do Sleeper (`ai_and_sleeper/`)
Ajustes nos algoritmos de blefe e sabotagem dos Estagiários infiltrados:
* **`experiment_sleeper_calibration.py`**: Calibração da probabilidade de camuflagem do Estagiário Sleeper na Rodada 1 e Rodada 2.
* **`test_sleeper_camouflaged.py`**: Investigação de partidas em que o Sleeper se comporta como banqueiro exemplar até a Rodada 4.
* **`test_sleeper_empowerment.py`**: Avaliação do impacto do Sleeper quando acumulava recursos para sabotagens devastadoras no Tier 6 e 7.
* **`test_sleeper_pair.py`**: Dinâmica de interação quando ambos os Estagiários atuam como camuflados simultaneamente.
* **`test_sleeper_supremacy.py`**: Teste de estresse para evitar que o perfil Sleeper se tornasse estritamente dominante sobre os demais.
* **`test_sleeper_trust_network.py`**: Modelagem da rede de confiança que o Sleeper constrói ao aprovar contratos iniciais.
* **`test_punish_aggressive.py`**: Mecanismos de punição e detecção rápida contra o Estagiário Agressivo (sabotador desde a R1).
* **`benchmark_profiles_final.py`**: Comparador histórico preliminar de Win Rate entre os 3 perfis.

---

## 3. 🏛️ Governança & Dedução Social (`governance_and_deduction/`)
Desenvolvimento das regras de votação na mesa diretora e das heurísticas de suspeita bayesiana:
* **`test_governance.py`**: Avaliação do limiar de vetos consecutivos e rotação do Chairman.
* **`test_natural_governance.py`**: Simulação de aprovações e vetos baseados estritamente na confiança percebida pelo jogador, sem regras forçadas.
* **`test_compliance_veto.py`**: Investigação de vetos automáticos de compliance corporativo.
* **`test_banker_solidarity.py`**: Teste de comportamento onde banqueiros confirmados votam em bloco.
* **`test_deduction_fixed.py`**: Implementação das matrizes de suspeita com decaimento pós-vitória e penalidade pós-falha.
* **`test_smart_deduction.py`**: Dedução contextual separando falhas por insumo ausente de falhas por falta de valor bruto.
* **`test_prioritize_trust.py`**: Heurística de montagem de comitê que prioriza operadores com menor média de suspeita.

---

## 4. ⚖️ Balanceamento de Tiers & Clímax (`balance_and_tiers/`)
Calibração das metas de pontuação e transição dramática do jogo ao longo das 7 rodadas:
* **`test_7_rounds.py`**: Estudo da transição de jogos de 5 rodadas para a estrutura oficial de 7 rodadas (Race to 4).
* **`test_climax_7th_round.py`** & **`test_climax_balance.py`**: Ajustes para assegurar que partidas equilibradas atinjam a 7ª rodada com alto valor dramático.
* **`test_guaranteed_climax.py`**: Análise de sensibilidade das metas para maximizar decisões no limite (4x3 e 3x4).
* **`test_master_balance.py`**: Bateria consolidada de testes de equilíbrio global da primeira geração.
* **`test_tier4_size4.py`** & **`test_tier4_target13.py`**: Experimentos de escala do Tier 4 (Refino Metalúrgico / Consórcio Agro-Industrial).
* **`test_tier5_four_players.py`**: Estudo precursor da regra de expansão condicional do Tier 5 para 4 operadores.
* **`test_tier5_tuning.py`**: Ajuste das metas de valor (10 pontos) e cotas de insumos no Tier 5.
* **`test_generics.py`**: Baterias de testes genéricos de sanidade estatística.

---

## 5. 📦 Protótipos Legados (`legacy_prototypes/`)
Versões monolíticas e utilitários que pavimentaram o caminho para a arquitetura modular atual (`src/btg/`):
* **`btg_simulation.py`**: O primeiro simulador Monte Carlo monolítico do projeto.
* **`run_experiments.py`**: O orquestrador original de baterias de testes.
* **`manual_btg_madagascar.md`**: Versão inicial (v1.0) do manual de regras, hoje formalizada em `docs/manual_regras_v14.md`.
* **`create_dashboard.py`** & **`game_traces.json`**: Primeira iteração do gerador de traces e visualização de dados.
* **`trace_game.py`**, **`trace_social_deduction.py`** & **`verify_traces.py`**: Scripts de serialização que deram origem ao módulo `src/btg/tracer.py`.
