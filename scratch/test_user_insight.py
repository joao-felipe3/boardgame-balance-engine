import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Vamos verificar quantas vezes um comitê que falha tinha exatamente 1 novato e veteranos
from src.btg import simulate_single_match, Role

single_newcomer_fails = 0
total_fails_tier3_plus = 0

for seed in range(500):
    match = simulate_single_match(seed, seed=888800 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    intern_ids = set([pid for pid, r in roles.items() if r in ('Estagiario', 'Estagiário')])
    
    passed_members = set()
    for r in match['rounds_data']:
        if r['is_success']:
            passed_members.update(r['committee'])
        else:
            tier = r['contract']['tier']
            if tier >= 3:
                total_fails_tier3_plus += 1
                comm = r['committee']
                vets = [p for p in comm if p in passed_members]
                news = [p for p in comm if p not in passed_members]
                if len(news) == 1 and len(vets) >= 1:
                    culprit = news[0]
                    is_intern = culprit in intern_ids
                    if is_intern:
                        single_newcomer_fails += 1

print(f"Total falhas no Tier 3+: {total_fails_tier3_plus}")
print(f"Falhas onde havia EXATAMENTE 1 novato com veteranos e o novato ERA O ESTAGIÁRIO: {single_newcomer_fails} ({single_newcomer_fails/total_fails_tier3_plus*100:.1f}%)")
