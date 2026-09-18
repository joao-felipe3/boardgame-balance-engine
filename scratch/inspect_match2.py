import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile

res = simulate_single_match(2, seed=987652, record_trace=True)
meta = res['players_metadata']
roles = {p['id']: p['role'] for p in meta}
print(f"Match 2 roles: {roles}")
for r in res['rounds_data']:
    rnd = r['round_num']
    c = r['contract']
    print(f"\nR{rnd} (Tier {c['tier']}, Meta {c['target']}, Req {c['req_commodity']}):")
    print(f"  Chair: P{r['chair_id']}, Comm: {r['committee']}")
    print(f"  Declarations: {[(pid, d['claims_req'], d['claimed_val']) for pid, d in r['declarations'].items()]}")
    for cd in r['submitted']:
        print(f"  Submitted by P{cd['player_id']} ({roles[cd['player_id']]}): {[c['name'] for c in cd['cards']]}, Tokens: {cd['tokens_spent']}")
