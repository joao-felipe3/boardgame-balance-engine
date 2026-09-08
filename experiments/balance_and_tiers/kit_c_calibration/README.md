# 🧪 Calibração e Experimentos do Kit C (Arquivo Histórico)

Este diretório preserva os scripts e rotinas de calibração criados durante a fase de validação e balanceamento do catálogo de contratos **Kit C** antes da consolidação no manual e catálogo oficial da v14.0.

---

## 📁 Arquivos Arquivados

* `run_kit_c_monte_carlo.py`: Implementação monolítica da simulação Monte Carlo calibrada sobre os contratos do Kit C.
* `sim_kit_c_full.py`: Simulação exploratória e validação de rodadas para o Kit C.
* `tune_kit_c.py`: Script de busca e ajuste de parâmetros de targets e custos dos contratos.
* `analyze_kit_c.py`: Consolidador estatístico e gerador de resumos da calibração do Kit C.
* `run_comparison.py`: Comparador empírico entre configurações de regras e variantes do Kit C.
* `inspect_deduction.py`: Experimento de avaliação da precisão bayesiana no ambiente do Kit C.

> **Nota:** Para simulações oficiais do jogo atual, utilize os módulos em `simulations/` ou o ponto de entrada principal `run.py`.
