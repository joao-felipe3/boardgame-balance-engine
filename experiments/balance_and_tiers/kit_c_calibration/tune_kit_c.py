#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Fine-Tuning para o Kit C (BTG Madagascar)
Explora variações de metas para atingir ~50% WR com 4x0 < 8%.
"""

import sys
import os
import random
import time
from collections import Counter
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from btg.constants import CardType, Role, InternProfile, ContractSpec
from btg.player import PlayerAI
from btg.deck import ResourceCard, DeckManager
import btg.engine as engine_mod
from run_comparison import _run_game_loop


def make_catalog(t1_vn, t2_vn, t3_ti, t3_co, t4_ti, t4_vn, t5_ti, t5_vn, t6_ti, t6_sf, t7_sf):
    return {
        1: [
            ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=3),
            ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=t1_vn,
                         req_commodity=CardType.VN, req_commodity_count=1),
        ],
        2: [
            ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=3),
            ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=t2_vn,
                         req_commodity=CardType.VN, req_commodity_count=1),
        ],
        3: [
            ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=t3_ti,
                         req_commodity=CardType.TI, req_commodity_count=2),
            ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=t3_co,
                         req_commodity=CardType.CO, req_commodity_count=2),
        ],
        4: [
            ContractSpec("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=t4_ti,
                         req_commodity=CardType.TI, req_commodity_count=2),
            ContractSpec("Consorcio Agro-Industrial", 4, committee_size=3, cost_per_player=1, target_value=t4_vn,
                         req_commodity=CardType.VN, req_commodity_count=2),
        ],
        5: [
            ContractSpec("Megaconsorcio Industrial", 5, committee_size=3, cost_per_player=1, target_value=t5_ti,
                         req_commodity=CardType.TI, req_commodity_count=2,
                         expandable_on_prior_failure=True, expanded_committee_size=4),
            ContractSpec("Cofre de Commodities", 5, committee_size=3, cost_per_player=1, target_value=t5_vn,
                         req_commodity=CardType.VN, req_commodity_count=2,
                         expandable_on_prior_failure=True, expanded_committee_size=4),
        ],
        6: [
            ContractSpec("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=t6_ti,
                         req_commodity=CardType.TI, req_commodity_count=2),
            ContractSpec("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=t6_sf,
                         req_commodity=CardType.SF, req_commodity_count=2),
        ],
        7: [
            ContractSpec("Holding Global BTG", 7, committee_size=3, cost_per_player=2, target_value=t7_sf,
                         req_commodity=CardType.SF, req_commodity_count=2),
        ],
    }


def simulate_kit_c_match(game_idx: int, profile: InternProfile, catalog: Dict, profile_c_early: bool = False, seed: Optional[int] = None) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    intern_count = 0
    players = []
    for i in range(5):
        is_active = (roles[i] == Role.INTERN and intern_count == 0)
        if roles[i] == Role.INTERN:
            intern_count += 1
        players.append(PlayerAI(i, roles[i], profile, rng, is_active_saboteur=is_active))

    deck = DeckManager(seed=rng.randint(0, 10**9))
    deck.refill_open_market(3)
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

    return _run_game_loop(players, deck, rng, profile, catalog, economy='new', profile_c_early=profile_c_early)


def test_catalog(name: str, catalog: Dict, n_games: int = 10000, profile_c_early: bool = False):
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    all_results = []
    score_counter = Counter()

    t0 = time.time()
    for i in range(n_games):
        prof = profiles[i % 3]
        res = simulate_kit_c_match(i, prof, catalog, profile_c_early=profile_c_early)
        all_results.append(res)
        score_counter[res['score_key']] += 1

    elapsed = time.time() - t0
    banker_wins = sum(1 for r in all_results if r['winner'] == 'BANKER')
    intern_wins = n_games - banker_wins
    avg_rounds = sum(r['rounds'] for r in all_results) / n_games
    four_zero = score_counter.get('4x0', 0) / n_games * 100
    three_four = score_counter.get('3x4', 0) / n_games * 100
    four_three = score_counter.get('4x3', 0) / n_games * 100

    print(f"| {name:<35} | {intern_wins/n_games*100:>6.2f}% | {banker_wins/n_games*100:>6.2f}% | {four_zero:>5.1f}% | {three_four:>5.1f}% | {four_three:>5.1f}% | {avg_rounds:>4.2f} | {elapsed:>4.1f}s |")
    return {
        'name': name,
        'banker_wr': banker_wins/n_games*100,
        'intern_wr': intern_wins/n_games*100,
        '4x0': four_zero,
        '3x4': three_four,
        '4x3': four_three,
        'avg_rounds': avg_rounds,
        'scores': score_counter,
    }


if __name__ == '__main__':
    print(f"| {'Configuracao':<35} | {'Intern':>7} | {'Banker':>7} | {'4x0':>6} | {'3x4':>6} | {'4x3':>6} | {'Dur.':>5} | {'Tempo':>5} |")
    print("|" + "-"*37 + "|" + "-"*9 + "|" + "-"*9 + "|" + "-"*8 + "|" + "-"*8 + "|" + "-"*8 + "|" + "-"*7 + "|" + "-"*7 + "|")

    # Baseline Catalog BC
    c_current = make_catalog(t1_vn=6, t2_vn=6, t3_ti=7, t3_co=6, t4_ti=8, t4_vn=8, t5_ti=10, t5_vn=10, t6_ti=13, t6_sf=14, t7_sf=16)
    test_catalog("1. Atual (T1:6, T2:6, T3:7/6, T4:8)", c_current, 6000)

    # Ajuste 1: Aliviar T1 e T2 de VN (meta 4 em vez de 6)
    c_v1 = make_catalog(t1_vn=4, t2_vn=4, t3_ti=7, t3_co=6, t4_ti=8, t4_vn=8, t5_ti=10, t5_vn=10, t6_ti=13, t6_sf=14, t7_sf=16)
    test_catalog("2. T1/T2 VN=4 (restante igual)", c_v1, 6000)

    # Ajuste 2: T1/T2 VN=4 + T3=7/6 + T4=8/8
    c_v2 = make_catalog(t1_vn=4, t2_vn=4, t3_ti=7, t3_co=6, t4_ti=7, t4_vn=7, t5_ti=9, t5_vn=9, t6_ti=13, t6_sf=14, t7_sf=16)
    test_catalog("3. T1/T2 VN=4 + T4=7 + T5=9", c_v2, 6000)

    # Ajuste 3: T1/T2 VN=5 + T3=7/6 + T4=7 + T5=9
    c_v3 = make_catalog(t1_vn=5, t2_vn=5, t3_ti=7, t3_co=6, t4_ti=8, t4_vn=7, t5_ti=10, t5_vn=9, t6_ti=13, t6_sf=14, t7_sf=16)
    test_catalog("4. T1/T2 VN=5 + T4=8/7 + T5=10/9", c_v3, 6000)

    # Ajuste 4: T1/T2 VN=4 + T3=6/6 + T4=7/7 + T5=9/9 + T6=12/13 + T7=15
    c_v4 = make_catalog(t1_vn=4, t2_vn=4, t3_ti=6, t3_co=6, t4_ti=7, t4_vn=7, t5_ti=9, t5_vn=9, t6_ti=12, t6_sf=13, t7_sf=15)
    test_catalog("5. Mais suave global (T1:4, T3:6)", c_v4, 6000)
