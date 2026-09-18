import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

for seed in range(5):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    print(f"\n================ MATCH {seed} (Winner: {match['winner']}) ================")
    print(f"Roles: {roles}")
    for r in match['rounds_data']:
        r_num = r['round_num']
        chair = r['chair_id']
        comm = r['committee']
        success = r['is_success']
        total_val = r.get('total_value', '?')
        target = r['contract']['target']
        req = r['contract']['req_commodity']
        has_req = r['has_req']
        roles_comm = [f"P{pid}({roles[pid][0]})" for pid in comm]
        chair_str = f"P{chair}({roles[chair][0]})"
        cards = {d['player_id']: [c['type'] for c in d['cards']] for d in r.get('submitted', [])}
        sus = r['suspicions']['by_banker']
        
        print(f"R{r_num} | Chair {chair_str} | Comm: {roles_comm} | Target: {target} (req={req}) | Success: {success} (Val: {total_val}, has_req={has_req})")
        print(f"   Submitted: {cards}")
        banker_ids = [pid for pid, ro in roles.items() if ro in ('Banqueiro', Role.BANKER.value)]
        sus_str = " | ".join([f"B{b}->{[f'P{k}:{round(v,2)}' for k,v in sus[b].items() if k!=b]}" for b in banker_ids])
        print(f"   Suspicions: {sus_str}")
