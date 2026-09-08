#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulação Consolidada do Kit C com Defesa Ativa de Match-Point
Testa com os 3 perfis (A, B, C) em 10.000 partidas.
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
from tune_kit_c import make_catalog
from run_comparison import _update_suspicions


def simulate_game(game_idx: int, profile: InternProfile, catalog: Dict, seed: Optional[int] = None) -> Dict:
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
    # Kit C: CO + TI + 2 secretas
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

    banker_score = 0
    intern_score = 0
    round_count = 0

    while banker_score < 4 and intern_score < 4 and round_count < 7:
        round_count += 1
        contract = catalog[round_count][0]
        chair = players[(round_count - 1) % 5]

        declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
        chosen_comm, assigned_supplier = engine_mod.choose_optimal_committee(
            chair, players, contract, declarations
        )

        votes = {p.id: p.vote_on_proposal(chair.id, chosen_comm, contract, round_count) for p in players}
        if sum(votes.values()) < 3:
            # Veto resolution
            chair = players[(chair.id + 1) % 5]
            chosen_comm, assigned_supplier = engine_mod.choose_optimal_committee(
                chair, players, contract, declarations
            )

        # Bench draw & interest
        for p in players:
            if p.id not in chosen_comm:
                p.accumulate_holding_interest()
                if p.role == Role.BANKER:
                    preferred = None
                    for ct in [contract.req_commodity, CardType.WILD, CardType.SF, CardType.TI]:
                        if ct is not None and ct in deck.open_market:
                            preferred = ct
                            break
                    if preferred:
                        c = deck.draw_from_market(preferred)
                        p.public_known_cards.append(preferred)
                    else:
                        c = deck.draw_blind(1)[0]
                else:
                    c = deck.draw_blind(1)[0]
                p.hand.append(c)

        comm_objs = [players[pid] for pid in chosen_comm]

        submitted_cards = []
        total_tokens = 0
        is_match_point = (banker_score == 3)

        for p in comm_objs:
            is_req_responsible = (p.id == assigned_supplier)
            should_sabotage = False

            if p.role == Role.INTERN:
                # REGRA DE SOBREVIVÊNCIA NATURAL: em match point (3x0 ou 3xX), NENHUM traidor deixa o adversário vencer de graça
                if is_match_point:
                    should_sabotage = True
                elif p.profile == InternProfile.A_AGGRESSIVE:
                    should_sabotage = True
                elif p.profile == InternProfile.B_SLEEPER:
                    should_sabotage = (round_count >= 3) if p.is_active_saboteur else (round_count >= 4)
                elif p.profile == InternProfile.C_HEDGE:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                    toxic_sab = has_toxic and round_count >= 3
                    quota_sab = is_req_responsible and contract.req_commodity is not None and round_count >= 4
                    should_sabotage = toxic_sab or quota_sab or (round_count >= 5)

            if should_sabotage:
                c, t = p.plan_sabotage_contribution(contract, round_count, is_req_responsible)
            else:
                c, t, _ = p.plan_honest_contribution(
                    contract, round_count, is_req_responsible, contract.target_value / len(chosen_comm),
                    is_match_point=is_match_point
                )

            p.interest_tokens -= t
            total_tokens += t
            for card in c:
                if card in p.hand:
                    p.hand.remove(card)
            submitted_cards.extend(c)

        deck.discard(submitted_cards)
        is_pure = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = engine_mod.evaluate_contract_outcome(
            submitted_cards, total_tokens, contract, is_pure_banker_committee=is_pure
        )

        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()
        else:
            intern_score += 1

        _update_suspicions(players, comm_objs, is_success)

    return {
        'banker_score': banker_score,
        'intern_score': intern_score,
        'rounds': round_count,
        'winner': 'BANKER' if banker_score >= 4 else 'INTERN',
        'score_key': f"{banker_score}x{intern_score}",
    }


def run_benchmark(catalog, name, n_games=10000):
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    results = []
    score_counter = Counter()
    prof_results = {p: [] for p in profiles}

    t0 = time.time()
    for i in range(n_games):
        prof = profiles[i % 3]
        res = simulate_game(i, prof, catalog)
        results.append(res)
        prof_results[prof].append(res)
        score_counter[res['score_key']] += 1

    elapsed = time.time() - t0
    b_wins = sum(1 for r in results if r['winner'] == 'BANKER')
    i_wins = n_games - b_wins
    avg_rds = sum(r['rounds'] for r in results) / n_games

    f_zero = score_counter.get('4x0', 0) / n_games * 100
    t_four = score_counter.get('3x4', 0) / n_games * 100
    f_three = score_counter.get('4x3', 0) / n_games * 100

    print(f"\n{'='*75}")
    print(f"  {name}")
    print(f"{'='*75}")
    print(f"  Banqueiros : {b_wins/n_games*100:5.2f}% ({b_wins:,} vitórias)")
    print(f"  Estagiários: {i_wins/n_games*100:5.2f}% ({i_wins:,} vitórias)")
    print(f"  Taxa 4x0   : {f_zero:5.2f}%  (Alvo: < 8%)")
    print(f"  Taxa Clímax: {t_four + f_three:5.2f}%  (3x4: {t_four:.1f}%, 4x3: {f_three:.1f}%)")
    print(f"  Duração    : {avg_rds:5.2f} rounds | Tempo: {elapsed:.1f}s")
    print("\n  Placares mais comuns:")
    for sk, cnt in sorted(score_counter.items(), key=lambda x: -x[1])[:5]:
        print(f"    {sk:6s}: {cnt:>5,} ({cnt/n_games*100:5.1f}%)")
    print("\n  Por Perfil (Intern WR):")
    for p in profiles:
        pres = prof_results[p]
        pi_w = sum(1 for r in pres if r['winner'] == 'INTERN')
        print(f"    {p.value[:28]:28s}: {pi_w/len(pres)*100:5.2f}% Intern WR")

    return {
        'banker_wr': b_wins/n_games*100,
        'intern_wr': i_wins/n_games*100,
        '4x0': f_zero,
        'climax': t_four + f_three,
        'avg_rds': avg_rds
    }


if __name__ == '__main__':
    # Calibração 1: Metas balanceadas (T1:4, T2:4, T3:7/6, T4:8/8, T5:10, T6:13/14, T7:16)
    c1 = make_catalog(t1_vn=4, t2_vn=4, t3_ti=7, t3_co=6, t4_ti=8, t4_vn=8, t5_ti=10, t5_vn=10, t6_ti=13, t6_sf=14, t7_sf=16)
    run_benchmark(c1, "Calibração 1: T1/T2 VN=4, T3=7/6, T4=8/8", 10000)

    # Calibração 2: T3 um pouco mais acessível para comitê desgastado (T3=6/6, T4=7/7)
    c2 = make_catalog(t1_vn=4, t2_vn=4, t3_ti=6, t3_co=6, t4_ti=7, t4_vn=7, t5_ti=9, t5_vn=9, t6_ti=12, t6_sf=13, t7_sf=15)
    run_benchmark(c2, "Calibração 2: T3=6/6, T4=7/7, T5=9, T6=12/13, T7=15", 10000)

    # Calibração 3: T1/T2 VN=4, T3=7/6, T4=7/7, T5=9, T6=13/14, T7=16
    c3 = make_catalog(t1_vn=4, t2_vn=4, t3_ti=7, t3_co=6, t4_ti=7, t4_vn=7, t5_ti=9, t5_vn=9, t6_ti=13, t6_sf=14, t7_sf=16)
    run_benchmark(c3, "Calibração 3: Ponto de Ajuste Fino", 10000)
