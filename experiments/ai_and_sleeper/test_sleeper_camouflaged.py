# -*- coding: utf-8 -*-
"""
Teste de Sabotagem Camuflada Efetiva para Sleeper no R3/R4
"""

import random
import itertools
import numpy as np
import pandas as pd
from btg_simulation import *


def effective_camouflaged_sabotage(
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

    # 1. Bomba Tóxica no Tier 4 (4 ops) ou em momentos decisivos (R4+):
    if toxic_cards and (contract.committee_size >= 4 or round_num >= 4):
        chosen.append(toxic_cards.pop(0))
        while len(chosen) < cost and low_pos:
            chosen.append(low_pos.pop(0))
        while len(chosen) < cost and self.hand:
            chosen.append(self.hand[0])
        return chosen[:cost], 0

    # 2. Troca de Insumo na Cota (Tier 3/4):
    # Se o Estagiário prometeu ser um dos fornecedores do insumo, ele joga Cobalto (+1) ou Baunilha (+2)
    # NÃO gasta tokens extras, garantindo que o contrato falhe por falta de insumo OU por déficit de pontos!
    if is_responsible_for_req and contract.req_commodity is not None:
        non_req_cards = [c for c in low_pos if c.card_type not in (contract.req_commodity, CardType.WILD)]
        if non_req_cards:
            chosen.append(non_req_cards[0])
            while len(chosen) < cost and low_pos:
                chosen.append(low_pos.pop(0))
            return chosen[:cost], 0

    # 3. Sabotagem por Sub-Aporte (Under-delivering / Economia de Tokens):
    # Joga a carta mais fraca disponível (Cobalto 1pt) com ZERO tokens
    while len(chosen) < cost and low_pos:
        chosen.append(low_pos.pop(0))
    while len(chosen) < cost and self.hand:
        chosen.append(self.hand[0])

    return chosen[:cost], 0


PlayerAI.plan_sabotage_contribution = effective_camouflaged_sabotage

n = 20000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game(i, prof, seed=667000 + i)
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
