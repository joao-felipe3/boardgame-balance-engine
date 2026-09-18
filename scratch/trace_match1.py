import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile

res = simulate_single_match(1, seed=123401, record_trace=True)
meta = res['players_metadata']
roles = {p['id']: p['role'] for p in meta}
print(f"Roles: {roles}")
for r in res['rounds_data']:
    rnd = r['round_num']
    c = r['contract']
    print(f"\nR{rnd} (T{c['tier']}, Meta {c['target']}, Req {c['req_commodity']}):")
    print(f"  Chair: P{r['chair_id']}, Comm: {r['committee']}, Success: {r['is_success']}")
    print(f"  Suspicions by P0: {r['suspicions']['by_banker'].get(0)}")
    print(f"  Submitted: {[(cd['player_id'], [x['name'] for x in cd['cards']], cd['tokens_spent']) for cd in r['submitted']]}")
