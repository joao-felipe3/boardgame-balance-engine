# -*- coding: utf-8 -*-
"""
Teste de Isolamento Estrito de Sabotadores Precoces & Valorização do Sleeper
"""

import random
import numpy as np
import pandas as pd
from btg_simulation import *

def strict_vote_on_proposal(self, proposer: int, committee: List[int], contract: ContractSpec, round_num: int) -> bool:
    if self.role == Role.BANKER:
        for p in committee:
            if p in self.known_traitors or self.suspicions[p] >= 0.60:
                return False
        if self.id in committee:
            others = [p for p in committee if p != self.id]
            max_sus = max([self.suspicions[p] for p in others], default=0.0)
            return max_sus < 0.50
        else:
            avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
            return avg_sus < 0.45
    else:
        if self.profile == InternProfile.A_AGGRESSIVE:
            return (self.id in committee) or (self.rng.random() < 0.30)
        elif self.profile == InternProfile.B_SLEEPER:
            if contract.tier <= 2:
                return True
            if self.id in committee:
                return True
            return self.rng.random() < 0.20
        elif self.profile == InternProfile.C_HEDGE:
            if self.id in committee:
                return True
            return self.rng.random() < 0.25
    return True

PlayerAI.vote_on_proposal = strict_vote_on_proposal

def strict_choose_optimal_committee(chair: PlayerAI, players: List[PlayerAI], contract: ContractSpec, declarations: Dict[int, PlayerDeclaration]):
    c_size = contract.committee_size
    clean_pids = [p.id for p in players if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.60]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in players if p.id not in chair.known_traitors]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in players]

    candidate_comms = list(itertools.combinations(clean_pids, c_size))
    evaluated_comms = []

    for comm in candidate_comms:
        supplier_id = None
        if contract.req_commodity is not None:
            suppliers = [pid for pid in comm if declarations[pid].claims_req]
            if len(suppliers) < contract.req_commodity_count:
                continue
            suppliers.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid].req_commodity_value))
            supplier_id = suppliers[0]

        total_declared = sum(declarations[pid].claimed_value for pid in comm)
        is_viable = (total_declared >= contract.target_value)
        avg_sus = sum(chair.suspicions[pid] for pid in comm if pid != chair.id) / len(comm)
        has_chair = (chair.id in comm)
        bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)

        evaluated_comms.append({
            'comm': list(comm),
            'supplier_id': supplier_id,
            'is_viable': is_viable,
            'avg_sus': avg_sus,
            'has_chair': has_chair,
            'bench_count': bench_count,
            'total_declared': total_declared
        })

    if not evaluated_comms:
        chosen = [chair.id] + [p for p in clean_pids if p != chair.id][:c_size - 1]
        return chosen, (chair.id if declarations[chair.id].claims_req else None)

    evaluated_comms.sort(key=lambda x: (
        not x['is_viable'],
        x['bench_count'],
        x['avg_sus'],
        not x['has_chair'],
        -x['total_declared']
    ))

    best = evaluated_comms[0]
    return best['comm'], best['supplier_id']

import btg_simulation
btg_simulation.choose_optimal_committee = strict_choose_optimal_committee

n = 20000
results = []
profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

for i in range(n):
    prof = random.choice(profiles)
    res = simulate_game(i, prof, seed=888000 + i)
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
    print(f"  * {sc:<10}: {cnt:>6,d} ({(cnt/n)*100:5.2f}%)")
