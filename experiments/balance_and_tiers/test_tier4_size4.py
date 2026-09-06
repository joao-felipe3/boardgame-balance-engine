# -*- coding: utf-8 -*-
"""
Teste de Comitê de 4 Operadores no Tier 4 (Eliminação de 4x0 e Maximização do Clímax na 7ª Rodada)
"""

import random
import itertools
import numpy as np
import pandas as pd
from btg_simulation import *

# Atualiza catálogo com Tier 4 = 4 ops (forçando 1 Estagiário no comitê!)
TIERS_CATALOG_V12_1 = {
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

# Substitui o catálogo no simulador
import btg_simulation
btg_simulation.SEVEN_TIERS_CATALOG = TIERS_CATALOG_V12_1

n = 20000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game(i, prof, seed=123000 + i)
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
