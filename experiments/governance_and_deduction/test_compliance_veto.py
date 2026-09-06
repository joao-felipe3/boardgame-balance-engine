# -*- coding: utf-8 -*-
"""
Teste com Intervenção de Compliance nos 3 Vetos & Punição ao Rush Agressivo
"""

import random
import time
import sys
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import itertools
import pandas as pd
import numpy as np
from test_banker_solidarity import *

def simulate_game_compliance(game_idx: int, profile: InternProfile, seed: Optional[int] = None) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    catalog = SEVEN_TIERS_CATALOG

    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    players = [PlayerAI(i, roles[i], profile, rng) for i in range(5)]

    deck = DeckManager(seed=rng.randint(0, 10**9))
    deck.refill_open_market(3)

    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.VN), ResourceCard(CardType.TI)] + deck.draw_blind(1)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    round_count = 0
    ops = [rng.choice(catalog[t]) for t in range(1, 8)]

    for r_idx, contract in enumerate(ops):
        round_count += 1

        for p in players:
            needed = max(0, 4 - len(p.hand))
            for _ in range(needed):
                if p.role == Role.BANKER and contract.req_commodity in deck.open_market:
                    c = deck.draw_from_market(contract.req_commodity)
                    p.public_known_cards.append(contract.req_commodity)
                elif p.role == Role.BANKER and any(card in deck.open_market for card in [CardType.SF, CardType.WILD, CardType.TI]):
                    noble = next(card for card in [CardType.WILD, CardType.SF, CardType.TI] if card in deck.open_market)
                    c = deck.draw_from_market(noble)
                    p.public_known_cards.append(noble)
                else:
                    c = deck.draw_blind(1)[0]
                p.hand.append(c)

        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        all_declarations = {}

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            all_declarations = declarations

            chosen_comm, assigned_req_player = choose_optimal_committee(chair, players, contract, declarations)

            votes = {p.id: p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count) for p in players}
            if sum(votes.values()) >= 3:
                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        # Se houver 3 vetoes consecutivos, a Intervenção de Compliance assume e escolhe os 3 operadores mais limpos da mesa
        if approved_committee is None:
            bankers_clean = sorted([p for p in players], key=lambda p: (
                p.id in players[curr_chair].known_traitors,
                sum(b.suspicions[p.id] for b in players if b.role == Role.BANKER)
            ))
            approved_committee = [p.id for p in bankers_clean[:contract.committee_size]]
            promised_supplier = None

        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        planning_order = []
        if promised_supplier is not None:
            sup_obj = next((p for p in comm_objs if p.id == promised_supplier), None)
            if sup_obj:
                planning_order.append(sup_obj)
        for p in comm_objs:
            if p not in planning_order:
                planning_order.append(p)

        submitted_all_cards = []
        total_tokens_spent = 0
        cumulative_committed_val = 0
        is_match_point = (banker_score == 3)

        for idx, p in enumerate(planning_order):
            is_req_responsible = (p.id == promised_supplier)
            remaining_members = len(planning_order) - idx
            remaining_target = max(0, contract.target_value - cumulative_committed_val)
            quota_for_p = remaining_target / remaining_members

            declared_p_val = all_declarations[p.id][1] if p.id in all_declarations else 0
            if p.role == Role.BANKER and round_count >= 3 and contract.target_value >= 8:
                quota_for_p = max(quota_for_p, min(declared_p_val, contract.target_value / contract.committee_size))

            should_sabotage = False
            if p.role == Role.INTERN:
                if p.profile == InternProfile.A_AGGRESSIVE:
                    should_sabotage = True
                elif p.profile == InternProfile.B_SLEEPER:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                    should_sabotage = (round_count >= 3 and has_toxic) or (round_count >= 4)
                elif p.profile == InternProfile.C_HEDGE:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                    should_sabotage = (has_toxic and round_count >= 3) or (round_count >= 4)

            honest_cards, honest_tokens, honest_val = p.plan_honest_contribution(contract, round_count, is_req_responsible, quota_for_p, is_match_point=is_match_point)
            cumulative_committed_val += honest_val

            if not should_sabotage:
                actual_cards = honest_cards
                actual_tokens = honest_tokens
            else:
                actual_cards, actual_tokens = p.plan_sabotage_contribution(contract, round_count, is_req_responsible)

            p.interest_tokens -= actual_tokens
            total_tokens_spent += actual_tokens

            for c in actual_cards:
                if c in p.hand:
                    p.hand.remove(c)
                if c.card_type in p.public_known_cards:
                    p.public_known_cards.remove(c.card_type)

            submitted_all_cards.extend(actual_cards)

        deck.discard(submitted_all_cards)

        is_pure_bankers = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_all_cards, total_tokens_spent, contract, is_pure_banker_committee=is_pure_bankers)

        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()

            decay = 0.08 if contract.tier <= 2 else (0.15 if contract.tier <= 4 else 0.20)
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id and cid not in bp.known_traitors:
                            bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - decay)
        else:
            intern_score += 1
            has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_all_cards)
            penalty = 0.35 if len(approved_committee) >= 4 else (0.50 if len(approved_committee) == 3 else 0.70)

            for bp in players:
                if bp.role == Role.BANKER:
                    if len(approved_committee) == 2 and bp.id in approved_committee:
                        partner_id = next(cid for cid in approved_committee if cid != bp.id)
                        bp.suspicions[partner_id] = 1.00
                        bp.known_traitors.add(partner_id)
                    else:
                        for cid in approved_committee:
                            if cid != bp.id:
                                bp.suspicions[cid] = min(0.95, bp.suspicions[cid] + penalty)

        if banker_score >= 4:
            return {"winner": Role.BANKER.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}
        elif intern_score >= 4:
            return {"winner": Role.INTERN.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return {"winner": w, "rounds": 7, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}


n = 30000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game_compliance(i, prof, seed=999000 + i)
    results.append(res)

df = pd.DataFrame(results)
b_wins = (df['winner'] == Role.BANKER.value).sum()
i_wins = (df['winner'] == Role.INTERN.value).sum()

print("=" * 80)
print(f"Banqueiros : {(b_wins/n)*100:6.2f}% ({b_wins:,})")
print(f"Estagiarios: {(i_wins/n)*100:6.2f}% ({i_wins:,})")
print(f"Duracao Media: {df['rounds'].mean():.2f} rodadas")

print("\nPERFORMANCE POR PERFIL:")
for prof in profiles:
    sub = df[df['profile'] == prof.value]
    sub_iw = (sub['winner'] == Role.INTERN.value).sum()
    print(f"{prof.value:<35} | WR Estagiarios: {(sub_iw/len(sub))*100:5.2f}%")

df['score'] = df['b_score'].astype(str) + ' x ' + df['i_score'].astype(str)
climax_pct = ((df['score'].isin(['4 x 3', '3 x 4'])).sum() / n) * 100
sweep_pct = ((df['score'] == '4 x 0').sum() / n) * 100
print(f"\nTOTAL NO CLÍMAX DA 7ª RODADA: {climax_pct:.2f}%")
print(f"TOTAL DE VARREDURA 4x0: {sweep_pct:.2f}%")

print("\nMATRIZ DE PLACARES:")
for sc, cnt in df['score'].value_counts().head(7).items():
    tag = "[Climax 7a Rodada]" if "4 x 3" in sc or "3 x 4" in sc else ""
    print(f"  * {sc:<10}: {cnt:>6,d} ({(cnt/n)*100:5.2f}%) {tag}")
print("=" * 80)
