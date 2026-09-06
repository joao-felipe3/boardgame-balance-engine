# -*- coding: utf-8 -*-
"""
Teste de Eliminação de 4x0 e Maximização do Clímax da 7ª Rodada no Tier 4
"""

import random
import itertools
import numpy as np
import pandas as pd
from btg_simulation import *


def guaranteed_climax_sabotage(
    self,
    contract: ContractSpec,
    round_num: int,
    is_responsible_for_req: bool
) -> Tuple[List[ResourceCard], int]:
    cost = contract.cost_per_player
    toxic_cards = [c for c in self.hand if c.card_type == CardType.TOXIC]
    pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
    low_pos = sorted(pos_cards, key=lambda c: c.base_value)

    chosen: List[ResourceCard] = []

    # 1. Bomba Tóxica no Tier 4 (4 ops) ou Tiers Decisivos (R4+):
    if toxic_cards and (contract.committee_size >= 4 or round_num >= 4):
        chosen.append(toxic_cards.pop(0))
        while len(chosen) < cost and low_pos:
            chosen.append(low_pos.pop(0))
        while len(chosen) < cost and self.hand:
            chosen.append(self.hand[0])
        return chosen[:cost], 0

    # 2. Troca de Insumo na Cota no Tier 3 / Tier 4:
    if is_responsible_for_req and contract.req_commodity is not None:
        non_req_cards = [c for c in low_pos if c.card_type not in (contract.req_commodity, CardType.WILD)]
        if non_req_cards:
            chosen.append(non_req_cards[0])
            while len(chosen) < cost and low_pos:
                chosen.append(low_pos.pop(0))
            return chosen[:cost], 0

    # 3. Sub-Aporte (Under-delivering / Cobalto de 1pt com 0 tokens):
    while len(chosen) < cost and low_pos:
        chosen.append(low_pos.pop(0))
    while len(chosen) < cost and self.hand:
        chosen.append(self.hand[0])

    return chosen[:cost], 0


PlayerAI.plan_sabotage_contribution = guaranteed_climax_sabotage

# No coordinate_committee_contributions, qualquer Estagiário no Tier 4 (4 ops) ou R4+ sabota com certeza
def climax_coordinate_committee_contributions(
    comm_objs: List[PlayerAI],
    contract: ContractSpec,
    round_num: int,
    promised_supplier_id: Optional[int],
    declarations: Dict[int, PlayerDeclaration],
    banker_score: int
) -> Tuple[List[ResourceCard], int, List[Dict], Dict[int, int]]:
    planning_order = []
    if promised_supplier_id is not None:
        sup_obj = next((p for p in comm_objs if p.id == promised_supplier_id), None)
        if sup_obj:
            planning_order.append(sup_obj)
    for p in comm_objs:
        if p not in planning_order:
            planning_order.append(p)

    submitted_all_cards: List[ResourceCard] = []
    total_tokens_spent = 0
    submitted_cards_data = []
    cumulative_committed_val = 0
    is_match_point = (banker_score == 3)
    promised_values = {}

    for idx, p in enumerate(planning_order):
        is_req_responsible = (p.id == promised_supplier_id)
        remaining_members = len(planning_order) - idx
        remaining_target = max(0, contract.target_value - cumulative_committed_val)
        quota_for_p = remaining_target / remaining_members

        declared_p_val = declarations[p.id].claimed_value if p.id in declarations else 0
        if p.role == Role.BANKER and round_num >= 3 and contract.target_value >= 8:
            quota_for_p = max(quota_for_p, min(declared_p_val, contract.target_value / contract.committee_size))

        should_sabotage = False
        if p.role == Role.INTERN:
            if p.profile == InternProfile.A_AGGRESSIVE:
                should_sabotage = True
            elif p.profile == InternProfile.B_SLEEPER:
                has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                # No Tier 4 (4 ops) ou na R4+, o Sleeper acorda com 100% de certeza!
                should_sabotage = (round_num >= 3 and has_toxic) or (contract.committee_size >= 4) or (round_num >= 4)
            elif p.profile == InternProfile.C_HEDGE:
                has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                should_sabotage = (round_num >= 3 and has_toxic) or (contract.committee_size >= 4) or (round_num >= 4)

        honest_cards, honest_tokens, honest_val = p.plan_honest_contribution(contract, round_num, is_req_responsible, quota_for_p, is_match_point=is_match_point)
        cumulative_committed_val += honest_val
        promised_values[p.id] = honest_val

        if not should_sabotage:
            actual_cards = honest_cards
            actual_tokens = honest_tokens
        else:
            actual_cards, actual_tokens = p.plan_sabotage_contribution(contract, round_num, is_req_responsible)

        p.interest_tokens -= actual_tokens
        total_tokens_spent += actual_tokens

        for c in actual_cards:
            if c in p.hand:
                p.hand.remove(c)

        submitted_all_cards.extend(actual_cards)
        submitted_cards_data.append({
            'player_id': p.id,
            'is_req_responsible': is_req_responsible,
            'tokens_spent': actual_tokens,
            'cards': [{
                'type': c.card_type.name,
                'name': c.card_type.value,
                'base': c.base_value
            } for c in actual_cards]
        })

    return submitted_all_cards, total_tokens_spent, submitted_cards_data, promised_values


import btg_simulation
btg_simulation.coordinate_committee_contributions = climax_coordinate_committee_contributions

n = 20000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game(i, prof, seed=778000 + i)
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
