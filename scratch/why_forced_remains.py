import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
from collections import Counter

# Inspect 50 matches that had forced_committees > 0
forced_cases = []

# Wrap simulate_single_match to inspect every forced round
for s in range(200):
    res = simulate_single_match(s, seed=555000 + s, record_trace=True)
    if res['forced_committees'] > 0:
        forced_cases.append(res)
        if len(forced_cases) >= 3:
            break

print(f"Total forced matches found: {len(forced_cases)}")
for idx, res in enumerate(forced_cases):
    meta = res['players_metadata']
    roles = {p['id']: p['role'] for p in meta}
    print(f"\n{'='*75}\nCASO FORÇADO {idx+1} (Winner: {res['winner']}, Forced: {res['forced_committees']})")
    print(f"Papéis: {roles}")
    for r in res['rounds_data']:
        v_dict = r['votes']
        v_yes = [pid for pid, v in v_dict.items() if v]
        v_no = [pid for pid, v in v_dict.items() if not v]
        c = r['contract']
        print(f"  R{r['round_num']} (T{c['tier']}): Chair P{r['chair_id']} ({roles[r['chair_id']]}) -> Comm {r['committee']}")
        print(f"    Votos: SIM={v_yes}, NAO={v_no} | Sucesso={r['is_success']}")
