# -*- coding: utf-8 -*-
"""
Teste de Calibragem para Maximizar o Clímax na 7ª Rodada (Motor v12.1)
"""

import random
import itertools
import numpy as np
import pandas as pd
from btg_simulation import *

# 1. Atualiza SEVEN_TIERS_CATALOG com curva perfeita de progressão
SEVEN_TIERS_CATALOG_CLIMAX = {
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
        ContractSpec("Refino Metalurgico (Megasindicato)", 4, committee_size=4, cost_per_player=1, target_value=11, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Agro-Industrial (Megasindicato)", 4, committee_size=4, cost_per_player=1, target_value=11, req_commodity=CardType.VN, req_commodity_count=2),
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

import btg_simulation
btg_simulation.SEVEN_TIERS_CATALOG = SEVEN_TIERS_CATALOG_CLIMAX

# 2. Refina a coordenação contábil para garantir que comitês limpos de Banqueiros vençam com consistência
def climax_plan_honest_contribution(
    self,
    contract: ContractSpec,
    round_num: int,
    is_responsible_for_req: bool,
    quota_needed: float,
    is_match_point: bool = False
) -> Tuple[List[ResourceCard], int, int]:
    cost = contract.cost_per_player
    pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
    if not pos_cards:
        return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

    valid_combos = list(itertools.combinations(pos_cards, cost))
    if not valid_combos:
        valid_combos = list(itertools.combinations(self.hand, cost))
    if not valid_combos:
        return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

    if contract.req_commodity is not None:
        req_combos = [cb for cb in valid_combos if any(c.card_type in (contract.req_commodity, CardType.WILD) for c in cb)]
        if req_combos:
            valid_combos = req_combos

    if is_match_point or contract.tier >= 6:
        best_combo = max(valid_combos, key=lambda cb: sum(c.base_value for c in cb))
        best_tokens = self.interest_tokens
        best_val = sum(c.base_value for c in best_combo) + best_tokens
        return list(best_combo), best_tokens, best_val

    best_combo = None
    best_tokens = 0
    best_val = -999
    best_score = (999, 999, 999, 999)

    for cb in valid_combos:
        base_v = sum(c.base_value for c in cb)
        needed_tokens = max(0, int(np.ceil(quota_needed - base_v)))
        tokens_to_use = min(self.interest_tokens, needed_tokens)
        total_v = base_v + tokens_to_use

        has_safira = any(c.card_type in (CardType.SF, CardType.WILD) for c in cb)
        penalty = 10 if (has_safira and round_num <= 3 and contract.req_commodity != CardType.SF) else 0

        if total_v >= quota_needed:
            score = (0, penalty, tokens_to_use, total_v - quota_needed)
        else:
            score = (1, penalty, -tokens_to_use, -(total_v - quota_needed))

        if best_combo is None or score < best_score:
            best_combo = cb
            best_tokens = tokens_to_use
            best_val = total_v
            best_score = score

    return list(best_combo), best_tokens, best_val


PlayerAI.plan_honest_contribution = climax_plan_honest_contribution

n = 20000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game(i, prof, seed=333000 + i)
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
