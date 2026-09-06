#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico de Curva de Dificuldade e Fine Tuning do Kit C
Analisa taxa de aprovação por Tier para comitês puros vs mistos.
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


def run_experiment(catalog, name, profile_c_early=False, n_games=10000):
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    results = []
    score_counter = Counter()

    for i in range(n_games):
        prof = profiles[i % 3]
        rng = random.Random(1000000 + i)
        roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
        rng.shuffle(roles)
        intern_count = 0
        players = []
        for p_idx in range(5):
            is_active = (roles[p_idx] == Role.INTERN and intern_count == 0)
            if roles[p_idx] == Role.INTERN:
                intern_count += 1
            players.append(PlayerAI(p_idx, roles[p_idx], prof, rng, is_active_saboteur=is_active))

        deck = DeckManager(seed=rng.randint(0, 10**9))
        deck.refill_open_market(3)
        # Kit C: CO + TI + 2 secretas
        for p in players:
            p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

        res = _run_game_loop(players, deck, rng, prof, catalog, economy='new', profile_c_early=profile_c_early)
        results.append(res)
        score_counter[res['score_key']] += 1

    banker_wins = sum(1 for r in results if r['winner'] == 'BANKER')
    intern_wins = n_games - banker_wins
    avg_rounds = sum(r['rounds'] for r in results) / n_games

    f_zero = score_counter.get('4x0', 0) / n_games * 100
    f_one = score_counter.get('4x1', 0) / n_games * 100
    f_two = score_counter.get('4x2', 0) / n_games * 100
    f_three = score_counter.get('4x3', 0) / n_games * 100
    t_four = score_counter.get('3x4', 0) / n_games * 100
    two_four = score_counter.get('2x4', 0) / n_games * 100
    one_four = score_counter.get('1x4', 0) / n_games * 100
    zero_four = score_counter.get('0x4', 0) / n_games * 100

    print(f"\n{'='*75}")
    print(f"  {name}")
    print(f"{'='*75}")
    print(f"  WR: Banqueiros {banker_wins/n_games*100:.2f}% | Estagiarios {intern_wins/n_games*100:.2f}% | Dur: {avg_rounds:.2f} rds")
    print(f"  Vitorias Banqueiros : 4x0={f_zero:4.1f}% | 4x1={f_one:4.1f}% | 4x2={f_two:4.1f}% | 4x3={f_three:4.1f}% (Total={banker_wins/n_games*100:.1f}%)")
    print(f"  Vitorias Estagiarios: 0x4={zero_four:4.1f}% | 1x4={one_four:4.1f}% | 2x4={two_four:4.1f}% | 3x4={t_four:4.1f}% (Total={intern_wins/n_games*100:.1f}%)")
    print(f"  Climax (3x4 + 4x3)  : {t_four + f_three:.1f}%")

    return {
        'banker_wr': banker_wins/n_games*100,
        'intern_wr': intern_wins/n_games*100,
        '4x0': f_zero,
        'climax': t_four + f_three,
        'avg_rounds': avg_rounds
    }


if __name__ == '__main__':
    from tune_kit_c import make_catalog

    # Grid de testes:
    # O que acontece se o T1 for viável (VN=4), mas T3/T4 exigirem coordenação real?
    
    # Teste A: T1 VN=4, T2 VN=4, T3 TI=7/CO=6, T4 TI=8/VN=8, T5=10, T6=13/14, T7=16
    # (Com profile_c_early=True para simular jogador humano que não dorme até R5)
    cat_A = make_catalog(t1_vn=4, t2_vn=4, t3_ti=7, t3_co=6, t4_ti=8, t4_vn=8, t5_ti=10, t5_vn=10, t6_ti=13, t6_sf=14, t7_sf=16)
    run_experiment(cat_A, "Teste A: Metas Suaves T1/T2 (VN=4) + Profile C Antecipado", profile_c_early=True, n_games=10000)

    # Teste B: Metas Suaves T1/T2 (VN=4), mas T3 mais exigente (TI=8, CO=7), T4 (TI=9, VN=9)
    cat_B = make_catalog(t1_vn=4, t2_vn=4, t3_ti=8, t3_co=7, t4_ti=9, t4_vn=9, t5_ti=11, t5_vn=11, t6_ti=14, t6_sf=15, t7_sf=17)
    run_experiment(cat_B, "Teste B: Metas T1/T2 (VN=4) + T3/T4 Exigentes (TI=8/9) + Profile C Antecipado", profile_c_early=True, n_games=10000)

    # Teste C: Ponto de Equilíbrio intermediário
    cat_C = make_catalog(t1_vn=4, t2_vn=5, t3_ti=7, t3_co=7, t4_ti=8, t4_vn=8, t5_ti=10, t5_vn=10, t6_ti=13, t6_sf=14, t7_sf=16)
    run_experiment(cat_C, "Teste C: Intermediário (T1:4, T2:5, T3:7, T4:8) + Profile C Antecipado", profile_c_early=True, n_games=10000)

    # Teste D: Intermediário sem Profile C Antecipado (Profile C conservador)
    run_experiment(cat_C, "Teste D: Intermediário (T1:4, T2:5, T3:7, T4:8) + Profile C Normal", profile_c_early=False, n_games=10000)
