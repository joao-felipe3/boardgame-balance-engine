# -*- coding: utf-8 -*-
"""
BTG Madagascar - Gerador e Serializador de Traces para o Dashboard Visual
"""

import json
import os
from typing import Dict
from .constants import Role, InternProfile
from .engine import simulate_single_match


def generate_trace_dataset(
    output_path: str = "visualizer/data/game_traces.json",
    seeds: Dict[str, int] = None
) -> Dict:
    """Gera um conjunto padrão de 3 partidas (Sleeper, Agressivo, Hedge) com traces completos."""
    if seeds is None:
        seeds = {
            'sleeper': 112233,
            'aggressive': 445566,
            'hedge': 778899
        }

    g1 = simulate_single_match(101, InternProfile.B_SLEEPER, seed=seeds['sleeper'], record_trace=True)
    g2 = simulate_single_match(202, InternProfile.A_AGGRESSIVE, seed=seeds['aggressive'], record_trace=True)
    g3 = simulate_single_match(303, InternProfile.C_HEDGE, seed=seeds['hedge'], record_trace=True)

    def format_trace(g, prof, seed):
        players_meta = g['players_metadata']
        banker_ids = [p['id'] for p in players_meta if p['role'] == Role.BANKER.value]
        intern_ids = [p['id'] for p in players_meta if p['role'] == Role.INTERN.value]
        return {
            'seed': seed,
            'profile': prof.value,
            'players': players_meta,
            'banker_ids': banker_ids,
            'intern_ids': intern_ids,
            'final_winner': g['winner'],
            'final_score': f"{g['b_score']} x {g['i_score']}",
            'total_rounds': g['rounds'],
            'rounds': g['rounds_data']
        }

    all_traces = {
        'sleeper_game': format_trace(g1, InternProfile.B_SLEEPER, seeds['sleeper']),
        'aggressive_game': format_trace(g2, InternProfile.A_AGGRESSIVE, seeds['aggressive']),
        'hedge_game': format_trace(g3, InternProfile.C_HEDGE, seeds['hedge'])
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_traces, f, indent=2, ensure_ascii=False)

    return all_traces
