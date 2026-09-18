# -*- coding: utf-8 -*-
"""
Investigação Profunda: Por que os Estagiários ainda vencem 43% na simulação
quando no jogo real os Banqueiros os isolam e dominam facilmente?
"""
import sys
import os
import random
import pandas as pd
import numpy as np
from collections import Counter, defaultdict

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import Role, InternProfile, BankerProfile, simulate_single_match

def run_investigation(n_games=3000):
    print("=" * 80)
    print(f"INVESTIGAÇÃO DA TAXA DE VITÓRIA DOS ESTAGIÁRIOS ({n_games} PARTIDAS)")
    print("=" * 80)

    results = []
    infiltrations_per_game = []
    forced_comm_games = 0
    intern_chair_proposals_passed = 0
    banker_invited_intern_count = 0
    infiltrations_by_round = defaultdict(int)
    why_intern_in_comm = Counter()
    untested_intern_picked = 0
    winner_by_infiltrations = defaultdict(list)

    # Detalhamento de vitórias dos estagiários
    intern_win_causes = Counter()

    for i in range(n_games):
        res = simulate_single_match(
            i,
            seed=100000 + i,
            record_trace=False,
            banker_profile=BankerProfile.BALANCED,
            intern_profile=InternProfile.B_SLEEPER
        )
        results.append(res)
        
        infils = res.get('intern_appearances', 0)
        infiltrations_per_game.append(infils)
        winner_by_infiltrations[infils].append(res['winner'])

        tt = res.get('tier_telemetry', {})
        for rnd, data in tt.items():
            ic = data.get('intern_count', 0)
            if ic > 0:
                infiltrations_by_round[rnd] += ic

    df = pd.DataFrame(results)
    banker_wr = (df['winner'] == Role.BANKER.value).mean() * 100
    intern_wr = (df['winner'] == Role.INTERN.value).mean() * 100

    print(f"\n1. RESULTADO GLOBAL:")
    print(f"   Win Rate Banqueiros : {banker_wr:.2f}%")
    print(f"   Win Rate Estagiários: {intern_wr:.2f}%")
    print(f"   Média de Infiltrações de Estagiários por Jogo: {np.mean(infiltrations_per_game):.2f}")
    print(f"   Média de Vetos por Jogo: {df['total_vetoes'].mean():.2f}")
    print(f"   Total de Comitês Forçados: {df['forced_committees'].sum()} (em {df['forced_committees'].gt(0).sum()} jogos)")

    print(f"\n2. TAXA DE VITÓRIA DO BANCO POR TOTAL DE INFILTRAÇÕES NO JOGO:")
    print(f"{'Infiltrações':<15} | {'Jogos':<8} | {'Freq %':<8} | {'WR Banco %':<12} | {'WR Estag %':<12}")
    print("-" * 65)
    for inf in sorted(winner_by_infiltrations.keys()):
        outcomes = winner_by_infiltrations[inf]
        cnt = len(outcomes)
        b_wins = sum(1 for w in outcomes if w == Role.BANKER.value)
        b_pct = (b_wins / cnt) * 100
        i_pct = 100 - b_pct
        freq = (cnt / n_games) * 100
        print(f"{inf:<15} | {cnt:<8} | {freq:6.1f}% | {b_pct:9.2f}% | {i_pct:9.2f}%")

    print(f"\n3. INFILTRAÇÕES DE ESTAGIÁRIOS POR RODADA (TOTAL EM {n_games} JOGOS):")
    for rnd in range(1, 8):
        count = infiltrations_by_round[rnd]
        rate = (count / n_games) * 100
        print(f"   Rodada {rnd} (Tier {rnd}): {count:5d} estagiários infiltrados ({rate:5.1f}% dos jogos)")

    print(f"\n4. COMO OS ESTAGIÁRIOS VENCEM (QUANDO ELES GANHAM)?")
    intern_wins_df = df[df['winner'] == Role.INTERN.value]
    print(f"   Placares das Vitórias dos Estagiários:")
    scores = intern_wins_df['b_score'].astype(str) + " x " + intern_wins_df['i_score'].astype(str)
    for sc, c in scores.value_counts().items():
        print(f"      {sc}: {c:4d} jogos ({c/len(intern_wins_df)*100:.1f}%)")

if __name__ == '__main__':
    run_investigation(3000)
