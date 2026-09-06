# -*- coding: utf-8 -*-
"""
Teste de Confiança e Infiltração Profunda do Sleeper no Pós-Tier 4
"""

import random
import itertools
import numpy as np
import pandas as pd
from btg_simulation import *

TIERS_CATALOG_CLIMAX_T4 = {
    1: [
        ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=3),
        ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.CO, req_commodity_count=1),
        ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    3: [
        ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=8, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=7, req_commodity=CardType.CO, req_commodity_count=2),
    ],
    4: [
        ContractSpec("Refino Metalurgico (Megasindicato)", 4, committee_size=4, cost_per_player=1, target_value=12, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Agro-Industrial (Megasindicato)", 4, committee_size=4, cost_per_player=1, target_value=12, req_commodity=CardType.VN, req_commodity_count=2),
    ],
    5: [
        ContractSpec("Fundicao Estrategica", 5, committee_size=2, cost_per_player=2, target_value=12, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Cofre de Gemas", 5, committee_size=2, cost_per_player=2, target_value=13, req_commodity=CardType.SF, req_commodity_count=2),
    ],
    6: [
        ContractSpec("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=16, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=17, req_commodity=CardType.SF, req_commodity_count=2),
    ],
    7: [
        ContractSpec("Holding Global BTG (Climax)", 7, committee_size=3, cost_per_player=2, target_value=21, req_commodity=CardType.SF, req_commodity_count=3),
    ]
}

def simulate_game_sleeper_trust(
    game_idx: int,
    profile: InternProfile,
    seed: Optional[int] = None
) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    catalog = TIERS_CATALOG_CLIMAX_T4

    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    players = [PlayerAI(i, roles[i], profile, rng) for i in range(5)]

    deck = DeckManager(seed=rng.randint(0, 10**9))
    for p in players:
        p.hand = deck.draw(3)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    round_count = 0
    ops = [rng.choice(catalog[t]) for t in range(1, 8)]

    for r_idx, contract in enumerate(ops):
        round_count += 1

        for p in players:
            p.hand.extend(deck.draw(1))

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

        if approved_committee is None:
            chair = players[curr_chair]
            others = [p.id for p in players if p.id != chair.id]
            approved_committee = [chair.id] + others[:contract.committee_size - 1]
            promised_supplier = None

        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        submitted_cards, total_tokens_spent, submitted_cards_data, promised_values = coordinate_committee_contributions(
            comm_objs, contract, round_count, promised_supplier, all_declarations, banker_score
        )

        deck.discard(submitted_cards)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_cards, total_tokens_spent, contract)

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
            has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_cards)

            # Diluição precisa de suspeita por tamanho de comitê:
            if len(approved_committee) >= 4:
                penalty = 0.20
            elif len(approved_committee) == 3:
                penalty = 0.35
            else:
                penalty = 0.55

            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id:
                            if has_toxic and len(approved_committee) == 2:
                                bp.suspicions[cid] = 1.00
                                bp.known_traitors.add(cid)
                            else:
                                bp.suspicions[cid] = min(0.95, bp.suspicions[cid] + penalty)

        if banker_score >= 4:
            return {"winner": Role.BANKER.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}
        elif intern_score >= 4:
            return {"winner": Role.INTERN.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return {"winner": w, "rounds": 7, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}


n = 20000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game_sleeper_trust(i, prof, seed=888000 + i)
    results.append(res)

df = pd.DataFrame(results)
b_wins = (df['winner'] == Role.BANKER.value).sum()
i_wins = (df['winner'] == Role.INTERN.value).sum()

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
print(f"\nTOTAL NO CLÍMAX DA 7ª RODADA: {climax_pct:.2f}%")

print("\nMATRIZ DE PLACARES:")
for sc, cnt in df['score'].value_counts().head(7).items():
    tag = "[Climax 7a Rodada]" if "4 x 3" in sc or "3 x 4" in sc else ""
    print(f"  * {sc:<10}: {cnt:>6,d} ({(cnt/n)*100:5.2f}%) {tag}")
