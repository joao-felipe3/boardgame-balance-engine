# -*- coding: utf-8 -*-
"""
Motor Analítico de Cadeias de Markov Absorventes - BTG Madagascar v14.0
=======================================================================
Modela a dinâmica estocástica do jogo como uma Cadeia de Markov Absorvente finita,
eliminando ruídos amostrais e calculando valores analíticos exatos para:

1. Probabilidades Analíticas de Vitória Global e Distribuição de Placares Finais.
2. Matriz Fundamental de Kemeny & Snell: N = (I - Q)^(-1).
3. Probabilidades Exatas de Virada (Comeback Probabilities a partir de qualquer déficit).
4. Duração Esperada e Contagem de Rodadas Remanescentes a partir de cada estado.
5. Gradientes de Sensibilidade de Game Design (Elasticidade de Vitória por Tier).

Uso CLI:
  python simulations/analyze_markov.py --calibrate 10000 --export visualizer/data/markov_chain_summary.json
"""

import os
import sys
import argparse
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from btg.constants import Role
from simulations.run_monte_carlo import run_monte_carlo


# Definição dos 16 estados transitórios (b, i) onde 0 <= b <= 3 e 0 <= i <= 3
# b: pontos dos banqueiros | i: pontos dos estagiários | rodada = b + i + 1
TRANSIENT_STATES = [(b, i) for b in range(4) for i in range(4)]
STATE_TO_IDX = {s: idx for idx, s in enumerate(TRANSIENT_STATES)}

# Definição dos 8 estados absorventes (placares finais)
# 4 vitórias para Banqueiros (4x0, 4x1, 4x2, 4x3)
# 4 vitórias para Estagiários (0x4, 1x4, 2x4, 3x4)
ABSORBING_BANKER = [f"4 x {i}" for i in range(4)]
ABSORBING_INTERN = [f"{b} x 4" for b in range(4)]
ALL_ABSORBING = ABSORBING_BANKER + ABSORBING_INTERN
ABSORBING_TO_IDX = {s: idx for idx, s in enumerate(ALL_ABSORBING)}


class BTGMarkovChain:
    """Resolvedor Analítico de Cadeia de Markov Absorvente para o BTG Madagascar."""

    def __init__(self, transition_probs: Optional[Dict[Tuple[int, int], float]] = None):
        """
        Inicializa a cadeia.
        transition_probs: Dict mapeando (b, i) -> probabilidade do Banco vencer a rodada t = b + i + 1.
        Se None, utiliza as taxas médias históricas de aprovação observadas por Tier.
        """
        if transition_probs is None:
            # Taxas nominais empíricas médias de aprovação por Tier (1 a 7)
            # Tier 1: ~86%, Tier 2: ~71%, Tier 3: ~46%, Tier 4: ~52%, Tier 5: ~57%, Tier 6: ~38%, Tier 7: ~10%
            nominal_tier_wr = {
                1: 0.855,
                2: 0.710,
                3: 0.460,
                4: 0.525,
                5: 0.565,
                6: 0.380,
                7: 0.100
            }
            transition_probs = {}
            for b, i in TRANSIENT_STATES:
                tier = b + i + 1
                transition_probs[(b, i)] = nominal_tier_wr.get(tier, 0.50)

        self.transition_probs = transition_probs
        self.n_transient = len(TRANSIENT_STATES)      # 16
        self.n_absorbing = len(ALL_ABSORBING)          # 8

        # Construção das Matrizes Q (transiente -> transiente) e R (transiente -> absorvente)
        self.Q = np.zeros((self.n_transient, self.n_transient), dtype=float)
        self.R = np.zeros((self.n_transient, self.n_absorbing), dtype=float)

        self._build_matrices()
        self._solve_chain()

    def _build_matrices(self):
        """Constrói as submatrizes Q e R da forma canônica de Markov."""
        for (b, i), u in STATE_TO_IDX.items():
            p_banker = self.transition_probs.get((b, i), 0.50)
            p_intern = 1.0 - p_banker

            # Se Banqueiros vencem a rodada:
            next_b = b + 1
            if next_b == 4:
                # Transição para estado absorvente de vitória do Banco: "4 x i"
                target_abs = f"4 x {i}"
                v = ABSORBING_TO_IDX[target_abs]
                self.R[u, v] += p_banker
            else:
                # Transição para estado transitório: (b+1, i)
                v = STATE_TO_IDX[(next_b, i)]
                self.Q[u, v] += p_banker

            # Se Estagiários vencem a rodada:
            next_i = i + 1
            if next_i == 4:
                # Transição para estado absorvente de vitória dos Estagiários: "b x 4"
                target_abs = f"{b} x 4"
                v = ABSORBING_TO_IDX[target_abs]
                self.R[u, v] += p_intern
            else:
                # Transição para estado transitório: (b, i+1)
                v = STATE_TO_IDX[(b, next_i)]
                self.Q[u, v] += p_intern

    def _solve_chain(self):
        """Resolve analiticamente a cadeia: Matriz Fundamental N, Absorção B e Duração E[T]."""
        I = np.eye(self.n_transient)
        # N = (I - Q)^(-1)
        self.N = np.linalg.inv(I - self.Q)

        # B = N * R (Probabilidades de atingir cada um dos 8 estados absorventes)
        self.B = np.matmul(self.N, self.R)

        # Tempo esperado de rodadas até a absorção partindo de cada estado: t = N * 1
        self.expected_steps = np.sum(self.N, axis=1)

    def get_win_probabilities(self, state: Tuple[int, int]) -> Dict[str, float]:
        """Retorna a probabilidade analítica de vitória a partir de um estado (b, i)."""
        u = STATE_TO_IDX[state]
        b_probs = self.B[u, :4]  # 4 x 0, 4 x 1, 4 x 2, 4 x 3
        i_probs = self.B[u, 4:]  # 0 x 4, 1 x 4, 2 x 4, 3 x 4

        p_banker_win = float(np.sum(b_probs))
        p_intern_win = float(np.sum(i_probs))

        return {
            'banker_win': p_banker_win,
            'intern_win': p_intern_win,
            'scores': {ALL_ABSORBING[idx]: float(self.B[u, idx]) for idx in range(self.n_absorbing)},
            'expected_remaining_rounds': float(self.expected_steps[u])
        }

    def compute_sensitivity(self, delta: float = 0.01) -> Dict[int, float]:
        """
        Calcula o gradiente analítico dP(Banker Win)/dp_t para cada Tier t in [1..7].
        Mede o impacto marginal de balanceamento de cada contrato no resultado global.
        """
        base_win = self.get_win_probabilities((0, 0))['banker_win']
        gradients = {}

        for tier in range(1, 8):
            # Cria cópia perturbando apenas os estados correspondentes ao Tier t
            perturbed_probs = dict(self.transition_probs)
            for (b, i) in TRANSIENT_STATES:
                if b + i + 1 == tier:
                    perturbed_probs[(b, i)] = min(1.0, perturbed_probs[(b, i)] + delta)

            alt_chain = BTGMarkovChain(transition_probs=perturbed_probs)
            alt_win = alt_chain.get_win_probabilities((0, 0))['banker_win']
            gradients[tier] = (alt_win - base_win) / delta

        return gradients


def calibrate_markov_from_telemetry(n_games: int = 15000, num_workers: Optional[int] = None) -> Dict[Tuple[int, int], float]:
    """
    Simula n_games e extrai as probabilidades condicionais reais de transição P(Sucesso | Estado b, i).
    Captura os efeitos não-estáticos de dedução social acumulada e exaustão de cartas.
    """
    print(f"\n[Markov] Coletando telemetria empírica de {n_games:,} partidas para calibração estocástica...")
    df = run_monte_carlo(n_games=n_games, num_workers=num_workers)

    # Dicionário acumulador: {(b, i): [sucessos, total]}
    state_counts = {s: [0, 0] for s in TRANSIENT_STATES}

    # Para cada partida, reconstrói a trajetória de estados (b, i)
    # Como a telemetria do Monte Carlo registra tier_telemetry e placares finais:
    for _, row in df.iterrows():
        tt = row.get('tier_telemetry', {})
        curr_b, curr_i = 0, 0
        for tier in range(1, 8):
            if tier not in tt or curr_b == 4 or curr_i == 4:
                break
            t_data = tt[tier]
            if not t_data.get('played', False):
                break

            state = (curr_b, curr_i)
            if state in state_counts:
                is_success = t_data.get('success', False)
                state_counts[state][1] += 1
                if is_success:
                    state_counts[state][0] += 1
                    curr_b += 1
                else:
                    curr_i += 1

    # Calcula probabilidades empíricas condicionais
    transition_probs = {}
    default_tier_rates = {1: 0.85, 2: 0.70, 3: 0.46, 4: 0.52, 5: 0.56, 6: 0.38, 7: 0.10}

    for state, (succ, tot) in state_counts.items():
        tier = state[0] + state[1] + 1
        if tot >= 30:
            transition_probs[state] = succ / tot
        else:
            # Fallback para taxa padrão do Tier caso o estado seja raramente visitado
            transition_probs[state] = default_tier_rates.get(tier, 0.50)

    return transition_probs


def run_markov_analysis(
    calibrate_games: int = 15000,
    num_workers: Optional[int] = None,
    export_json: Optional[str] = None
) -> Dict:
    """Executa a análise analítica completa de Markov e exibe os relatórios formatados."""
    print("=" * 86)
    print("       RESOLVEDOR ANALÍTICO DE CADEIAS DE MARKOV - BTG MADAGASCAR v14.0")
    print("       Mapeamento Exato de Estados, Probabilidades de Virada e Absorção")
    print("=" * 86)

    # 1. Calibração ou Inicialização
    if calibrate_games > 0:
        trans_probs = calibrate_markov_from_telemetry(n_games=calibrate_games, num_workers=num_workers)
    else:
        trans_probs = None

    chain = BTGMarkovChain(transition_probs=trans_probs)

    # 2. Absorção a partir do Estado Inicial (0, 0)
    initial_sol = chain.get_win_probabilities((0, 0))
    b_wr = initial_sol['banker_win'] * 100
    i_wr = initial_sol['intern_win'] * 100
    exp_rounds = initial_sol['expected_remaining_rounds']

    print("\n" + "=" * 86)
    print(" 1. EQUILÍBRIO GLOBAL ANALÍTICO (ESTADO INICIAL 0 x 0)")
    print("=" * 86)
    print(f"  * Probabilidade Exata de Vitória dos Banqueiros  : {b_wr:6.2f}%")
    print(f"  * Probabilidade Exata de Vitória dos Estagiários : {i_wr:6.2f}%")
    print(f"  * Duração Esperada da Partida                    : {exp_rounds:6.2f} rodadas")
    print("\n  DISTRIBUIÇÃO ANALÍTICA DOS 8 PLACARES FINAIS:")
    print("  " + "-" * 78)
    for score in ALL_ABSORBING:
        prob = initial_sol['scores'][score] * 100
        faction = "🛡️ Banqueiros" if "4 x" in score else "🕵️ Estagiários"
        print(f"    Placar {score:<6} | {prob:6.2f}% | Vitória {faction}")

    # 3. Matriz de Probabilidade de Virada (Comeback Probabilities)
    print("\n" + "=" * 86)
    print(" 2. MATRIZ ANALÍTICA DE VIRADAS (COMEBACK PROBABILITIES)")
    print("=" * 86)
    print("Mostra a probabilidade matemática exata de vencer o jogo a partir de qualquer déficit ou empate:")
    print("-" * 86)
    print(f"{'Estado Atual':<16} | {'Rodada':<8} | {'Prob. Vitória Banco':<22} | {'Prob. Vitória Estag':<22} | {'Cenário':<20}")
    print("-" * 86)

    test_states = [
        # Empates
        ((0, 0), "Abertura Neutra"),
        ((1, 1), "Empate Inicial"),
        ((2, 2), "Meio-Jogo Crítico"),
        ((3, 3), "Clímax / Match Point"),
        # Déficit dos Banqueiros
        ((0, 1), "Banco atrás por 1"),
        ((0, 2), "Banco atrás por 2 (Alerta)"),
        ((0, 3), "Banco atrás por 3 (À beira do abismo)"),
        ((1, 2), "Banco atrás por 1 no R4"),
        ((1, 3), "Banco atrás por 2 no R5"),
        ((2, 3), "Banco atrás por 1 no R6"),
        # Déficit dos Estagiários
        ((1, 0), "Estag atrás por 1"),
        ((2, 0), "Estag atrás por 2 (Alerta)"),
        ((3, 0), "Estag atrás por 3 (À beira do sweep)"),
        ((2, 1), "Estag atrás por 1 no R4"),
        ((3, 1), "Estag atrás por 2 no R5"),
        ((3, 2), "Estag atrás por 1 no R6"),
    ]

    comebacks_summary = {}

    for state, desc in test_states:
        sol = chain.get_win_probabilities(state)
        b_p = sol['banker_win'] * 100
        i_p = sol['intern_win'] * 100
        tier = state[0] + state[1] + 1
        state_str = f"{state[0]} x {state[1]}"
        print(f"{state_str:<16} | Tier {tier:<3} | {b_p:6.2f}%{' 🟢' if b_p >= 50 else ' 🔴':<14} | {i_p:6.2f}%{' 🟢' if i_p >= 50 else ' 🔴':<14} | {desc:<20}")
        comebacks_summary[state_str] = {
            'state': state,
            'tier': tier,
            'description': desc,
            'p_banker_win': b_p,
            'p_intern_win': i_p,
            'expected_rounds_left': sol['expected_remaining_rounds']
        }

    # 4. Gradientes de Sensibilidade de Game Design
    print("\n" + "=" * 86)
    print(" 3. GRADIENTES DE SENSIBILIDADE DE GAME DESIGN (ELASTICIDADE POR TIER)")
    print("=" * 86)
    print("Indica quantos pontos percentuais (p.p.) a taxa global do Banco varia para cada +1.0% de aprovação no Tier:")
    print("-" * 86)
    gradients = chain.compute_sensitivity(delta=0.01)
    sorted_grad = sorted(gradients.items(), key=lambda x: -x[1])

    for tier, grad in sorted_grad:
        weight_bar = "█" * int(grad * 15)
        print(f"  • Tier {tier:<2} : Elasticidade = {grad:+.3f} p.p.  {weight_bar} (Impacto {'MUITO ALTO' if grad > 0.4 else ('ALTO' if grad > 0.25 else 'MODERADO')})")

    most_critical_tier = sorted_grad[0][0]
    print(f"\n👉 Insight Causal Markoviano: O **Tier {most_critical_tier}** é o contrato de maior alavancagem sistêmica do jogo.")

    # 5. Exportação JSON
    payload = {
        'initial_equilibrium': {
            'banker_win_prob': float(b_wr),
            'intern_win_prob': float(i_wr),
            'expected_duration': float(exp_rounds),
            'final_scores': {k: float(v * 100) for k, v in initial_sol['scores'].items()}
        },
        'comeback_probabilities': comebacks_summary,
        'tier_sensitivities': {f"tier_{t}": float(g) for t, g in gradients.items()},
        'most_critical_tier': most_critical_tier,
        'state_map': {
            f"{b}_{i}": {
                'p_banker': float(chain.get_win_probabilities((b, i))['banker_win'] * 100),
                'p_intern': float(chain.get_win_probabilities((b, i))['intern_win'] * 100),
                'expected_rounds_left': float(chain.expected_steps[STATE_TO_IDX[(b, i)]])
            } for b, i in TRANSIENT_STATES
        }
    }

    if export_json:
        with open(export_json, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Relatório analítico de Markov exportado com sucesso em: {export_json}")

    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Resolvedor Analítico de Cadeias de Markov - BTG Madagascar v14.0")
    parser.add_argument("--calibrate", "-c", type=int, default=10000, help="Partidas para calibração empírica (padrão: 10.000; 0 para nominal)")
    parser.add_argument("--workers", "-w", type=int, default=None, help="Workers paralelos para simulação de calibração")
    parser.add_argument("--export", "-e", type=str, default="visualizer/data/markov_chain_summary.json", help="Arquivo JSON de destino")
    args = parser.parse_args()

    run_markov_analysis(
        calibrate_games=args.calibrate,
        num_workers=args.workers,
        export_json=args.export
    )
