import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

burned_reasons = {}

for seed in range(100):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = [pid for pid, r in roles.items() if r in ('Banqueiro', Role.BANKER.value)]
    
    for r in match['rounds_data']:
        sus = r['suspicions']['by_banker']
        # check if any banker suspects another banker >= 0.50
        for b1 in banker_ids:
            for b2 in banker_ids:
                if b1 != b2 and sus[b1].get(b2, 0) >= 0.50:
                    comm = r['committee']
                    succ = r['is_success']
                    r_num = r['round_num']
                    key = f"R{r_num}_in_comm:{b2 in comm}_chair:{r['chair_id']==b2}_succ:{succ}"
                    burned_reasons[key] = burned_reasons.get(key, 0) + 1

for k, v in sorted(burned_reasons.items(), key=lambda x: -x[1])[:15]:
    print(f"{k}: {v}")
