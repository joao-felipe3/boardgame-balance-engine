# -*- coding: utf-8 -*-
"""
Motor de Teoria da Informação & Entropia de Shannon - BTG Madagascar v14.0
==========================================================================
Quantifica o fluxo dedutivo, a dissipação da incerteza e o vazamento de informação
na mesa de jogo medindo em bits:

1. Entropia de Shannon H(X) sobre o espaço dos 6 mundos possíveis de traição.
2. Ganho de Informação (Information Gain em bits) por evento e tipo de comitê.
3. Curva de Decaimento da Entropia ao longo das 7 rodadas.
4. Índice de Eficiência de Camuflagem por Perfil de Estagiário (bits preservados).
5. Rodada Média de Colapso Dedutivo (H < 0.20 bits).

Uso CLI:
  python simulations/analyze_information.py --games 5000 --export visualizer/data/information_entropy_summary.json
"""

import os
import sys
import time
import argparse
import json
import itertools
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import multiprocessing as mp

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from btg.constants import Role, InternProfile, BankerProfile
from btg.engine import simulate_single_match


# -----------------------------------------------------------------------------
# ESPAÇO DE MUNDOS POSSÍVEIS (HYPOTHESIS SPACE)
# -----------------------------------------------------------------------------
# Do ponto de vista de um Banqueiro (ex: Jogador 0), existem 4 outros jogadores (1, 2, 3, 4)
# entre os quais exatamente 2 são Estagiários.
# Espaço amostral: C(4, 2) = 6 mundos possíveis:
WORLDS = list(itertools.combinations([1, 2, 3, 4], 2))
# WORLDS = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
N_WORLDS = len(WORLDS)  # 6
INITIAL_SHANNON_ENTROPY = float(np.log2(N_WORLDS))  # log2(6) = 2.58496 bits


def compute_world_probabilities(suspicions_dict: Dict[int, float], banker_id: int = 0) -> np.ndarray:
    """
    Calcula a distribuição de probabilidade a posteriori P(w) sobre os 6 mundos possíveis,
    dadas as probabilidades individuais de suspeita s_j atribuídas pelo Banqueiro aos outros jogadores.
    """
    other_pids = [pid for pid in range(5) if pid != banker_id]

    likelihoods = []
    eps = 1e-6
    for w in WORLDS:
        # w é uma tupla (j, k) indicando que j e k são os traidores, e os outros dois são honestos
        prob = 1.0
        for pid in other_pids:
            s_val = np.clip(suspicions_dict.get(pid, 0.40), eps, 1.0 - eps)
            if pid in w:
                prob *= s_val
            else:
                prob *= (1.0 - s_val)
        likelihoods.append(prob)

    likelihoods = np.array(likelihoods, dtype=float)
    total_l = np.sum(likelihoods)
    if total_l <= 0:
        return np.ones(N_WORLDS) / N_WORLDS
    return likelihoods / total_l


def shannon_entropy(probs: np.ndarray) -> float:
    """Calcula a Entropia de Shannon H(X) = -sum(p * log2(p)) em bits."""
    probs = np.clip(probs, 1e-12, 1.0)
    return float(-np.sum(probs * np.log2(probs)))


def _run_single_entropy_match(args_tuple):
    seed, intern_prof_name = args_tuple

    # Simula partida registrando trace detalhado de rodadas e histórico de suspeitas
    res = simulate_single_match(
        seed,
        seed=seed,
        record_trace=True,
        banker_profile="BALANCED",
        intern_profile=intern_prof_name
    )

    rounds_data = res.get('rounds_data', [])
    players_meta = res.get('players_metadata', {})
    
    # Identifica o primeiro Banqueiro como observador de referência
    banker_ids = [p['id'] for p in players_meta if p.get('role') == Role.BANKER.value]
    obs_banker = banker_ids[0] if banker_ids else 0

    # Identifica os verdadeiros estagiários
    true_interns = set(p['id'] for p in players_meta if p.get('role') == Role.INTERN.value)

    # Rastreamento da entropia ao longo do tempo:
    # R0: Entropia inicial a priori = log2(6) = 2.585 bits
    entropy_by_round = [INITIAL_SHANNON_ENTROPY]
    leakage_events = []

    h_prev = INITIAL_SHANNON_ENTROPY

    for r_idx, r_data in enumerate(rounds_data, start=1):
        # Coleta as suspeitas do observador após a rodada
        sus_info = r_data.get('suspicions', {}).get('by_banker', {}).get(obs_banker, {})
        if not sus_info:
            # Fallback para média da mesa
            sus_info = r_data.get('suspicions', {}).get('avg', {})

        probs = compute_world_probabilities(sus_info, banker_id=obs_banker)
        h_curr = shannon_entropy(probs)
        entropy_by_round.append(h_curr)

        info_gain = max(0.0, h_prev - h_curr)
        comm = r_data.get('committee', [])
        is_success = r_data.get('is_success', False)
        interns_in_comm = sum(1 for cid in comm if cid in true_interns)

        event_type = f"Comitê {len(comm)} ({'Aprovado' if is_success else 'Sabotado'} | {interns_in_comm} Infiltrado{'s' if interns_in_comm != 1 else ''})"
        leakage_events.append({
            'round': r_idx,
            'event_type': event_type,
            'info_gain': info_gain
        })
        h_prev = h_curr

    final_entropy = entropy_by_round[-1]
    
    # Rodada em que a incerteza caiu abaixo de 0.20 bits (certeza dedutiva quase total)
    collapsed_round = None
    for r_num, h_val in enumerate(entropy_by_round):
        if h_val <= 0.20:
            collapsed_round = r_num
            break

    return {
        'profile': intern_prof_name,
        'rounds': len(rounds_data),
        'final_entropy': final_entropy,
        'entropy_by_round': entropy_by_round,
        'collapsed_round': collapsed_round,
        'leakage_events': leakage_events,
        'banker_won': 1 if res['winner'] == Role.BANKER.value else 0
    }


def run_information_analysis(
    n_games: int = 4000,
    num_workers: Optional[int] = None,
    export_json: Optional[str] = None
) -> Dict:
    """Executa a análise de Teoria da Informação e Entropia de Shannon."""
    if num_workers is None:
        num_workers = max(1, os.cpu_count() or 4)

    print("=" * 86)
    print("       MOTOR DE TEORIA DA INFORMAÇÃO & ENTROPIA DE SHANNON - BTG MADAGASCAR v14.0")
    print(f"       Espaço de Hipóteses: C(4, 2) = 6 Mundos Possíveis | Entropia Inicial H0 = {INITIAL_SHANNON_ENTROPY:.3f} bits")
    print(f"       Amostragem: {n_games:,} Partidas com Telemetria Fina | Workers: {num_workers}")
    print("=" * 86)

    t0 = time.time()

    # Divide a amostragem igualmente entre os 5 perfis de estagiários
    profiles = [p.value for p in InternProfile]
    games_per_prof = max(100, n_games // len(profiles))

    tasks = []
    seed_idx = 42000
    for p_name in profiles:
        for _ in range(games_per_prof):
            tasks.append((seed_idx, p_name))
            seed_idx += 1

    print(f"\n[Shannon] Executando simulação de rastreamento de crenças bayesianas...")
    results = []
    with mp.Pool(processes=num_workers) as pool:
        for r in pool.imap_unordered(_run_single_entropy_match, tasks, chunksize=100):
            results.append(r)

    # 1. Curva Média de Decaimento da Entropia por Rodada (R0 a R7)
    max_rounds = 7
    decay_curve = [[] for _ in range(max_rounds + 1)]
    decay_curve[0] = [INITIAL_SHANNON_ENTROPY] * len(results)

    for r in results:
        e_list = r['entropy_by_round']
        for round_idx in range(1, min(len(e_list), max_rounds + 1)):
            decay_curve[round_idx].append(e_list[round_idx])

    mean_decay = [float(np.mean(vals)) if vals else 0.0 for vals in decay_curve]

    print("\n" + "=" * 86)
    print(" 1. CURVA MÉDIA DE DISSIPAÇÃO DA INCERTEZA (ENTROPIA DE SHANNON POR RODADA)")
    print("=" * 86)
    print("Mede em BITS a velocidade com que a incerteza da mesa é eliminada pelos Banqueiros:")
    print("-" * 86)
    print(f"{'Momento / Rodada':<22} | {'Entropia H(X)':<16} | {'Incerteza Residual':<22} | {'Barra de Entropia':<20}")
    print("-" * 86)

    for r_idx, h_val in enumerate(mean_decay):
        pct_left = (h_val / INITIAL_SHANNON_ENTROPY) * 100
        bar = "█" * int(pct_left / 5)
        label = "Abertura (H0 Inicial)" if r_idx == 0 else f"Fim da Rodada {r_idx} (Tier {r_idx})"
        print(f"{label:<22} | {h_val:6.3f} bits     | {pct_left:5.1f}% de incerteza    | {bar:<20}")

    # 2. Eficiência de Camuflagem por Perfil de Estagiário
    print("\n" + "=" * 86)
    print(" 2. ÍNDICE DE EFICIÊNCIA DE CAMUFLAGEM POR PERFIL DE ESTAGIÁRIO")
    print("=" * 86)
    print("Mede quantos bits de incerteza cada perfil consegue PRESERVAR na mesa até o fim do jogo:")
    print("-" * 86)
    print(f"{'Perfil do Estagiário':<38} | {'Entropia Final':<16} | {'Bits Retidos':<16} | {'Taxa de Desmascaramento':<20}")
    print("-" * 86)

    by_profile = {}
    for p_name in profiles:
        sub = [r for r in results if r['profile'] == p_name]
        h_final = float(np.mean([r['final_entropy'] for r in sub]))
        bits_preserved_pct = (h_final / INITIAL_SHANNON_ENTROPY) * 100
        # Taxa de partidas onde a entropia colapsou abaixo de 0.20 bits
        collapsed_pct = float(np.mean([1 if r['collapsed_round'] is not None else 0 for r in sub]) * 100)

        by_profile[p_name] = {
            'avg_final_entropy': h_final,
            'bits_preserved_pct': bits_preserved_pct,
            'collapsed_pct': collapsed_pct
        }

        print(f"{p_name:<38} | {h_final:6.3f} bits     | {bits_preserved_pct:5.1f}% retidos     | {collapsed_pct:5.1f}% desmascarado")

    # 3. Ranking de Vazamento de Informação por Tipo de Evento (Information Leakage)
    print("\n" + "=" * 86)
    print(" 3. TOP 6 EVENTOS DE MAIOR VAZAMENTO DE INFORMAÇÃO (INFORMATION LEAKAGE)")
    print("=" * 86)
    print("Indica quais eventos do jogo fornecem o maior salto de certeza (Information Gain em bits):")
    print("-" * 86)

    event_gains = {}
    for r in results:
        for ev in r['leakage_events']:
            e_name = ev['event_type']
            if e_name not in event_gains:
                event_gains[e_name] = []
            event_gains[e_name].append(ev['info_gain'])

    ranked_events = []
    for e_name, gains in event_gains.items():
        if len(gains) >= 50:
            ranked_events.append({
                'event': e_name,
                'avg_gain': float(np.mean(gains)),
                'occurrences': len(gains)
            })

    ranked_events.sort(key=lambda x: -x['avg_gain'])

    print(f"{'Evento Observado na Mesa':<46} | {'Ganho Médio (IG)':<18} | {'Impacto Dedutivo':<18}")
    print("-" * 86)
    for item in ranked_events[:6]:
        gain = item['avg_gain']
        impact = "MUITO ALTO (Colapso)" if gain > 0.8 else ("ALTO" if gain > 0.4 else "MODERADO")
        print(f"{item['event']:<46} | {gain:6.3f} bits        | {impact:<18}")

    total_time = time.time() - t0
    print(f"\n⚡ Análise de Teoria da Informação concluída com sucesso em {total_time:.2f}s!")

    payload = {
        'initial_shannon_entropy_bits': INITIAL_SHANNON_ENTROPY,
        'entropy_decay_curve_by_round': mean_decay,
        'camouflage_efficiency_by_profile': by_profile,
        'top_information_leakage_events': ranked_events[:6],
        'total_time_seconds': total_time
    }

    if export_json:
        with open(export_json, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"📁 Relatório de Teoria da Informação exportado com sucesso em: {export_json}")

    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Motor de Teoria da Informação & Entropia de Shannon - BTG Madagascar v14.0")
    parser.add_argument("--games", "-g", type=int, default=4000, help="Partidas a simular (padrão: 4.000)")
    parser.add_argument("--workers", "-w", type=int, default=None, help="Workers paralelos")
    parser.add_argument("--export", "-e", type=str, default="visualizer/data/information_entropy_summary.json", help="Arquivo JSON de destino")
    args = parser.parse_args()

    run_information_analysis(
        n_games=args.games,
        num_workers=args.workers,
        export_json=args.export
    )
