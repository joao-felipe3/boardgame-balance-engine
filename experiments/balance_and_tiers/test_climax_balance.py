# -*- coding: utf-8 -*-
"""
Teste de Calibragem para Clímax na 7ª Rodada & Punição ao Blefe Agressivo
"""

import random
import itertools
import numpy as np
import pandas as pd
from btg_simulation import *


def calibrated_plan_honest_contribution(
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

    # Se precisa do insumo, prioriza combos com o insumo ou coringa
    if contract.req_commodity is not None:
        req_combos = [cb for cb in valid_combos if any(c.card_type in (contract.req_commodity, CardType.WILD) for c in cb)]
        if req_combos:
            valid_combos = req_combos

    best_combo = None
    best_tokens = 0
    best_val = -999
    best_score = (999, 999, 999, 999)

    if is_match_point or contract.tier >= 6:
        best_combo = max(valid_combos, key=lambda cb: sum(c.base_value for c in cb))
        best_tokens = self.interest_tokens
        best_val = sum(c.base_value for c in best_combo) + best_tokens
        return list(best_combo), best_tokens, best_val

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


PlayerAI.plan_honest_contribution = calibrated_plan_honest_contribution

n = 20000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game(i, prof, seed=999000 + i)
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
print("\nMATRIZ DE PLACARES:")
for sc, cnt in df['score'].value_counts().head(7).items():
    tag = "[Climax 7a Rodada]" if "4 x 3" in sc or "3 x 4" in sc else ""
    print(f"  * {sc:<10}: {cnt:>6,d} ({(cnt/n)*100:5.2f}%) {tag}")
